import {connect} from "react-redux";
import {LabelInterface} from "../components/LabelInterface.jsx";

function getBatchWithId(state, id) {
    const batch = state.batches.imageBatches.find(x => x.id == id);
    return batch;
}

function getTaskWithId(state, batch, id) {
    const task = state.batches.imageBatches.find(x => x.id == batch).tasks.find(x => x.id == id);
    return task;
}

const mapStateToProps = (state, {match} ) => {
    return {
        batch: getBatchWithId(state, match.params.batch_id),
        task: getTaskWithId(state, match.params.batch_id, match.params.task_id)
    };
}

const mapDispatchToProps = dispatch => ({
    //toggleTodo: id => dispatch(toggleTodo(id))
})

// Tie state and visualization together
export default connect(
    mapStateToProps,
    mapDispatchToProps
)(LabelInterface)