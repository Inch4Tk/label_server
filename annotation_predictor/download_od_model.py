import os
import urllib.request as urllib
import tarfile
def download_od_model():
    model_name = 'ssdlite_mobilenet_v2_coco_2018_05_09'
    fname = '{}.tar.gz'.format(model_name)
    url = "http://download.tensorflow.org/models/object_detection/{}".format(fname)
    model_dir = os.path.join('models', model_name)

    if not os.path.exists(os.path.join(model_dir, '1', 'saved_model.pb')):
        file = urllib.URLopener()
        file.retrieve(url, fname)

        tar = tarfile.open(fname, "r:gz")
        tar.extractall('models')
        tar.close()
        os.remove(fname)
        os.rename(os.path.join(model_dir, 'saved_model'), os.path.join(model_dir, '1'))


if __name__ == '__main__':
    download_od_model()