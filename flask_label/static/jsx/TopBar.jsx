import React from "react";
import { Link, Route } from "react-router-dom"
import { Breadcrumb } from "./Breadcrumb.jsx"

class UserInfo extends React.Component {
    render() {
        return (
            <div className="user-info">
                <a href="/auth/logout">Logout</a>
            </div>
        )
    }
}

class Logo extends React.Component {
    render() {
        return (
            <div className="logo">
                <Link to="/">Flask Label</Link>
            </div>
        )
    }
}


class Navigation extends React.Component {
    render() {
        // Dynamic = Things like instructions/settings, context aware
        const navDynamic = this.props.navDynamic ? this.props.navDynamic : [];
        return (
            <div className="navigation">
                <nav className="nav-breadcrumbs">
                    {/* Start our nav breadcrumbs on the first level, not root. */}
                    <Route path={"/:name"} component={Breadcrumb}/>
                </nav>
                <nav className="nav-dynamic">
                    {navDynamic.map((dyn, index) => (<Link to={dyn.link} key={index}>{dyn.name}</Link>))}
                </nav>
            </div>
        );
    }
}

class TopBar extends React.Component {
    render() {
        return (
            <div className="top-bar">
                <Logo />
                <Navigation />
                <UserInfo />
            </div>
        )
    }
}

export { TopBar };