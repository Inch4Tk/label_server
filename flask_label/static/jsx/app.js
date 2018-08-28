// SCSS Assets
import "./../scss/app.scss"

// JS Assets
import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Switch, Redirect } from "react-router-dom"

// Components
import { TopBar } from "./components/TopBar.jsx";
import { NoMatch } from "./components/NoMatch.jsx";

// Containers
import BatchOverviewApp from "./containers/BatchOverviewApp.jsx";
import ImageBatchDetailApp from "./containers/ImageBatchDetailApp.jsx";
import AnnotationInterfaceApp from "./containers/LabelInterfaceApp.jsx";

// Redux
import thunkMiddleware from 'redux-thunk'
import { Provider } from 'react-redux'
import { createStore, applyMiddleware } from "redux"
import rootReducer from "./reducers";
import {fetchBatches} from "./actions";

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
        path: "/label_images",
        exact: true,
        navDynamic: [],
        main: () => (<Redirect to="/" />)
    },
    {
        path: "/label_images/:batch_id",
        exact: true,
        navDynamic: [{ link: "/todo", name: "settings" }, { link: "/todo", name: "instructions" }],
        main: (props) => (<ImageBatchDetailApp {...props}/>)
    },
    {
        path: "/label_images/:batch_id/:task_id",
        exact: true,
        navDynamic: [{ link: "/todo", name: "settings" }, { link: "/todo", name: "instructions" }],
        main: (props) => (<AnnotationInterfaceApp {...props}/>)
    },
    {
        path: "/todo",
        exact: true,
        navDynamic: [{ link: "/todo", name: "anotherdyntestlink" }],
        main: () => (<h1>TODO</h1>)
    }
];

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
);

// Put the SPA to the document root
let doc_root = document.getElementById("react-root");
ReactDOM.render(
    <Provider store={store}>
        <Router>
            <App />
        </Router>
    </Provider>,
    doc_root
);