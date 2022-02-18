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
    this.state = { imgUrl: '', owner: '', ownerImgUrl:'', ownerShowUrl:'', postShowUrl:'', postid: 1, created: '', numlikes: 1};
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
          numlikes: data.likes.numLikes
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    // returns HTML representing this component
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { imgUrl, owner, ownerImgUrl, ownerShowUrl, postShowUrl, postid, created, numlikes} = this.state;
    let likestr = '';
    if (numlikes === 1) likestr = '1 like';
    else likestr = numlikes.toString() + ' likes';
    console.log(imgUrl, owner, ownerImgUrl, ownerShowUrl, postShowUrl, postid, created, numlikes)
    // Render number of post image and post owner
    //"font-size: 20px; padding: 5px"
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
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

// export default Post;
export default Allpost;