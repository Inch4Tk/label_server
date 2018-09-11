import {connect} from "react-redux";
import {LabelInterface} from "../components/LabelInterface.jsx";
import {fetchBatches} from "../actions";

function getBatchWithId(state, id) {
    return state.batches.imageBatches.find(x => x.id == id);
}

function getTaskWithId(state, batch, id) {
    return state.batches.imageBatches.find(x => x.id == batch).tasks.find(x => x.id == id);
}

function getLabelsWithId(state, id) {
    return state.labels.annotations.find(x => x.id == id)
}

const mapStateToProps = (state, {match} ) => {
    return {
        key: match.params.task_id,
        batch: getBatchWithId(state, match.params.batch_id),
        task: getTaskWithId(state, match.params.batch_id, match.params.task_id),
        labels: getLabelsWithId(state, match.params.task_id)
    };
};

const mapDispatchToProps = dispatch => ({
    update_store: () => dispatch(fetchBatches()),
});

// Tie state and visualization together
export default connect(
    mapStateToProps,
    mapDispatchToProps
)(LabelInterface)