DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS image_task;
DROP TABLE IF EXISTS image_batch;
DROP TABLE IF EXISTS video_batch;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE image_task (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL,
  is_labeled BOOLEAN NOT NULL,
  batch_id INTEGER NOT NULL,
  FOREIGN KEY (batch_id) REFERENCES image_batch (id)
);

CREATE TABLE image_batch (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dirname TEXT UNIQUE NOT NULL
);

CREATE TABLE video_batch (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dirname TEXT UNIQUE NOT NULL
);
