# coding: utf8

import os
import sys
sys.path.append("/opt/docker")

from string import Template
from docker import get_links

APP = ['nodejs', '/opt/bitbot/app.js',]
CONF_FILE = '/opt/bitbot/config.js'
ENV_VARS = [
    'ENABLED',
    'EXCHANGE',
    'PAIR',
    'ASSET',
    'CURRENCY',
    'APIKEY',
    'SECRET',
    'INDICATOR',
    'DATABASE',
    'CANDLESTICK',
]

FALSE_VAL = ['0', 'false', 'none', '']

def check_env():
    for var in ENV_VARS:
        if var not in os.environ:
            raise Exception("{} not in environment".format(var))
        if len(os.environ[var]) == 0:
            raise Exception("{} is not set".format(var))

def check_args(args):
    # set options to default
    if args[1][0] == '-':
        return APP + args
    else:
        args.pop(0)
        return args

def set_mongo():
    """ Set mongo link """
    links = get_links()
    for name, link in links.items():
        if "MONGO_MAJOR" in link["environment"] and len(link["ports"]):
            # return link name and port
            for port in link["ports"]:
                return "{}:{}/{}".format(name, port, os.environ["DATABASE"])
    raise Exception("No mongodb link found")

def clean_env():
    """ Remove config vars from environment """
    for var in ENV_VARS:
        del os.environ[var]
    del os.environ["mongostring"]

def config():
    settings = os.environ
    settings["MONGOSTRING"] = set_mongo()
    if settings["ENABLED"] in FALSE_VAL:
        settings["ENABLED"] = 'false'
    else:
        settings["ENABLED"] = 'true'
    with open (CONF_FILE, "r") as f:
        conf = f.read()
    t = Template(conf)
    with open (CONF_FILE, "w") as f:
        f.write(t.substitute(settings))

def run(args):
    clean_env
    os.execvp(args[0], args)

def main(args):
    try:
        args = check_args(args)
        if args[0] != APP[0] or args[1] != APP[1]:
            return run(args)
        # Check env
        check_env()
        config()
        run(args)
    except Exception as e:
        print(e, file=sys.stderr)

if __name__ == '__main__':
    main(sys.argv)
