"""REST API for posts."""
from tracemalloc import start
import flask
import insta485
import hashlib
import uuid
from flask import jsonify, session


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
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def authenticate():
  """Validate the username and password / the user is logging in."""
  if flask.request.authorization is None:
    if 'username' not in flask.session:
      raise InvalidUsage("Forbidden", status_code=403)
    return flask.session['username'],0

  username = flask.request.authorization['username']
  password = flask.request.authorization['password']

  if not username or not password:
    raise InvalidUsage("Forbidden", status_code=403)
  
  return username,password



def context_generator(username, postid=None):
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

  num_post = len(posts)
  postid_lte = flask.request.args.get("postid_lte", type=int)
  page = flask.request.args.get("page",type=int)
  size = flask.request.args.get("size",type=int)
  

  if size is None:
    size=10
  else:
    context['url'] += "?size="+str(size)

  if page is None:
    page=0
  else:
    context['url'] += "&page="+str(page)

  if postid_lte is None:
    postid_lte=posts[0]['postid']
  else:
    context['url'] += "&postid_lte="+str(postid_lte)

  
  if size < 0 or page < 0:
    raise InvalidUsage("Bad request", status_code=400)
  
  start_idx = 0
  for i in range(num_post):
    if posts[i]["postid"] == postid_lte:
      start_idx = i
      break
    elif posts[i]["postid"] < postid_lte:
      start_idx = i
      break
  start_idx += page*size

  count = 0
  while start_idx < num_post and count < size:
    id = posts[start_idx]["postid"]
    if id <= postid_lte:
      context["results"].append({"postid":id,"url":flask.request.path+str(id)+"/"})
      count += 1
    start_idx += 1

  if count == size:
    context['next'] = flask.request.path+"?size="+str(size)+"&page="+str(page+1)+"&postid_lte="+str(postid_lte)
  
  return context
    
@insta485.app.route('/api/v1/posts/')
def get_all_post():
    """Return 10 newest posts."""

    username, password = authenticate()
    if password == 0:
      return username
    connection = insta485.model.get_db()
    real_password = connection.execute(
        "SELECT password FROM users WHERE username = ?", (username, )
    ).fetchall()[0]['password']

    password_salt = real_password.split('$')[1]
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = password_salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    my_password = "$".join([algorithm,password_salt,password_hash])

    if my_password != real_password:
      print(password)
      print(real_password)
      raise InvalidUsage("Forbidden", status_code=403)

    context = context_generator(username)
    return flask.jsonify(**context)





@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post detail on postid."""
    username, password = authenticate()
    if password == 0:
      return username

    context = {
        "comments":[],
        "created": "",
        "imgUrl": "",
        "likes": {"lognameLikesThis":False,
                  "numLikes":0,
                  "url":"null"},
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
      return handle_invalid_usage(InvalidUsage("Forbidden", 404))
      
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
            (postid_url_slug,username)
        )
    like = cur.fetchall()
    if like is not None:
      context["likes"]["lognameLikesThis"] = True
      context["likes"]["url"] = "/api/v1/likes/"+str(like[0]["likeid"])+"/"
    
    cur = connection.execute(
            "SELECT * "
            "FROM likes "
            "WHERE postid = ?",
            (postid_url_slug,)
        )
    context["likes"]["numLikes"] = len(cur.fetchall())

   
    return flask.jsonify(**context)