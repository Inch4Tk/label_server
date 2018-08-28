import React from "react";
import {Link} from "react-router-dom"
import {Redirect} from "react-router";

function render_filename(task, current_task) {
    if (task === current_task) {
        return <mark>{task.filename}</mark>
    }
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

function compute_resize_factor(img_width, img_height) {
    //Resize factor w.r.t. the canvas size (1200,800) s.t. image fits the canvas as well as possible
    //Add a border of width 10 in order to make clicks close to the boarder easier to handle
    let resize_factor_width = 1180 / img_width;
    let resize_factor_height = 780 / img_height;
    return Math.min(resize_factor_width, resize_factor_height);
}

class LabelInterface extends React.Component {
    constructor(props) {
        super(props);
        this.mouse_position = undefined;
        this.canvasRev = React.createRef();
        this.state = {
            classes: [],
            boxes: [],
            deleted: [],
            task_id: -1,
            user_input: [],
            has_changed: false,
            redirect: undefined,
        };
        this.handle_click = this.handle_click.bind(this);
        this.track_mouse_position = this.track_mouse_position.bind(this);
        this.handle_keypress = this.handle_keypress.bind(this);
    }

    componentDidMount() {
        console.log("Component did mount");
        this.props.update_store();
        document.addEventListener('keydown', this.handle_keypress);

        let {task} = this.props;
        let image = this.load_image("/api/serve_image/" + task.id + "/");
        let deleted = [];
        let res_fac = undefined;

        fetch("/api/serve_labels/" + task.id + "/")
            .then(
                response => response.json(),
                error => console.log('An error occurred.', error))
            .then(json => {
                for (let i = 0; i < json.boxes.length; i++) {
                    res_fac = compute_resize_factor(parseInt(json.width, 10),
                        parseInt(json.height, 10));
                    deleted.push(false);
                    for (let j = 0; j < json.boxes[i].length; j++) {
                        json.boxes[i][j] = json.boxes[i][j] * res_fac;
                    }
                }

                this.setState({
                    classes: json.classes,
                    boxes: json.boxes,
                    deleted: deleted,
                    task_id: task.id,
                    image: image,
                    user_input: [undefined, undefined, undefined, undefined],
                    has_changed: false,
                    redirect: undefined,
                });
            });
    }

    componentWillUnmount() {
        console.log("Component will unmount");
        document.removeEventListener('keydown', this.handle_keypress);
        if (this.state.has_changed) {
            //do not save annotations that are deleted at this point
            let boxes = this.state.boxes;
            let classes = this.state.classes;
            let len = classes.length;
            let current = 0;
            for (let i = 0; i < len; i++) {
                if (this.state.deleted[i]) {
                    boxes.splice(current, 1);
                    classes.splice(current, 1);
                }
                else {
                    current++;
                }
            }

            //transform coordinates back to image size
            let resize_factor = compute_resize_factor(this.state.image.width, this.state.image.height);
            for (let i = 0; i < boxes.length; i++) {
                for (let j = 0; j < boxes[i].length; j++) {
                    boxes[i][j] = boxes[i][j] / resize_factor;
                }
            }
            let postData = JSON.stringify({
                'classes': classes,
                'boxes': boxes,
                'width': this.state.image.width,
                'height': this.state.image.height
            });
            let request = new XMLHttpRequest();
            let url = '/api/save_labels/' + this.state.task_id + '/';
            let shouldBeAsync = true;
            request.open('POST', url, shouldBeAsync);
            request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            request.send(postData);
        }
    }

    handle_click(event) {
        let ui = this.state.user_input;
        let img_width = this.state.image.width;
        let img_height = this.state.image.height;
        let resize_factor = compute_resize_factor(img_width, img_height);
        let new_width = img_width * resize_factor;
        let new_height = img_height * resize_factor;
        let bounds = this.canvasRev.current.getBoundingClientRect();
        //handle clicks on border and map input to image coordinates
        let x = Math.min(Math.max(event.clientX - bounds.left, 10), new_width + 10) - 10;
        let y = Math.min(Math.max(event.clientY - bounds.top, 10), new_height + 10) - 10;

        for (let i = 0; i < ui.length; i++) {
            if (!ui[i]) {
                ui.push(x, y);
            }
        }

        if (ui[0] && ui[1] && ui[2] && ui[3]) {
            this.add_new_bounding_box()
        }
    }

    track_mouse_position(event) {
        try {
            let prevState = this.state;
            let img_width = prevState.image.width;
            let img_height = prevState.image.height;
            let resize_factor = compute_resize_factor(img_width, img_height);
            let new_width = img_width * resize_factor;
            let new_height = img_height * resize_factor;
            let bounds = this.canvasRev.current.getBoundingClientRect();
            let x = Math.min(Math.max(event.clientX - bounds.left, 10), new_width + 10) - 10;
            let y = Math.min(Math.max(event.clientY - bounds.top, 10), new_height + 10) - 10;

            this.mouse_position = {x: x, y: y};
        }
        catch (e) {
        }
    }

    handle_keypress(key) {
        let kc = key.keyCode;
        let {task, batch} = this.props;
        let task_ids = batch.tasks.map((t) => t.id);

        let open_tasks_ids = batch.tasks.filter(
            (t) => !t.is_labeled && t.id !== task.id).map((t) => t.id);
        let prevState = this.state;

        //Q: backwards
        if (kc === 81 && task_ids.includes(task.id - 1)) {
            this.setState({
                classes: prevState.classes,
                boxes: prevState.boxes,
                image_list: prevState.image_list,
                deleted: prevState.deleted,
                task_id: prevState.task_id,
                image: prevState.image,
                user_input: prevState.user_input,
                has_changed: prevState.has_changed,
                redirect: "/label_images/" + batch.id + "/" + (task.id - 1),
            });
        }

        //E: forwards
        if (kc === 69 && task_ids.includes(task.id + 1)) {
            this.setState({
                classes: prevState.classes,
                boxes: prevState.boxes,
                image_list: prevState.image_list,
                deleted: prevState.deleted,
                task_id: prevState.task_id,
                image: prevState.image,
                user_input: prevState.user_input,
                has_changed: prevState.has_changed,
                redirect: "/label_images/" + batch.id + "/" + (task.id + 1)
            });
        }

        //WASD: points of extreme clicking
        else if ([65, 68, 83, 87].includes(kc)) {
            let mp = this.mouse_position;
            let ui = prevState.user_input;
            //W 1st point of extreme clicking
            if (kc === 87) {
                ui[0] = [mp.x, mp.y]
            }
            //A: 2nd point of extreme clicking
            else if (kc === 65) {
                ui[1] = [mp.x, mp.y]
            }
            //S: 3rd point of extreme clicking
            else if (kc === 83) {
                ui[2] = [mp.x, mp.y]
            }
            //D: 4th point of extreme clicking
            else if (kc === 68) {
                ui[3] = [mp.x, mp.y]
            }

            if (ui[0] && ui[1] && ui[2] && ui[3]) {
                this.add_new_bounding_box()
            }

            else {
                this.setState({
                    classes: prevState.classes,
                    boxes: prevState.boxes,
                    image_list: prevState.image_list,
                    deleted: prevState.deleted,
                    task_id: prevState.task_id,
                    image: prevState.image,
                    user_input: ui,
                    has_changed: prevState.has_changed,
                    redirect: prevState.redirect
                })
            }
        }

        //R: jump to random, unlabeled task from current batch
        else if (kc === 82) {
            let new_task_id = open_tasks_ids[Math.floor(Math.random() * open_tasks_ids.length)];
            this.setState({
                classes: prevState.classes,
                boxes: prevState.boxes,
                image_list: prevState.image_list,
                deleted: prevState.deleted,
                task_id: prevState.task_id,
                image: prevState.image,
                user_input: prevState.user_input,
                has_changed: prevState.has_changed,
                redirect: "/label_images/" + batch.id + "/" + new_task_id,
            });
        }


        //numbers for deleting / adding bounding box with this index
        if (kc > 48 && kc < 58 && prevState.classes.length >= (kc - 48)) {
            prevState.deleted[kc - 49] = !prevState.deleted[kc - 49];

            this.setState({
                classes: prevState.classes,
                boxes: prevState.boxes,
                image_list: prevState.image_list,
                deleted: prevState.deleted,
                task_id: prevState.task_id,
                image: prevState.image,
                user_input: prevState.user_input,
                has_changed: prevState.has_changed,
                redirect: prevState.redirect
            })
        }

    }

    render_image() {
        try {
            let img_width = this.state.image.width;
            let img_height = this.state.image.height;
            let b = this.state.boxes;
            let c = this.state.classes;
            let d = this.state.deleted;
            let resize_factor = compute_resize_factor(img_width, img_height);
            let new_width = img_width * resize_factor;
            let new_height = img_height * resize_factor;
            let colors = ['red', 'blue', 'orange', 'purple', 'brown', 'turquoise'];
            const ctx = this.canvasRev.current.getContext('2d');
            ctx.drawImage(this.state.image, 10, 10, new_width, new_height);
            ctx.font = "20px Arial";

            //show existing user input via points, add border size of 10 to each point
            let ui = this.state.user_input;
            ctx.beginPath();
            ctx.fillStyle = colors[c.length % colors.length];
            ctx.strokeStyle = colors[c.length % colors.length];
            ctx.lineWidth = 5;
            for (let i = 0; i < ui.length; i++) {
                if (ui[i]) {
                    ctx.rect(ui[i][0] + 10, ui[i][1] + 10, 1, 1);
                }
            }
            ctx.stroke();

            //render finished and non-deleted bounding boxes
            for (let i = 0; i < b.length; i++) {
                ctx.beginPath();
                ctx.lineWidth = 3;
                ctx.fillStyle = colors[i % colors.length];
                ctx.strokeStyle = colors[i % colors.length];
                if (!d[i]) {
                    ctx.fillText((i + 1) + ': ' + c[i], b[i][0] + 15, b[i][1] + 30);
                    ctx.rect(b[i][0] + 10, b[i][1] + 10, b[i][2] - b[i][0], b[i][3] - b[i][1]);
                    ctx.stroke();
                }
            }
        }
        catch (e) {
        }
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
        let x_min = Math.min(ui[0][0], ui[1][0], ui[2][0], ui[3][0]);
        let x_max = Math.max(ui[0][0], ui[1][0], ui[2][0], ui[3][0]);
        let y_min = Math.min(ui[0][1], ui[1][1], ui[2][1], ui[3][1]);
        let y_max = Math.max(ui[0][1], ui[1][1], ui[2][1], ui[3][1]);

        let new_box = [x_min, y_min, x_max, y_max];

        let c = prompt("Please enter the class of your label");

        if (c) {
            prevState.boxes.push(new_box);
            prevState.classes.push(c);
            prevState.deleted.push(false);
        }

        this.setState({
            classes: prevState.classes,
            boxes: prevState.boxes,
            image_list: prevState.image_list,
            deleted: prevState.deleted,
            task_id: prevState.task_id,
            image: prevState.image,
            user_input: [undefined, undefined, undefined, undefined],
            has_changed: true,
            redirect: undefined,
        });
    }

    render() {
        if (this.state.redirect) {
            return <Redirect push to={this.state.redirect}/>;
        }
        console.log("rendering");
        let state = this.state;
        let {task, batch} = this.props;
        console.log(state);

        if (state.image) {
            this.render_image();

        }
        let tasks = batch.tasks;
        let image_list = tasks.map((t) =>
            <li key={t.id}>
                <Link to={"/label_images/" + batch.id + "/" + t.id}>
                    {render_filename(t, task)}
                </Link>
            </li>
        );

        let history_list = state.deleted.map((is_deleted, index) =>
            <li key={index}>
                <button onClick={() => {
                    state.deleted[index] = !state.deleted[index];
                    this.setState({
                        classes: state.classes,
                        boxes: state.boxes,
                        deleted: state.deleted,
                        task_id: state.task_id,
                        image: state.image,
                        user_input: state.user_input,
                        has_changed: true,
                        redirect: undefined,
                    })
                }}>{(is_deleted ? 'add ' : 'remove ') + (index + 1) + ': ' + state.classes[index]}
                </button>
            </li>
        );

        let index = get_index_for_image(image_list, state.task_id);
        return ([
            <div key="1" className="filenav">
                <ul>{image_list}</ul>
            </div>,
            <div key="2" className="historynav">
                <ul>{history_list}</ul>
            </div>,
            <h1 key="3"> Label Image</h1>,
            <em key="4" className="alignleft">
                {image_list[index - 1]}
            </em>,
            <em key="5" className="alignright">
                {image_list[index + 1]}
            </em>,
            <canvas key="6" ref={this.canvasRev} width="1200" height="800"
                    onClick={this.handle_click} onMouseMove={this.track_mouse_position}/>
        ])
    }
}

export {LabelInterface}