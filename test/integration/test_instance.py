import re


def test_get_instance_info(get_client):
    instance = get_client.get_instance()

    assert isinstance(instance['id'], int)
    assert re.match(r'^[a-z\-]+$', instance['label'])
    assert re.match(r'^[a-z\-]+$', instance['region'])
    assert re.match(r'^[a-z\d\-]+$', instance['type'])
    assert isinstance(instance['specs']['vcpus'], int)
    assert isinstance(instance['specs']['memory'], int)
    assert isinstance(instance['specs']['gpus'], int)
    assert isinstance(instance['specs']['transfer'], int)
    assert isinstance(instance['specs']['disk'], int)
    assert isinstance(instance['backups']['enabled'], bool)
    assert instance['backups']['status'] is None
    assert re.match(r'^[a-f\d]+$', instance['host_uuid'])
    assert isinstance(instance['tags'], list)
