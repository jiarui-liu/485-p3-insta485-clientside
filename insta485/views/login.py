"""
Insta485 login page view.

URLs include:
/accounts/login/, /accounts/logout/
"""


import flask
import insta485


@insta485.app.route('/accounts/login/')
def log_in_page():
    """GET /accounts/login/."""
    return flask.render_template('login.html')


@insta485.app.route('/accounts/logout/', methods=['POST'])
def log_out_page():
    """POST /accounts/logout/."""
    # whether or not username is in the session does not matter
    flask.session.clear()
    return flask.redirect(flask.url_for('log_in_page'))
