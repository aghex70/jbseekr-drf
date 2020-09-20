// import React from 'react';
// import ReactDOM from 'react-dom';
// import App from './App';
//
// ReactDOM.render(<App />, document.getElementById('root'));

import React from "react";
import { render } from "react-dom";
import PositionsList from "./components/PositionsList";
import data from "./data/positions.json";

render(<PositionsList positions={data} />, document.getElementById("root"));