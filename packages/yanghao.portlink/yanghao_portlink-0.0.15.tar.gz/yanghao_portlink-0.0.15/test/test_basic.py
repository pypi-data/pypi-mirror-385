import importlib

def test_import():
    """验证包可以正确导入"""
    pkg = importlib.import_module("yanghao.portlink.client")
    assert pkg is not None


def test_version():
    """验证包版本信息可以正确获取"""
    import importlib.metadata
    version = importlib.metadata.version("yanghao.portlink")
    assert version.startswith("0.")