"""
Insta485 account-related pages view.

URLs include:
/accounts/create/, /accounts/delete/, /accounts/edit/, /accounts/password/
"""

import os
import pathlib
import hashlib
import uuid
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort
import flask
import insta485


def generate_password_hash(password):
    """Generate password hash."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def check_password_hash(password_to_check, password_hash):
    """Check password hash."""
    salt = password_hash.split('$')[1]
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password_to_check
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash_after = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash_after])
    return password_db_string == password_hash


def generate_filename(filename):
    """Generate filename."""
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"
    return uuid_basename


def check_filename(filename_to_check, filename_hash):
    """Check file name."""
    filename_split = os.path.splitext(filename_hash)
    stem = filename_split[0]
    suffix = pathlib.Path(filename_hash).suffix
    uuid_basename = f"{stem}{suffix}"
    return filename_to_check == uuid_basename


@insta485.app.route('/accounts/create/')
def create_page():
    """GET /accounts/create/."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('edit_page'))
    return flask.render_template('create.html')


@insta485.app.route('/accounts/delete/')
def delete_page():
    """GET /accounts/delete/."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template('delete.html', **context)


@insta485.app.route('/accounts/edit/')
def edit_page():
    """GET /accounts/edit/."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    context = {"logname": logname}
    connection = insta485.model.get_db()
    user_info = connection.execute(
        "SELECT fullname, email, filename FROM users "
        "WHERE username = ?",
        (logname, )
    ).fetchall()
    context["user_info"] = user_info
    return flask.render_template('edit.html', **context)


@insta485.app.route('/accounts/password/')
def password_page():
    """GET /accounts/password/."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('log_in_page'))
    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template('password.html', **context)


def process_accounts_login(connection):
    """Process accounts login."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    username = flask.request.form['username']
    password = flask.request.form['password']
    # check empty field
    if not username or not password:
        abort(400, 'Username or password fields are empty')
    cur = connection.execute(
        'SELECT password FROM users WHERE username=?',
        (username,)
    ).fetchall()
    # check username authentication
    if len(cur) == 0:
        abort(403, 'Incorrect username.')
    correct_password = cur[0]['password']
    # check password hash
    if not check_password_hash(password, correct_password):
        abort(403, 'Incorrect password.')
        # set a session cookie
    flask.session.clear()
    flask.session['username'] = username
    return None


