// SCSS Assets
import "./../scss/app.scss"

// JS Assets
import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom"

// Components
import { TopBar } from "./components/TopBar.jsx";
import BatchOverviewApp from "./containers/BatchOverviewApp.jsx";

// Containers

// Redux
import thunkMiddleware from 'redux-thunk'
import { Provider } from 'react-redux'
import { createStore, applyMiddleware } from "redux"
import rootReducer from "./reducers";
import { fetchBatches } from "./actions";

const store = createStore(rootReducer, applyMiddleware(thunkMiddleware));
store.dispatch(fetchBatches());

// All our routes
const routes = [
    {
        path: "/",
        exact: true,
        navDynamic: [{ link: "/todo", name: "testlink" }], // These are context aware links in navbar
        main: () => (<BatchOverviewApp />)
    },
    {
        path: "/todo",
        exact: true,
        navDynamic: [{ link: "/todo", name: "anotherdyntestlink" }],
        main: () => (<h1>TODO</h1>)
    }
]

const NoMatch = () => (
    <h1>404: Could not find route</h1>
)

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
    <Provider store={store}>
        <Router>
            <App />
        </Router>
    </Provider>,
    doc_root
);