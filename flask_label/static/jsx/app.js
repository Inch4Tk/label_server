// SCSS Assets
import "./../scss/app.scss"

// JS Assets
import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom'

import ExtremeClicking from "./ExtremeClicking.jsx";
import { TopBar } from "./TopBar.jsx";

const NoMatch = () => (
    <h1>404: Could not find route</h1>
)

const App = () => (
    <div>
        <TopBar />

        <Switch>
            <Route exact path='/' render={()=>(<h1>Home</h1>)}/>
            <Route exact path='/test' render={() => (<h1>Test</h1>)} />
            <Route component={NoMatch}/>
        </Switch>
    </div>
)

var doc_root = document.getElementById("react-root");
ReactDOM.render(
    <Router>
        <App />
    </Router>
    ,doc_root
);