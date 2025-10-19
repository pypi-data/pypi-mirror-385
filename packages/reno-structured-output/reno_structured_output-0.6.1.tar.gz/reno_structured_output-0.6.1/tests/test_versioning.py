from importlib import metadata


def test_version():
    assert metadata.version("reno-structured-output")
