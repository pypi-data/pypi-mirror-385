# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from flask import render_template
from seedboxsync.core.dao import Download, Lock, SeedboxSync
from seedboxsync.core.db import sizeof
from seedboxsync_front.cache import cache
from seedboxsync_front.views import bp
from seedboxsync_front.utils import init_flash
from seedboxsync_front.__version__ import __version__ as version


@bp.route('/info')
@cache.cached(timeout=60)
def info() -> str:
    """
    Information page view.
    """
    init_flash()

    query = Download.select().where(Download.finished != 0)
    total_files = query.count()
    total_size = sum([d.seedbox_size for d in query if d.seedbox_size])

    try:
        sync_blackhole = Lock.get(Lock.key == 'sync_blackhole')
    except Lock.DoesNotExist:
        sync_blackhole = False
    try:
        sync_seedbox = Lock.get(Lock.key == 'sync_seedbox')
    except Lock.DoesNotExist:
        sync_seedbox = False

    info = {
        'stats_total_files': total_files,
        'stats_total_size': sizeof(total_size),
        'version': version,
        'seedboxsync_version': SeedboxSync.get_version(),
        'seedboxsync_db_version': SeedboxSync.get_db_version(),
        'sync_blackhole': sync_blackhole,
        'sync_seedbox': sync_seedbox
    }

    return render_template('info.html', info=info)
