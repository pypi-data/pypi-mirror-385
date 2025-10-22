from onellmclient import Client, __version__


def test_imports_and_version():
    assert isinstance(__version__, str)
    c = Client()
    assert c is not None
