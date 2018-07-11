import React from "react";
import { Link } from "react-router-dom"
import { NoMatch } from "./NoMatch.jsx"

const ImageTaskListElement = ({ batchId, task }) => (
    <li>
        <Link to={"/image_batch/" + batchId + "/" + task.id}>
            {task.id}: {task.filename}
        </Link> labeled: {task.is_labeled.toString()}
    </li>
)

const ImageTaskList = ({ batchId, tasks }) => (
    <ul>
        {tasks.map((task) => (<ImageTaskListElement key={task.id} batchId={batchId} task={task} />)) }
    </ul>
)

const ImageBatchDetail = ({ batch }) => {
    console.log(batch)
    if (!batch) {
        return (<NoMatch />)
    }
    else {
        return (
            <div>
                <h1>Batch { batch.dirname }</h1>
                <div>
                    <h2>Statistics</h2>
                    <p>
                        Images: {batch.imgCount}
                        <br /> Labels: {batch.labeledCount}
                        <br /> Percentage: {batch.labeledCount / batch.imgCount * 100}%
                    </p>
                </div>
                <div>
                    <h2>Image Task List</h2>
                    <ImageTaskList batchId={batch.id} tasks={batch.tasks} />
                </div>
            </div>
        )
    }
}

export { ImageBatchDetail };