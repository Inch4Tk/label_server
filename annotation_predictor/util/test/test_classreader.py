import pytest

from annotation_predictor.util.test.conftest import test_data, test_classreader

def test_get_class_from_id_with_nonexistent_id():
    with pytest.raises(KeyError, message='This ID does not exist'):
        test_classreader.get_class_from_id(test_data[0]['LabelName'])

def test_get_class_from_id_with_existent_id():
    assert test_classreader.get_class_from_id(test_data[1]['LabelName']) == 'Hamburger'
