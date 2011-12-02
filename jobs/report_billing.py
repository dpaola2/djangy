#! /srv/djangy/run/python-virtual/bin/python
#
# Report usage information to the billing agent.
#
# Author: Dave Paola <dpaola2@gmail.com>
#

from master_api import report_all_usage
import sys

def main():
    return report_all_usage()

if __name__ == '__main__':
    main()
