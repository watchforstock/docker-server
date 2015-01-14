from flask import Flask, render_template, redirect, request
import json

from dock import DockerController

app = Flask(__name__)

running_stacks = {
}

def get_stack_info():
    return json.loads(open('stacks.json').read())

@app.route('/')
def index():
    return redirect('/static/index.html')

@app.route('/stacks/')
def get_stacks():
    return json.dumps(get_stack_info().values()), 200, {'Content-Type': 'application/json'}

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
    stack = d.start_stack(data['username'], data['stackid'], get_stack_info()[data['stackid']])

    running_stacks[data['stackid'] + '-' + data['username']] = stack

    return "ok"

@app.route('/stacks/<identifier>/<stack_id>/', methods=['DELETE'])
def stop_stack(identifier, stack_id):
    d = DockerController()
    d.stop_stack(identifier, stack_id, get_stack_info()[stack_id])
    return "ok"

def populate_already_running():
    global running_stacks
    d = DockerController()
    running_stacks = d.get_running_containers(get_stack_info())

if __name__ == '__main__':
    populate_already_running()
    app.run(debug=True, host="0.0.0.0")
