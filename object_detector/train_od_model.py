import os
import shutil

from object_detection.utils.config_util import get_configs_from_pipeline_file, \
    create_pipeline_proto_from_configs

from annotation_predictor.util.settings import model_dir
from object_detector.exporter import export_inference_graph

def train():
    od_model_dir = os.path.join(model_dir, 'ssdlite_mobilenet_v2_coco_2018_05_09')

    existent_checkpoints = [name for name in os.listdir(od_model_dir) if
                            os.path.isdir(os.path.join(od_model_dir, name))]
    existent_checkpoints.sort(key=int)

    while True:
        actual_checkpoint_dir = ''
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

    # Create proto from model configuration
    configs = get_configs_from_pipeline_file(os.path.join(od_model_dir, 'pipeline.config'))
    pipeline_config = create_pipeline_proto_from_configs(configs=configs)

    # save new frozen graph for tensorflow serving
    export_inference_graph(input_type='image_tensor', pipeline_config=pipeline_config,
                           trained_checkpoint_prefix=os.path.join(actual_checkpoint_dir,
                                                                  'model.ckpt'),
                           output_directory=od_model_dir)

    shutil.move(os.path.join(od_model_dir, 'saved_model'), new_checkpoint_dir)

if __name__ == '__main__':
    train()
