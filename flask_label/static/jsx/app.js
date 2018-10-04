// SCSS Assets
import "./../scss/app.scss"
// JS Assets
import React from "react";
import ReactDOM from "react-dom";
import {BrowserRouter as Router, Redirect, Route, Switch} from "react-router-dom"
// Components
import {TopBar} from "./components/TopBar.jsx";
import {NoMatch} from "./components/NoMatch.jsx";
// Containers
import BatchOverviewApp from "./containers/BatchOverviewApp.jsx";
import ImageBatchDetailApp from "./containers/ImageBatchDetailApp.jsx";
import AnnotationInterfaceApp from "./containers/LabelInterfaceApp.jsx";
// Redux
import thunkMiddleware from 'redux-thunk'
import {Provider} from 'react-redux'
import {applyMiddleware, createStore} from "redux"
import rootReducer from "./reducers";
import {fetchBatches, fetchClasses, fetchLabels, fetchPredictions} from "./actions";

// All our routes
const routes = [
    {
        path: "/",
        exact: true,
        navDynamic: [{link: "/todo", name: "testlink"}], // These are context aware links in navbar
        main: () => (<BatchOverviewApp/>)
    },
    {
        path: "/label_images",
        exact: true,
        navDynamic: [],
        main: () => (<Redirect to="/"/>)
    },
    {
        path: "/label_images/:batch_id",
        exact: true,
        navDynamic: [
            {link: "/todo", name: "settings"},
            {link: "/instructions", name: "instructions"}
        ],
        main: (props) => (<ImageBatchDetailApp {...props}/>)
    },
    {
        path: "/label_images/:batch_id/:task_id",
        exact: true,
        navDynamic: [
            {link: "/todo", name: "settings"},
            {link: "/instructions", name: "instructions"}
        ],
        main: (props) => (<AnnotationInterfaceApp {...props}/>)
    },
    {
        path: "/instructions",
        exact: true,
        navDynamic: [],
        main: () => (
            <ol>
                <li>
                    Use "w, a, s, d, " or mouse clicks to mark the four extremas (top, bottom,
                    leftmost, rightmost points) of an object
                </li>
                <li>
                    When you are finished, press "e" to get to the next image, "q" to get to the
                    image before or "r" to get to the next non-annotated image. You can also use the
                    file-navigator on the left
                </li>
                <li>
                    You can always delete an annotation by clicking on its label on the right or by
                    pressing the corresponding number on your keyboard. In the same way you can also
                    restore any annotation
                </li>
                <li>
                    You can always redo the last task by pressing "u". This works multiple times.
                    Note that this also deletes the respective annotation.
                    This does not work for non-detected objects that you annotated. For this,
                    use the delete mechanism instead.
                </li>
            </ol>)
    },
    {
        path: "/todo",
        exact: true,
        navDynamic: [{link: "/todo", name: "anotherdyntestlink"}],
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

export const store = createStore(rootReducer, applyMiddleware(thunkMiddleware));
let doc_root = document.getElementById("react-root");

// Loading screen while fetching data
ReactDOM.render(
    <Provider store={store}>
        <Router>
            <h1>Loading App. Please Wait</h1>
        </Router>
    </Provider>,
    doc_root
);

// Fetch information about image/video-batches, already existing labels, object- and annotation-
// predictions
Promise.all([
    store.dispatch(fetchBatches()),
    store.dispatch(fetchLabels()),
    store.dispatch(fetchPredictions()),
    store.dispatch(fetchClasses())
]).then(() => {
    console.log('Initialized store');

    // Put the SPA to the document root
    ReactDOM.render(
        <Provider store={store}>
            <Router>
                <App/>
            </Router>
        </Provider>,
        doc_root
    );
});