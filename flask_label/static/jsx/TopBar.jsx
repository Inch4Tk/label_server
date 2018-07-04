import React from 'react';
import { Link } from 'react-router-dom'

class UserInfo extends React.Component {
    render() {
        return (
            <div className="user-info">
                <a href="/auth/logout">Logout</a>
            </div>
        )
    }
}

class Navigation extends React.Component {
    render() {
        const navPills = this.props.navPills ? this.props.navPills : [];
        const navDynamic = this.props.navDynamic ? this.props.navDynamic : [];
        return (
            <div className="navigation">
                <nav className="nav-pills">
                    {navPills.map((pill, index) => (<Link to={pill.link} key={index}>{pill.name}</Link>))}
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
                <Navigation navPills={[{link: "/test", name: "test"}, {link: "/derp", name: "derp"}]}/>
                <UserInfo />
            </div>
        );
    }
}

export { TopBar };