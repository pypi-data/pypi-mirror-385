import pyatmoweb

def test_version():
    assert pyatmoweb.__version__ == "0.0.1"
    assert isinstance(pyatmoweb.__version__, str)
    assert len(pyatmoweb.__version__) > 0


def test_import_function():
    assert hasattr(pyatmoweb, "get_temp_1")  
