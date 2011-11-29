import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from models import *
