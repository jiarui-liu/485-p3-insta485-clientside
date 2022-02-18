import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import InfiniteScroll from 'react-infinite-scroll-component';

class Allpost extends React.Component {

  constructor(props){
    super(props);
    this.state = { urls: [], next: "" }
  }

  componentDidMount(){
    const {url} = this.props;
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          urls: data.results,
          next: data.next
        });
      })
      .catch((error) => console.log(error));
  }

  fetchMoreData = () => {
    setTimeout(() => {
      const next_url = this.state.next;
      fetch(next_url, { credentials: 'same-origin' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState({
            urls: this.state.urls.concat(data.results),
            next: data.next
          });
        })
        .catch((error) => console.log(error));
    }, 500);
  };


  render(){
    const {urls,next} = this.state;
    console.log(urls.length)
    let posts = urls.map( (dic) =>
      <Post url={dic.url} key={dic.url}/>
    );
    return (
      <InfiniteScroll dataLength={urls.length} next={this.fetchMoreData} hasMore={true} loader={<h4>Loading...</h4>} >
      <ul>{posts}</ul>
      </InfiniteScroll>
    );
  }
}


class Post extends React.Component {
  /* Display number of image and post owner of a single post
 */

  constructor(props) {
    // runs when an instance is created
    // Initialize mutable state
    super(props);
    this.state = { imgUrl: '', owner: '', ownerImgUrl:'', ownerShowUrl:'', postShowUrl:'', postid: 1, created: '',
     numlikes: 1, loglike: true, likeurl: '', comments: []};
    this.handleLike = this.handleLike.bind(this);
    this.deleteComment = this.deleteComment.bind(this);
    this.createComment = this.createComment.bind(this);
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
          comments: data.comments
        });
      })
      .catch((error) => console.log(error));
  }

  handleLike(){
    if (this.state.loglike){
      this.setState(prevState =>({
        loglike: !prevState.loglike,
        numlikes: prevState.numlikes - 1
      }));
      const requestOption = {
        method: 'DELETE',
        credentials: 'same-origin'
      }
      fetch(this.state.likeurl, requestOption)
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .catch((error) => console.log(error));
    }
    else{
      this.setState(prevState =>({
        loglike: !prevState.loglike,
        numlikes: prevState.numlikes + 1
      }));
      const requestOption = {
        method: 'POST',
        credentials: 'same-origin'
      }
      const url = "http://localhost:8000/api/v1/likes/?postid=" + this.state.postid.toString();
      fetch(url, requestOption)
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          console.log(response)
          return response.json();
        })
        .then(data => {
          this.setState({ likeurl: data.url });
          console.log(this.state.likeurl, data.likeid)
        })
        .catch((error) => console.log(error));
    }
  }

  deleteComment(commentid){
    let newComments = this.state.comments.slice();
    for (var i=0; i<newComments.length; i++){
      if (newComments[i].commentid == commentid){
        newComments.splice(i,1);
      }
    }
    this.setState({ comments: newComments });
    const requestOption = {
      method: 'DELETE',
      credentials: 'same-origin'
    }
    const url = "/api/v1/comments/" + commentid.toString() + "/";
    fetch(url, requestOption)
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
      })
      .catch((error) => console.log(error));
  }

  createComment(inputText){
    const requestOption = {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: inputText}),
    }
    const url = "/api/v1/comments/?postid=" + this.state.postid.toString();
    fetch(url, requestOption)
    .then((response) => {
      if (!response.ok) throw Error(response.statusText);
      return response.json();
    })
    .then(data => {
      let newComments = this.state.comments.slice();
      newComments.push(data);
      this.setState({ comments: newComments });
    })
    .catch((error) => console.log(error));
  }
  
  render() {
    // returns HTML representing this component
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { imgUrl, owner, ownerImgUrl, ownerShowUrl, postShowUrl, postid, created, numlikes, loglike, likeurl,comments} = this.state;
    let likestr = '';
    if (numlikes === 1) likestr = '1 like';
    else likestr = numlikes.toString() + ' likes';

    let commentField = comments.map( (comment) =>
    <Comment comment={comment} deleteComment={this.deleteComment}  key={comment.url}/>
    );
    
    // console.log(loglike)
    return (
      <div className="myDivSubBody">
        <ul className='head'>
          <li className="leftAlignHead">
            <ul className='head'>
              <li className='leftAlignHead'>
                <a href={ownerShowUrl}> <img src={ownerImgUrl} width="40" /> </a>
              </li>
              <li className="leftAlignHead">
                <a href={ownerShowUrl}> {owner} </a>
              </li>
            </ul>
          </li>
          <li className="rightSubAlign"><a href={postShowUrl}>{created}</a></li>
        </ul>
        <img src={imgUrl} />
        <p >
          {likestr}
        </p>
        <LikeButton islike={loglike} handleLike={this.handleLike} />
        <ul className="main">{commentField}</ul>
        <CommentCreateForm createComment={this.createComment} />
      </div>
    );
  }
}



class LikeButton extends React.Component {
  constructor(props){
    super(props);
  }
  render(){
    return (
      <button  className="like-unlike-button" onClick={() => {this.props.handleLike()}}>
        {this.props.islike? 'unlike':'like'}
      </button>
    );
  }
}


class Comment extends React.Component{
  constructor(props){
    super(props);
  }
  render(){
    return (
      <li className="comment">
      <b><a href = { this.props.comment.ownerShowUrl }>{ this.props.comment.owner }: </a></b> 
      { this.props.comment.text }
      {
        this.props.comment.lognameOwnsThis && 
        <button className="delete-comment-button" onClick={() => {this.props.deleteComment(this.props.comment.commentid)}} >
          Delete comment
        </button>
      }
      </li>
    );
  }
}


class CommentCreateForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {value: ''};

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({value: event.target.value});
  }

  handleSubmit(event) {
    this.setState({value: ''});
    this.props.createComment(this.state.value);
    event.preventDefault();
  }

  render() {
    return (
      <form className="comment-form" onSubmit={this.handleSubmit}>
        <label>
          Create Comment: 
          <input type="text" value={this.state.value} onChange={this.handleChange} />
        </label>
      </form>
    );
  }
}






Post.propTypes = {
  url: PropTypes.string.isRequired,
};

// export default Post;
export default Allpost;