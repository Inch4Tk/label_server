import fetch from 'cross-fetch'
import {store} from '../app'

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
        return fetch("/api/serve_labels/")
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
        return fetch("/api/serve_predictions/")
            .then(
                response => response.json(),
                error => console.log('An error occurred.', error))
            .then(json => dispatch(receivePredictions(json)))
    }
}

export function updateStore(batch, id, labels, predictions) {
    // Save data to redux store
    let state = store.getState();
    let b = state.batches.imageBatches.find(x => x.id == batch);
    let task = b.tasks.find(x => x.id == id);
    let label = state.labels.annotations.find(x => x.id == id);

    task['is_labeled'] = labels['boxes'].length > 0;
    label['classes'] = labels['classes'];
    label['boxes'] = labels['boxes'];
    label['width'] = labels['width'];
    label['height'] = labels['height'];
    state.predictions.pred.find(x => x.id == id).predictions = predictions;

    return {type: 'UPDATE_STORE', state: state}
}

export function updateBackend(id, labels, predictions) {
    // Save data to backend and retrain models with new data
    fetch('/api/save_labels/' + id + '/', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json; charset=utf-8",
        },
        body: JSON.stringify(labels)
    })
        .then(
            response => console.log(response.status, response.statusText, ':', response.url)
        );

    fetch('/api/save_predictions/' + id + '/', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json; charset=utf-8",
        },
        body: JSON.stringify(predictions)
    })
        .then(
            response => console.log(response.status, response.statusText, ':', response.url)
        )
        .then(
            fetch('/api/train_models/')
        );

    return {type: 'UPDATE_BACKEND', state: store.getState()}
}