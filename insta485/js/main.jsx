import React from 'react';
import ReactDOM from 'react-dom';
import Allpost from './post';


window.onbeforeunload = function () {
  window.scrollTo(0, 0);
};


// This method is only called once
ReactDOM.render(
  // Insert the post component into the DOM
  <Allpost url='/api/v1/posts/' />,
  document.getElementById('reactEntry'),
);