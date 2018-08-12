import React from "react";
import {Link} from "react-router-dom"

function render_filename(task) {
    if (task.is_labeled === true) {
        return <s>{task.filename}</s>
    }
    else {
        return task.filename
    }
}

function get_index_for_image(image_list, id) {
    let i;
    for (i = 0; i < image_list.length; i++) {
        if (parseInt(image_list[i].key, 10) === id) {
            return i
        }
    }
    return -1
}

class LabelInterface extends React.Component {
    constructor(props) {
        super(props);
        this.canvasRev = React.createRef();
        this.state = {
            boxes: [],
            image_list: [],
            task_id: -1
        };
        this.handle_click = this.handle_click.bind(this);
    }

    componentDidMount() {
        console.log("Component did mount");
        const {task, batch} = this.props;

        const tasks = batch.tasks;
        let image_list = tasks.map((task) =>
            <li key={task.id}>
                <Link
                    to={"/label_images/" + batch.id + "/" + task.id}> {render_filename(task)}</Link>
            </li>
        );

        let image = this.load_image("/api/serve_image/" + task.id + "/");

        this.setState({
            boxes: this.state.boxes,
            image_list: image_list,
            task_id: task.id,
            image: image
        });
        console.log("Component initialized")
    }

    render_image() {
        const ctx = this.canvasRev.current.getContext('2d');
        ctx.lineWidth = 5;
        //Resize image w.r.t. the canvas size (1200,800) s.t. it fits the canvas as well as possible
        let resize_factor_width = 1200 / this.state.image.width;
        let resize_factor_height = 800 / this.state.image.height;
        let resize_factor = Math.min(resize_factor_width, resize_factor_height);
        let new_width = this.state.image.width * resize_factor;
        let new_height = this.state.image.height * resize_factor;
        ctx.drawImage(this.state.image, 0, 0, new_width, new_height);

        ctx.beginPath();
        ctx.strokeStyle = "red";
        for (let i = 0; i < this.state.boxes.length; i++) {
            ctx.rect(this.state.boxes[i][0], // fill at (x, y) with (width, height)
                this.state.boxes[i][1],
                this.state.boxes[i][2],
                this.state.boxes[i][3]);
        }
        ctx.stroke();

    }

    handle_click(event) {
        let bounds = this.canvasRev.current.getBoundingClientRect();
        let x = event.clientX - bounds.left;
        let y = event.clientY - bounds.top;
        console.log(x);
        console.log(y)
    }

    load_image(url) {
        let image = new Image();
        image.onload = this.render_image.bind(this);
        image.src = url;
        return image
    }

    render() {
        let image_list = this.state.image_list;
        let index = get_index_for_image(image_list, this.state.task_id);
        return ([
            <div key="1" className="sidenav">
                <ul>{image_list}</ul>
            </div>,
            <h1 key="2"> Label Image</h1>,
            <em key="3" className="alignleft">
                {image_list[index - 1]}
            </em>,
            <em key="4" className="alignright">
                {image_list[index + 1]}
            </em>,
            <canvas key="5" ref={this.canvasRev} width="1200" height="800"
                    onClick={this.handle_click}/>
        ])
    }
}


export {LabelInterface}