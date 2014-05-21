from a import api_app
from flask import request, jsonify
from Database import db
from Functions import *

u_prefix = '/db/api/user'

@api_app.route(u_prefix + "/create/", methods=["POST"])
def user_create():
    json = request.json
    response = {}
    response["name"] = json["name"]
    response["email"] = json["email"]
    uniq = get_id_by_data(json['email'], 'email')
    if uniq != -1:
        return send_response(user_data(uniq, 'id')) 
    if "isAnonymous" in json:
        response["isAnonymous"] = json["isAnonymous"]
    else:
        response["isAnonymous"] = False
    if response["isAnonymous"] is True:
        db.insert("INSERT INTO users(email,anonymous) values (%s,%s) ", (response["email"], response["isAnonymous"]))
        id = db.query("SELECT LAST_INSERT_ID() as id")
        response["id"] = id[0]["id"]
        response['name'] = None
        response = {u'code': 0, u'response': response}
        return jsonify(response)
    response["username"] = json["username"]
    response["about"] = json["about"]
    print "Inserting..."
    db.insert("INSERT INTO users(username,email,about,name) values (%s,%s,%s,%s) ",
              (response["username"], response["email"], response["about"], response["name"]))
    id = db.query("SELECT LAST_INSERT_ID() as id")
    response["id"] = id[0]["id"]
    response = {u'code': 0, u'response': response}
    return jsonify(response)

@api_app.route(u_prefix + "/details/", methods=["GET"])
def user_details():
    json = get_json(request)
    check_data(json, ['user'])
    return send_response(user_data(json["user"], 'email'), "No such user found")

@api_app.route(u_prefix + "/follow/", methods=["POST"])
def user_follow():
    json = request.json
    follower = json["follower"]
    followee = json["followee"]
    follower_id = db.query("SELECT * FROM users where email=%s", follower)[0]['id']
    followee_id = db.query("SELECT * FROM users where email=%s", followee)[0]['id']
    db.insert("INSERT INTO followers (follower,followee) values (%s, %s) ON DUPLICATE KEY UPDATE active=1",
              (follower_id, followee_id))
    return send_response(user_data(follower_id, 'id'), "No such user found")

@api_app.route(u_prefix + "/listFollowers/", methods=["GET"])
def user_listFollowers(): 
    json = get_json(request) 
    params = ()
    id = get_user_by_email(json['user'])['id']
    params += (id,)
    quer = """SELECT %s from followers inner join users u on %s=u.id where %s=%%s AND active=1""" % (
    'follower', 'follower', 'followee')
    if 'since_id' in json:
        quer += ' AND %s >= %%s' % ('follower')
        params += (json['since_id'],)
    if 'order' in json:
        order = json['order']
    else:
        order = 'desc'
    quer += ' ORDER BY u.name %s ' % (order)
    if 'limit' in json:
        quer += ' LIMIT %s' % (json['limit'])
    followers = db.query(quer, params);
    res = []
    for folw in followers:
        res.append(user_data(folw['follower'], 'id'))
    return send_response(res,'')

@api_app.route(u_prefix + "/listFollowing/", methods=["GET"])
def user_listFollowing():
    json = get_json(request)
    params = ()
    id = get_user_by_email(json['user'])['id']
    params += (id,)
    quer = """SELECT %s from followers inner join users u on %s=u.id where %s=%%s AND active=1""" % (
    'followee', 'followee', 'follower')
    if 'since_id' in json:
        quer += ' AND %s >= %%s' % ('followee')
        params += (json['since_id'],)
    if 'order' in json:
        order = json['order']
    else:
        order = 'desc'
    quer += ' ORDER BY u.name %s ' % (order)
    if 'limit' in json:
        quer += ' LIMIT %s' % (json['limit'])
    followers = db.query(quer, params);
    res = []
    for folw in followers:
        res.append(user_data(folw['followee'], 'id'))
    return send_response(res,'')

@api_app.route(u_prefix + "/listPosts/", methods=["GET"])
def user_listPosts():
    return send_response(list_posts(get_json(request)),'')

@api_app.route(u_prefix + "/unfollow/", methods=["POST"])
def user_unfollow():
    json = request.json
    follower = json["follower"]
    followee = json["followee"]
    follower_id = db.query("SELECT * FROM users where email=%s", follower)[0]['id']
    followee_id = db.query("SELECT * FROM users where email=%s", followee)[0]['id']
    db.insert("UPDATE followers SET active=0 where follower=%s AND followee=%s", (follower_id, followee_id))
    return send_response(user_data(follower_id, 'id'), "No such user found")

@api_app.route(u_prefix + "/updateProfile/", methods=["POST"])
def user_updateprofile():
    json = request.json
    check_data(json, ['about', 'user', 'name'])
    if get_id_by_data(json['user'], 'email') == -1:
        return send_response({}, "No such user found")
    db.insert("UPDATE users SET about=%s, name=%s where email=%s", (json['about'], json['name'], json['user']))
    return send_response(user_data(json['user'], 'email'), "No such user found")