def process_accounts_create(connection):
    """Process accounts create."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('edit_page'))
    file = flask.request.files['file']
    fullname = flask.request.form['fullname']
    username = flask.request.form['username']
    email = flask.request.form['email']
    password = flask.request.form['password']
    filename = secure_filename(file.filename)
    # check empty field
    if not fullname or not username \
            or not password or not email or not filename:
        abort(400, 'Username/password/fullname/email/file is empty.')
    cur = connection.execute(
        "SELECT username FROM users"
    ).fetchall()
    # check conflict error
    for cur_item in cur:
        if cur_item['username'] == username:
            abort(
                409,
                'You try to create an account with \
                    an existing username in the database.')
    uuid_basename = generate_filename(filename)
    file.save(
        os.path.join(
            insta485.app.config['UPLOAD_FOLDER'],
            uuid_basename))
    # generate password hash
    password_db_string = generate_password_hash(password)
    connection.execute(
        "INSERT INTO "
        "users(username, fullname, email, filename, password) "
        "VALUES (?, ?, ?, ?, ?)",
        (username, fullname, email, uuid_basename, password_db_string))
    flask.session.clear()
    flask.session['username'] = username
    return None


def process_accounts_delete(connection):
    """Process accounts delete."""
    # check log in
    if 'username' not in flask.session:
        abort(403, 'You are not logged in.')
    logname = flask.session['username']
    # select this user's posts
    postid_list = connection.execute(
        "SELECT postid FROM posts WHERE owner = ?", (logname, )
    ).fetchall()
    # delete related likes to this user from likes table
    for postid in postid_list:
        connection.execute(
            "DELETE FROM likes WHERE postid = ?", (postid['postid'], )
        )
    # delete this user from likes table
    connection.execute(
        "DELETE FROM likes WHERE "
        "owner = ?", (logname, )
    )
    # delete related comments to this user from comment table
    for postid in postid_list:
        connection.execute(
            "DELETE FROM comments WHERE postid = ?", (postid['postid'], )
        )
    # delete this user from comment table
    connection.execute(
        "DELETE FROM comments WHERE "
        "owner = ?", (logname, )
    )
    # delete filename
    filename = connection.execute(
        "SELECT filename FROM posts WHERE "
        "owner = ?", (logname, )
    ).fetchall()[0]['filename']
    os.remove(os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename))
    # delete this user from posts table
    connection.execute(
        "DELETE FROM posts WHERE "
        "owner = ?", (logname, )
    )
    # delete this user from following table
    connection.execute(
        "DELETE FROM following WHERE "
        "username1 = ? OR username2 = ?",
        (logname, logname, )
    )
    # delete filename
    filename = connection.execute(
        "SELECT filename FROM users WHERE "
        "username = ?", (logname, )
    ).fetchall()[0]['filename']
    os.remove(os.path.join(insta485.app.config['UPLOAD_FOLDER'], filename))
    # delete this user from user table
    connection.execute(
        "DELETE FROM users WHERE "
        "username = ?", (logname, )
    )
    # clear session
    flask.session.clear()


def process_accounts_update_password(connection):
    """Process accounts update password."""
    # check log in
    if 'username' not in flask.session:
        abort(403, 'You are not logged in.')
    logname = flask.session['username']
    password = flask.request.form['password']
    new_password1 = flask.request.form['new_password1']
    new_password2 = flask.request.form['new_password2']
    # check empty field
    if not password or not new_password1 or not new_password2:
        abort(400, 'Password/new_password1/new_password2 is empty.')
    real_old_password = connection.execute(
        "SELECT password FROM users WHERE username = ?", (logname, )
    ).fetchall()[0]['password']
    # check old password hash
    if not check_password_hash(password, real_old_password):
        abort(403, 'Incorrect old password')
    # check new password mismatch
    elif new_password1 != new_password2:
        abort(401, 'Two new passwords mismatch')
    # hash new password
    new_password_hash = generate_password_hash(new_password1)
    # update new password
    connection.execute(
        "UPDATE users "
        "SET password = ? "
        "WHERE username = ?",
        (new_password_hash, logname, )
    )


def process_accounts_edit_account(connection):
    """Process_accounts_edit_account."""
    # check log in
    if 'username' not in flask.session:
        abort(403, 'You are not logged in.')
    logname = flask.session['username']
    file = flask.request.files['file']
    fullname = flask.request.form['fullname']
    email = flask.request.form['email']
    filename = secure_filename(file.filename)
    # check empty field
    if not fullname or not email:
        abort(400, 'Fullname/email is empty.')
    # whether photo file is included``
    if filename:
        # remove old
        old_filename = connection.execute(
            "SELECT filename FROM posts WHERE "
            "owner = ?", (logname, )
        ).fetchall()[0]['filename']
        os.remove(
            os.path.join(
                insta485.app.config['UPLOAD_FOLDER'],
                old_filename))
        # save new
        basename = generate_filename(filename)
        file.save(
            os.path.join(
                insta485.app.config['UPLOAD_FOLDER'],
                basename))
        connection.execute(
            "UPDATE users "
            "SET filename = ?, fullname = ?, email = ? "
            "WHERE username = ?",
            (basename, fullname, email, logname,))
    else:
        connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username = ?", (fullname, email, logname, )
        )


@insta485.app.route('/accounts/', methods=['POST'])
def process_accounts():
    """POST /accounts/?target=URL."""
    operation = flask.request.form['operation']
    connection = insta485.model.get_db()
    # operation: login
    if operation == 'login':
        process_accounts_login(connection)
    # operation: create
    elif operation == 'create':
        process_accounts_create(connection)
    # operation: delete
    elif operation == 'delete':
        process_accounts_delete(connection)
    # operation: update_password
    elif operation == 'update_password':
        process_accounts_update_password(connection)
    # operation: edit_account
    elif operation == 'edit_account':
        process_accounts_edit_account(connection)
    # target
    target = flask.request.args.get('target')
    if not target:
        target = '/'
    return flask.redirect(target)
