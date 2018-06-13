import React from 'react';
import { Link } from 'react-router-dom'

class Navigation extends React.Component {
    render() {
        return (
            <nav>
                <h1>Derptest This is a navigation</h1>
                <Link to="/test">Test</Link>
                <a href="/auth/logout">Logout</a>
            </nav>
        );
    }
}

export { Navigation };