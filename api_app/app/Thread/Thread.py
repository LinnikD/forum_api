from a import api_app
from flask import request, jsonify
from Database import db
from Functions import *

t_prefix = '/db/api/thread'

@api_app.route(t_prefix + "/close/", methods=["POST"])
def thread_close():
    return moderate_thread(get_json(request), 'close')

@api_app.route(t_prefix + "/create/", methods=["POST"])
def thread_create():
    json = request.json
    check_data(json, ['title', 'slug', 'forum', 'isClosed', 'user', 'date', 'message'])
    if "isDeleted" in json:
        deleted = json['isDeleted']
        json['isDeleted'] = deleted
    else:
        deleted = 0
        json['isDeleted'] = False

    closed = json['isClosed']
    json['isClosed'] = closed
    user_id = get_id_by_data(json["user"], 'email')
    forum_id = get_id_by_data(json["forum"], 'name')
    db.insert("""INSERT INTO threads (title, slug, forum_id, closed, deleted, user_id, date, message) 
                 values (%s,%s,%s,%s,%s,%s,%s,%s) """,
              (json["title"], json["slug"], forum_id, closed, deleted, user_id, json['date'], json['message']))
    thread_id = db.query("SELECT LAST_INSERT_ID() as id")
    json['id'] = thread_id[0]['id']
    return send_response(json,'')

@api_app.route(t_prefix + "/details/", methods=["GET"])
def thread_details():
    json = get_json(request)
    check_data(json, ['thread'])
    if 'related' in json:
        t = thread_data(json['thread'], json['related'])
    else:
        t = thread_data(json['thread'])
    return send_response(t, "No such thread found")

@api_app.route(t_prefix + "/list/", methods=["GET"])
def thread_list():
    json = get_json(request)
    return send_response(list_threads(json),'')

@api_app.route(t_prefix + "/listPosts/", methods=["GET"])
def thread_listPosts():
    json = get_json(request)
    check_data(json, ['thread'])
    return send_response(list_posts(json),'')

@api_app.route(t_prefix + "/open/", methods=["POST"])
def thread_open():
    return moderate_thread(get_json(request), 'open')

@api_app.route(t_prefix + "/remove/", methods=["POST"])
def thread_remove():
    return moderate_thread(get_json(request), 'remove')

@api_app.route(t_prefix + "/restore/", methods=["POST"])
def thread_restore():
    return moderate_thread(get_json(request), 'restore')

@api_app.route(t_prefix + "/subscribe/", methods=["POST"])
def thread_subscribe():
    json = get_json(request)
    check_data(json, ['user', 'thread'])
    user_email = get_id_by_data(json['user'], 'email')
    quer = "INSERT INTO subscriptions(users_id, threads_id,active) VALUES (%s,%s,1) ON DUPLICATE KEY UPDATE active=1" 
    db.insert(quer, (user_email, json['thread']))
    return send_response(json,'')

@api_app.route(t_prefix + "/unsubscribe/", methods=["POST"])
def thread_unsubscribe():
    json = get_json(request)
    check_data(json, ['user', 'thread'])
    user_email = get_id_by_data(json['user'], 'email')
    quer = "INSERT INTO subscriptions(users_id, threads_id,active) VALUES (%s,%s,0) ON DUPLICATE KEY UPDATE active=0" 
    db.insert(quer, (user_email, json['thread']))
    return send_response(json,'')

@api_app.route(t_prefix + "/update/", methods=["POST"])
def thread_update():
    json = request.json
    check_data(json, ['thread', 'slug', 'message'])
    db.insert("UPDATE threads SET slug=%s, message=%s, date=date where tid=%s",
              (json['slug'], json['message'], json['thread']))
    return send_response(thread_data(json['thread']), "No such thread found")

@api_app.route(t_prefix + "/vote/", methods=["POST"])
def thread_vote():
    return vote_thread(get_json(request))
