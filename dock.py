from docker import Client
import yaml

class DockerController:
    
    def __init__(self):
        self.c = Client(base_url='unix://var/run/docker.sock', version='1.15')
    
        self.start_port = 10000

    def adjust_name(self, name, username, stackid):
        return '%s-%s-%s' % (username, stackid, name)
        
    def start_container(self, cli, name, spec, username, stackid):
        image = spec['image']
        ports = spec['ports'] or []
        command = spec['command']
        name = self.adjust_name(name, username, stackid)
        container = cli.create_container(image=image, command=command)
        port_bindings={}
        for port in ports:
            port_bindings[int(port)] = self.start_port
            self.start_port+=1
        # Need to add links here
        return cli.start(container=container.get('Id'), port_bindings=port_bindings)

    def start_stack(self, username, stackid):
        config = yaml.load(open(stackid + '.yaml'))

        # Need to sort out ordering here
        for name, config in config.iteritems():
            self.start_container(self.c, name, config, username, stackid)