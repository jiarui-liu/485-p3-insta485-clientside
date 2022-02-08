"""
Insta485 login page view.

URLs include:
/users/<user_url_slug>/
"""


import flask
from werkzeug.exceptions import abort
import insta485


def context_generator_users(logname, username):
    """User information."""
    connection = insta485.model.get_db()
    context = {}
    context["logname"], context["username"] = logname, username

    # get fullname
    cur = connection.execute(
        "SELECT fullname FROM users WHERE username=?", (username,)
    ).fetchall()
    # check username existence
    if (cur) == 0:
        abort(404, 'You try to access a user that does not exist.')
    context["fullname"] = cur[0]["fullname"]

    # get following number
    cur = connection.execute(
        "SELECT username2 FROM following WHERE username1=?", (username, )
    ).fetchall()
    context["following"] = len(cur)

    # get follower number
    cur = connection.execute(
        "SELECT username1 FROM following WHERE username2=?", (username,)
    ).fetchall()
    context["followers"] = len(cur)

    # get logname_follows_username
    cur = connection.execute(
        "SELECT * FROM following WHERE username1=? AND username2=?",
        (logname, username,)).fetchall()
    if len(cur) == 0:
        context["logname_follows_username"] = False
    else:
        context["logname_follows_username"] = True

    # get posts information
    posts = connection.execute(
        "SELECT postid, filename FROM posts WHERE owner=?", (username,)
    ).fetchall()
    context["total_posts"] = len(posts)
    context["posts"] = posts

    return context


@insta485.app.route('/users/<username>/')
def user_page(username):
    """GET /users/<user_url_slug>."""
    # the 'username' below has nothing to do with
    # the passed-in argument <username>
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    context = context_generator_users(logname, username)
    return flask.render_template("user.html", **context)


@insta485.app.route('/following/', methods=['POST'])
def operation():
    """POST /following/?target=URL."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    operations = flask.request.form['operation']
    connection = insta485.model.get_db()

    # insert the following pair into the database
    if operations == "follow":
        username = flask.request.form['username']
        cur = connection.execute(
            "SELECT username2 FROM following WHERE username1 = ?", (logname, )
        ).fetchall()
        for cur_item in cur:
            if cur_item['username2'] == username:
                abort(409, 'You try to follow a user \
                    that you have already followed')
        connection.execute(
            "INSERT INTO following(username1, username2) VALUES (?,?) ",
            (logname, username))

    # delete the following pair from the database
    elif operations == "unfollow":
        username = flask.request.form['username']
        cur = connection.execute(
            "SELECT username2 FROM following WHERE username1 = ?", (logname, )
        ).fetchall()
        flag = 0
        for cur_item in cur:
            if cur_item['username2'] == username:
                flag = 1
        if not flag:
            abort(409, 'You try to unfollow a user that you do not follow.')
        connection.execute(
            "DELETE FROM following WHERE username1 = ? AND username2 = ?",
            (logname, username))
    target = flask.request.args.get('target')
    if not target:
        target = '/'
    return flask.redirect(target)
