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

function get_instructions(prediction) {
    //Create a message that gets displayed to a user when a prediction from the neural networks
    //is available.
    if (prediction === undefined) {
        return ['Annotate any object you see below.'];
    }

    let cls = prediction['LabelName'];
    let action = (prediction['acceptance_prediction'] === 0) ? 'annotate a ' : 'verify the ';
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

function get_open_prediction(predictions) {
    //Return an open prediction, e.g. one that has not yet been worked on, from a set of predictions
    for (let i = 0; i < predictions.length; i++) {
        if (!predictions[i].hasOwnProperty('was_successful')) {
            return predictions[i];
        }
    }
    return undefined;
}

function compute_iou(annotation, prediction) {
    //Compute Intersection over Union between a user annotation and a prediction from the
    //object detector
    let x_min = Math.max(annotation[0], prediction['XMin']);
    let y_min = Math.max(annotation[1], prediction['YMin']);
    let x_max = Math.min(annotation[2], prediction['XMax']);
    let y_max = Math.min(annotation[3], prediction['YMax']);

    let intersection_area = Math.max(0.0, x_max - x_min) * Math.max(0.0, y_max - y_min);

    let ann_area = (annotation[2] - annotation[0]) * (annotation[3] - annotation[1]);
    let pred_area = (prediction['XMax'] - prediction['XMin']) *
        (prediction['YMax'] - prediction['YMin']);

    return intersection_area / (ann_area + pred_area - intersection_area);
}

function should_have_been_verified(annotation, predictions) {
    for (let i = 0; i < predictions.length; i++) {
        let p = predictions[i];
        let iou = compute_iou(annotation, p);
        if (iou > 0.5) {
            return true;
        }
    }
    return false;
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

        let task = this.props.task;
        this.task_id = task.id;
        let labels = this.props.labels;
        let predictions = this.props.predictions;
        let image = this.load_image("/api/serve_image/" + task.id + "/");
        let deleted = [];
        let res_fac = undefined;

        for (let i = 0; i < labels.boxes.length; i++) {
            res_fac = compute_resize_factor(parseInt(labels.width, 10),
                parseInt(labels.height, 10));
            deleted.push(false);
            for (let j = 0; j < labels.boxes[i].length; j++) {
                labels.boxes[i][j] = labels.boxes[i][j] * res_fac;
            }
        }
        let open_pred = get_open_prediction(predictions);
        this.image = image;
        this.setState({
            classes: labels.classes,
            boxes: labels.boxes,
            deleted: deleted,
            user_input: [undefined, undefined, undefined, undefined],
            predictions: predictions,
            instructions: get_instructions(open_pred),
            redirect: undefined,
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

            let url = '/api/save_labels/' + this.task_id + '/';
            let postData = JSON.stringify({
                'classes': classes,
                'boxes': boxes,
                'width': this.image.width,
                'height': this.image.height
            });

            fetch(url, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json; charset=utf-8",
                },
                body: postData
            })
                .then(
                    response => response.json(),
                    error => console.log('An error occurred.', error))
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
        let newState = this.state;
        let width = this.image.width;
        let height = this.image.height;
        let res_fac = compute_resize_factor(width, height);
        let predictions = newState.predictions;
        let pred = get_open_prediction(predictions);
        let pred_index = pred ? predictions.indexOf(pred) : predictions.length;

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

        //R: jump to next, unlabeled task from current batch
        else if (kc === 82) {
            let open_tasks_ids = batch.tasks.filter(
                (t) => !t.is_labeled).map((t) => t.id);
            let new_task_id = open_tasks_ids[0];
            for (let i = 0; i < open_tasks_ids.length; i++) {
                if (open_tasks_ids[i] > task.id) {
                    new_task_id = open_tasks_ids[i];
                    break;
                }
            }
            newState.redirect = "/label_images/" + batch.id + "/" + new_task_id;
        }

        //1-9: delete / re-add bounding box with this index
        else if (kc > 48 && kc < 58 && newState.classes.length >= (kc - 48)) {
            newState.deleted[kc - 49] = !newState.deleted[kc - 49];
            this.has_changed = true;
        }

        //U: undo last task completion
        else if (kc === 85 && pred_index > 0) {
            delete predictions[pred_index - 1]['was_successful'];

            if (predictions[pred_index - 1].hasOwnProperty('label_index')) {
                let label_index = predictions[pred_index - 1]['label_index'];
                newState.classes.splice(label_index, 1);
                newState.boxes.splice(label_index, 1);
                newState.deleted.splice(label_index, 1);
                delete predictions[pred_index - 1]['label_index']
            }
            let open_pred = get_open_prediction(predictions);
            newState.instructions = get_instructions(open_pred);
        }

        else if (pred) {
            //F: falsify proposal
            if (kc === 70) {
                //don't care about falsified annotation proposals as it was fault of object detector
                //still set variable to true to mark this proposal as complete
                pred['was_successful'] = (pred['acceptance_prediction'] === 0);
            }

            //V: verify a proposal
            else if (kc === 86 && pred['acceptance_prediction'] === 1) {
                this.has_changed = true;
                pred['was_successful'] = true;
                pred['label_index'] = newState.classes.length;
                newState.classes.push(pred['LabelName']);
                newState.boxes.push([
                    pred['XMin'] * res_fac * width,
                    pred['YMin'] * res_fac * height,
                    pred['XMax'] * res_fac * width,
                    pred['YMax'] * res_fac * height]);
                newState.deleted.push(false)
            }

            newState.instructions = get_instructions(get_open_prediction(predictions));
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
            let p = get_open_prediction(this.state.predictions);
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
                let x_min = p['XMin'] * width * res_fac;
                let x_max = p['XMax'] * width * res_fac;
                let y_min = p['YMin'] * height * res_fac;
                let y_max = p['YMax'] * height * res_fac;

                ctx.fillText(p['LabelName'], x_min + 15, y_min + 30);
                ctx.rect(x_min + 10, y_min + 10, x_max - x_min, y_max - y_min);
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
        let ui = newState.user_input;
        let width = this.image.width;
        let height = this.image.height;
        let res_fac = compute_resize_factor(width, height);
        let x_min = Math.min(ui[0][0], ui[1][0], ui[2][0], ui[3][0]);
        let x_max = Math.max(ui[0][0], ui[1][0], ui[2][0], ui[3][0]);
        let y_min = Math.min(ui[0][1], ui[1][1], ui[2][1], ui[3][1]);
        let y_max = Math.max(ui[0][1], ui[1][1], ui[2][1], ui[3][1]);

        let new_box = [x_min, y_min, x_max, y_max];

        let pred = get_open_prediction(newState.predictions);
        let c = undefined;
        if (pred && pred['acceptance_prediction'] === 0) {
            c = pred['LabelName'];
            //get relative box coordinates i.o. to compute IoU
            let b = new_box.slice();
            b[0] = b[0] / res_fac / width;
            b[1] = b[1] / res_fac / width;
            b[2] = b[2] / res_fac / height;
            b[3] = b[3] / res_fac / height;
            let relevant_predictions = newState.predictions.filter(p => p['LabelName'] === c);
            pred['was_successful'] = !should_have_been_verified(b, relevant_predictions);
            pred['label_index'] = newState.classes.length;
            let new_pred = get_open_prediction(newState.predictions);
            newState.instructions = get_instructions(new_pred);
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