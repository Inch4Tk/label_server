import {combineReducers} from "redux"
import batches from "./batches"
import labels from "./labels"
import predictions from "./predictions"
import is_training from "./is_training"
import classes from "./classes"

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
        isFetching: false,
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
    },
    predictions: {
        isFetching: false,
        pred: [
            {
                id: 42,
                predictions: {
                    Confidence: 0.8,
                    LabelName: 'Person',
                    XMax: 0.3,
                    XMin: 0.5,
                    YMax: 0.2,
                    YMin: 0.4,
                    acceptance_prediction: false,
                    was_successful: true
                }
            }
        ]
    },

    classes: {
        isFetching: false,
        classes: ["Hamburger", "Tomato"]
    },
    is_training: {
        isTraining: false
    }
    // user: {
    //     id: 1234,
    //     username: "horst"
    // } // TODO add this user
};


export default combineReducers({
    batches, labels, predictions, classes, is_training
})