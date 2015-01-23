from flask import Flask, render_template, redirect, request
import json
from glob import glob

from dock import DockerController

app = Flask(__name__)

running_stacks = {
}

def get_stack_info():
    ret = {}
    for scope in get_scopes():
        ret[scope] = json.loads(open('%s.json' % scope).read())
#    print ret
    return ret

def get_scopes():
    return [x.split('.')[0] for x in glob('*.yaml')]

@app.route('/')
def index():
    return redirect('/static/index.html')

@app.route('/stacks/')
def get_stacks():
    stacks = []
 #   print json.dumps(get_stack_info(), indent=4)
    for scope, data in get_stack_info().iteritems():
  #      print json.dumps(data, indent=4)
        for k,v in data.iteritems():
    #        print 'value'
   #         print json.dumps(v,indent=4)
            v['scope'] = scope
            stacks.append(v)
    #stacks = [data.values() for scope, data in get_stack_info().iteritems()]
    #print stacks
    return json.dumps(stacks), 200, {'Content-Type': 'application/json'}

@app.route('/running/')
def get_running_stacks():
    global running_stacks
    d = DockerController()
    all_containers = d.running_containers()

    still_going = {}

    for name, stack in running_stacks.iteritems():
        to_remove = []
        for machine, contid in stack['machines'].iteritems():
            if not contid in all_containers:
                # Has gone
                to_remove.append(machine)
        for x in to_remove:
            del stack['machines'][x]
        if len(stack['machines'])>0:
            # Something still going
            still_going[name] = stack
    running_stacks = still_going

    return json.dumps(running_stacks.values()), 200, {'Content-Type': 'application/json'}

@app.route('/stacks/', methods=['POST'])
def create_stack():
    # request.get_json()
    print request.get_json()

    data = request.get_json()

    d = DockerController()
    stack = d.start_stack(data['scope'], data['identifier'], data['stackid'], get_stack_info()[data['scope']][data['stackid']])

    running_stacks[data['scope'] + '-' + data['stackid'] + '-' + data['identifier']] = stack

    return "ok"

@app.route('/scopes/')
def get_scopes_detail():
    return json.dumps(get_scopes())

@app.route('/stacks/<scope>/<identifier>/<stack_id>/<name>/logs/', methods=['GET'])
def log(scope, identifier, stack_id, name):
    d = DockerController()
    return json.dumps(d.get_logs(scope, name, identifier, stack_id), 200, {'Content-Type': 'application/json'})

@app.route('/stacks/<scope>/<identifier>/<stack_id>/', methods=['DELETE'])
def stop_stack(scope, identifier, stack_id):
    d = DockerController()
    d.stop_stack(scope, identifier, stack_id, get_stack_info().get(scope)[stack_id])
    return "ok"

def populate_already_running():
    global running_stacks
    d = DockerController()
    running_stacks = d.get_running_containers(get_stack_info())

if __name__ == '__main__':
    populate_already_running()
    app.run(debug=True, host="0.0.0.0", port=80)
