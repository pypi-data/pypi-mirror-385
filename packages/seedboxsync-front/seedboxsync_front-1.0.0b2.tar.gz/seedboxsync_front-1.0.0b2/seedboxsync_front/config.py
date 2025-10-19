# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import os
import yaml
from flask import Flask
from cement.utils import fs


class Config(object):
    """
    Config.

    Attributes:
        app (Flask): The database object.
    """

    CONFIG_PATHS = [
        os.path.expanduser("~/.config/seedboxsync/seedboxsync.yml"),
        os.path.expanduser("~/.seedboxsync.yml"),
        os.path.expanduser("~/.seedboxsync/config/seedboxsync.yml"),
        "/etc/seedboxsync/seedboxsync.yml",
    ]

    def __init__(self, app: Flask, test_config: dict[str, str] | None = None):
        """
        Initialize a new Config instance.

        Args:
            app (Flask): The database object.
        """

        self.app = app
        self.app.config.from_prefixed_env()  # Set from env prefixed by 'FLASK_'

        # Load config
        if test_config is not None:
            self.app.config.from_mapping(test_config)  # load the test config if passed in
        else:
            # Load config from SeedboxSync yaml
            yaml_config = self.__load_yaml_config()
            if not yaml_config:
                raise Exception('No SeedboxSync configuration file found!')
            self.app.config.update(yaml_config)

        self.__check_config()  # Do all checks
        self.app.config.setdefault('CACHE_TYPE', 'SimpleCache')  # Init Flask Cache
        self.app.config.setdefault('DATABASE', fs.abspath(str((self.app.config.get('local') or {}).get('db_file', 'default.db'))))  # Get DB file
        self.app.config.setdefault('SWAGGER_UI_DOC_EXPANSION', 'list')  # Expense swager namespaces
        self.app.config['PROPAGATE_EXCEPTIONS'] = False

    def __check_config(self) -> None:
        """
        Check all configurations needed.
        """
        # SECRET_KEY warning
        if self.app.config.get('SECRET_KEY') is None:
            self.app.logger.warning('Warning: SECRET_KEY is still not set. Set it in production to secure your sessions.')

    def __load_yaml_config(self) -> dict:  # type: ignore[type-arg]
        """
        Load config from the seedboxsync cli yaml.
        """
        for path in Config.CONFIG_PATHS:
            if os.path.exists(path):
                with open(path, "r") as f:
                    return yaml.safe_load(f)  # type: ignore[no-any-return]
        return {}
