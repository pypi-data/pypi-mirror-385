# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from flask_restx import fields, Namespace
from typing import Any
from seedboxsync.core.dao import Lock
from seedboxsync_front.apis import DateTimeOrZero, Resource

api = Namespace('locks', description='Operations related to lock')


# ==========================
# Models
# ==========================
lock_model = api.model('Locks', {
    'key': fields.String(required=True, description="Unique lock identifier", example="sync_blackhole"),
    'pid': fields.Integer(required=True, description="Process ID holding the lock", example=999),
    'locked': fields.Boolean(dt_format='iso8601', required=True, description="Whether the lock is currently active", example=False),
    'locked_at': DateTimeOrZero(dt_format='iso8601', required=False, description="Timestamp when the lock was acquired"),
    'unlocked_at': DateTimeOrZero(dt_format='iso8601', required=True, description="Timestamp when the lock was released"),
})
lock_list_envelope = Resource.build_envelope_model(api, 'LockList', lock_model)
lock_envelope = Resource.build_envelope_model(api, 'Lock', lock_model, False)


# ==========================
# Endpoints
# ==========================
@api.route('')
class LocksList(Resource):
    """
    Endpoint for managing lock list.

    Provides a list of lock.
    """

    @api.doc('list_lock')  # type: ignore[misc]
    @api.marshal_with(lock_list_envelope, code=200, description="List of locks")  # type: ignore[misc]
    def get(self) -> dict[str, Any]:
        """
        Retrieve a list of lock.
        """
        query = Lock.select(
            Lock.key,
            Lock.pid,
            Lock.locked,
            Lock.locked_at,
            Lock.unlocked_at,
        )

        return self.build_envelope(list(query.dicts()), 'Lock', 200)


@api.route('/<string:key>')
@api.response(404, 'Lock not found')
@api.param('key', 'The lock key')
class Locks(Resource):
    """
    Endpoint for managing locks.

    Provides locks operations.
    """

    @api.doc('get_lock')  # type: ignore[misc]
    @api.marshal_with(lock_envelope, code=200, description="Lock element")  # type: ignore[misc]
    def get(self, key: str) -> dict[str, Any]:
        """
        Retrieve a lock.
        """
        try:
            result = Lock.select(
                Lock.key,
                Lock.pid,
                Lock.locked,
                Lock.locked_at,
                Lock.unlocked_at,
            ).where(Lock.key == key).dicts().get()
        except Lock.DoesNotExist:
            api.abort(404, "Lock {} doesn't exist".format(key))

        return self.build_envelope(result, 'Lock', 200)
