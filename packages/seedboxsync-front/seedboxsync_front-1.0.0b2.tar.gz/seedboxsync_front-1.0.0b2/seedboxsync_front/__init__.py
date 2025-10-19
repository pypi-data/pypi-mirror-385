# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import os
from flask import Flask, Response, request, send_from_directory
from flask_babel import format_datetime
from datetime import datetime
from typing import Callable
from seedboxsync_front.views import bp as bp_frontend, error as error_front
from seedboxsync_front.apis import bp as bp_api, error as error_api
from seedboxsync_front.babel import babel, get_locale
from seedboxsync_front.db import Database
from seedboxsync_front.cache import cache
from seedboxsync_front.config import Config
from seedboxsync_front.__version__ import __version__ as version, __api_version__ as api_version, __api_path_version__ as api_path_version

__version__ = version


def __handle_http_exception(e: Exception) -> tuple[Response, int | None] | tuple[str, int | None]:
    """
    Global 404 handler.

    Returns:
        tuple[Response, int | None] | tuple[str, int | None]: JSON for /api routes, else return frontend template.
    """
    if request.path.startswith(f'/api/{api_path_version}') or request.blueprint == 'api':
        return error_api.error(e)
    return error_front.error(e)


def create_app(test_config: dict[str, str] | None = None) -> Flask:
    """
    Flask create app.
    """
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Load config
    Config(app, test_config)

    # Babel loading
    babel.init_app(app, locale_selector=get_locale)

    # Inject Jinja function / variables
    @app.context_processor
    def inject_formatters() -> dict[str, Callable[[datetime], str]]:
        return dict(format_datetime=format_datetime)

    @app.context_processor
    def inject_globals() -> dict[str, str]:
        return {
            'version': version,
            'api_version': api_version
        }

    # Cache loading
    cache.init_app(app)

    # DB loading
    Database(app)

    # Register blueprint and error handler
    app.register_blueprint(bp_frontend)
    app.register_blueprint(bp_api)
    app.register_error_handler(Exception, __handle_http_exception)  # type: ignore[arg-type]

    # Favicon fix
    @app.route('/favicon.ico')
    def favicon() -> Response:
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.png', mimetype='image/png')

    return app
