import React from 'react';

class LikeButton extends React.Component {
  constructor(props) {
    super(props);
  }
  render() {
    return (
      <button
        className='like-unlike-button'
        onClick={() => {
		  this.props.handleLike();
		}}
	  >
	  {this.props.islike ? 'unlike' : 'like'}
	  </button>
	);
  }
}
