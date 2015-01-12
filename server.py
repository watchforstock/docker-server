from flask import Flask, render_template, redirect, request
import json

app = Flask(__name__)

stacks = [
    {
        'id': 'test1',
        'name': 'test 1',
        'versions': {
            'db': '14',
            'ds': '16',
            'we': '122'
        }
    },
    {
        'id': 'test2',
        'name': 'test 2',
        'versions': {
            'db': '15',
            'ds': '17',
            'we': '128'
        }
    },
]
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
    return json.dumps(stacks), 200, {'Content-Type': 'application/json'}

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
    return "ok"

@app.route('/stacks/<stack_id>/', methods=['DELETE'])
def stop_stack(stack_id):
    pass

def populate_already_running():
    pass

if __name__ == '__main__':
    populate_already_running()
    app.run(debug=True)