import React from "react";
import { Link, Route, Switch } from "react-router-dom"
import { Breadcrumb } from "./Breadcrumb.jsx"


const UserInfo = () => (
    <div className="user-info">
        <a href="/auth/logout">Logout</a>
    </div>
)

const Logo = () => (
    < div className="logo" >
        <Link to="/">Flask Label</Link>
    </div >
)

const BreadcrumbNav = () => (
    <nav className="nav-breadcrumbs">
        {/* Start our nav breadcrumbs on the first level, not root. */}
        <Route path={"/:name"} component={Breadcrumb} />
    </nav>
)

const DynamicNav = (props) => {
    return (
        <nav className="nav-dynamic">
            {props.entries.map((dyn, index) => (<Link to={dyn.link} key={index}>{dyn.name}</Link>))}
        </nav>
    );
};

class Navigation extends React.Component {
    render() {
        return (
            <div className="navigation">
                <BreadcrumbNav />
                <Switch>
                    {
                        // Add all context-aware, dynamic route options
                        this.props.routes.map((route, index) => (
                            <Route
                                key={index}
                                exact={route.exact}
                                path={route.path}
                                render={() => (<DynamicNav entries={route.navDynamic} />)}
                            />
                        ))
                    }
                </Switch>
            </div>
        );
    }
}

class TopBar extends React.Component {
    render() {
        return (
            <div className="top-bar">
                <Logo />
                <Navigation routes={this.props.routes}/>
                <UserInfo />
            </div>
        )
    }
}

export { TopBar };