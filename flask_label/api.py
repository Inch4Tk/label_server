import os
import random
import xml.etree.ElementTree as ET
from xml.dom import minidom

from flask import (
    Blueprint, current_app, send_from_directory, jsonify, request
)

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

@bp.route("/serve_labels/<int:img_id>/")
@api_login_required
def serve_labels(img_id):
    """Serves labels from an xml-file for an image from the instance folder

    Args:
        img_id (int): Is the same as task id, since every task is matched to one image.
    """

    classes = []
    boxes = []

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
    width = 0
    height = 0

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

    return jsonify({'classes': classes, 'boxes': boxes, 'width': width, 'height': height})

@bp.route('/save_labels/<int:img_id>/', methods=['POST'])
@api_login_required
def save_labels(img_id):
    """"Saves labels entered by a labeler for an image from the instance folder

    Args:
        img_id (int): Is the same as task id, since every task is matched to one image.
    """

    data = request.get_json()
    classes = data['classes']
    boxes = data['boxes']
    width = data['width']
    height = data['height']

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

        db_update_task()

    elif os.path.exists(path):
        os.remove(path)

    return jsonify(success=True)
