from flask import request, jsonify
from api_app.Database import db
import urlparse, time

def get_json(request):
    if request.method == 'GET':
        return dict((k, v if len(v) > 1 else v[0] )
                    for k, v in urlparse.parse_qs(request.query_string).iteritems())
    else:
        return request.json

def send_response(data, msg):
    if (data.__len__() == 0) and ( msg != ''):
        return jsonify({u'code': 1, u'message': msg})
    return jsonify({u'code': 0, u'response': data})

def get_user_by_email(email):
    res = db.query("SELECT * FROM users where email=%s", email)
    return res[0]

def get_data_by_id(id, what):
    result = []
    if what == 'following':
        res = db.query("SELECT email FROM followers INNER JOIN users on followee=id where follower=%s and active=1", id)
        for followee in res:
            result.append(followee['email'])
    else:
        if what == 'followers':
            res = db.query("SELECT email FROM followers INNER JOIN users on follower=id where followee=%s and active=1", id)
            for followee in res:
                result.append(followee['email'])
        else:
            if what == 'subscriptions':
                res = db.query("SELECT * FROM subscriptions where users_id=%s AND active=1 order by threads_id desc", id)
                for subs in res:
                    result.append(subs['threads_id'])
            else:
                if what == 'email':
                    res = db.query("SELECT email FROM users where id=%s", id)
                    return res[0]['email']
                else:
                    if what == 'shortname':
                        name = db.query("SELECT shortname from forums where fid=%s", id)
                        return name[0]['shortname']
                    else:
                        raise Exception("Wrong second argument in get_data_by_id()")
    return result

def get_id_by_data(data, what):
    if what == 'email':
        res = db.query("SELECT id FROM users where email=%s", data)
        if res.__len__() > 0:
            return res[0]['id']
        return -1
        return res[0]['id']
    if what == 'slug':
        res = db.query("SELECT tid FROM threads where slug=%s", data)
        return res[0]['tid']
    if what == 'name':
        id = db.query("SELECT fid from forums where shortname=%s", data)
        return id[0]['fid']
    else:
        raise Exception("Wrong second argument in get_id_by_data()")

def check_data(json, data):
    for var in data:
        if var not in json:
            raise Exception("Wrong data")

def user_data(id, what):
    q = "SELECT * FROM users where %s=%%s" % what
    print(q)
    r = db.query(q, id)
    user = {}
    if r.__len__() != 0:
        uid = r[0]["id"]
        user["followers"] = get_data_by_id(uid, 'followers')
        user["following"] = get_data_by_id(uid, 'following')
        user["subscriptions"] = get_data_by_id(uid, 'subscriptions')
        user["id"] = uid
        user["isAnonymous"] = bool(r[0]["anonymous"])
        user["email"] = r[0]["email"]
        user["username"] = r[0]["username"]
        user["about"] = r[0]["about"]
        user["name"] = r[0]["name"]
    return user

def list_users(json):
    method = 'forum_id'
    id = get_id_by_data(json['forum'], 'name')
    try:
        int(id)
    except:  
        id = get_id_by_data(id, 'slug')
    if 'related' in json:
        rel = json['related']
    else:
        rel = []
    query_str = "SELECT distinct user_id FROM posts where forum_id=%s"
    parametrs = ()
    parametrs += (id,)
    if 'since' in json:
        query_str += " AND date >= %s"
        parametrs += (json['since'],)
    if 'since_id' in json:
        query_str += " AND user_id >= %s"
        parametrs += (json['since_id'],)
    if 'order' in json:
        order = json['order']
    else:
        order = 'desc'
    t_order = 'user_id'
    query_str += " ORDER BY %s %s" % (t_order, order)
    if 'limit' in json:
        query_str += " LIMIT %s" % (json['limit'])
    lst = db.query(query_str, parametrs)
    result = []
    if lst.__len__() > 0:
        for ids in lst: 
            thr = user_data(ids['user_id'], 'id')
            result.append(thr)
    return result

def list_posts(json):
    if 'forum' in json:
        method = 'forum_id'
        id = get_id_by_data(json['forum'], 'name')
    if 'user' in json:
        method = 'user_id'
        id = get_id_by_data(json['user'], 'email')
    if 'thread' in json:
        method = 'thread_id'
        id = json['thread']
        try:
            int(id)
        except:  
            id = get_id_by_data(id, 'slug')
    if 'related' in json:
        rel = json['related']
    else:
        rel = []
    query_str = "SELECT all pid FROM posts where %s=%%s" % (method)
    parametrs = ()
    parametrs += (id,)
    if 'since' in json:
        query_str += " AND date >= %s"
        parametrs += (json['since'],)
    if 'since_id' in json:
        query_str += " AND user_id >= %s"
        parametrs += (json['since_id'],)
    if 'order' in json:
        order = json['order']
    else:
        order = 'desc'
    t_order = 'date'
    query_str += " ORDER BY %s %s" % (t_order, order)
    if 'limit' in json:
        query_str += " LIMIT %s" % (json['limit'])
    lst = db.query(query_str, parametrs)
    result = []
    if lst.__len__() > 0:
        for ids in lst: 
            thr = post_data(ids['pid'], rel)
            result.append(thr)
    return result

