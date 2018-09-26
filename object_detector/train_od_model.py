import os
import shutil
import subprocess

from annotation_predictor.util.settings import model_dir, path_to_pipeline_config, \
    path_to_od_lib

def train():
    od_model_dir = os.path.join(model_dir, 'ssdlite_mobilenet_v2_coco_2018_05_09')

    existent_checkpoints = [name for name in os.listdir(od_model_dir) if
                            os.path.isdir(os.path.join(od_model_dir, name))]
    existent_checkpoints.sort(key=int)

    while True:
        if len(existent_checkpoints) == 0:
            new_checkpoint_dir = os.path.join(od_model_dir, '1')
            break

        actual_checkpoint = existent_checkpoints[len(existent_checkpoints) - 1]
        actual_checkpoint_dir = os.path.join(od_model_dir, actual_checkpoint)

        if len(os.listdir(actual_checkpoint_dir)) > 0:
            new_checkpoint_dir = os.path.join(od_model_dir, str(int(actual_checkpoint) + 1))
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
