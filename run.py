#!flask/bin/python

import sys
sys.path.insert(0, '/root/forum_api/api_app')

from a import api_app

api_app.run(host='0.0.0.0',port=80)
