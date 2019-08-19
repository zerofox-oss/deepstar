import contextlib
import mock
import os

from deepstar.deepstar import Deepstar
from deepstar.models.model import Model
from deepstar.util.tempdir import tempdir


@contextlib.contextmanager
def deepstar_path():
    with tempdir() as tempdir_:
        with mock.patch.dict(os.environ, {'DEEPSTAR_PATH': tempdir_}):
            Deepstar.init()

            try:
                yield
            finally:
                Model.close()
