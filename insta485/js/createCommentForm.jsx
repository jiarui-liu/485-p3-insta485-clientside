import React from 'react';
import PropTypes from 'prop-types';

class CommentCreateForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = { value: '' };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({ value: event.target.value });
  }

  handleSubmit(event) {
    const { createComment } = this.props;
    const { value } = this.state;
    this.setState({ value: '' });
    createComment(value);
    event.preventDefault();
  }

  render() {
    const { value } = this.state;
    return (
      <form className="comment-form" onSubmit={this.handleSubmit}>
        <label htmlFor="first-name">
          Create Comment:
          <input type="text" value={value} onChange={this.handleChange} />
        </label>
      </form>
    );
  }
}

CommentCreateForm.propTypes = {
  createComment: PropTypes.string.isRequired,
};

export default CommentCreateForm;
