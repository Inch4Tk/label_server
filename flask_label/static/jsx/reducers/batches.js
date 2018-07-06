import { REQUEST_BATCHES, RECEIVE_BATCHES } from "../actions"

const batches = (state = { isFetching: true, imageBatches: [], videoBatches: [] }, action) => {
    switch (action.type) {
        case REQUEST_BATCHES:
            return Object.assign({}, state, {
                isFetching: true,
            })
        case RECEIVE_BATCHES:
            console.log(action)
            return Object.assign({}, state, {
                isFetching: false,
                imageBatches: action.data.imageBatches,
                videoBatches: action.data.videoBatches
            })
        default:
            return state;
    }
}

export default batches