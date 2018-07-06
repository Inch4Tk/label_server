import React from "react";
import { Link, Route } from "react-router-dom"

const Breadcrumb = (props) => (
    <div className="breadcrumb">
        {
            // This is a recursive definition of breadcrumbs
            // Match is kind of a react-router magic bullet, where you can get the
            // route params and url automagically.
            // So we build a link to the current recursion level, then add a route
            // that will render the next navigation level
        }
        <Link to={props.match.url}>{props.match.params.name}</Link>
        <Route path={props.match.url + "/:name"} component={Breadcrumb} />
    </div>
)

export { Breadcrumb };