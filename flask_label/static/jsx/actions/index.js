import fetch from 'cross-fetch'

export const REQUEST_BATCHES = "REQUEST_BATCHES";
const requestBatches = () => ({
    type: REQUEST_BATCHES
});

export const RECEIVE_BATCHES = "RECEIVE_BATCHES";
const receiveBatches = (data) => ({
    type: RECEIVE_BATCHES,
    data: data
});

export const REQUEST_LABELS = "REQUEST_LABELS";
const requestLabels = () => ({
    type: REQUEST_LABELS,
});

export const RECEIVE_LABELS = "RECEIVE_LABELS";
const receiveLabels = (data) => ({
    type: RECEIVE_LABELS,
    data: data
});

export const REQUEST_PREDICTIONS = "REQUEST_PREDICTIONS";
const requestPredictions = () => ({
    type: REQUEST_PREDICTIONS,
});

export const RECEIVE_PREDICTIONS = "RECEIVE_PREDICTIONS";
const receivePredictions = (data) => ({
    type: RECEIVE_PREDICTIONS,
    data: data
});

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

export function fetchLabels() {
    // Async call to /api/labels, using thunk middleware (aka returning a function)
    return function (dispatch) {
        dispatch(requestLabels());
        return fetch("/api/labels/")
            .then(
                response => response.json(),
                error => console.log('An error occurred.', error))
            .then(json => dispatch(receiveLabels(json)))
    }
}

export function fetchPredictions() {
    // Async call to /api/predictions, using thunk middleware (aka returning a function)
    return function (dispatch) {
        dispatch(requestPredictions());
        return fetch("/api/predictions/")
            .then(
                response => response.json(),
                error => console.log('An error occurred.', error))
            .then(json => dispatch(receivePredictions(json)))
    }
}