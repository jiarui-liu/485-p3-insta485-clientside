import React from 'react';
import ReactDOM from 'react-dom';
import Allpost from './post';

// This method is only called once
ReactDOM.render(
  // Insert the post component into the DOM
  <Allpost url='/api/v1/posts/' />,
  document.getElementById('reactEntry'),
);