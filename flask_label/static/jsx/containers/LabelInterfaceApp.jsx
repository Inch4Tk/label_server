import {connect} from "react-redux";
import {LabelInterface} from "../components/LabelInterface.jsx";

function getBatchWithId(state, id) {
    return state.batches.imageBatches.find(x => x.id == id);
}

function getTaskWithId(state, batch, id) {
    return state.batches.imageBatches.find(x => x.id == batch).tasks.find(x => x.id == id);
}

const mapStateToProps = (state, {match} ) => {
    return {
        key: match.params.task_id,
        batch: getBatchWithId(state, match.params.batch_id),
        task: getTaskWithId(state, match.params.batch_id, match.params.task_id)
    };
};

const mapDispatchToProps = dispatch => ({
    //toggleTodo: id => dispatch(toggleTodo(id))
});

// Tie state and visualization together
export default connect(
    mapStateToProps,
    mapDispatchToProps
)(LabelInterface)