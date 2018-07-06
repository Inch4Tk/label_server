import React from "react";
import { Link, Route } from "react-router-dom"

class Breadcrumb extends React.Component {
    render() {
        // This is a recursive definition of breadcrumbs
        // Match is kind of a react-router magic bullet, where you can get the
        // route params and url automagically.
        // So we build a link to the current recursion level, then add a route
        // that will render the next navigation level
        return (
            <div className="breadcrumb">
                <Link to={this.props.match.url}>{this.props.match.params.name}</Link>
                <Route path={this.props.match.url + "/:name"} component={Breadcrumb}/>
            </div>
        )
    }
}

export { Breadcrumb };