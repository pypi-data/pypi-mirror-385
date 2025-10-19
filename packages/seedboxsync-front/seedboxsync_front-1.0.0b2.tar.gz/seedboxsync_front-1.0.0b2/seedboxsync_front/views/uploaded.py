# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from flask import render_template
from seedboxsync_front.views import bp
from seedboxsync_front.cache import cache
from seedboxsync_front.utils import init_flash


@bp.route('/uploaded')
@cache.cached(timeout=300)
def uploaded() -> str:
    """
    Uploaded list view.
    """
    init_flash()

    return render_template('uploaded.html')
