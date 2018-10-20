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

export const IS_TRAINING = "IS_TRAINING";
const isTraining = () => ({
    type: IS_TRAINING,
    data: true
});

export const IS_NOT_TRAINING = "IS_NOT_TRAINING";
const isNotTraining = () => ({
    type: IS_NOT_TRAINING,
    data: false
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
    let known_classes = state.classes.classes;

    task['is_labeled'] = labels['boxes'].length > 0;
    label['classes'] = labels['classes'];
    label['boxes'] = labels['boxes'];
    label['width'] = labels['width'];
    label['height'] = labels['height'];
    state.predictions.pred.find(x => x.id == id).predictions = predictions;

    let cls_labels = labels['classes'];
    for (let i = 0; i < cls_labels.length; i++) {
        if (!known_classes.includes(cls_labels[i])) {
            known_classes.push(cls_labels[i])
        }
    }

    return {type: 'UPDATE_STORE', state: state}
}

export function setIsTraining() {
    return function (dispatch) {
        dispatch(isTraining());
    }
}

export function setIsNotTraining() {
    return function (dispatch) {
        dispatch(isNotTraining());
    }
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

function saveLabelsandPrediction(id, labels, predictions) {
    return Promise.all([saveLabels(id, labels), savePredictions(id, predictions)])
}

export function trainModels() {
    let state = store.getState();
    console.log(state.is_training.isTraining);
    if (!state.is_training.isTraining) {
        store.dispatch(setIsTraining());
        return fetch('/api/train_models/')
            .then(
                response => response.json(),
                error => console.log('An error occurred.', error)
            )
            .then(
                () => {
                    store.dispatch(updatePredictions())
                        .then(store.dispatch(setIsNotTraining()))
                }
            )
    }
}

function updatePredictions() {
    return function (dispatch) {
        dispatch(requestPredictions());
        return fetch("/api/update_predictions/")
            .then(
                response => response.json(),
                error => console.log('An error occurred.', error))
            .then(json => dispatch(receivePredictions(json)))
    }
}

export function updateBackend(id, labels, predictions) {
    // Save data to backend and retrain models with new dat
    let state = store.getState();
    let is_training = state.is_training.isTraining;
    saveLabelsandPrediction(id, labels, predictions)
        .then(() => trainModels());
    return {type: 'UPDATE_BACKEND', state: store.getState()}
}