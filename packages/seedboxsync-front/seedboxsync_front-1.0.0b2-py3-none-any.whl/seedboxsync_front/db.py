# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import os
from cement.utils import fs
from flask import Flask
from playhouse.flask_utils import FlaskDB
from seedboxsync.core.dao import Download, Lock, SeedboxSync, Torrent
from seedboxsync.core.db import sizeof
from seedboxsync_front.utils import byte_to_gi


class Database(object):
    """
    Database connector using peewee.

    Attributes:
        app (Flask): The database object.
    """

    def __init__(self, app: Flask):
        """
        Initialize a new Database instance.

        Args:
            app (Flask): The database object.
            database (SqliteDatabase | None): The database object.
        """
        self.__app = app
        self.__load_database()
        self.__register_functions()

    def __load_database(self) -> None:
        """
        Load SeedboxSync DB from SeedboxSyncFront.
        """

        # Get DB from config
        db_file = fs.abspath(self.__app.config['DATABASE'])
        db_url = 'sqlite:///' + db_file

        if not os.path.exists(db_file):
            self.__app.logger.error('No database %s found', db_url)
            self.__app.config['INIT_ERROR'] = "Can't load seedbox database!"
        else:
            db_wrapper = FlaskDB(self.__app, db_url)
            self.db = db_wrapper.database
            self.db.bind([Download, Lock, SeedboxSync, Torrent])
            self.__app.logger.debug('Use database %s', db_url)

    def __register_functions(self) -> None:
        """
        Register DB functions.
        """
        @self.db.func('byte_to_gi')  # type: ignore
        def db_byte_to_gi(num: float, suffix: str = 'B') -> str:
            return byte_to_gi(num, suffix)

        @self.db.func('sizeof')  # type: ignore
        def db_sizeof(num: float, suffix: str = 'B') -> str:
            return sizeof(num, suffix)  # type: ignore[no-any-return]
