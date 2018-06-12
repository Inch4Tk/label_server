from .database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, unique=True, nullable=False)

class ImageTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)
    is_labeled = db.Column(db.Boolean, nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey("image_batch.id"), nullable=False)
    batch = db.relationship("ImageBatch", backref=db.backref("tasks", lazy=True))

class ImageBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dirname = db.Column(db.Text, nullable=False)

class VideoBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dirname = db.Column(db.Text, nullable=False)