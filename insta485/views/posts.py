"""
Insta485 posts page view.

URLs include:
/posts/<postid_url_slug>/
"""

import flask
import insta485


@insta485.app.route('/posts/<postid>/')
def posts_page(postid):
    """GET /posts/<postid_url_slug>/."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    context = insta485.views.index.context_generator_index(logname, postid)
    return flask.render_template("post.html", **context)
