import React from "react";
import {Link} from "react-router-dom"
import {Redirect} from "react-router";
import {AutoCompleter} from "../components/AutoCompleter.jsx"

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

    if (img_width < 1 || img_height < 1) {
        return undefined;
    }

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
        this.task_id = undefined;
        this.image = undefined;
        this.resize_factor = undefined;
        this.canvasRef = React.createRef();
        this.was_trained = [];
        this.state = {
            classes: [],
            boxes: [],
            deleted: [],
            user_input: [],
            predictions: [],
            instructions: [],
            redirect: undefined,
            need_label: false
        };
        this.handle_click = this.handle_click.bind(this);
        this.handle_submit = this.handle_submit.bind(this);
        this.track_mouse_position = this.track_mouse_position.bind(this);
        this.handle_keypress = this.handle_keypress.bind(this);
    }

    componentDidMount() {
        console.log("Component did mount");
        document.addEventListener('keyup', this.handle_keypress);

        let task = this.props.task;
        this.task_id = task.id;
        this.image = this.load_image("/api/serve_image/" + task.id + "/");
        let labels = this.props.labels;

        if (this.props.labels.was_trained) {
            this.was_trained = this.props.labels.was_trained;
        }

        let predictions = this.props.predictions;
        let deleted = [];
        if (labels.boxes.length > 0) {
            this.resize_factor = compute_resize_factor(labels.width, labels.height);
            for (let i = 0; i < labels.boxes.length; i++) {
                deleted.push(false);
                for (let j = 0; j < labels.boxes[i].length; j++) {
                    labels.boxes[i][j] = labels.boxes[i][j] * this.resize_factor;
                }
            }
        }
        let open_pred = get_open_prediction(predictions);
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
            let prediction_data = this.state.predictions;
            let len = classes.length;
            let current = 0;
            for (let i = 0; i < len; i++) {
                if (this.state.deleted[i]) {
                    boxes.splice(current, 1);
                    classes.splice(current, 1);
                    this.was_trained.splice(current, 1)
                }
                else {
                    current++;
                }
            }

            //transform coordinates back to image size
            for (let i = 0; i < boxes.length; i++) {
                for (let j = 0; j < boxes[i].length; j++) {
                    boxes[i][j] = boxes[i][j] / this.resize_factor;
                }
            }
            let label_data = {
                'classes': classes,
                'boxes': boxes,
                'was_trained': this.was_trained,
                'width': this.image.width,
                'height': this.image.height
            };

            this.props.save_data(this.props.batch.id, this.task_id, label_data, prediction_data);
        }
    }

    handle_click(event) {
        let newState = this.state;

        if (newState.need_label) {
            return;
        }

        let ui = this.state.user_input;
        let img_width = this.image.width;
        let img_height = this.image.height;
        let new_width = img_width * this.resize_factor;
        let new_height = img_height * this.resize_factor;
        let bounds = this.canvasRef.current.getBoundingClientRect();
        //handle clicks on border and map input to image coordinates
        let x = Math.min(Math.max(event.clientX - bounds.left, 10), new_width + 10) - 10;
        let y = Math.min(Math.max(event.clientY - bounds.top, 10), new_height + 10) - 10;

        for (let i = 0; i < ui.length; i++) {
            if (!ui[i]) {
                ui[i] = [x, y];
                this.setState({
                    user_input: ui,
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
            let new_width = img_width * this.resize_factor;
            let new_height = img_height * this.resize_factor;
            let bounds = this.canvasRef.current.getBoundingClientRect();
            let x = Math.min(Math.max(event.clientX - bounds.left, 10), new_width + 10) - 10;
            let y = Math.min(Math.max(event.clientY - bounds.top, 10), new_height + 10) - 10;

            this.mouse_position = {x: x, y: y};
        }
        catch (e) {
        }
    }

    handle_keypress(key) {
        let newState = this.state;
        let kc = key.keyCode;

        if (newState.need_label) {
            if (kc === 27) {
                this.was_trained.pop();
                newState.need_label = false;
                newState.deleted.pop();
                newState.boxes.pop();

                this.setState({
                    boxes: newState.boxes,
                    deleted: newState.deleted,
                    need_label: newState.need_label
                })
            }
            return;
        }

        let {task, batch} = this.props;
        let task_ids = batch.tasks.map((t) => t.id);
        let width = this.image.width;
        let height = this.image.height;
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
            this.has_changed = true;
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
                this.has_changed = true;
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
                    pred['XMin'] * this.resize_factor * width,
                    pred['YMin'] * this.resize_factor * height,
                    pred['XMax'] * this.resize_factor * width,
                    pred['YMax'] * this.resize_factor * height]);
                newState.deleted.push(false);
                this.was_trained.push(false);
            }

            newState.instructions = get_instructions(get_open_prediction(predictions));
        }

        this.setState({
            classes: newState.classes,
            boxes: newState.boxes,
            deleted: newState.deleted,
            user_input: newState.user_input,
            predictions: predictions,
            instructions: newState.instructions,
            redirect: newState.redirect,
        })
    }

    handle_submit(event) {
        event.preventDefault();
        let label = this._auto_completer.getValue();
        let newState = this.state;
        newState.classes.push(label);
        if (!this.props.known_classes.includes(label)) {
            this.props.known_classes.push(label)
        }

        this.setState({
            classes: newState.classes,
            need_label: false
        })
    }

    render_image(alpha) {
        try {
            console.log('Rendering image');
            let img_width = this.image.width;
            let img_height = this.image.height;
            let b = this.state.boxes;
            let c = this.state.classes;
            let d = this.state.deleted;
            let p = get_open_prediction(this.state.predictions);

            if (this.resize_factor === undefined) {
                this.resize_factor = compute_resize_factor(img_width, img_height);
            }

            let new_width = img_width * this.resize_factor;
            let new_height = img_height * this.resize_factor;
            let colors = ['red', 'blue', 'orange', 'purple', 'brown', 'turquoise'];
            const ctx = this.canvasRef.current.getContext('2d');
            ctx.globalAlpha = alpha;
            ctx.clearRect(0, 0, 1200, 800);
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
                //convert to absolute coordinates
                let x_min = p['XMin'] * width * this.resize_factor;
                let x_max = p['XMax'] * width * this.resize_factor;
                let y_min = p['YMin'] * height * this.resize_factor;
                let y_max = p['YMax'] * height * this.resize_factor;

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
        let width = this.image.width;
        let height = this.image.height;
        let ui = this.state.user_input;
        let need_label = false;
        let x_min = Math.min(ui[0][0], ui[1][0], ui[2][0], ui[3][0]);
        let x_max = Math.max(ui[0][0], ui[1][0], ui[2][0], ui[3][0]);
        let y_min = Math.min(ui[0][1], ui[1][1], ui[2][1], ui[3][1]);
        let y_max = Math.max(ui[0][1], ui[1][1], ui[2][1], ui[3][1]);

        let new_box = [x_min, y_min, x_max, y_max];

        let pred = get_open_prediction(newState.predictions);

        let is_annotation_request = pred && pred['acceptance_prediction'] === 0;

        if (is_annotation_request) {
            let cls = pred['LabelName'];
            //get relative box coordinates i.o. to compute IoU
            let b = new_box.slice();
            b[0] = b[0] / this.resize_factor / width;
            b[1] = b[1] / this.resize_factor / width;
            b[2] = b[2] / this.resize_factor / height;
            b[3] = b[3] / this.resize_factor / height;
            let relevant_predictions = newState.predictions.filter(p => p['LabelName'] === cls);
            pred['was_successful'] = !should_have_been_verified(b, relevant_predictions);
            pred['label_index'] = newState.classes.length;
            newState.classes.push(cls);
        }

        else {
            need_label = true;
        }

        let new_pred = get_open_prediction(newState.predictions);
        newState.instructions = get_instructions(new_pred);
        newState.boxes.push(new_box);
        newState.deleted.push(false);
        this.was_trained.push(false);
        this.has_changed = true;

        this.setState({
            classes: newState.classes,
            boxes: newState.boxes,
            deleted: newState.deleted,
            user_input: [undefined, undefined, undefined, undefined],
            predictions: newState.predictions,
            instructions: newState.instructions,
            need_label: need_label
        });
    }

    render() {
        if (this.state.redirect) {
            return <Redirect push to={this.state.redirect}/>;
        }
        let state = this.state;
        let {task, batch} = this.props;
        let tasks = batch.tasks;

        console.log("rendering");

        let alpha = 1.0;
        if (state.need_label) {
            alpha = 0.1
        }

        this.render_image(alpha);

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
                        need_label: state.need_label
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

        let components = [
            <div key="1" className="filenav">
                <ul>{image_list}</ul>
            </div>,
            <div key="2" className="historynav">
                <ul>{history_list}</ul>
            </div>,
            <div key="3">
                <ul>{instruction_list}</ul>
            </div>,
            <div key="4">
            <canvas ref={this.canvasRef} width="1200" height="800"
                    onClick={this.handle_click} onMouseMove={this.track_mouse_position}/>
            </div>
        ];
        if (state.need_label) {
            components[3] =
                <div key="4" className="wrapper">
                    <canvas ref={this.canvasRef} width="1200" height="800"
                            onClick={this.handle_click} onMouseMove={this.track_mouse_position}/>
                    <form onSubmit={this.handle_submit}><AutoCompleter
                        className="autocompleter" suggestions={['a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c','a','b','c',]}
                        alwaysRenderSuggestions={true} ref={(ref) => this._auto_completer = ref}/>
                    </form>
                </div>
        }
        return (components)
    }
}

export {LabelInterface}