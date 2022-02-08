"""
Insta485 index (main) view.

URLs include:
/
"""
import os
import flask
import arrow
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort
import insta485


# generate all posts related to the logname.  \
# Namely, users the logname is following and logname itself.


def all_posts_generator(connection, logname):
    """Query information from post table."""
    # The following relation is username1 follows username2
    # the most recent post is at the top
    cur = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE owner IN "
        "(SELECT username2 FROM following WHERE username1 = ?) OR owner = ? "
        "ORDER BY postid DESC",
        (logname, logname,)
    )
    return cur


def single_posts_generator(connection, postid):
    """Generate a single post specified by postid."""
    cur = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE postid = ?",
        (postid, )
    )
    return cur


def context_generator_index(logname, postid=None):
    """Generate a context by logname and postid."""
    # Connect to database
    connection = insta485.model.get_db()

    if postid is None:
        cur = all_posts_generator(connection, logname)
    else:
        cur = single_posts_generator(connection, postid)

    # fetchall() return a list of rows
    posts = cur.fetchall()

    # each post is a dictionary
    for post in posts:
        # add in comments for each post
        # oldest comment at the top: order by commentid
        cur = connection.execute(
            "SELECT commentid, owner, text "
            "FROM comments "
            "WHERE postid = ?"
            "ORDER BY commentid",
            (post["postid"],)
        )
        post["comments"] = cur.fetchall()

        # add in likes for each post
        cur = connection.execute(
            "SELECT likeid FROM likes WHERE postid = ?",
            (post["postid"],)
        )
        post["likes"] = len(cur.fetchall())

        # change timestamp to human readable format
        past = arrow.get(post["created"])
        present = arrow.utcnow()
        post["created"] = past.humanize(present)

        # add post owner's image
        cur = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (post["owner"],)
        )
        post["owner_img_url"] = cur.fetchall()[0]['filename']

        # see if log in user liked this post
        cur = connection.execute(
            "SELECT * FROM likes WHERE owner = ? AND postid = ?",
            (logname, post["postid"], )
        )
        post["isLiked"] = len(cur.fetchall())

    # print(posts[0])
    return {"logname": logname, "posts": posts}


@insta485.app.route('/')
def show_index():
    """GET /."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    connection = insta485.model.get_db()
    # check the logname exists in users
    cur = connection.execute(
        "SELECT * FROM users "
        "WHERE username = ?",
        (logname, )
    ).fetchall()
    if len(cur) == 0:
        flask.session.clear()
        return flask.redirect(flask.url_for('log_in_page'))

    # generate all posts in the root page /
    context = context_generator_index(logname)
    return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<path:filename>')
def upload_file(filename):
    """GET /uploads/<filename>."""
    if 'username' not in flask.session:
        abort(403, 'An unauthenticated user attempts to \
              access an uploaded file.')
    connection = insta485.model.get_db()
    cur1 = connection.execute(
        "SELECT filename FROM posts"
    ).fetchall()
    cur2 = connection.execute(
        "SELECT filename FROM users"
    ).fetchall()
    flag = 0
    for cur_item in cur1:
        if filename == cur_item['filename']:
            flag = 1
    for cur_item in cur2:
        if filename == cur_item['filename']:
            flag = 1
    if not flag:
        abort(
            404,
            'An authenticated user attempts to \
                access a file that does not exist.')
    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'],
        filename)


@insta485.app.route('/likes/', methods=['POST'])
def process_like():
    """POST /likes/?target=URL."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    operation = flask.request.form['operation']
    connection = insta485.model.get_db()
    postid = flask.request.form['postid']
    cur = connection.execute(
        "SELECT * FROM likes WHERE owner = ? AND postid = ?",
        (logname, postid, )
    ).fetchall()
    if operation == "like":
        if len(cur) != 0:
            abort(409, 'You try to like a post that you have already liked')
        connection.execute(
            "INSERT INTO likes(owner, postid)  VALUES (?,?)",
            (logname, postid, )
        )
    elif operation == "unlike":
        if len(cur) == 0:
            abort(409, 'You try to unlike a post that you have not liked')
        connection.execute(
            "DELETE FROM likes WHERE owner=? AND postid=?",
            (logname, postid, )
        )
    target = flask.request.args.get('target')
    if not target:
        target = '/'
    return flask.redirect(target)


@insta485.app.route('/comments/', methods=['POST'])
def process_comments():
    """POST /comments/?target=URL."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    operation = flask.request.form['operation']
    connection = insta485.model.get_db()
    if operation == "create":
        postid = flask.request.form['postid']
        text = flask.request.form['text']
        if not text:
            abort(400, 'You try to create an empty comment.')
        connection.execute(
            "INSERT INTO comments(owner, postid, text) VALUES (?,?,?)",
            (logname, postid, text)
        )
    elif operation == 'delete':
        commentid = flask.request.form['commentid']
        cur = connection.execute(
            "SELECT owner FROM comments WHERE commentid = ?", (commentid, )
        ).fetchall()[0]['owner']
        if cur != logname:
            abort(403, 'you try to delete a comment that they do not own.')
        connection.execute(
            "DELETE FROM comments "
            "WHERE commentid = ?",
            (commentid, )
        )
    target = flask.request.args.get('target')
    if not target:
        target = '/'
    return flask.redirect(target)


@insta485.app.route('/posts/', methods=['POST'])
def process_submit():
    """POST /posts/?target=URL."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    operation = flask.request.form['operation']
    connection = insta485.model.get_db()
    if operation == 'create':
        file = flask.request.files['file']
        filename = secure_filename(file.filename)
        if not filename:
            abort(400, 'you try to create a post with an empty file.')
        # use uuid
        uuid_basename = insta485.views.account.generate_filename(filename)
        file.save(
            os.path.join(
                insta485.app.config['UPLOAD_FOLDER'],
                uuid_basename))
        connection.execute(
            "INSERT INTO posts(filename, owner) VALUES (?,?)",
            (uuid_basename, logname))
    elif operation == "delete":
        postid = flask.request.form['postid']
        # if a user tries to delete a post they do not own
        cur = connection.execute(
            "SELECT owner FROM posts WHERE postid = ?", (postid, )
        ).fetchall()[0]['owner']
        if cur != logname:
            abort(403, 'you try to delete a post that you do not own.')
        # remove image file for postid from filesystem
        filename = connection.execute(
            "SELECT filename FROM posts WHERE postid = ?", (postid, )
        ).fetchall()[0]['filename']
        os.remove(os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename))
        # delete everything in the database related to this post
        # delete related likes
        connection.execute(
            "DELETE FROM likes WHERE postid = ?", (postid, )
        )
        # delete related comments
        connection.execute(
            "DELETE FROM comments "
            "WHERE postid = ?",
            (postid, )
        )
        # delete related posts
        connection.execute(
            "DELETE FROM posts "
            "WHERE postid = ?",
            (postid, )
        )
    target = flask.request.args.get('target')
    if not target:
        target = '/users/' + logname + '/'
    return flask.redirect(target)
