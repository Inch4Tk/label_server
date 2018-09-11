import {combineReducers} from "redux"
import batches from "./batches"
import labels from "./labels"

// HOW STATE TREE LOOKS LIKE
const example_state = {
    batches: {
        isFetching: true,
        imageBatches: [
            {
                id: 125435,
                dirname: "asdf",
                tasks: [
                    {
                        id: 46456,
                        filename: "qwerewr",
                        is_labeled: true,
                    }
                ],
                imgCount: 1234,
                labeledCount: 1234
            }
        ],
        videoBatches: [
            {
                id: 125435,
                dirname: "asdf",
            }
        ]
    },
    labels: {
        isFetching: true,
        annotations: [
            {
                id: 42,
                labels: {
                    classes: ['hamburger'],
                    boxes: [0.1, 0.2, 0.3, 0.4],
                    width: 1920,
                    height: 1080
                }
            }
        ]
    }
    // user: {
    //     id: 1234,
    //     username: "horst"
    // } // TODO add this user
};


export default combineReducers({
    batches, labels
})