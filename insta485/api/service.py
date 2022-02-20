"""REST API for services."""
import flask
import insta485


@insta485.app.route('/api/v1/', methods=['GET'])
def service():
    """GET /api/v1/, return a list of service."""
    context = {
      "comments": "/api/v1/comments/",
      "likes": "/api/v1/likes/",
      "posts": "/api/v1/posts/",
      "url": "/api/v1/"
      }
    return flask.jsonify(**context)
