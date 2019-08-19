import contextlib
import shutil
import tempfile


@contextlib.contextmanager
def tempdir():
    """
    This function creates, yields and removes a temporary directory.

    :yields: str
    """

    tempdir_ = tempfile.mkdtemp()

    try:
        yield tempdir_
    finally:
        shutil.rmtree(tempdir_)
