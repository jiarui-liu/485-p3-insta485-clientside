# task
- [ ] todo
- [ ] Delete all the jinja template code that displays the feed in insta485/templates/index.html
- [ ] GET	/api/v1/	Return API resource URLs
- [ ] GET	/api/v1/posts/	Return 10 newest post urls and ids
- [ ] GET	/api/v1/posts/?size=N	Return N newest post urls and ids
- [ ] GET	/api/v1/posts/?page=N	Return N’th page of post urls and ids
- [ ] GET	/api/v1/posts/?postid_lte=N	Return post urls and ids no newer than post id N
- [ ] GET	/api/v1/posts/<postid>/	Return one post, including comments and likes
- [ ] POST	/api/v1/likes/?postid=<postid>	Create a new like for the specified post id
- [ ] DELETE	/api/v1/likes/<likeid>/	Delete the like based on the like id
- [ ] POST	/api/v1/comments/?postid=<postid>	Create a new comment based on the text in the JSON body for the specified post id
- [ ] DELETE	/api/v1/comments/<commentid>/	Delete the comment based on the comment id
```
import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import CommentCreateForm from './createCommentForm';
import Comment from './comment';
import LikeButton from './likeButton';

class Post extends React.Component {
  /* Display number of image and post owner of a single post
 */

  constructor(props) {
    // runs when an instance is created
    // Initialize mutable state
    super(props);
    this.state = {
      imgUrl: '',
      owner: '',
      ownerImgUrl: '',
      ownerShowUrl: '',
      postShowUrl: '',
      postid: 1,
      created: '',
      numlikes: 1,
      loglike: true,
      likeurl: '',
      comments: [],
    };
    this.handleLike = this.handleLike.bind(this);
    this.deleteComment = this.deleteComment.bind(this);
    this.createComment = this.createComment.bind(this);
    this.dbClick = this.dbClick.bind(this);
  }

  componentDidMount() {
    // runs when an instance is added to the DOM
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          imgUrl: data.imgUrl,
          owner: data.owner,
          ownerImgUrl: data.ownerImgUrl,
          ownerShowUrl: data.ownerShowUrl,
          postShowUrl: data.postShowUrl,
          postid: data.postid,
          created: moment(data.created).fromNow(),
          numlikes: data.likes.numLikes,
          loglike: data.likes.lognameLikesThis,
          likeurl: data.likes.url,
          comments: data.comments,
        });
      })
      .catch((error) => console.log(error));
  }

  handleLike() {
    const { loglike, likeurl, postid } = this.state;
    if (loglike) {
      // console.log(likeurl, '--likeurl prepare to be delete');
      this.setState((prevState) => ({
        loglike: !prevState.loglike,
        numlikes: prevState.numlikes - 1,
      }));
      const requestOption = {
        method: 'DELETE',
        credentials: 'same-origin',
      };
      fetch(likeurl, requestOption)
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .catch((error) => console.log(error));
      this.setState({ likeurl: '' });
    } else {
      this.setState((prevState) => ({
        loglike: !prevState.loglike,
        numlikes: prevState.numlikes + 1,
      }));
      const requestOption = {
        method: 'POST',
        credentials: 'same-origin',
      };
      const url = `/api/v1/likes/?postid=${postid}`;
      fetch(url, requestOption)
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState({ likeurl: data.url });
        })
        .catch((error) => console.log(error));
    }
  }

  dbClick() {
    // let url = this.props.allpost
    const { loglike } = this.state;
    if (!loglike) {
      this.handleLike();
    }
  }

  deleteComment(commentid) {
    const { comments } = this.state;
    const newComments = comments.slice();
    for (let i = 0; i < newComments.length; i += 1) {
      if (newComments[i].commentid === commentid) {
        newComments.splice(i, 1);
      }
    }
    this.setState({ comments: newComments });
    const requestOption = {
      method: 'DELETE',
      credentials: 'same-origin',
    };
    const url = `/api/v1/comments/${commentid}/`;
    fetch(url, requestOption)
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
      })
      .catch((error) => console.log(error));
  }

  createComment(inputText) {
    const { postid, comments } = this.state;
    const requestOption = {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: inputText }),
    };
    const url = `/api/v1/comments/?postid=${postid}`;
    fetch(url, requestOption)
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const newComments = comments.slice();
        newComments.push(data);
        this.setState({ comments: newComments });
      })
      .catch((error) => console.log(error));
  }

  render() {
    // returns HTML representing this component
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const {
      imgUrl,
      owner,
      ownerImgUrl,
      ownerShowUrl,
      postShowUrl,
      created,
      numlikes,
      loglike,
      comments,
    } = this.state;
    let likestr = '';
    if (numlikes === 1) likestr = '1 like';
    else likestr = `${numlikes} likes`;

    const commentField = comments.map(
      (comment) => (
        <Comment
          comment={comment}
          deleteComment={this.deleteComment}
          key={comment.url}
        />
      ),
    );

    // console.log(loglike)
    return (
      <div className="myDivSubBody">
        <ul className="head">
          <li className="leftAlignHead">
            <ul className="head">
              <li className="leftAlignHead">
                <a href={ownerShowUrl}>
                  <img src={ownerImgUrl} width="40" alt="ownerImgUrl" />
                </a>
              </li>
              <li className="leftAlignHead">
                <a href={ownerShowUrl}>
                  {owner}
                </a>
              </li>
            </ul>
          </li>
          <li className="rightSubAlign"><a href={postShowUrl}>{created}</a></li>
        </ul>
        <Image imgUrl={imgUrl} onDoubleClick={this.dbClick} />
        <p>
          {likestr}
        </p>
        <LikeButton islike={loglike} handleLike={this.handleLike} />
        <ul className="main">{commentField}</ul>
        <CommentCreateForm createComment={this.createComment} />
      </div>
    );
  }
}

function Image(props) {
  const { imgUrl, onDoubleClick } = props;
  return (
    <img src={imgUrl} onDoubleClick={onDoubleClick} alt="imgUrl" />
  );
}

Image.propTypes = {
  imgUrl: PropTypes.string.isRequired,
  onDoubleClick: PropTypes.func.isRequired,
};

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;

```