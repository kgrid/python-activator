from urllib import parse


def test_urlparse():
    ######url manifest
    base_uri = "https://github.com/kgrid/collections/manifest.json"
    relative_path = "smple-python.zip"
    assert parse.urljoin(base_uri, relative_path)=="https://github.com/kgrid/collections/smple-python.zip"

    base_uri = "https://github.com/kgrid/collections/manifest.json"
    relative_path = "zipfiles/smple-python.zip"
    assert parse.urljoin(base_uri, relative_path)=="https://github.com/kgrid/collections/zipfiles/smple-python.zip"


    base_uri = "https://github.com/kgrid/collections/manifest.json"
    relative_path = "https://github.com/kgrid/collections/smple-python.zip"
    assert parse.urljoin(base_uri, relative_path)=="https://github.com/kgrid/collections/smple-python.zip"

    #incorrect manifest: manifest in url includes an absolute path
    base_uri = "https://github.com/kgrid/collections/manifest.json"
    relative_path = "/home/tests/zipfiles/smple-python.zip"
    test=parse.urljoin(base_uri, relative_path)
    assert parse.urljoin(base_uri, relative_path)=="https://github.com/home/tests/zipfiles/smple-python.zip"

    base_uri = "https://github.com/kgrid/collections/manifest.json"
    relative_path = ""
    test=parse.urljoin(base_uri, relative_path)
    assert parse.urljoin(base_uri, relative_path)=="https://github.com/kgrid/collections/manifest.json"



    ########Path manifest
    base_uri = "file:///example/resources/manifest.json"
    relative_path = "smple-python.zip"
    assert parse.urljoin(base_uri, relative_path)=="file:///example/resources/smple-python.zip"

    base_uri = "file:///example/resources/manifest.json"
    relative_path = "zipfiles/smple-python.zip"
    assert parse.urljoin(base_uri, relative_path)=="file:///example/resources/zipfiles/smple-python.zip"

    base_uri = "file:///example/resources/manifest.json"
    relative_path = "/home/tests/zipfiles/smple-python.zip"
    assert parse.urljoin(base_uri, relative_path)=="file:///home/tests/zipfiles/smple-python.zip"

    base_uri = "file:///example/resources/manifest.json"
    relative_path = "https://github.com/kgrid/collections/smple-python.zip"
    assert parse.urljoin(base_uri, relative_path)=="https://github.com/kgrid/collections/smple-python.zip"

    base_uri = "file:///example/resources/manifest.json"
    relative_path = ""
    assert parse.urljoin(base_uri, relative_path)=="file:///example/resources/manifest.json"
