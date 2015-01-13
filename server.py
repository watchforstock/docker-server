from flask import Flask, render_template, redirect, request
import json

from dock import DockerController

app = Flask(__name__)

stacks = {
    'timsk395':
    {
        'id': 'timsk395',
        'name': 'TIMSK 395 permissioning in web ui',
        'versions': {
            'db': '9',
            'ws': '117',
            'es': '14',
            'ds': '14',
            'as': '25',
            'asinit':'25'
        }
    },
    'test2':
    {
        'id': 'test2',
        'name': 'test 2',
        'versions': {
            'db': 'ubuntu-14.04',
            'web': 'ubuntu-12.04',
        }
    },
}
running_stacks = {
}

@app.route('/')
def index():
    return redirect('/static/index.html')

@app.route('/stacks/')
def get_stacks():
    return json.dumps(stacks.values()), 200, {'Content-Type': 'application/json'}

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

@app.route('/stacks/<stack_id>/', methods=['GET'])
def stack_details(stack_id):
    pass

@app.route('/stacks/', methods=['POST'])
def create_stack():
    # request.get_json()
    print request.get_json()

    data = request.get_json()

    d = DockerController()
    stack = d.start_stack(data['username'], data['stackid'], stacks[data['stackid']])

    running_stacks[data['stackid'] + '-' + data['username']] = stack

    return "ok"

@app.route('/stacks/<stack_id>/', methods=['DELETE'])
def stop_stack(stack_id):
    pass

def populate_already_running():
    pass

if __name__ == '__main__':
    populate_already_running()
    app.run(debug=True, host="0.0.0.0")
