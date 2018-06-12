// SCSS Assets
import "./../scss/app.scss"

// JS Assets
import React from 'react';
import ReactDOM from 'react-dom';

import ExtremeClicking from "./ExtremeClicking.jsx";


// #MyHackRouter
var doc_root = document.getElementById("react_root");
var attribute = doc_root.getAttribute("react-page");
if (attribute === "label_interface") {
    ReactDOM.render(
        <Clock />,
        doc_root
    );
}
else if (attribute === "other_attribute") {
    ReactDOM.render(
        <h1>Placeholder</h1>,
        doc_root
    );
}

