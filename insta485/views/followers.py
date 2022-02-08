"""
Insta485 followers page view.

URLs include:
/users/<user_url_slug>/followers/
"""

import flask
from werkzeug.exceptions import abort
import insta485


@insta485.app.route('/users/<username>/followers/')
def followers_page(username):
    """GET /users/<user_url_slug>/followers/."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session["username"]

    connection = insta485.model.get_db()
    cur1 = connection.execute(
        "SELECT username1 FROM following WHERE username2 = ?", (username,)
    ).fetchall()
    follower_names = [elt['username1'] for elt in cur1]

    cur1 = connection.execute(
        "SELECT * FROM users WHERE username=?", (username,)
    ).fetchall()

    # check username existence
    if len(cur1) == 0:
        abort(404, 'You try to access a user that does not exist.')

    followers_info = []
    for follower_name in follower_names:
        follower_dict = {}
        follower_dict["username"] = follower_name
        cur = connection.execute(
            "SELECT filename FROM users WHERE username=?", (follower_name,)
        ).fetchall()
        follower_dict["user_img_url"] = cur[0]["filename"]
        cur = connection.execute(
            "SELECT * FROM following WHERE username1=? AND username2=?",
            (logname, follower_name,)).fetchall()
        if len(cur) == 0:
            follower_dict["logname_follows_username"] = False
        else:
            follower_dict["logname_follows_username"] = True
        followers_info.append(follower_dict)

    context = {"logname": logname, "followers": followers_info}
    return flask.render_template("followers.html", **context)
