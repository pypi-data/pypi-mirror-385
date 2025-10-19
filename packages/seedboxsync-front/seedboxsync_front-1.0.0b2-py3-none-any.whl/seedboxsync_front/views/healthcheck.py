# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from flask import jsonify, Response
from seedboxsync_front.views import bp


@bp.route("/healthcheck")
def healthcheck() -> tuple[Response, int]:
    """
    healthcheck view
    """
    return jsonify({"status": "ok"}), 200
