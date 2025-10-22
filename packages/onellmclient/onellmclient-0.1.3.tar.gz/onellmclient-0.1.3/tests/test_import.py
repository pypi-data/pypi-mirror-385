from onellmclient import Client


def test_imports():
    c = Client()
    assert c is not None
