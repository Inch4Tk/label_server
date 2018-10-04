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

export const REQUEST_CLASSES = "REQUEST_CLASSES";
const requestClasses = () => ({
    type: REQUEST_CLASSES,
});

export const RECEIVE_CLASSES = "RECEIVE_CLASSES";
const receiveClasses = (data) => ({
    type: RECEIVE_CLASSES,
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

export function fetchClasses() {
    // Async call to /api/predictions, using thunk middleware (aka returning a function)
    return function (dispatch) {
        dispatch(requestClasses());
        return fetch("/api/serve_classes/")
            .then(
                response => response.json(),
                error => console.log('An error occurred.', error))
            .then(json => dispatch(receiveClasses(json)))
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
    label['was_trained'] = labels['was_trained'];
    state.predictions.pred.find(x => x.id == id).predictions = predictions;

    return {type: 'UPDATE_STORE', state: state}
}

function saveLabels(id, labels) {
    return fetch('/api/save_labels/' + id + '/', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json; charset=utf-8",
        },
        body: JSON.stringify(labels)
    });
}

function savePredictions(id, predictions) {
    return fetch('/api/save_predictions/' + id + '/', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json; charset=utf-8",
        },
        body: JSON.stringify(predictions)
    });
}

function getNumberofTrainableLabels() {
    let state = store.getState();
    let nr_of_trainable_labels = 0;
    for (let i = 0; i < state.labels.annotations.length; i++) {
        let label = state.labels.annotations[i];
        for (let j = 0; j < label.was_trained.length; j++) {
            if (label.was_trained[j] === false) {
                nr_of_trainable_labels++;
            }
        }
    }
    return nr_of_trainable_labels
}

function saveLabelsandPrediction(id, labels, predictions) {
    return Promise.all([saveLabels(id, labels), savePredictions(id, predictions)])
}

function trainModels(nr_of_trainable_labels) {
    if(nr_of_trainable_labels > 49) {
        return fetch('/api/train_models/')
            .then(
                response => response.json(),
                error => console.log('An error occurred.', error)
            )
    }
    else {
        console.log('Not enough labels to train: ' + nr_of_trainable_labels + ' of 50')
    }
}

function updatePredictions(nr_of_trainable_labels) {
    if(nr_of_trainable_labels > 49) {
        return fetch("/api/update_predictions/")
            .then(
                response => response.json(),
                error => console.log('An error occurred.', error)
            )
    }
    console.log('Not enough labels to update predictions: ' + nr_of_trainable_labels + ' of 50')
}

export function updateBackend(id, labels, predictions) {
    // Save data to backend and retrain models with new data
    let nr_of_trainable_labels = getNumberofTrainableLabels();
    saveLabelsandPrediction(id, labels, predictions)
        .then(trainModels(nr_of_trainable_labels))
        .then(updatePredictions(nr_of_trainable_labels));

    return {type: 'UPDATE_BACKEND', state: store.getState()}
}