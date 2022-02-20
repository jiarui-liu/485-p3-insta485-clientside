import React from 'react';

class Comment extends React.Component
{
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