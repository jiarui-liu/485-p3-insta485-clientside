"""REST API for posts."""
import flask
import insta485


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv

@insta485.app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def authenticate():
    """Validate the username and password the user is logging in."""
    # authentication with session cookies
    if flask.request.authorization is None:
        if 'username' not in flask.session:
            raise InvalidUsage("Forbidden", status_code=403)
        return flask.session['username']

    # HTTP basic authentication
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']

    # check empty username or password
    if not username or not password:
        raise InvalidUsage("Forbidden", status_code=403)
    
    # get real password from database
    connection = insta485.model.get_db()
    real_password = connection.execute(
        "SELECT password FROM users WHERE username = ?", (username, )
    ).fetchall()[0]['password']
    
    # if password is not correct
    if not insta485.views.account.check_password_hash(password, real_password):
        raise InvalidUsage("Forbidden", status_code=403)

    return username



def context_generator(username, postid=None):
    """Generate a context by logname and postid."""
    # Connect to database
    connection = insta485.model.get_db()

    if postid is None:
        cur = insta485.views.index.all_posts_generator(connection, username)
    else:
        cur = insta485.views.index.single_posts_generator(connection, postid)
    
    posts = cur.fetchall()
    context={"next":"",
                "results":[],
                "url":flask.request.path
            }

    # the length of posts
    num_post = len(posts)
    postid_lte = flask.request.args.get("postid_lte", type=int)
    page = flask.request.args.get("page",type=int)
    size = flask.request.args.get("size",type=int)
    if size is not None or page is not None or postid_lte is not None:
        context['url'] = flask.request.full_path
    else:
        context['url'] = flask.request.path
    
    if size is None:
        size = 10
    if page is None:
        page = 0
    if postid_lte is None:
        if num_post > 0:
            postid_lte = posts[0]['postid']
        else: 
            postid_lte = 0

    # postid_lte is hte ID of the most recent post on the current page
    # consider cases of empty posts

    # check size and page non-negative integers
    if size < 0 or page < 0:
        raise InvalidUsage("Bad request", status_code=400)

    cur = connection.execute(
        "SELECT * FROM posts ORDER BY postid DESC"
    ).fetchall()
    cnt = 0
    for item in cur:
        if item['postid'] > postid_lte:
            cnt += 1
    
    cur = connection.execute(
        "SELECT * FROM posts ORDER BY postid DESC LIMIT ? OFFSET ?", (size, page * size + cnt, )
    ).fetchall()
    if len(cur) >= size:
        for iter in range(size):
            context["results"].append({'postid': cur[iter]['postid'],
            'url': flask.request.path+str(cur[iter]['postid'])+'/'
            })
        new_postid_lte = postid_lte
        context['next'] = flask.request.path+"?size="+str(size)+"&page="+str(page+1)+"&postid_lte="+str(new_postid_lte)
    else:
        for iter in range(len(cur)):
            context["results"].append({'postid': cur[iter]['postid'],
            'url': flask.request.path+str(cur[iter]['postid'])+'/'
            })
    
    return context
    
@insta485.app.route('/api/v1/posts/')
def get_all_post():
    """GET /api/v1/posts/, return 10 newest posts."""
    username = authenticate()
    context = context_generator(username)
    return flask.jsonify(**context), 200

@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """GET /api/v1/posts/<postid>/, return post detail on postid."""
    username = authenticate()

    context = {
        "comments":[],
        "created": "",
        "imgUrl": "",
        "likes": {"lognameLikesThis": False,
                  "numLikes": 0,
                  "url": None},
        "owner": "",
        "ownerImgUrl": "",
        "ownerShowUrl": "",
        "postShowUrl": "",
        "postid": 0,
        "url": ""
    }
    connection = insta485.model.get_db()
     # Select post detail and owner.
    cur = connection.execute(
            "SELECT * "
            "FROM posts "
            "WHERE postid = ?",
            (postid_url_slug,)
    )
    cur = cur.fetchall()
    if len(cur) == 0:
      return handle_invalid_usage(InvalidUsage("Not Found", 404))
      
    owner = cur[0]["owner"]
    context["created"] = cur[0]["created"]
    cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (owner,)
    )
    context["owner"] = owner
    context["ownerImgUrl"] = "/uploads/"+cur.fetchall()[0]["filename"]
    context["ownerShowUrl"] =  "/users/{}/".format(owner)
    context["postShowUrl"] = "/posts/{}/".format(postid_url_slug)
    context["postid"] = postid_url_slug
    context["url"] = "/api/v1/posts/{}/".format(postid_url_slug)

    # Select comment.
    cur = connection.execute(
            "SELECT commentid, owner, text "
            "FROM comments "
            "WHERE postid = ?"
            "ORDER BY commentid",
            (postid_url_slug,)
        )
    for comment in cur.fetchall():
      context["comments"].append({
        "commentid":comment["commentid"],
        "lognameOwnsThis":username==comment["owner"],
        "owner":comment["owner"],
        "ownerShowUrl": "/users/"+ comment["owner"]+"/",
        "text": comment["text"],
        "url": "/api/v1/comments/{}/".format(comment["commentid"])
      })
    # Select image.
    cur = connection.execute(
            "SELECT filename "
            "FROM posts "
            "WHERE postid = ?",
            (postid_url_slug,)
        )
    context["imgUrl"]="/uploads/"+cur.fetchall()[0]["filename"]
    
    # Select likes.
    cur = connection.execute(
            "SELECT likeid "
            "FROM likes "
            "WHERE postid = ? AND owner = ?",
            (postid_url_slug, username,)
        )
    like = cur.fetchall()
    if like:
      context["likes"]["lognameLikesThis"] = True
      context["likes"]["url"] = "/api/v1/likes/"+str(like[0]["likeid"])+"/"
    
    cur = connection.execute(
            "SELECT * "
            "FROM likes "
            "WHERE postid = ?",
            (postid_url_slug,)
        )
    context["likes"]["numLikes"] = len(cur.fetchall())

    return flask.jsonify(**context), 200