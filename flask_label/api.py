import json
import os
import random
import xml.etree.ElementTree as ET
from xml.dom import minidom

import tensorflow as tf
from flask import (
    Blueprint, current_app, send_from_directory, jsonify, request
)
from object_detection.utils import dataset_util

from annotation_predictor import accept_prob_predictor
from annotation_predictor.send_od_request import send_od_request
from annotation_predictor.util.class_reader import ClassReader
from annotation_predictor.util.send_accept_prob_request import send_accept_prob_request
from settings import known_class_ids_annotation_predictor, \
    known_class_ids_od
from annotation_predictor.util.util import compute_feature_vector
from flask_label.auth import api_login_required
from flask_label.database import db
from flask_label.database_cli import db_update_task
from flask_label.models import (
    ImageTask, ImageBatch, VideoBatch, image_batch_schema, video_batch_schema, image_task_schema
)
from object_detector import train_od_model
from object_detector.util import parse_class_ids_json_to_pbtxt, update_number_of_classes

bp = Blueprint("api", __name__,
               url_prefix="/api")

def batch_statistics(batch):
    lc = 0
    for task in batch["tasks"]:
        if task["is_labeled"]:
            lc += 1

    return (len(batch["tasks"]), lc)

def get_path_to_image(img_id):
    img_task = ImageTask.query.filter_by(id=img_id).first()

    img_path = os.path.join(
        current_app.instance_path,
        current_app.config["IMAGE_DIR"],
        img_task.batch.dirname,
        img_task.filename
    )

    return img_path

def get_path_to_label(img_id):
    img_task = ImageTask.query.filter_by(id=img_id).first()

    path = os.path.join(
        current_app.instance_path,
        current_app.config['IMAGE_DIR'],
        img_task.batch.dirname,
        current_app.config['IMAGE_LABEL_SUBDIR'],
        img_task.filename
    )
    base = os.path.splitext(path)[0]
    path = base + '.xml'

    return path

def get_path_to_prediction(img_id):
    img_task = ImageTask.query.filter_by(id=img_id).first()

    pred_dir_path = os.path.join(
        current_app.instance_path,
        current_app.config["IMAGE_DIR"],
        img_task.batch.dirname,
        current_app.config['IMAGE_PREDICTIONS_SUBDIR'],
        img_task.filename
    )

    base = os.path.splitext(pred_dir_path)[0]
    pred_path = base + '.json'

    return pred_path

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

def create_tf_example(example):
    width = int(example[0])
    height = int(example[1])
    filename = str.encode(example[2])

    with tf.gfile.GFile(example[3], 'rb') as f:
        encoded_image_data = bytes(f.read())
    image_format = b'jpg'

    boxes = example[5]
    xmins = []
    ymins = []
    xmaxs = []
    ymaxs = []

    for b in boxes:
        xmins.append(b[0])
        ymins.append(b[1])
        xmaxs.append(b[2])
        ymaxs.append(b[3])

    xmins = [x / width for x in xmins]
    xmaxs = [x / width for x in xmaxs]
    ymins = [y / height for y in ymins]
    ymaxs = [y / height for y in ymaxs]

    class_reader = ClassReader(known_class_ids_annotation_predictor)

    classes_text = example[4][:]
    classes = []

    for i, cls in enumerate(classes_text):
        classes.append(class_reader.get_index_of_class_from_label(cls))
        class_encoded = str.encode(cls)
        classes_text[i] = class_encoded

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_image_data),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example

@bp.route("/batches/")
@api_login_required
def batches():
    """Return all image and video directories and their stats."""
    img_batches = ImageBatch.query.options(db.joinedload('tasks')).all()
    video_batches = VideoBatch.query.all()

    image_batch_data = image_batch_schema.dump(img_batches, many=True)
    video_batch_data = video_batch_schema.dump(video_batches, many=True)

    # Add postprocessing info about statistics
    for batch in image_batch_data:
        batch["imgCount"], batch["labeledCount"] = batch_statistics(batch)

    return jsonify({"imageBatches": image_batch_data, "videoBatches": video_batch_data})

@bp.route("/img_batch/<int:batch_id>")
@api_login_required
def img_batch(batch_id):
    """Return data to a single image batch"""
    img_batch = ImageBatch.query.filter_by(id=batch_id).options(db.joinedload('tasks')).first()

    batch = image_batch_schema.dump(img_batch)
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
    img_path = get_path_to_image(img_id)

    current_app.logger.info(img_path)

    path, file = os.path.split(img_path)
    return send_from_directory(path, file)

@bp.route("/serve_labels/")
@api_login_required
def serve_labels():
    """Serves labels for all images from the instance folder"""
    db_update_task()
    labels = []
    img_batches = ImageBatch.query.options(db.joinedload('tasks')).all()
    image_batch_data = image_batch_schema.dump(img_batches, many=True)
    for batch in image_batch_data:
        for task in batch['tasks']:
            label_path = get_path_to_label(task['id'])

            width, height, classes, boxes = read_labels_from_xml(label_path)

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

    label_path = get_path_to_label(img_id)

    if not os.path.exists(os.path.dirname(label_path)):
        os.mkdir(label_path)

    save_labels_to_xml(data, label_path)

    db_update_task()

    return jsonify(success=True)

