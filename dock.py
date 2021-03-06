from docker import Client
import yaml
import json
import subprocess
import socket 
import time
from collections import defaultdict, deque

class DockerController:
    
    def __init__(self):
        self.c = Client(base_url='unix://var/run/docker.sock', version='1.15')

    def adjust_name(self, scope, name, identifier, stackid):
        ''' generate a container name '''
        return '%s-%s-%s-%s' % (scope, identifier, stackid, name)

    def get_logs(self, scope, name, identifier, stackid):
        name = self.adjust_name(scope, name, identifier, stackid)
        return [self.c.logs(container=name, stdout=True, stderr=True, timestamps=True, tail=100).splitlines()]

    def check_image_exists(self, image, tag):
        images = self.c.images()
        target = '%s:%s' % (image, tag)
        for img in images:
            for t in img['RepoTags']:
                if t == target:
                    print 'Found matching image'
                    return
        # Need to get the image locally
        print 'Pulling image %s:%s' % (image, tag)
        subprocess.call(['docker', 'pull', '%s:%s' % (image, tag)])
        # This call isn't running for some reason
        # self.c.pull(image, tag=tag, insecure_registry=True)

    def running_containers(self):
        ''' Get all the IDs of all running containers '''
        return dict([[x['Id'], 0] for x in self.c.containers(quiet=True)])
        
    def get_links(self, scope, spec, identifier, stackid):
        links = []
        
        if 'links' in spec:
            all_links = []
            for link in spec.get('links'):
                if ':' in link:
                    all_links.append(link.split(':'))
                else:
                    all_links.append([link, link])
            links = [[self.adjust_name(scope, service, identifier, stackid),alias] for service,alias in all_links]
        return links

    def check_port_open(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        return result==0

    def wait_for_port_open(self, port, timeout):
        for i in range(timeout):
            if self.check_port_open(port):
                return True
            time.sleep(1)
        return False

    def start_container(self, scope, name, spec, tag, identifier, stackid):
        image = spec['image'] + ':' + tag

        # Pull the image if required
        self.check_image_exists(spec['image'], tag)

        ports = spec.get('ports') or []
        post_delay = spec.get('delay')
        links = self.get_links(scope, spec, identifier, stackid)
        command = spec.get('command')
        name = self.adjust_name(scope, name, identifier, stackid)

        # Remove any existing container with the same name
        try:
            self.c.remove_container(name)
        except:
            pass
        
        print 'Creating container with name %s' % name
        container = self.c.create_container(image=image, command=command, name=name, ports=ports)

        # Determine port bindings to request
        port_bindings={}
        for port in ports:
            port_bindings[int(port)] = None
        
        self.c.start(container=container.get('Id'), 
                     port_bindings=port_bindings,
                     links=links)

        # Now determine where ports have ended up being mapped
        port_mappings = {}
        for port in ports:
            ext_port = self.c.port(container.get('Id'), port)
            port_mappings[port] = ext_port
            self.wait_for_port_open(int(ext_port[0]['HostPort']), 30)

        if post_delay is not None:
            time.sleep(int(post_delay))

        return container.get('Id'), image, port_mappings

    def get_running_containers(self, stack_config):
        containers = self.c.containers()
        
        stacks = {}
                  
        for container in containers:
            container_id = container['Id']
            names = container['Names']
            ports = container['Ports']
                  
            # Turn name into constituent parts
            scope, identifier, stackid, name = names[0][1:].split('-')      
                
            key = '%s-%s-%s' % (scope, stackid, identifier)
                  
            if key not in stacks:
                stack_info = stack_config.get(scope).get(stackid)
                stacks[key] = {'identifier': identifier, 'stack': stack_info, 'ports': [], 'machines':{}, 'scope': scope}
            
            stacks[key]['machines'][name] = container_id
            
            container_ports = [[x['PrivatePort'], x['PublicPort']] for x in ports if 'PublicPort' in x]
            stacks[key]['ports'].append({'component': name, 'port': container_ports})
                  
        return stacks
            
                  
    def order_machines(self, config):
        ''' Use links to determine order to instantiate containers '''
        all_machines = config.keys()
        to_build = []

        last_length = len(all_machines)
        while len(all_machines)>0:
            unsatisfied = []
            for machine in all_machines:
                links = config[machine].get('links') or []
                if len(links) == 0:
                    # can build now
                    to_build.append(machine)
                elif all([link.split(':')[0] in to_build for link in links]):
                    # all dependencies satisfied
                    to_build.append(machine)
                else:
                    unsatisfied.append(machine)
            all_machines = unsatisfied
            
            if len(all_machines)>0 and len(all_machines)==last_length:
                # We're iterating without doing anything
                raise Exception("Circular or unresolved dependency")
        return to_build
    
    def start_stack(self, scope, identifier, stackid, stack_info):
        config = yaml.load(open(scope + '.yaml'))

        stack = {'identifier': identifier, 'stack': stack_info, 'ports': [], 'machines':{}, 'scope': scope}

        to_build = self.order_machines(config)

        # Need to sort out ordering here
        for container_name in to_build:
            
            container_config = config[container_name] 
            container_tag = stack_info['versions'].get(container_name)
            
            container_id, image, ports = self.start_container(scope,
                                                              container_name, 
                                                              container_config, 
                                                              container_tag, 
                                                              identifier, 
                                                              stack_info['id'])

            port_info = []
            for cont, other in ports.iteritems():
                port_info.extend([(cont, x['HostPort']) for x in other])
            stack['ports'].append({'component': container_name, 'port': port_info})
            stack['machines'][container_name] = container_id
        return stack

    def stop_stack(self, scope, identifier, stackid, stack_info):
        config = yaml.load(open(scope + '.yaml'))

        for name, config in config.iteritems():
            image_name = self.adjust_name(scope, name, identifier, stack_info['id'])
            try:
                self.c.stop(image_name)
                self.c.remove_container(image_name)
            except:
                pass
