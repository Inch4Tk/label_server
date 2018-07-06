import { FETCH_BATCHES } from "../actions"

const batches = (state = { isFetching: true, imageBatches: [], videoBatches: [] }, action) => {
    switch (action.type) {
        case FETCH_BATCHES:
            if (action.status == "fetching") {
                return Object.assign({}, state, {
                    isFetching: true,
                })
            }
            else if (action.status == "success") {
                return Object.assign({}, state, {
                    isFetching: false,
                    imageBatches: action.data.imageBatches,
                    videoBatches: action.data.videoBatches
                })
            }
            else {
                return Object.assign({}, state, {
                    isFetching: false,
                })
            }
        default:
            return state;
    }
}

export default batches