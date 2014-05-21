from flask import Flask

api_app = Flask(__name__)

from User import User
from Forum import Forum
from Post import Post
from Thread import Thread
from Clear import *

