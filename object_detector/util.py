import json

from annotation_predictor.util.class_reader import ClassReader
from annotation_predictor.util.settings import path_to_known_class_ids, path_to_known_class_pbtxt, \
    path_to_pipeline_config

def parse_class_ids_json_to_pbtxt():
    with open(path_to_known_class_ids, 'r') as f:
        data = json.load(f)
    ids = list(data.keys())
    ids.sort()
    end = '\n'
    s = ' '
    out = ''
    for id in ids:
        cls = data[id]
        out += 'item' + s + '{' + end
        out += s*2 + 'id:' + ' ' + str(id) + end
        out += s*2 + 'name:' + ' ' + '\'' + cls + '\'' + end
        out += '}' + end*2

    with open(path_to_known_class_pbtxt, 'w') as f:
        f.write(out)

def update_number_of_classes():
    class_reader = ClassReader(path_to_known_class_ids)
    nr_of_classes = len(class_reader.class_ids)
    with open(path_to_pipeline_config, 'r') as f:
        data = f.readlines()

    data[2] = '    num_classes: {}\n'.format(nr_of_classes)

    with open(path_to_pipeline_config, 'w') as f:
        f.writelines(data)

def update_finetune_checkpoint(path_to_new_checkpoint):
    with open(path_to_pipeline_config, 'r') as f:
        data = f.readlines()

    data[156] = '  fine_tune_checkpoint: {}\n'.format(f'"{path_to_new_checkpoint}"')

    with open(path_to_pipeline_config, 'w') as f:
        f.writelines(data)
