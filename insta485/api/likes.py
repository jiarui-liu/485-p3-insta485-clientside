"""REST API for likes."""
import flask
import insta485


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_like():
    """POST /api/v1/likes/?postid=<postid>."""
    username = insta485.api.posts.authenticate()
    context = {}
    connection = insta485.model.get_db()
    postid = flask.request.args.get('postid', type=int)
    if postid is None:
        return insta485.api.posts.handle_invalid_usage(
            insta485.api.posts.InvalidUsage(
                "The postid is not found", 404))
    cur = connection.execute(
        "SELECT * FROM likes "
        "WHERE owner = ? AND postid = ?",
        (username, postid, )
    ).fetchall()
    # initialize response
    response = None
    # create context dict
    # if the like already exists
    if len(cur) != 0:
        context["likeid"] = cur[0]["likeid"]
        context["url"] = "/api/v1/likes/" + str(cur[0]["likeid"]) + "/"
        response = 200
        return flask.jsonify(**context), response
    # if the like does not exist

    # create one like
    connection.execute(
        "INSERT INTO likes(owner, postid) VALUES (?, ?)",
        (username, postid, )
    )
    cur = connection.execute(
        "SELECT likeid FROM likes WHERE owner = ? AND postid = ?",
        (username, postid)
    ).fetchall()
    context["likeid"] = cur[0]["likeid"]
    context["url"] = "/api/v1/likes/" + str(context["likeid"]) + "/"
    response = 201

    return flask.jsonify(**context), response


@insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """DELETE /api/v1/likes/<likeid>/."""
    username = insta485.api.posts.authenticate()
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM likes "
        "WHERE likeid = ?",
        (likeid, )
    ).fetchall()
    # if the likeid does not exist, return 404
    if len(cur) == 0:
        return insta485.api.posts.handle_invalid_usage(
            insta485.api.posts.InvalidUsage(
                "The likeid is not found", 404))
    # if the user does not own the like, return 403
    if cur[0]["owner"] != username:
        return insta485.api.posts.handle_invalid_usage(
            insta485.api.posts.InvalidUsage(
                "The user does not own the like", 403))
    # delete one "like", return 204 on success
    postid = cur[0]["postid"]
    connection.execute(
        "DELETE FROM likes "
        "WHERE owner = ? AND postid = ?",
        (username, postid, )
    )
    return flask.jsonify({}), 204
