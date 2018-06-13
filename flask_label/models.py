from flask_label.database import db, ma

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


# ---------------------------------------------------------------------
# SCHEMAS

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

class ImageTaskSchema(ma.ModelSchema):
    batch = ma.Nested("ImageBatchSchema", exclude=("tasks"))
    class Meta:
        model = ImageTask

class ImageBatchSchema(ma.ModelSchema):
    tasks = ma.Nested("ImageTaskSchema", many=True, exclude=("batch", "batch_id"))
    class Meta:
        model = ImageBatch

class VideoBatchSchema(ma.ModelSchema):
    class Meta:
        model = VideoBatch

user_schema = UserSchema()
user_safe_schema = UserSchema(exclude=["password"])
image_task_schema = ImageTaskSchema()
image_batch_schema = ImageBatchSchema()
video_batch_schema = VideoBatchSchema()
