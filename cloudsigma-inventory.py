#!/usr/bin/env python

'''
Cloudsigma external inventory script
=================================
Generates inventory that Ansible can understand by making API request to
Cloudsigma using the cloudsigma library.

NOTE: This script assumes Ansible is being executed where the environment
variables needed for cloudsigma library have already been set:
    export CLOUDSIGMA_CONFIG='.cloudsigma.conf' (default : ~/.cloudsigma.conf)

Content of .cloudsigma.conf (change zrh by lvs if your use las vegas datacenter)
    api_endpoint = https://zrh.cloudsigma.com/api/2.0/
    ws_endpoint = wss://direct.zrh.cloudsigma.com/websocket
    username = user@domain.com
    password = secret

Since this file includes credentials, it is highly recommended that you set the permission of the file to 600 :
    chmod 600 ~/.cloudsigma.conf
'''

import sys
import cloudsigma
from pprint import pprint

try:
    import json
except ImportError:
    import simplejson as json

class CloudsigmaInventory(object):
    def __init__(self):
    	self.server = cloudsigma.resource.Server()
        self.inventory = {}
        self.hostvars = {}

        if len(sys.argv) == 2 and sys.argv[1] == '--list':
            self.get_servers()
            self.inventory['_meta'] = {'hostvars': self.hostvars}
            print json.dumps(self.inventory)
#        elif len(sys.argv) == 3 and sys.argv[1] == '--host':
        else:
            print "command.py --list | --host <host>"
        
    def get_servers(self):
        servers = self.server.list_detail()
        
        for server in servers:
            self.add_server(server)

    def add_server(self,server):
        if server['status'] != 'running':
            return
        
        default_ansible_host = server['name'].lower().replace(' ', '_')
        ansible_host = getattr(server['meta'], 'dns_name', default_ansible_host)
        
        self.inventory[server['uuid']] = [ansible_host]

        if hasattr(server['meta'],'groups'):
            for group in server['meta']['groups'].split(','):
                self.push(self.inventory,group,ansible_host)

        self.hostvars[ansible_host]  = {'ansible_ssh_host' : server['nics'][0]['runtime']['ip_v4']['uuid'] }
        self.push(self.inventory, 'cloudsigma',ansible_host)

    def push(self, mydict, key, element):
        if key in mydict:
            mydict[key].append(element);
        else:
            mydict[key] = [element]
    

# Run the script
CloudsigmaInventory()
