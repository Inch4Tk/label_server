import React from "react";
import { Link } from "react-router-dom"

function render_filename(task) {
    if (task.is_labeled === true) {
        return <s>{task.filename}</s>
    }
    else {
        return task.filename
    }
}

function get_index_for_image(imagelist, id) {
    let i
    for (i = 0; i < imagelist.length; i++) {
        if(parseInt(imagelist[i].key, 10) === id) {
            return i
        }
    }
    return -1
}

const LabelInterface = ({task, batch} ) => {
    console.log(batch)
    console.log(task)

    const tasks = batch.tasks
    const ImageList = tasks.map((task) =>
        <li key={task.id}>
            <Link to={"/label_images/" + batch.id + "/" + task.id}> {render_filename(task)}</Link>
        </li>
    );
    const index = get_index_for_image(ImageList, task.id)
    console.log(index)
    return (
    <div className="label-interface">
        <div className="sidenav">
            <ul>{ImageList}</ul>
        </div>
        <h1>Label Image</h1>
        <p className="alignleft">
            {ImageList[index-1]}
        </p>
        <p className="alignright">
            {ImageList[index+1]}
        </p>
        <img src={"/api/serve_image/" + task.id + "/"}/>
    </div>
    )
}

export {LabelInterface}