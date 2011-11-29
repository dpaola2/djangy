#!/usr/bin/env python
#
# Copy the /etc/hosts file to all other Djangy servers.
#
# We assume there is a line in /etc/hosts of the form "# djangy internal\n",
# and all host lines below that specify the internal IP address of all the
# Djangy servers.  There may be duplicates, e.g., master1.srv.djangy.com and
# worker1.srv.djangy.com might have the same IP address.  We only copy the
# /etc/hosts file to a given IP address once.
#

import re, subprocess

def read_lines(path):
    with open(path, 'r') as f:
        return f.readlines()

def get_hosts():
    in_djangy_section = False
    host_addresses = []
    for etc_hosts_line in read_lines('/etc/hosts'):
        if re.match(r'\s*#\s*djangy\s*internal.*\n', etc_hosts_line):
            in_djangy_section = True
        elif in_djangy_section:
            matches = re.match(r'^\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+', etc_hosts_line)
            if matches:
                host_addresses.append(matches.group(1))
    return set(host_addresses)

if __name__ == '__main__':
    for host in get_hosts():
        print host
        subprocess.call(['scp', '/etc/hosts', host + ':/etc/hosts'])
