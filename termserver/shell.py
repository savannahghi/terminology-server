#!/usr/bin/env python
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
working_dir = os.path.dirname(__file__)
os.chdir(working_dir)
