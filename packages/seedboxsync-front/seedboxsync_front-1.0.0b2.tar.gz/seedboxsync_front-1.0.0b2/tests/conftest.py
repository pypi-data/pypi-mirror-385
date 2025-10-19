import os
import pytest
import shutil
import tempfile
from seedboxsync_front import create_app


@pytest.fixture
def app():
    """
    Create app fixture
    """
    db_fd, tmp_db = tempfile.mkstemp()

    # Copy database
    test_db = os.path.abspath("tests/resources/seedboxsync.db")
    shutil.copy(test_db, tmp_db)

    app = create_app({
        'TESTING': True,
        'DATABASE': tmp_db,
        'SECRET_KEY': 'pytest',
        'CACHE_TYPE': 'NullCache',
        'BABEL_DEFAULT_LOCALE': 'en'
    })
    yield app

    os.close(db_fd)
    os.unlink(tmp_db)


@pytest.fixture
def client(app):
    """
    Create client fixture
    """
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
