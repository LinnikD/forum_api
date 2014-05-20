from a import api_app
from flask import request, jsonify
from Database import db
from Functions import *

p_prefix = '/db/api/post'

@api_app.route(p_prefix + "/create/", methods=["POST"])
def post_create():
    json = get_json(request)
    check_data(json, ['date', 'thread', 'message', 'user', 'forum'])
    user_id = get_id_by_data(json['user'], 'email')
    forum_id = get_id_by_data(json['forum'], 'name')
    if 'parent' in json:
        par = json['parent']
    else:
        par = None
        json['parent'] = None
    if 'isApproved' in json:
        approv = json['isApproved']
    else:
        approv = 0
        json['isApproved'] = 0
    if 'isHighlighted' in json:
        high = json['isHighlighted']
    else:
        high = 0
        json['isHighlighted'] = 0
    if 'isEdited' in json:
        edit = json['isEdited']
    else:
        edit = 0
        json['isEdited'] = 0
    if 'isSpam' in json:
        spam = json['isSpam']
    else:
        spam = 0
        json['isSpam'] = 0
    if 'isDeleted' in json:
        deleted = json['isDeleted']
    else:
        deleted = 0
        json['isDeleted'] = 0
    db.insert("""INSERT INTO posts (date,thread_id,message,user_id,forum_id,parent,approved,highlighted,edited,spam,deleted) 
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (
    json['date'], json['thread'], json['message'], user_id, forum_id, par, approv, high, edit, spam, deleted))
    post_id = db.query("SELECT LAST_INSERT_ID() as id")[0]['id']
    json['id'] = post_id
    return send_response(json, '')

@api_app.route(p_prefix + "/details/", methods=["GET"])
def post_details():
    json = get_json(request)
    check_data(json, ['post'])
    rel = []
    if 'related' in json:
        rel = json['related']
    return send_response(post_data(json['post'], rel), "No such post")

@api_app.route(p_prefix + "/list/", methods=["GET"])
def post_list():
    return send_response(list_posts(get_json(request)),'')

@api_app.route(p_prefix + "/remove/", methods=["POST"])
def post_remove():
    json = request.json
    check_data(json, ['post'])
    moderate_post(json, 'remove')
    return send_response(json,'')

@api_app.route(p_prefix + "/restore/", methods=["POST"])
def post_restore():
    json = request.json
    check_data(json, ['post'])
    moderate_post(json, 'restore')
    return send_response(json, '')

@api_app.route(p_prefix + "/update/", methods=["POST"])
def post_update():
    json = request.json
    check_data(json, ['post', 'message'])
    db.insert("UPDATE posts SET message=%s, date=date where pid=%s", (json['message'], json['post']))
    return send_response(post_data(json['post']), "No such post found")

@api_app.route(p_prefix + "/vote/", methods=["POST"])
def post_vote():
    return vote_post(get_json(request))
