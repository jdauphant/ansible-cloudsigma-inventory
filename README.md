ansible-cloudsigma-inventory
============================

Script for retreive Ansible inventory from Cloudsigma

Example commands
====

Ping all your device (need ssh keys on each servers)
    ansible -i cloudsigma-inventory.py -m ping
