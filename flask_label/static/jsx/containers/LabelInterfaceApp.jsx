import {connect} from "react-redux";
import {LabelInterface} from "../components/LabelInterface.jsx";
import {retrainModels, updateBackend, updatePredictions, updateStore} from "../actions";

function cloneObject(src) {
    //clones an object by parsing all jsonifyable attributes and saving them in another object
    return JSON.parse(JSON.stringify(src));
}

function getBatchWithId(state, id) {
    return state.batches.imageBatches.find(x => x.id == id);
}

function getTaskWithId(state, batch, id) {
    return state.batches.imageBatches.find(x => x.id == batch).tasks.find(x => x.id == id);
}

function getLabelsWithId(state, id) {
    return cloneObject(state.labels.annotations.find(x => x.id == id));
}

function getPredictionsWithId(state, id) {
    return cloneObject(state.predictions.pred.find(x => x.id == id).predictions);
}

const mapStateToProps = (state, {match}) => {
    return {
        key: match.params.task_id,
        batch: getBatchWithId(state, match.params.batch_id),
        task: getTaskWithId(state, match.params.batch_id, match.params.task_id),
        labels: getLabelsWithId(state, match.params.task_id),
        predictions: getPredictionsWithId(state, match.params.task_id),
        known_classes: state.classes.classes

    };
};

const mapDispatchToProps = dispatch => ({
    save_data: (batch_id, task_id, labels, predictions) => {
        dispatch(updateStore(batch_id, task_id, labels, predictions));
        dispatch(updateBackend(batch_id, task_id, labels, predictions))
    }
});

// Tie state and visualization together
export default connect(
    mapStateToProps,
    mapDispatchToProps
)(LabelInterface)