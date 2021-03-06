# Label Server and Client

##First Time Setup
* Install miniconda or update existing conda a few times: 
```
conda update conda
```

* Install conda environment 
```
conda env create -f conda_env.yml 
activate flask_label 
```

* Or update existing env
```
conda env update -f conda_env.yml 
```

* Or locally 
```
conda env create --prefix ./conda_env -f conda_env.yml 
activate ./conda_env 
``` 

* Install nodejs and npm. E.g. nvm for ubuntu [[https://github.com/creationix/nvm]], or nwm-windows on windows
[[https://github.com/coreybutler/nvm-windows]]
(to update npm: npm install -g npm) 

* Activate Node:
```
nvm use node
```

* Install Tensorflow models:
```
# from root directory of project
git clone https://github.com/tensorflow/models.git od_models

git clone https://github.com/cocodataset/cocoapi.git
cd cocoapi/PythonAPI
make
cp -r pycocotools ../../od_models/research/
cd ../../
rm -rf cocoapi

# From od_models/research/
protoc object_detection/protos/*.proto --python_out=.
python setup.py install

# Add the following line to your .bashrc (set $PATH_TO_PROJECT to your local path)
export PYTHONPATH=$PYTHONPATH:$PATH_TO_PROJECT/od_models/research:$PATH_TO_PROJECT/od_models/research/slim

source ~/.bashrc
```

* Test if tensorflow-models is working flawlessly
```
python od_models/research/object_detection/builders/model_builder_test.py
```

* Install Docker (e.g. on Ubuntu:)
```
sudo apt-get install docker-io
```

* Building the docker image:
```
# From root directory ("label_server")
docker build -f docker/Dockerfile_cpu -t labelserver_models_cpu .
```

Running the docker container:
```
docker run -p 9000:9000 -p 9001:9001 -v $ABSOLUTE_PATH_TO_ROOT_DIR/models:/models
--name labelserver_models_cpu labelserver_models_cpu &
```

Stopping the docker container:
```
docker kill labelserver_models_cpu
```

* Setup whole project 
```
# From project root directory
python setup.py install
npm install
```

* Adapt root_dir in **settings.py** to match the absolute path to your project root

### Using your nvidia GPU (recommended)

######If you own a NVIDIA GPU, it is recommended to follow these steps to enable GPU processing which speeds up computations a lot.
* Install CUDA (an exemplary guide for Linux can be found here: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)

* Install nvidia-docker to use your GPU in docker:
```
# exemplary for Linux

curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
  sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu16.04/amd64/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install nvidia-docker
```

* Install tensorflow-gpu:
```
pip install tensorflow-gpu==1.11.0rc0
```

* Build the docker image for GPU usage and use this image to create your containers
```
# from root directory
docker build -f docker/Dockerfile_gpu -t labelserver_models_gpu .
```

# The application

* The following file tree shows and shortly explains the functionality of important files of the project
<pre>
├── <b>annotation_predictor</b>: Contains all files related to the acceptance probability predictor
│   ├── <b>metadata</b>: Contains all training- and detection-records and log-files
|   |   └── <b>known_class_ids.json</b>: Contains all classes on which the acceptance probability predictor will be trained
│   ├── <b>util</b>: utility-functions without a main-directive that are used in other scripts
│   ├── <b>accept_prob_predictor.py</b>: Contains the architecture definitions, training and prediction functionality
│   ├── <b>prepare_groundtruth.py</b>: Download and postprocess groundtruth data of the Open Images Dataset
│   ├── <b>create_detection_record.py</b>: Create a record of object detections
│   └── <b>create_training_record.py</b>: Converts a detection_record to a TFRecord which is later used for trainign the acceptance probability predictor
├── <b>conda_env.yml</b>: external dependencies of the project
├── <b>docker</b>: contains Dockerfiles from which docker images and containers are created
├── <b>flask_label</b>: Flask application which connects the backend with the frontend
│   └── <b>api.py</b>: Contains all REST-interfaces that are used by the frontend to communicate with the backend
├── <b>instance</b>: Contains images and videos that shall be labeled
├── <b>models</b>: all files that define the neural networks which are used in this project
│   ├── <b>accept_prob_predictor</b>: binary classifier that rates a bounding box as "good" or "bad"
│   └── <b>ssd_mobilenet_v1_coco_2018_01_28</b>: object detection model from Tensorflow Model Zoo (must be downloaded first)
├── <b>object_detector</b>: all files concerning the object detector
│   ├── <b>metadata</b>: contains all files needed by the object detector, e.g. classcodes for the classes in the Open Images Dataset
│   ├── <b>download_od_model.py</b>: downloads a default model from the Tensorflow Model zoo
│   ├── <b>send_od_request.py</b>: sends an object detection request to the object detection model in the docker container
│   └── <b>train_od_model.py</b>: retrains the object detection model, called automatically during labeling
└── <b>settings.py</b>: mostly contains path expressions to important parts of the code
</pre>

## Preparing the application
* Download the object detection model from the [Tensorflow Model Zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) by executing
 ```
 python object_detector/download_od_model.py
 ```
* Add the images you want to label to **instance/images** or videos to **instance/videos**
* PURELY OPTIONAL: If you have test sets for your classes, add the test images and your ground-truth in json-format 
  to **object_detector/metadata/test** 
  * if your ground truth is in csv-format you need to convert it to json-format by using
 ```
 python python annotation_predictor/convert_oi_gt_to_jsons.py 
 
 # adapt the variable path_to_od_test_data_gt in settings.py to point to your ground truth data json
 ```
* The repository already contains a pretrained version of the acceptance probability predictor
  * **If you wish to retrain it manually**, you need a set of images with respective ground truth data
    * If you want to use images from the OID. you can use **prepare_groundtruth.py** to download the 
      whole OID groundtruth data
  * First, use create_detection record to create a json-record of the detections
  * Then, create an evaluation record using **create_evaluation_record.py**
  * Then, create a training record using **create_training_record.py**
  * Adapt **path_to_test_data** to point to this file
  * Train your network by using **accept_prob_predictor.py**
  * **Note**: Training will only work, if your object detector is already trained on the objects
    in your image. For example, for the pretrained version you find here, the Open Images Dataset
    was used which contained instances of all classes of the COCO dataset on which the default
    object detector that gets downloaded by **download_od_model.py** was trained

## Running the application
* Before running the first time we need to initialize and seed the database:
```
flask db upgrade  # Applies migrations and creates tables
flask db-init-user  # Custom cli-script which seeds the test user
flask db-update-task  # Custom cli-script which seeds the tasks
```

* "flask db-update-task" has to be called every time new images are added to or removed from the instance folder. Later on this should be replaced with a frontend uploader/inserter.

* Compile/Watch javascript/css. You can use any of the following commands:
```
npm run build
npm run build-watch
npm run build-prod
```

* Additional workflow, when changing database layouts, use the following commands to reflect the migration:
```
flask db migrate
flask db upgrade
```

* Make sure one of the Docker containers is up and running. You can check this by using 
```
docker ps
```

* Run dev server:
```
flask run
```

* You can then access the application on **localhost:5000**

* Default user for login:
  * user: test
  * pw: test
  
# Testing
```
pytest 
coverage run -m pytest
coverage html
```
