import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

class Allpost extends React.Component {
  constructor(props) {
    super(props);
    this.state = { urls: [], next: '', hasMore: true };
    this.fetchMoreData = this.fetchMoreData.bind(this);
  }

  componentDidMount() {
    if (String(window.performance.getEntriesByType('navigation')[0].type) === 'back_forward') {
      const pastState = window.history.state;
      this.setState({
        urls: pastState.urls,
        next: pastState.next,
      });
    } else {
      const { url } = this.props;
      fetch(url, { credentials: 'same-origin' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          // console.log(data);
          this.setState({
            urls: data.results,
            next: data.next,
          });
        })
        .catch((error) => console.log(error));
    }
  }

  fetchMoreData() {
    const { next } = this.state;
    const nextUrl = next;
    if (nextUrl === '') {
      this.setState({ hasMore: false });
      return;
    }
    // console.log(this.state.hasMore)
    // console.log(this.state.urls)

    fetch(nextUrl, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // console.log(data);
        this.setState((prevState) => ({
          urls: prevState.urls.concat(data.results),
          next: data.next,
        }));
        // console.log(data.results.length);
      })
      .catch((error) => console.log(error));
    window.history.pushState(this.state, '');
  }

  render() {
    const { urls, hasMore } = this.state;
    const posts = urls.map((elt) => <Post url={elt.url} key={elt.url} />);
    return (
      <InfiniteScroll
        dataLength={urls.length}
        next={this.fetchMoreData}
        hasMore={hasMore}
        loader={<h4>Loading...</h4>}
      >
        <ul>{posts}</ul>
      </InfiniteScroll>
    );
  }
}

Allpost.propTypes = {
  url: PropTypes.string.isRequired,
};

// export default Post;
export default Allpost;
