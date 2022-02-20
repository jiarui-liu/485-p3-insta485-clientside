import React from 'react';
import PropTypes from 'prop-types';

function LikeButton(props) {
  const { dbClick, islike } = props;
  return (
    <button
      type="button"
      className="like-unlike-button"
      onDoubleClick={() => {
        dbClick();
      }}
    >
      {islike ? 'unlike' : 'like'}
    </button>
  );
}

LikeButton.propTypes = {
  dbClick: PropTypes.func.isRequired,
  islike: PropTypes.bool.isRequired,
};

export default LikeButton;
