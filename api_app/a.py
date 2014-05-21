from flask import Flask

api_app = Flask(__name__)

import sys
sys.path.insert(0, '/home/uzzz/forum_api/api_app')

from User import User
from Forum import Forum
from Post import Post
from Thread import Thread
from Clear import *

if __name__ == '__main__':
    api_app.run()