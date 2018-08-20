import { connect } from 'react-redux'
import { ImageBatchDetail } from '../components/ImageBatchDetail.jsx'

function getBatchWithId(state, id) {
    const batch = state.batches.imageBatches.find(x => x.id == id);
    return batch;
}

const mapStateToProps = (state, { match }) => {
    return {
        batch: getBatchWithId(state, match.params.batch_id)
    };
}

const mapDispatchToProps = dispatch => ({
    //toggleTodo: id => dispatch(toggleTodo(id))
})

// Tie state and visualization together
export default connect(
    mapStateToProps,
    mapDispatchToProps
)(ImageBatchDetail)