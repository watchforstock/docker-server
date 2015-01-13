from flask import Flask, render_template, redirect, request
import json

from dock import DockerController

app = Flask(__name__)

stacks = {
    'test1':
    {
        'id': 'test1',
        'name': 'test 1',
        'versions': {
            'db': 'ubuntu-12.04',
            'web': 'ubuntu-14.04'
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
running_stacks = [
    {
        'username': 'test1',
        'stack': {
            'id': 'test1',
            'name': 'test 1',
            'versions': {
                'db': '14',
                'ds': '16',
                'we': '122'
            }
        },
        'ports': [
            {
                'component': 'db',
                'port': '5432'
            }
        ]
    }
]

@app.route('/')
def index():
    return redirect('/static/index.html')

@app.route('/stacks/')
def get_stacks():
    return json.dumps(stacks.values()), 200, {'Content-Type': 'application/json'}

@app.route('/running/')
def get_running_stacks():
    return json.dumps(running_stacks), 200, {'Content-Type': 'application/json'}

@app.route('/stacks/<stack_id>/', methods=['GET'])
def stack_details(stack_id):
    pass

@app.route('/stacks/', methods=['POST'])
def create_stack():
    # request.get_json()
    print request.get_json()

    data = request.get_json()

    d = DockerController()
    d.start_stack(data['username'], data['stackid'], stacks[data['stackid']])

    return "ok"

@app.route('/stacks/<stack_id>/', methods=['DELETE'])
def stop_stack(stack_id):
    pass

def populate_already_running():
    pass

if __name__ == '__main__':
    populate_already_running()
    app.run(debug=True, host="0.0.0.0")
