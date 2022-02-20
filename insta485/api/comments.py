"""REST API for comments."""
import flask
import insta485


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def create_comment():
    """POST /api/v1/comments/?postid=<postid>."""
    username = insta485.api.posts.authenticate()
    connection = insta485.model.get_db()
    # get postid
    postid = flask.request.args.get('postid', type=int)
    # get text
    json_data = flask.request.json
    text = json_data['text']
    # add one comment to the database
    connection.execute(
        "INSERT INTO comments(owner, postid, text) VALUES (?, ?, ?)",
        (username, postid, text)
    )
    # construct context
    context = {}
    # get commentid
    cur = connection.execute(
        "SELECT last_insert_rowid()"
    ).fetchall()
    commentid = cur[0]['last_insert_rowid()']
    context['commentid'] = commentid
    # get lognameOwnsThis and others
    context['lognameOwnsThis'] = True
    context['owner'] = username
    context['ownerSHowUrl'] = '/users/' + username + '/'
    context['text'] = text
    context['url'] = '/api/v1/comments/' + str(commentid) + '/'
    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """DELETE /api/v1/comments/<commentid>/."""
    username = insta485.api.posts.authenticate()
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM comments "
        "WHERE commentid = ?",
        (commentid, )
    ).fetchall()

    # if the commentid does not exist, return 404
    if len(cur) == 0:
        return insta485.api.posts.handle_invalid_usage(
            insta485.api.posts.InvalidUsage(
                "The commentid is not found", 404))
    # if the user does not own the comment, return 403
    if cur[0]['owner'] != username:
        return insta485.api.posts.handle_invalid_usage(
            insta485.api.posts.InvalidUsage(
                "The user does not own the comment", 403))
    # delete one comment, return 204 on success
    connection.execute(
        "DELETE FROM comments "
        "WHERE commentid = ?",
        (commentid, )
    )

    return flask.jsonify({}), 204
