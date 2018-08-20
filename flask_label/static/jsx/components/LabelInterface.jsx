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
            classes: [],
            boxes: [],
            image_list: [],
            task_id: -1,
            user_input: []
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

        fetch("/api/serve_labels/" + task.id + "/")
            .then(
                response => response.json(),
                error => console.log('An error occurred.', error))
            .then(json => this.setState({
                classes: json.classes,
                boxes: json.boxes,
            }));
        let prevState = this.state;

        this.setState({
            classes: prevState.classes,
            boxes: prevState.boxes,
            image_list: image_list,
            task_id: task.id,
            image: image,
            user_input: []
        });
    }

    render_image() {
        //Resize image w.r.t. the canvas size (1200,800) s.t. it fits the canvas as well as possible
        let resize_factor_width = 1200 / this.state.image.width;
        let resize_factor_height = 800 / this.state.image.height;
        let resize_factor = Math.min(resize_factor_width, resize_factor_height);
        let new_width = this.state.image.width * resize_factor;
        let new_height = this.state.image.height * resize_factor;

        const ctx = this.canvasRev.current.getContext('2d');
        ctx.drawImage(this.state.image, 0, 0, new_width, new_height);
        ctx.beginPath();
        ctx.lineWidth = 3;
        ctx.font = "20px Arial";
        ctx.fillStyle = "red";
        ctx.strokeStyle = "red";

        //show existing user input via points
        let ui = this.state.user_input;
        for (let i = 0; i < (ui.length / 2); i++) {
            ctx.rect(ui[0], ui[1], 1, 1);
            ctx.rect(ui[2], ui[3], 1, 1);
            ctx.rect(ui[4], ui[5], 1, 1);
            ctx.rect(ui[6], ui[7], 1, 1);
        }

        //render finished bounding boxes
        let b = this.state.boxes;
        let c = this.state.classes;
        for (let i = 0; i < b.length; i++) {
            ctx.fillText(c[i], b[i][0]+5, b[i][1]+20);
            ctx.rect(b[i][0], b[i][1], b[i][2], b[i][3]);
        }
        ctx.stroke();

    }

    handle_click(event) {
        let bounds = this.canvasRev.current.getBoundingClientRect();
        let x = event.clientX - bounds.left;
        let y = event.clientY - bounds.top;

        this.state.user_input.push(x, y);

        if (this.state.user_input.length === 8) {
            this.add_new_bounding_box()
        }
        this.render_image()

    }

    load_image(url) {
        let image = new Image();
        image.onload = this.render_image.bind(this);
        image.src = url;
        return image
    }

    add_new_bounding_box() {
        let prevState = this.state;
        let ui = this.state.user_input;
        let x_min = Math.min(ui[0], ui[2], ui[4], ui[6]);
        let x_max = Math.max(ui[0], ui[2], ui[4], ui[6]);
        let y_min = Math.min(ui[1], ui[3], ui[5], ui[7]);
        let y_max = Math.max(ui[1], ui[3], ui[5], ui[7]);

        let new_box = [x_min, y_min, x_max - x_min, y_max - y_min];

        let c = prompt("Please enter the class of your label");

        prevState.boxes.push(new_box);
        prevState.classes.push(c);

        this.setState({
            classes: prevState.classes,
            boxes: prevState.boxes,
            image_list: prevState.image_list,
            task_id: prevState.task_id,
            image: prevState.image,
            user_input: []
        });
    }

    render() {
        console.log("rendering");
        if (this.state.image) {
            this.render_image();
        }
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