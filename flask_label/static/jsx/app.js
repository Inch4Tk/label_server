// SCSS Assets
import "./../scss/app.scss"

// JS Assets
import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom"

import ExtremeClicking from "./ExtremeClicking.jsx";
import { TopBar } from "./TopBar.jsx";

const NoMatch = () => (
    <h1>404: Could not find route</h1>
)

// All our routes
const routes = [
    {
        path: "/",
        exact: true,
        navDynamic: [{ link: "/todo", name: "testlink" }], // These are context aware links in navbar
        main: () => (<h1>Home</h1>)
    },
    {
        path: "/todo",
        exact: true,
        navDynamic: [{ link: "/todo", name: "anotherdyntestlink" }],
        main: () => (<h1>TODO</h1>)
    }
]

// Initialize the app
const App = () => (
    <div>
        <TopBar routes={routes}/>

        <Switch>
            {
                // Add all routes to the main content switch
                routes.map((route, index) => (
                    <Route
                        key={index}
                        exact={route.exact}
                        path={route.path}
                        component={route.main}
                    />
                ))
            }
            <Route component={NoMatch}/>
        </Switch>
    </div>
)

// Put the SPA to the document root
var doc_root = document.getElementById("react-root");
ReactDOM.render(
    <Router>
        <App />
    </Router>,
    doc_root
);