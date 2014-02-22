ansible-cloudsigma-inventory
============================

Script for retreive Ansible inventory from Cloudsigma

# Example commands

Ping all your device (need ssh keys on each servers)
    ansible -i cloudsigma-inventory.py -m ping

# Notes
- You can have problem if some server have the same name ( If it's your case : use dns_name meta for correct that )
