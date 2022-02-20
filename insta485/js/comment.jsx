import React from 'react';
import PropTypes from 'prop-types';

function Comment(props) {
  const { comment, deleteComment } = props;
  return (
    <li className="comment">
      <b>
        <a href={comment.ownerShowUrl}>
          { comment.owner }
          :
          {' '}
        </a>
      </b>
      { comment.text }
      {
        comment.lognameOwnsThis
        && (
        <button type="button" className="delete-comment-button" onClick={() => { deleteComment(comment.commentid); }}>
          Delete comment
        </button>
        )
    }
    </li>
  );
}

Comment.propTypes = {
  comment: PropTypes.shape({
    ownerShowUrl: PropTypes.string,
    owner: PropTypes.string,
    text: PropTypes.string,
    lognameOwnsThis: PropTypes.bool,
    commentid: PropTypes.number,
  }).isRequired,
  deleteComment: PropTypes.func.isRequired,
};

export default Comment;
