import json
import os
import random
import xml.etree.ElementTree as ET
from xml.dom import minidom

from flask import (
    Blueprint, current_app, send_from_directory, jsonify, request
)

from annotation_predictor.send_od_request import send_od_request
from annotation_predictor.util.class_reader import ClassReader
from annotation_predictor.util.send_accept_prob_request import send_accept_prob_request
from annotation_predictor.util.settings import class_ids_oid_file
from annotation_predictor.util.util import compute_feature_vector
from flask_label.auth import api_login_required
from flask_label.database import db
from flask_label.database_cli import db_update_task
from flask_label.models import (
    ImageTask, ImageBatch, VideoBatch, image_batch_schema, video_batch_schema, image_task_schema
)

bp = Blueprint("api", __name__,
               url_prefix="/api")

def batch_statistics(batch):
    lc = 0
    for task in batch["tasks"]:
        if task["is_labeled"]:
            lc += 1

    return (len(batch["tasks"]), lc)

def read_labels_from_xml(path):
    """
    Reads in an xml-file containing labels for an image and transforms it to a json.

    Returns:
        width: width of the respective image of the label
        height: height of the respective image of the label
        classes: classes of annotated objects
        boxes: position of annotated objects
    """

    width = '-1'
    height = '-1'
    classes = []
    boxes = []

    if os.path.exists(path):
        tree = ET.parse(path)
        root = tree.getroot()
        for name in root.findall('./size/width'):
            width = name.text

        for name in root.findall('./size/height'):
            height = name.text

        for name in root.findall('./object/name'):
            classes.append(name.text)

        for i, xmin in enumerate(root.findall('./object/bndbox/xmin')):
            boxes.append([])
            boxes[i].append(int(xmin.text, 10))

        for i, ymin in enumerate(root.findall('./object/bndbox/ymin')):
            boxes[i].append(int(ymin.text, 10))

        for i, xmax in enumerate(root.findall('./object/bndbox/xmax')):
            boxes[i].append(int(xmax.text, 10))

        for i, ymax in enumerate(root.findall('./object/bndbox/ymax')):
            boxes[i].append(int(ymax.text, 10))

    return width, height, classes, boxes

def save_labels_to_xml(data, path):
    """
    Save labels in data to xml-file specified by path or deletes the file, when data is empty.

    Args:
        data: dict containing the label data
        path: path to xml-file where the labels will be saved
    """

    classes = data['classes']
    boxes = data['boxes']
    width = data['width']
    height = data['height']
    if len(classes) != 0:
        root = ET.Element('annotation')

        size = ET.SubElement(root, 'size')
        ET.SubElement(size, 'width').text = str(width)
        ET.SubElement(size, 'height').text = str(height)

        for i, c in enumerate(classes):
            obj = ET.SubElement(root, 'object')
            ET.SubElement(obj, 'name').text = c
            box = ET.SubElement(obj, 'bndbox')
            ET.SubElement(box, 'xmin').text = str(round(boxes[i][0]))
            ET.SubElement(box, 'ymin').text = str(round(boxes[i][1]))
            ET.SubElement(box, 'xmax').text = str(round(boxes[i][2]))
            ET.SubElement(box, 'ymax').text = str(round(boxes[i][3]))

        rough_str = ET.tostring(root)
        pretty_str = minidom.parseString(rough_str).toprettyxml(indent="  ")

        with open(path, 'w') as f:
            f.write(pretty_str)

    elif os.path.exists(path):
        os.remove(path)

@bp.route("/batches/")
@api_login_required
def batches():
    """Return all image and video directories and their stats."""
    img_batches = ImageBatch.query.options(db.joinedload('tasks')).all()
    video_batches = VideoBatch.query.all()

    image_batch_data = image_batch_schema.dump(img_batches, many=True).data
    video_batch_data = video_batch_schema.dump(video_batches, many=True).data

    # Add postprocessing info about statistics
    for batch in image_batch_data:
        batch["imgCount"], batch["labeledCount"] = batch_statistics(batch)

    return jsonify({"imageBatches": image_batch_data, "videoBatches": video_batch_data})

@bp.route("/img_batch/<int:batch_id>")
@api_login_required
def img_batch(batch_id):
    """Return data to a single image batch"""
    img_batch = ImageBatch.query.filter_by(id=batch_id).options(db.joinedload('tasks')).first()

    batch = image_batch_schema.dump(img_batch).data
    batch["imgCount"], batch["labeledCount"] = batch_statistics(batch)

    return jsonify(batch)

@bp.route("/img_task/<int:task_id>")
@api_login_required
def image_task(task_id):
    img_task = ImageTask.query.filter_by(id=task_id).first()

    return image_task_schema.jsonify(img_task)

@bp.route("/img_task/random/<int:batch_id>")
@api_login_required
def image_task_random(batch_id):
    img_tasks = []
    labeled = request.args.get("labeled")
    if labeled == "true":
        img_tasks = ImageTask.query.filter_by(batch_id=batch_id, is_labeled=True).all()
    elif labeled == "false":
        img_tasks = ImageTask.query.filter_by(batch_id=batch_id, is_labeled=False).all()
    else:
        img_tasks = ImageTask.query.filter_by(batch_id=batch_id).all()

    if not img_tasks:
        return jsonify(dict())

    img_task = random.choice(img_tasks)
    return image_task_schema.jsonify(img_task)

