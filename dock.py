from docker import Client
import yaml
import json
import subprocess

class DockerController:
    
    def __init__(self):
        self.c = Client(base_url='unix://var/run/docker.sock', version='1.15')

    def adjust_name(self, name, username, stackid):
        return '%s-%s-%s' % (username, stackid, name)

    def check_image_exists(self, image,tag):
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
        #for line in self.c.pull(image, tag=tag, stream=True, insecure_registry=True):
        #    pass
#            print(json.dumps(json.loads(line), indent=4))
    def running_containers(self):
        return dict([[x['Id'], 0] for x in self.c.containers(quiet=True)])
        
    def start_container(self, name, spec, tag, username, stackid):
        image = spec['image'] + ':' + tag

        self.check_image_exists(spec['image'], tag)

        ports = spec.get('ports') or []
        links = []
        print 'Sorting links'
        if 'links' in spec:
            all_links = []
            for link in spec.get('links'):
                if ':' in link:
                    all_links.append(link.split(':'))
                else:
                    all_links.append([link, link])
            links = [[self.adjust_name(service, username, stackid),alias] for service,alias in all_links]
        print links
        command = spec.get('command')
        name = self.adjust_name(name, username, stackid)

        try:
            self.c.remove_container(name)
        except:
            pass
        print 'Creating container with name %s' % name
        container = self.c.create_container(image=image, command=command, name=name, ports=ports)
        port_bindings={}
        for port in ports:
            port_bindings[int(port)] = None
        # Need to add links here
        self.c.start(container=container.get('Id'), port_bindings=port_bindings,links=links)

        # Now determine port bindings
        port_mappings = {}
        for port in ports:
            ext_port = self.c.port(container.get('Id'), port)
            port_mappings[port] = ext_port
        return container.get('Id'), image, port_mappings

    def start_stack(self, username, stackid, stack_info):
        config = yaml.load(open('config.yaml'))

        stack = {'username': username, 'stack': stack_info, 'ports': [], 'machines':{}}

        all_machines = config.keys()
        to_build = []

        while len(all_machines)>0:
            unsatisfied = []
            for machine in all_machines:
                links = config[machine].get('links') or []
                if len(links) == 0:
                    # can build now
                    to_build.append(machine)
                elif all([link.split(':')[0] in to_build for link in links]):
                    # all depemdemces satisfied
                    to_build.append(machine)
                else:
                    unsatisfied.append(machine)
            all_machines = unsatisfied

        # Need to sort out ordering here
        for name in to_build:
            conf = config[name] 
            contid, image, ports = self.start_container(name, conf, stack_info['versions'].get(name), username, stack_info['id'])
        #    for port in ports:
            port_info = []
            for cont, other in ports.iteritems():
                port_info.extend([(cont, x['HostPort']) for x in other])
            stack['ports'].append({'component': name, 'port': port_info})
            stack['machines'][name] = contid
        return stack

    def stop_stack(self, username, stackid):
        config = yaml.load(open('config.yaml'))

        stack_info = {
		'id': 'test1'
        }

        for name, config in config.iteritems():
            image_name = self.adjust_name(name, username, stack_info['id'])
            try:
                self.c.stop(image_name)
                self.c.remove_container(image_name)
            except:
                pass
