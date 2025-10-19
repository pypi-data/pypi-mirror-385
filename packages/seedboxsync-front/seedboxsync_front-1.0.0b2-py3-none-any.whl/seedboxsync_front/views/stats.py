# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from flask import render_template
from seedboxsync.core.dao import Download
from seedboxsync.core.db import sizeof
from seedboxsync_front.views import bp
from seedboxsync_front.cache import cache
from seedboxsync_front.utils import init_flash


@bp.route('/stats')
@cache.cached(timeout=300)
def stats() -> str:
    """
    Stats page view.
    """
    init_flash()

    query = Download.select().where(Download.finished != 0)
    total_files = query.count()
    total_size = sum([d.seedbox_size for d in query if d.seedbox_size])

    stats_total = {
        'files': total_files,
        'total_size': sizeof(total_size),
    }

    return render_template('stats.html', stats_total=stats_total)
