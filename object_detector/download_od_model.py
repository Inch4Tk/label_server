import os
import shutil
import tarfile
import urllib.request as urllib

from annotation_predictor.util.settings import model_dir

def download_od_model():
    """
    Downloads a mobile model from the Tensorflow model zoo and prepares it for usage in
    Tensorflow Serving.
    """
    model_name = 'ssdlite_mobilenet_v2_coco_2018_05_09'
    fname = '{}.tar.gz'.format(model_name)
    url = "http://download.tensorflow.org/models/object_detection/{}".format(fname)
    mobile_dir = os.path.join(model_dir, model_name)

    if not os.path.exists(mobile_dir):
        os.mkdir(mobile_dir)
        file = urllib.URLopener()
        file.retrieve(url, fname)

        tar = tarfile.open(fname, "r:gz")
        tar.extractall('models')
        tar.close()
        os.remove(fname)

        checkpoint_dir = os.path.join(mobile_dir, '1')
        os.rename(os.path.join(mobile_dir, 'saved_model'), checkpoint_dir)
        shutil.move(os.path.join(mobile_dir, 'checkpoint'),
                    os.path.join(checkpoint_dir, 'checkpoint'))
        shutil.move(os.path.join(mobile_dir, 'frozen_inference_graph.pb'),
                    os.path.join(checkpoint_dir, 'frozen_inference_graph.pb'))
        shutil.move(os.path.join(mobile_dir, 'model.ckpt.data-00000-of-00001'),
                    os.path.join(checkpoint_dir, 'model.ckpt.data-00000-of-00001'))
        shutil.move(os.path.join(mobile_dir, 'model.ckpt.index'),
                    os.path.join(checkpoint_dir, 'model.ckpt.index'))
        shutil.move(os.path.join(mobile_dir, 'model.ckpt.meta'),
                    os.path.join(checkpoint_dir, 'model.ckpt.meta'))
        shutil.move(os.path.join(mobile_dir, 'pipeline.config'),
                    os.path.join(checkpoint_dir, 'pipeline.config'))

if __name__ == '__main__':
    download_od_model()
