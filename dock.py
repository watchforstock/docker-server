from docker import Client
import yaml
import json

class DockerController:
    
    def __init__(self):
        self.c = Client(base_url='unix://var/run/docker.sock', version='1.15')

    def adjust_name(self, name, username, stackid):
        return '%s-%s-%s' % (username, stackid, name)

    def check_image_exists(self, image,tag):
        images = self.c.images(image)
        target = '%s:%s' % (image, tag)
        for img in images:
            for t in img['RepoTags']:
                if t == target:
                    print 'Found matching image'
                    return
        # Need to get the image locally
        print 'Pulling image %s:%s' % (image, tag)
        for line in self.c.pull(image, tag=tag, stream=True, insecure_registry=True):
            pass
#            print(json.dumps(json.loads(line), indent=4))

        
    def start_container(self, name, spec, tag, username, stackid):
        image = spec['image'] + ':' + tag

        self.check_image_exists(spec['image'], tag)

        ports = spec.get('ports') or []
        command = spec['command']
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
        self.c.start(container=container.get('Id'), port_bindings=port_bindings)

        # Now determine port bindings
        port_mappings = {}
        for port in ports:
            ext_port = self.c.port(container.get('Id'), port)
            port_mappings[port] = ext_port
        return port_mappings

    def start_stack(self, username, stackid, stack_info):
        config = yaml.load(open('config.yaml'))

        # Need to sort out ordering here
        for name, config in config.iteritems():
            print self.start_container(name, config, stack_info['versions'].get(name), username, stack_info['id'])

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