@bp.route("/serve_image/<int:img_id>/")
@api_login_required
def serve_image(img_id):
    """Serves an image from the instance folder

    Args:
        img_id (int): Is the same as task id, since every task is matched to one image.
    """
    img_task = ImageTask.query.filter_by(id=img_id).first()

    img_path = os.path.join(
        current_app.instance_path,
        current_app.config["IMAGE_DIR"],
        img_task.batch.dirname
    )

    current_app.logger.info(os.path.join(img_path, img_task.filename))
    return send_from_directory(img_path, img_task.filename)

@bp.route("/labels/")
@api_login_required
def labels():
    """Serves labels for all images from the instance folder"""
    labels = []
    img_batches = ImageBatch.query.options(db.joinedload('tasks')).all()
    image_batch_data = image_batch_schema.dump(img_batches, many=True).data
    for batch in image_batch_data:
        for task in batch['tasks']:
            img_task = ImageTask.query.filter_by(id=task['id']).first()

            path = os.path.join(
                current_app.instance_path,
                current_app.config['IMAGE_DIR'],
                img_task.batch.dirname,
                current_app.config['IMAGE_LABEL_SUBDIR'],
                img_task.filename
            )
            base = os.path.splitext(path)[0]
            path = base + '.xml'

            width, height, classes, boxes = read_labels_from_xml(path)

            labels.append({'id': str(task['id']),
                           'classes': classes,
                           'boxes': boxes,
                           'width': width,
                           'height': height})

    return jsonify(labels)

@bp.route('/save_labels/<int:img_id>/', methods=['POST'])
@api_login_required
def save_labels(img_id):
    """"Saves labels entered by a labeler for an image from the instance folder

    Args:
        img_id (int): Is the same as task id, since every task is matched to one image.
    """

    data = request.get_json()

    img_task = ImageTask.query.filter_by(id=img_id).first()

    label_path = os.path.join(
        current_app.instance_path,
        current_app.config['IMAGE_DIR'],
        img_task.batch.dirname,
        current_app.config['IMAGE_LABEL_SUBDIR'],
    )
    if not os.path.exists(label_path):
        os.mkdir(label_path)

    file_path = os.path.join(label_path, img_task.filename)
    base = os.path.splitext(file_path)[0]
    file_path = base + '.xml'

    save_labels_to_xml(data, file_path)

    db_update_task()

    return jsonify(success=True)

@bp.route('/predictions/')
@api_login_required
def predictions():
    """Serves predictions for all images from the instance folder"""
    predictions = []
    img_batches = ImageBatch.query.options(db.joinedload('tasks')).all()
    image_batch_data = image_batch_schema.dump(img_batches, many=True).data
    for batch in image_batch_data:
        for task in batch['tasks']:
            img_task = ImageTask.query.filter_by(id=task['id']).first()

            img_path = os.path.join(
                current_app.instance_path,
                current_app.config["IMAGE_DIR"],
                img_task.batch.dirname,
                img_task.filename
            )
            pred_path = os.path.join(
                current_app.instance_path,
                current_app.config["IMAGE_DIR"],
                img_task.batch.dirname,
                current_app.config['IMAGE_PREDICTIONS_SUBDIR'])

            json_path = os.path.join(
                pred_path,
                img_task.filename
            )

            base = os.path.splitext(json_path)[0]
            json_path = base + '.json'

            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    predictions.append({'id': str(task['id']), 'predictions': json.load(f)})
            else:
                prediction = send_od_request(img_path)
                prediction = list(prediction.values())[0]
                if len(prediction) > 0:
                    feature_vectors = []
                    for i, _ in enumerate(prediction):
                        feature_vectors.append(compute_feature_vector(prediction, i))
                    acceptance_prediction = send_accept_prob_request(feature_vectors)

                    class_reader = ClassReader(class_ids_oid_file)
                    for i, p in enumerate(acceptance_prediction):
                        prediction[i]['acceptance_prediction'] = p
                        prediction[i]['LabelName'] = class_reader.get_class_from_id(
                            prediction[i]['LabelName'])
                    prediction.sort(key=lambda p: p['acceptance_prediction'], reverse=True)

                predictions.append({'id': str(task['id']), 'predictions': prediction})

                if not os.path.exists(pred_path):
                    os.mkdir(pred_path)
                with open(json_path, 'w') as f:
                    json.dump(prediction, f)
    return jsonify(predictions)

@bp.route('/save_predictions/<int:img_id>/', methods=['POST'])
@api_login_required
def save_predictions(img_id):
    predictions = request.get_json()
    img_task = ImageTask.query.filter_by(id=img_id).first()

    path = os.path.join(
        current_app.instance_path,
        current_app.config['IMAGE_DIR'],
        img_task.batch.dirname,
        current_app.config['IMAGE_PREDICTIONS_SUBDIR'],
    )

    if not os.path.exists(path):
        os.mkdir(path)

    file_path = os.path.join(path, img_task.filename)
    base = os.path.splitext(file_path)[0]
    file_path = base + '.json'

    result = []
    for p in predictions:
        result.append(p)

    with open(file_path, 'w') as f:
        json.dump(result, f)

    return jsonify(success=True)
