import { combineReducers } from "redux"
import batches from "./batches"

// HOW STATE TREE LOOKS LIKE
const dummy_state = {
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
                        isLabeled: true,
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
    user: {
        id: 1234,
        username: "horst"
    }
}


export default combineReducers({
  batches
})