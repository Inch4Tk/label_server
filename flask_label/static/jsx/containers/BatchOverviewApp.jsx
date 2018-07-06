import { connect } from 'react-redux'
import { BatchOverview } from '../components/BatchOverview.jsx'

const mapStateToProps = state => ({
    imageBatches: state.batches.imageBatches,
    videoBatches: state.batches.videoBatches
})

const mapDispatchToProps = dispatch => ({
    //toggleTodo: id => dispatch(toggleTodo(id))
})

// Tie state and visualization together
export default connect(
    mapStateToProps,
    mapDispatchToProps
)(BatchOverview)