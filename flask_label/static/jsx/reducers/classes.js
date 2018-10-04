import { REQUEST_CLASSES, RECEIVE_CLASSES } from "../actions"

const classes = (state = { isFetching: true, classes: [] }, action) => {
    switch (action.type) {
        case REQUEST_CLASSES:
            return Object.assign({}, state, {
                isFetching: true,
            });
        case RECEIVE_CLASSES:
            return Object.assign({}, state, {
                isFetching: false,
                classes: action.data,
            });
        default:
            return state;
    }
};

export default classes