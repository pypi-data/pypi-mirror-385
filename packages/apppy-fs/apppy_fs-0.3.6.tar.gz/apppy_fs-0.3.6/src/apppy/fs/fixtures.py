import pytest

from apppy.env import DictEnv, Env
from apppy.env.env_fixtures import current_test_name
from apppy.fs import FileSystem, FileSystemSettings
from apppy.fs.local import LocalFileSystem, LocalFileSystemSettings


@pytest.fixture(scope="session")
def local_fs():
    fs_env: Env = DictEnv(name=current_test_name(), d={})
    fs_settings = FileSystemSettings(fs_env)
    fs = FileSystem(fs_settings)

    fs_local_env: Env = DictEnv(name=current_test_name(), d={})
    fs_local_settings = LocalFileSystemSettings(fs_local_env)
    _ = LocalFileSystem(fs_local_settings, fs)

    yield fs
