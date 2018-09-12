import { REQUEST_PREDICTIONS, RECEIVE_PREDICTIONS } from "../actions"

const predictions = (state = { isFetching: true, pred: [] }, action) => {
    switch (action.type) {
        case REQUEST_PREDICTIONS:
            return Object.assign({}, state, {
                isFetching: true,
            });
        case RECEIVE_PREDICTIONS:
            return Object.assign({}, state, {
                isFetching: false,
                pred: action.data,
            });
        default:
            return state;
    }
};

export default predictions