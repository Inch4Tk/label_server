import { REQUEST_LABELS, RECEIVE_LABELS } from "../actions"

const labels = (state = { isFetching: true, annotations: [] }, action) => {
    switch (action.type) {
        case REQUEST_LABELS:
            return Object.assign({}, state, {
                isFetching: true,
            });
        case RECEIVE_LABELS:
            return Object.assign({}, state, {
                isFetching: false,
                annotations: action.data,
            });
        default:
            return state;
    }
};

export default labels