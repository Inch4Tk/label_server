import fnmatch
import os
import shutil
import subprocess

from settings import model_dir, path_to_pipeline_config, \
    path_to_od_lib, path_to_od_dir
from object_detector.util import update_finetune_checkpoint

def train():
    """
    Retrain the current version of the object detection model.
    Normally, this function is only called by train_models() in flask_label/api.py.
    It is assumed that a train record called 'train.record' exists in the metadata directory and
    that the pipeline.config in the metadata directory is updated accordingly.
    These assumptions are fulfilled when api.py/train_models is used.
    """
    new_ckpt = ''
    od_model_dir = os.path.join(model_dir, 'ssd_mobilenet_v2_coco_2018_03_29')

    existent_checkpoints = [name for name in os.listdir(od_model_dir) if
                            os.path.isdir(os.path.join(od_model_dir, name))]
    existent_checkpoints.sort(key=int)

    # remove incomplete checkpoints
    for ckpt in existent_checkpoints:
        is_legit = False
        path_to_ckpt = os.path.join(od_model_dir, ckpt)
        chkpt_files = os.listdir(path_to_ckpt)
        for f in chkpt_files:
            if fnmatch.fnmatch(f, 'saved_model.pb'):
                is_legit = True
                break

        if not is_legit:
            shutil.rmtree(path_to_ckpt)
            existent_checkpoints.remove(ckpt)

    # only keep last 10 checkpoints
    if len(existent_checkpoints) > 10:
        path_to_ckpt = os.path.join(od_model_dir, existent_checkpoints[0])
        shutil.rmtree(path_to_ckpt)

    actual_checkpoint = existent_checkpoints[-1]
    actual_checkpoint_dir = os.path.join(od_model_dir, actual_checkpoint)
    new_checkpoint_dir = os.path.join(od_model_dir, str(int(actual_checkpoint) + 1))

    files_in_actual_ckpt = os.listdir(actual_checkpoint_dir)
    for f in files_in_actual_ckpt:
        if fnmatch.fnmatch(f, 'model.ckpt*'):
            update_finetune_checkpoint(os.path.join(actual_checkpoint_dir, 'model.ckpt'))
            break

    path_to_train_script = os.path.join(path_to_od_dir, 'model_main.py')
    path_to_export_script = os.path.join(path_to_od_lib, 'export_inference_graph.py')

    train_command = ['python', path_to_train_script, '--pipeline_config_path',
                     path_to_pipeline_config, '--model_dir', new_checkpoint_dir]
    p = subprocess.Popen(train_command, shell=False, stdout=subprocess.PIPE)
    p.communicate()

    files_in_new_ckpt = os.listdir(new_checkpoint_dir)
    for f in files_in_new_ckpt:
        if fnmatch.fnmatch(f, 'model.ckpt*'):
            new_ckpt = os.path.splitext(f)[0]
            break

    path_to_model_ckpt = os.path.join(new_checkpoint_dir, new_ckpt)
    export_command = ['python', path_to_export_script, '--input_type', 'image_tensor',
                      '--pipeline_config_path', path_to_pipeline_config,
                      '--trained_checkpoint_prefix', path_to_model_ckpt,
                      '--output_directory', new_checkpoint_dir]

    p = subprocess.Popen(export_command, shell=False, stdout=subprocess.PIPE)
    p.communicate()

    shutil.move(os.path.join(new_checkpoint_dir, 'saved_model', 'saved_model.pb'),
                os.path.join(new_checkpoint_dir, 'saved_model.pb'))

if __name__ == '__main__':
    train()
