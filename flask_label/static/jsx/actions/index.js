import fetch from 'cross-fetch'

export const REQUEST_BATCHES = "REQUEST_BATCHES"
const requestBatches = () => ({
    type: REQUEST_BATCHES
})

export const RECEIVE_BATCHES = "RECEIVE_BATCHES"
const receiveBatches = (data) => ({
    type: RECEIVE_BATCHES,
    data: data
})

export function fetchBatches() {
    // Async call to /api/batches, using thunk middleware (aka returning a function)
    return function (dispatch) {
        dispatch(requestBatches());
        return fetch("/api/batches/")
            .then(
                response => response.json(),
                error => console.log('An error occurred.', error))
            .then(json => dispatch(receiveBatches(json)))
    }
}