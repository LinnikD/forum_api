from a import api_app
from flask import request, jsonify
from Database import db
from Functions import *

f_prefix = '/db/api/forum' 

@api_app.route(f_prefix + "/create/", methods=["POST"])
def forum_create():
    json = request.json
    check_data(json, ['name', 'short_name', 'user'])
    user_id = get_id_by_data(json['user'], 'email')
    db.insert("INSERT INTO forums (fname,shortname,founder_id) values (%s,%s,%s)",
              (json['name'], json['short_name'], user_id))
    forum_id = db.query("SELECT LAST_INSERT_ID() as id")
    json['id'] = forum_id[0]['id']
    return send_response(json,'')

@api_app.route(f_prefix + "/details/", methods=["GET"])
def forum_details():
    json = get_json(request)
    check_data(json, ['forum'])
    det = forum_data(json['forum'])
    if det.__len__() != 0:
        if 'related' in json:
            if 'user' in json['related']:
                det['user'] = user_data(det['user'], 'email')
    return send_response(det, "No such forum found")

@api_app.route(f_prefix + "/listPosts/", methods=["GET"])
def forum_listPosts():
    json = get_json(request)
    check_data(json, ['forum'])
    return send_response(list_posts(json),'')

@api_app.route(f_prefix + "/listThreads/", methods=["GET"])
def forum_listThreads():
    json = get_json(request)
    check_data(json, ['forum'])
    return send_response(list_threads(json),'') 

@api_app.route(f_prefix + "/listUsers/", methods=["GET"])
def forum_listUsers():
    json = get_json(request)
    check_data(json, ['forum'])
    return send_response(list_users(json),'')
