import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';

class Allpost extends React.Component {

  constructor(props){
    super(props);
    this.state = { urls: [] }
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
          urls: data.results
        });
      })
      .catch((error) => console.log(error));
  }

  render(){
    const {urls} = this.state;
    let posts = urls.map( (dic) =>
      <Post url={dic.url} key={dic.url}/>
    );
    return <ul>{posts}</ul>;
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
     numlikes: 1, loglike: true, likeurl: ''};
    this.handleLike = this.handleLike.bind(this);
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
          likeurl: data.likes.url
        });
      })
      .catch((error) => console.log(error));
  }

  handleLike(){
    console.log(this.state)
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
    }
  }

  render() {
    // returns HTML representing this component
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { imgUrl, owner, ownerImgUrl, ownerShowUrl, postShowUrl, postid, created, numlikes, loglike, likeurl} = this.state;
    let likestr = '';
    if (numlikes === 1) likestr = '1 like';
    else likestr = numlikes.toString() + ' likes';
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
      <button onClick={() => {this.props.handleLike()}}>
        {this.props.islike? 'unlike':'like'}
      </button>
    );
  }
}



Post.propTypes = {
  url: PropTypes.string.isRequired,
};

// export default Post;
export default Allpost;