@bp.route('/serve_predictions/')
@api_login_required
def serve_predictions():
    """Serves predictions for all images from the instance folder"""
    predictions = []
    img_batches = ImageBatch.query.options(db.joinedload('tasks')).all()
    image_batch_data = image_batch_schema.dump(img_batches, many=True)
    for batch in image_batch_data:
        for task in batch['tasks']:
            img_path = get_path_to_image(task['id'])
            pred_path = get_path_to_prediction(task['id'])

            if os.path.exists(pred_path):
                with open(pred_path, 'r') as f:
                    predictions.append({'id': str(task['id']), 'predictions': json.load(f)})
            else:
                prediction = send_od_request(img_path)
                prediction = list(prediction.values())[0]
                if len(prediction) > 0:
                    feature_vectors = []
                    for i, _ in enumerate(prediction):
                        feature_vectors.append(compute_feature_vector(prediction, i))
                    acceptance_prediction = send_accept_prob_request(feature_vectors)

                    for i, p in enumerate(acceptance_prediction):
                        prediction[i]['acceptance_prediction'] = p
                    prediction.sort(key=lambda p: p['acceptance_prediction'], reverse=True)

                predictions.append({'id': str(task['id']), 'predictions': prediction})

                if not os.path.exists(os.path.dirname(pred_path)):
                    os.mkdir(os.path.dirname(pred_path))
                with open(pred_path, 'w') as f:
                    json.dump(prediction, f)

    return jsonify(predictions)

@bp.route('/update_predictions/')
@api_login_required
def update_predictions():
    """Updates predictions for all images from the instance folder"""
    predictions = []
    img_batches = ImageBatch.query.options(db.joinedload('tasks')).all()
    image_batch_data = image_batch_schema.dump(img_batches, many=True)
    for batch in image_batch_data:
        for task in batch['tasks']:
            img_path = get_path_to_image(task['id'])
            pred_path = get_path_to_prediction(task['id'])

            prediction = send_od_request(img_path)
            prediction = list(prediction.values())[0]
            if len(prediction) > 0:
                feature_vectors = []
                for i, _ in enumerate(prediction):
                    feature_vectors.append(compute_feature_vector(prediction, i))
                acceptance_prediction = send_accept_prob_request(feature_vectors)
                for i, p in enumerate(acceptance_prediction):
                    prediction[i]['acceptance_prediction'] = p
                prediction.sort(key=lambda p: p['acceptance_prediction'], reverse=True)

            predictions.append({'id': str(task['id']), 'predictions': prediction})

            if not os.path.exists(os.path.dirname(pred_path)):
                os.mkdir(os.path.dirname(pred_path))
            with open(pred_path, 'w') as f:
                json.dump(prediction, f)

    return jsonify(predictions)

@bp.route('/save_predictions/<int:img_id>/', methods=['POST'])
@api_login_required
def save_predictions(img_id):
    predictions = request.get_json()

    pred_path = get_path_to_prediction(img_id)

    if not os.path.exists(os.path.dirname(pred_path)):
        os.mkdir(os.path.dirname(pred_path))

    result = []
    for p in predictions:
        result.append(p)

    with open(pred_path, 'w') as f:
        json.dump(result, f)

    return jsonify(success=True)

@bp.route("/serve_classes/")
@api_login_required
def serve_classes():
    """Serves classes for all images from the instance folder"""
    class_reader = ClassReader(known_class_ids_od)

    return jsonify(list(class_reader.class_ids.values()))

@bp.route('/train_models/')
@api_login_required
def train_models():
    """Checks instance folder for new training data and uses it to further train models"""
    nr_of_labels = 0
    feature_vectors = []
    y_ = []
    img_batches = ImageBatch.query.options(db.joinedload('tasks')).all()
    image_batch_data = image_batch_schema.dump(img_batches, many=True)
    class_reader_od = ClassReader(known_class_ids_od)
    class_reader_acc_prob = ClassReader(known_class_ids_annotation_predictor)
    writer = tf.python_io.TFRecordWriter(
        '/home/schererc/IntelliJProjects/label_server/object_detector/data/train.record')

    for batch in image_batch_data:
        for task in batch['tasks']:
            label_path = get_path_to_label(task['id'])
            if os.path.exists(label_path):
                width, height, classes, boxes = read_labels_from_xml(label_path)
                for i, cls in enumerate(classes):
                    nr_of_labels += 1
                    image_path = get_path_to_image(task['id'])

                    class_id_od = class_reader_od.get_index_of_class_from_label(cls)
                    if class_id_od == -1:
                        class_reader_od.add_class_to_file(cls)
                        parse_class_ids_json_to_pbtxt()
                        update_number_of_classes()

                    class_id_accept_prob = class_reader_acc_prob.get_index_of_class_from_label(
                        cls)
                    if class_id_accept_prob == -1:
                        class_reader_acc_prob.add_class_to_file(cls)

                    tf_example = create_tf_example(
                        [width, height, task['filename'], image_path, classes, boxes])
                    writer.write(tf_example.SerializeToString())

            pred_path = get_path_to_prediction(task['id'])
            if os.path.exists(pred_path):
                with open(pred_path, 'r') as f:
                    predictions = json.load(f)
                for i, p in enumerate(predictions):
                    if 'was_successful' in p and not p['was_successful']:
                        label = p['LabelName']
                        feature_vectors.append(compute_feature_vector(predictions, i))
                        predictions[i]['LabelName'] = label

                        if p['acceptance_prediction'] is 0.0:
                            y_.append(1.0)
                        else:
                            y_.append(0.0)

                        # mark as complete
                        p['was_successful'] = True

                with open(pred_path, 'w') as f:
                    json.dump(predictions, f)
    writer.close()

    if len(feature_vectors) > 0:
        accept_prob_predictor.main(mode='train', user_feedback={'x': feature_vectors, 'y_': y_})

    if nr_of_labels > 0:
        train_od_model.train()

    return jsonify(success=True)