def list_threads(json):
    if 'forum' in json:
        method = 'forum_id'
        id = get_id_by_data(json['forum'], 'name')
    if 'user' in json:
        method = 'user_id'
        id = get_id_by_data(json['user'], 'email')
    if 'thread' in json:
        method = 'thread_id'
        id = json['thread']
        try:
            int(id)
        except:  
            id = get_id_by_data(id, 'slug')
    if 'related' in json:
        rel = json['related']
    else:
        rel = []
    query_str = "SELECT all tid FROM threads where %s=%%s" % (method)
    parametrs = ()
    parametrs += (id,)
    if 'since' in json:
        query_str += " AND date >= %s"
        parametrs += (json['since'],)
    if 'since_id' in json:
        query_str += " AND user_id >= %s"
        parametrs += (json['since_id'],)
    if 'order' in json:
        order = json['order']
    else:
        order = 'desc'
    t_order = 'date'
    query_str += " ORDER BY %s %s" % (t_order, order)
    if 'limit' in json:
        query_str += " LIMIT %s" % (json['limit'])
    lst = db.query(query_str, parametrs)
    result = []
    if lst.__len__() > 0:
        for ids in lst: 
            thr = thread_data(ids['tid'], rel)
            result.append(thr)
    return result

def forum_data(forum, how=None):
    data = {}
    if how is not None:
        id = how
    else:
        id = 'shortname'
    res = db.query("SELECT * from forums where %s=%%s" % id, forum)
    data['id'] = res[0]['fid']
    data['short_name'] = res[0]['shortname']
    data['name'] = res[0]['fname']
    data['user'] = get_data_by_id(res[0]['founder_id'],'email')
    return data

def moderate_thread(json, action):
    id = json['thread']
    act = 1 if (action == 'close' or action == 'remove') else 0
    targ = 'closed' if ( action == 'close' or action == 'open') else 'deleted'
    if (db.query("SELECT * from threads WHERE tid=%s", id)).__len__() > 0:
        db.insert(
            "UPDATE threads SET date=date, %s=%s " % (targ, act) + " where tid=%s",
            id)
        return send_response(json,'')
    else:
        return send_response({}, "No such %s found" % 'thread')

def thread_data(id, related=None):
    t = db.query("SELECT * from threads WHERE tid=%s", id)
    response = {}
    if t.__len__() != 0:
        if related is not None: 
            if 'user' in related:
                response['user'] = user_data(t[0]['user_id'], 'id')
            if 'forum' in related:
                response['forum'] = forum_data(get_data_by_id(t[0]['forum_id'], 'shortname'))
        if 'user' not in response:
            response['user'] = get_data_by_id(t[0]['user_id'],'email')
        if 'forum' not in response:
            response['forum'] = get_data_by_id(t[0]['forum_id'], 'shortname')
        response['date'] = str(t[0]['date'])
        response['title'] = t[0]['title']
        response['message'] = t[0]['message']
        response['dislikes'] = t[0]['dislikes']
        response['likes'] = t[0]['likes']
        response['points'] = t[0]['likes'] - t[0]['dislikes']
        response['slug'] = t[0]['slug']
        response['id'] = t[0]['tid']
        response['isClosed'] = bool(t[0]['closed'])
        response['isDeleted'] = bool(t[0]['deleted'])
        response['posts'] = (db.query("SELECT COUNT(*) as cnt from posts WHERE thread_id=%s", t[0]['tid']))[0]['cnt']
    return response

def vote_thread(json):
    check_data(json, ['vote', 'thread'])
    vt = int(json['vote'])
    type = 'likes' if (vt > 0) else 'dislikes'
    query = "UPDATE %s SET %s = %s + 1, date=date where %sid=%%s" % (
        'threads', type, type, 't') 
    db.insert(query, json['thread'])
    return send_response(thread_data(json['thread']), "No such thread found")

def post_data(id, related=None):
    p = db.query("SELECT * FROM posts where pid = %s", (id))
    if p.__len__() > 0:
        post = {
            'parent': p[0]['parent'],
            'isApproved': bool(p[0]['approved']),
            'isHighlighted': bool(p[0]['highlighted']),
            'isEdited': bool(p[0]['edited']),
            'isSpam': bool(p[0]['spam']),
            'isDeleted': bool(p[0]['deleted']),
            'date': str(p[0]['date']),
            'thread': p[0]['thread_id'],
            'message': p[0]['message'],
            'id': p[0]['pid'],
            'likes': p[0]['likes'],
            'dislikes': p[0]['dislikes'],
            'points': p[0]['likes'] - p[0]['dislikes']
        }
        if related is not None:
            if 'user' in related:
                post['user'] = user_data(p[0]['user_id'], 'id')
            else:
                post['user'] = get_data_by_id(p[0]['user_id'],'email')
            if 'thread' in related:
                post['thread'] = thread_data(post['thread'])
            if 'forum' in related:
                post['forum'] = forum_data(p[0]['forum_id'], 'fid')
            else:
                post['forum'] = get_data_by_id(p[0]['forum_id'], 'shortname')
        return post
    return {}

def moderate_post(json, action):
    id = json['post']
    act = 0
    if action == 'close' or action == 'remove':
        act = 1
    targ = 'closed' if ( action == 'close' or action == 'open') else 'deleted'
    if db.query("SELECT * from posts WHERE pid=%s", id).__len__() > 0:
        db.insert(
            "UPDATE posts SET date=date, %s=%s " % (targ, act) + " where pid=%s ",
            id)
        return send_response(json,'')
    else:
        return send_response({}, "No such post found")

def vote_post(json):
    check_data(json, ['vote', 'post'])
    vt = int(json['vote'])
    type = 'likes' if (vt > 0) else 'dislikes'
    query = "UPDATE %s SET %s = %s + 1, date=date where %sid=%%s" % (
        'posts', type, type, 'p') 
    db.insert(query, json['post'])
    return send_response(post_data(json['post']), "No such post found")
