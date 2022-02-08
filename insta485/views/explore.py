"""
Insta485 explore page view.

URLs include:
/explore/
"""
import flask
import insta485


def explore_generator(logname):
    """Explore page context."""
    connection = insta485.model.get_db()

    not_following = connection.execute(
        "SELECT username FROM users "
        "WHERE username NOT IN "
        "(SELECT username2 FROM following WHERE username1 = ?) "
        "AND username != ?",
        (logname, logname,)).fetchall()

    for user in not_following:
        cur = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (user["username"],)
        )
        user["user_img_url"] = cur.fetchall()[0]['filename']

    return {"logname": logname, "not_following": not_following}


@insta485.app.route('/explore/')
def explore_page():
    """GET /explore/."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    context = explore_generator(logname)
    return flask.render_template("explore.html", **context)
