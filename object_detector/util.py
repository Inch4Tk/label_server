import json

from annotation_predictor.util.class_reader import ClassReader
from settings import class_ids_od, path_to_known_class_pbtxt, \
    path_to_pipeline_config

def parse_class_ids_json_to_pbtxt():
    """
    Parse all classes from the class_ids_od file and generate a protobuf file based on it
    which is used by the training pipeline for the object detector
    """
    with open(class_ids_od, 'r') as f:
        data = json.load(f)
    ids = list(data.keys())
    ids.sort()
    end = '\n'
    s = ' '
    out = ''
    for id in ids:
        if id is not None:
            cls = data[id]
            out += 'item' + s + '{' + end
            out += s * 2 + 'id:' + ' ' + str(int(float(id))) + end
            out += s * 2 + 'name:' + ' ' + '\'' + cls + '\'' + end
            out += '}' + end * 2

    with open(path_to_known_class_pbtxt, 'w') as f:
        f.write(out)

def update_number_of_classes():
    """
    Update the number of classes in the training configuration based on the known_class_ids file
    """
    class_reader = ClassReader(class_ids_od)
    nr_of_classes = len(class_reader.class_ids)
    with open(path_to_pipeline_config, 'r') as f:
        data = f.readlines()

    data[2] = '    num_classes: {}\n'.format(nr_of_classes)

    with open(path_to_pipeline_config, 'w') as f:
        f.writelines(data)

def update_finetune_checkpoint(path_to_new_checkpoint):
    """
    Update the path to the checkpoint directory which should be retrained to the newest checkpoint
    directory
    """
    with open(path_to_pipeline_config, 'r') as f:
        data = f.readlines()

    data[156] = '  fine_tune_checkpoint: {}\n'.format(f'"{path_to_new_checkpoint}"')

    with open(path_to_pipeline_config, 'w') as f:
        f.writelines(data)
