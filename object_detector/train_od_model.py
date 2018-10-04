import fnmatch
import os
import shutil
import subprocess

from annotation_predictor.util.settings import model_dir, path_to_pipeline_config, \
    path_to_od_lib, path_to_od_dir
from object_detector.util import update_finetune_checkpoint

def train():
    od_model_dir = os.path.join(model_dir, 'ssdlite_mobilenet_v2_coco_2018_05_09')

    existent_checkpoints = [name for name in os.listdir(od_model_dir) if
                            os.path.isdir(os.path.join(od_model_dir, name))]
    existent_checkpoints.sort(key=int)

    # remove incomplete checkpoints
    for chkpt in existent_checkpoints:
        is_legit = False
        path_to_ckpt = os.path.join(od_model_dir, chkpt)
        chkpt_files = os.listdir(path_to_ckpt)
        for f in chkpt_files:
            if fnmatch.fnmatch(f, 'model.ckpt*'):
                is_legit = True
                break

        if not is_legit:
            shutil.rmtree(path_to_ckpt)
            existent_checkpoints.remove(chkpt)

    actual_checkpoint = str(len(existent_checkpoints))
    actual_checkpoint_dir = os.path.join(od_model_dir, actual_checkpoint)
    new_checkpoint_dir = os.path.join(od_model_dir, str(int(actual_checkpoint) + 1))

    files_in_actual_ckpt = os.listdir(actual_checkpoint_dir)
    for f in files_in_actual_ckpt:
        if fnmatch.fnmatch(f, 'model.ckpt*'):
            update_finetune_checkpoint(os.path.join(actual_checkpoint_dir, 'model.ckpt'))
            break

        existent_checkpoints.remove(actual_checkpoint)
        shutil.rmtree(actual_checkpoint_dir)

    path_to_train_script = os.path.join(path_to_od_lib, 'model_main.py')
    path_to_export_script = os.path.join(path_to_od_lib, 'export_inference_graph.py')
    path_to_model_ckpt = os.path.join(new_checkpoint_dir, 'model.ckpt-5')

    train_command = ['python', path_to_train_script, '--pipeline_config_path',
                     path_to_pipeline_config, '--model_dir', new_checkpoint_dir]
    export_command = ['python', path_to_export_script, '--input_type', 'image_tensor',
                      '--pipeline_config_path', path_to_pipeline_config,
                      '--trained_checkpoint_prefix', path_to_model_ckpt,
                      '--output_directory', new_checkpoint_dir]

    p = subprocess.Popen(train_command, shell=False, stdout=subprocess.PIPE)
    p.communicate()
    p = subprocess.Popen(export_command, shell=False, stdout=subprocess.PIPE)
    p.communicate()

    shutil.move(os.path.join(new_checkpoint_dir, 'saved_model', 'saved_model.pb'),
                os.path.join(new_checkpoint_dir, 'saved_model.pb'))

if __name__ == '__main__':
    train()
