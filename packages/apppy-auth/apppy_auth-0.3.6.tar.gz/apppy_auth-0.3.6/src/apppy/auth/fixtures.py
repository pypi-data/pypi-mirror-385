from pathlib import Path

import pytest
from fastapi_lifespan_manager import LifespanManager

from apppy.auth.jwks import JwksAuthStorage, JwksAuthStorageSettings
from apppy.env import DictEnv, Env
from apppy.env.env_fixtures import current_test_file, current_test_name
from apppy.fs import FileSystem

# from apppy.fs.fixtures import local_fs  # noqa: F401


@pytest.fixture
def jwks_auth_storage(local_fs: FileSystem):
    env: Env = DictEnv(
        name=current_test_name(),
        d={
            "enabled": True,
            # Create a unique jwks directory for each test to avoid collisions
            "root_dir": f"{current_test_file()}/{current_test_name()}",
        },
    )
    jwks_auth_settings = JwksAuthStorageSettings(env)
    jwks_auth_storage: JwksAuthStorage = JwksAuthStorage(
        settings=jwks_auth_settings,
        fs=local_fs,
        lifespan=LifespanManager(),
    )
    yield jwks_auth_storage


##### ##### ##### Pem Files ##### ##### #####
parent_dir = Path(__file__).parent


@pytest.fixture(scope="session")
def pem_file_bytes_private():
    pem_file_private = Path(f"{parent_dir}/test_examples", "test.key.pem")
    pem_file_bytes = pem_file_private.read_bytes()

    yield pem_file_bytes


@pytest.fixture(scope="session")
def pem_file_bytes_public():
    pem_file_public = Path(f"{parent_dir}/test_examples", "test.pub.pem")
    pem_file_bytes = pem_file_public.read_bytes()

    yield pem_file_bytes


@pytest.fixture(scope="session")
def pem_file_bytes_unauthorized():
    pem_file_unregistered = Path(f"{parent_dir}/test_examples", "unauthorized.key.pem")
    pem_file_bytes = pem_file_unregistered.read_bytes()

    yield pem_file_bytes
