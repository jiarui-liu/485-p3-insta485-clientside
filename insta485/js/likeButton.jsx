import React from 'react';
import PropTypes from 'prop-types';

function LikeButton(props) {
  const { handleLike, islike } = props;
  return (
    <button
      type="button"
      className="like-unlike-button"
      onClick={() => {
        handleLike();
      }}
    >
      {islike ? 'unlike' : 'like'}
    </button>
  );
}

LikeButton.propTypes = {
  handleLike: PropTypes.func.isRequired,
  islike: PropTypes.bool.isRequired,
};

export default LikeButton;
