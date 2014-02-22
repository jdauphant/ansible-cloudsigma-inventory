#!/usr/bin/env python

'''
Cloudsigma external inventory script
=================================
Generates inventory that Ansible can understand by making API request to
Cloudsigma using the cloudsigma library.

NOTE: This script assumes Ansible is being executed where the environment
variables needed for cloudsigma library have already been set:
    export CLOUDSIGMA_CONFIG='.cloudsigma.conf' (default : ~/.cloudsigma.conf)

Content of .cloudsigma.conf
    api_endpoint = https://zrh.cloudsigma.com/api/2.0/ (needed if you don't use clousigma.ini)
    username = user@domain.com
    password = secret

Since this file includes credentials, it is highly recommended that you set the permission of the file to 600 :
    chmod 600 ~/.cloudsigma.conf

This script can use an optional clousigma.ini file alongside it. You can specify a
different path for this file :
    export CLOUDSIGMA_CONFIG_PATH=/path/cloudsigma.ini

'''

import sys
import os
import cloudsigma
import ConfigParser

try:
    import json
except ImportError:
    import simplejson as json

class CloudsigmaInventory(object):
    def __init__(self):
    	self.api_server = {}
        self.inventory = {}
        self.hostvars = {}
        self.datacenters = ['default']
        self.groups_meta = "groups"
        self.dns_name_meta = "dns_name"

        self.read_settings()

        self.connect_to_datacenters()

        if len(sys.argv) == 2 and sys.argv[1] == '--list':
            self.list()
        elif len(sys.argv) == 3 and sys.argv[1] == '--host':
            self.host(sys.argv[2])
        else:
            print "command.py --list | --host <host>"

    def list(self):
        self.get_servers_from_all_datacenters()
        self.inventory['_meta'] = {'hostvars': self.hostvars}
        print json.dumps(self.inventory)

    def host(self,host):
        print "unsupported"

    def read_settings(self):
        config = ConfigParser.SafeConfigParser()
        default_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cloudsigma.ini')
        config_path = os.environ.get('CLOUDSIGMA_CONFIG_PATH', default_config_path)
        config.read(config_path)

        if config.has_option('cloudsigma','datacenters'):
            self.datacenters = config.get('cloudsigma','datacenters').split(",")
        if config.has_option('cloudsigma','groups_meta'):
            self.groups_meta = config.get('cloudsigma','groups_meta')
        if config.has_option('cloudsigma','dns_name_meta'):
            self.dns_name_meta = config.get('cloudsigma','dns_name_meta')

    def connect_to_datacenters(self):
        for datacenter in self.datacenters:
            if datacenter == 'default':
                self.api_server[datacenter] = cloudsigma.resource.Server()
            else:
                self.api_server[datacenter] = cloudsigma.resource.Server("https://"+datacenter+".cloudsigma.com/api/2.0/")

    def get_servers_from_all_datacenters(self):
        for datacenter in self.datacenters:
            self.get_servers_from_datacenter(datacenter)

    def get_servers_from_datacenter(self,datacenter):
        servers = self.api_server[datacenter].list_detail()
        
        for server in servers:
            self.add_server(server,datacenter)

    def add_server(self,server,datacenter):
        if server['status'] != 'running':
            return
        
        default_hostname = server['name'].lower().replace(' ', '_')
        hostname = getattr(server['meta'], self.dns_name_meta, default_hostname)
        
        self.inventory[server['uuid']] = [hostname]

        if server['meta'].has_key(self.groups_meta):
           for group in server['meta'][self.groups_meta].split(','):
               self.add_server_to_group(hostname,group)

        self.hostvars[hostname]  = {'ansible_ssh_host' : self.find_public_ip(server) }
        
        self.add_server_to_group(hostname,'cloudsigma')
        if datacenter != 'default':
            self.add_server_to_group(hostname, datacenter)

    def add_server_to_group(self,hostname,group):
        if group in self.inventory:
            self.inventory[group].append(hostname);
        else:
            self.inventory[group] = [hostname]
    
    def find_public_ip(self,server):
        for nic in server['nics']:
            if nic['runtime']['interface_type'] == 'public':
                return nic['runtime']['ip_v4']['uuid']

    
CloudsigmaInventory()
