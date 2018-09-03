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

function compute_resize_factor(img_width, img_height) {
    //Resize factor w.r.t. the canvas size (1200,800) s.t. image fits the canvas as well as possible
    //Add a border of width 10 in order to make clicks close to the boarder easier to handle
    let resize_factor_width = 1180 / img_width;
    let resize_factor_height = 780 / img_height;
    return Math.min(resize_factor_width, resize_factor_height);
}

function get_instructions(predictions) {
    //Create a message that gets displayed to a user when a prediction from the neural networks
    //is available.
    if (predictions.length === 0) {
        return ['Annotate any object you see below.'];
    }

    let cls = predictions[0]['LabelName'];
    let action = (predictions[0]['acceptance_prediction'] === 0) ? 'annotate a ' : 'verify the ';
    let instructions = [];
    instructions.push('Please ' + action + cls + ' you see in this picture.');
    if (action === 'verify the ') {
        instructions.push('Press "v" to verify or "f" to falsify.');
    }
    else {
        instructions.push('If there is no ' + cls + ' (left to annotate), press "f"')
    }
    return instructions;
}

class LabelInterface extends React.Component {
    constructor(props) {
        super(props);
        this.mouse_position = undefined;
        this.has_changed = false;
        this.task_id = -1;
        this.image = -1;
        this.canvasRev = React.createRef();
        this.state = {
            classes: [],
            boxes: [],
            deleted: [],
            user_input: [],
            predictions: [],
            instructions: [],
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
        this.task_id = task.id;
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
                fetch("/api/get_prediction/" + task.id + "/")
                    .then(
                        response => response.json(),
                        error => console.log('An error occurred.', error))
                    .then(pred => {
                        this.image = image;
                        this.setState({
                            classes: json.classes,
                            boxes: json.boxes,
                            deleted: deleted,
                            user_input: [undefined, undefined, undefined, undefined],
                            predictions: pred,
                            instructions: get_instructions(pred),
                            redirect: undefined,
                        });
                    });
            });
    }

    componentWillUnmount() {
        console.log("Component will unmount");
        document.removeEventListener('keydown', this.handle_keypress);
        if (this.has_changed) {
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
            let resize_factor = compute_resize_factor(this.image.width, this.image.height);
            for (let i = 0; i < boxes.length; i++) {
                for (let j = 0; j < boxes[i].length; j++) {
                    boxes[i][j] = boxes[i][j] / resize_factor;
                }
            }
            let postData = JSON.stringify({
                'classes': classes,
                'boxes': boxes,
                'width': this.image.width,
                'height': this.image.height
            });
            let request = new XMLHttpRequest();
            let url = '/api/save_labels/' + this.task_id + '/';
            let shouldBeAsync = true;
            request.open('POST', url, shouldBeAsync);
            request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            request.send(postData);
        }

        let request = new XMLHttpRequest();
        let url = '/api/save_predictions/' + this.task_id + '/';
        let shouldBeAsync = true;
        request.open('POST', url, shouldBeAsync);
        request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        request.send(JSON.stringify(this.state.predictions));

    }

    handle_click(event) {
        let newState = this.state;
        let ui = this.state.user_input;
        let img_width = this.image.width;
        let img_height = this.image.height;
        let resize_factor = compute_resize_factor(img_width, img_height);
        let new_width = img_width * resize_factor;
        let new_height = img_height * resize_factor;
        let bounds = this.canvasRev.current.getBoundingClientRect();
        //handle clicks on border and map input to image coordinates
        let x = Math.min(Math.max(event.clientX - bounds.left, 10), new_width + 10) - 10;
        let y = Math.min(Math.max(event.clientY - bounds.top, 10), new_height + 10) - 10;

        for (let i = 0; i < ui.length; i++) {
            if (!ui[i]) {
                ui[i] = [x, y];
                this.setState({
                    classes: newState.classes,
                    boxes: newState.boxes,
                    deleted: newState.deleted,
                    user_input: ui,
                    predictions: newState.predictions,
                    instructions: newState.instructions,
                    redirect: newState.redirect
                });
                break;
            }
        }
        if (ui[0] && ui[1] && ui[2] && ui[3]) {
            this.add_new_bounding_box()
        }
    }

    track_mouse_position(event) {
        try {
            let img_width = this.image.width;
            let img_height = this.image.height;
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
        let newState = this.state;

        //Q: backwards
        if (kc === 81 && task_ids.includes(task.id - 1)) {
            newState.redirect = "/label_images/" + batch.id + "/" + (task.id - 1)
        }

        //E: forwards
        if (kc === 69 && task_ids.includes(task.id + 1)) {
            newState.redirect = "/label_images/" + batch.id + "/" + (task.id + 1)
        }

        //WASD: points of extreme clicking
        else if ([65, 68, 83, 87].includes(kc)) {
            let mp = this.mouse_position;
            let ui = newState.user_input;
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
                this.add_new_bounding_box();
                return;
            }
        }

        //R: jump to random, unlabeled task from current batch
        else if (kc === 82) {
            let new_task_id = open_tasks_ids[Math.floor(Math.random() * open_tasks_ids.length)];
            newState.redirect = "/label_images/" + batch.id + "/" + new_task_id;
        }

        //1-9: delete / re-add bounding box with this index
        else if (kc > 48 && kc < 58 && newState.classes.length >= (kc - 48)) {
            newState.deleted[kc - 49] = !newState.deleted[kc - 49];
            this.has_changed = true;
        }

        else if (newState.predictions.length > 0) {
            //F: falsify proposal
            if (kc === 70) {
                newState.predictions.splice(0, 1);
            }

            //V: verify a proposal
            else if (kc === 86) {
                this.has_changed = true;
                let pred = newState.predictions.splice(0, 1)[0];

                newState.classes.push(pred['LabelName']);
                newState.boxes.push([pred['XMin'], pred['YMin'], pred['XMax'], pred['YMax']]);
                newState.deleted.push(false)
            }

            if (newState.predictions.length > 0) {
                newState.instructions = get_instructions(newState.predictions)
            }
            else {
                newState.instructions = ['Annotate any object you see below.'];
            }
        }


        this.setState({
            classes: newState.classes,
            boxes: newState.boxes,
            deleted: newState.deleted,
            user_input: newState.user_input,
            predictions: newState.predictions,
            instructions: newState.instructions,
            redirect: newState.redirect
        })
    }

    render_image() {
        try {
            console.log('Rendering image');
            let img_width = this.image.width;
            let img_height = this.image.height;
            let b = this.state.boxes;
            let c = this.state.classes;
            let d = this.state.deleted;
            let p = this.state.predictions[0];
            let resize_factor = compute_resize_factor(img_width, img_height);
            let new_width = img_width * resize_factor;
            let new_height = img_height * resize_factor;
            let colors = ['red', 'blue', 'orange', 'purple', 'brown', 'turquoise'];
            const ctx = this.canvasRev.current.getContext('2d');
            ctx.drawImage(this.image, 10, 10, new_width, new_height);
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

            //if a verification is to be made, render the proposed label
            if (p['acceptance_prediction'] === 1) {
                ctx.beginPath();
                ctx.lineWidth = 3;
                ctx.setLineDash([5, 15]);
                ctx.fillStyle = colors[b.length % colors.length];
                ctx.strokeStyle = colors[b.length % colors.length];

                let width = this.image.width;
                let height = this.image.height;
                let res_fac = compute_resize_factor(width, height);
                //convert to absolute coordinates
                p['XMin'] = p['XMin'] * width * res_fac;
                p['XMax'] = p['XMax'] * width * res_fac;
                p['YMin'] = p['YMin'] * height * res_fac;
                p['YMax'] = p['YMax'] * height * res_fac;

                ctx.fillText(p['LabelName'], p['XMin'] + 15, p['YMin'] + 30);
                ctx.rect(p['XMin'] + 10, p['YMin'] + 10,
                    p['XMax'] - p['XMin'], p['YMax'] - p['YMin']);
                ctx.stroke();
                ctx.setLineDash([]);
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
        let newState = this.state;
        let ui = this.state.user_input;
        let x_min = Math.min(ui[0][0], ui[1][0], ui[2][0], ui[3][0]);
        let x_max = Math.max(ui[0][0], ui[1][0], ui[2][0], ui[3][0]);
        let y_min = Math.min(ui[0][1], ui[1][1], ui[2][1], ui[3][1]);
        let y_max = Math.max(ui[0][1], ui[1][1], ui[2][1], ui[3][1]);

        let new_box = [x_min, y_min, x_max, y_max];

        let c = undefined;
        if (newState.predictions.length > 0 &&
            newState.predictions[0]['acceptance_prediction'] === 1) {
            let pred = newState.predictions.splice(0, 1)[0];
            newState.instructions = get_instructions(newState.predictions);
            c = pred['LabelName'];
        }
        else {
            c = prompt("Please enter the class of your label");
        }

        if (c) {
            newState.boxes.push(new_box);
            newState.classes.push(c);
            newState.deleted.push(false);
        }

        this.has_changed = true;
        this.setState({
            classes: newState.classes,
            boxes: newState.boxes,
            deleted: newState.deleted,
            user_input: [undefined, undefined, undefined, undefined],
            predictions: newState.predictions,
            instructions: newState.instructions,
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

        if (this.image) {
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
                    this.has_changed = true;
                    this.setState({
                        classes: state.classes,
                        boxes: state.boxes,
                        deleted: state.deleted,
                        user_input: state.user_input,
                        predictions: state.predictions,
                        instructions: state.instructions,
                        redirect: undefined,
                    })
                }}>{(is_deleted ? 'add ' : 'remove ') + (index + 1) + ': ' + state.classes[index]}
                </button>
            </li>
        );

        let instruction_list = state.instructions.map((instruction, index) =>
            <li key={index}>
                <b>{instruction}</b>
            </li>
        );

        return ([
            <div key="1" className="filenav">
                <ul>{image_list}</ul>
            </div>,
            <div key="2" className="historynav">
                <ul>{history_list}</ul>
            </div>,
            <div key="3">
                <ul>{instruction_list}</ul>
            </div>,
            <canvas key="4" ref={this.canvasRev} width="1200" height="800"
                    onClick={this.handle_click} onMouseMove={this.track_mouse_position}/>
        ])
    }
}

export {LabelInterface}