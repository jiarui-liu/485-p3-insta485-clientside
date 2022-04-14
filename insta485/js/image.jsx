import React from 'react';
import PropTypes from 'prop-types';

class Image extends React.Component {
  constructor(props) {
    super(props);
    this.dbClick = this.dbClick.bind(this);
  }

  dbClick() {
    const { dbClick } = this.props;
    dbClick();
  }

  render() {
    const { imgUrl } = this.props;
    console.log(imgUrl);
    return (
      <img
        src={imgUrl}
        // src="/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg"
        onDoubleClick={this.dbClick}
        alt="imgUrl"
      />
    );
  }
}

Image.propTypes = {
  imgUrl: PropTypes.string.isRequired,
  dbClick: PropTypes.func.isRequired,
};

export default Image;
