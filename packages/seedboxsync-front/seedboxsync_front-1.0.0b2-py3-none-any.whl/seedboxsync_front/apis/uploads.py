# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
from flask_restx import fields, Namespace, reqparse
from typing import Any
from seedboxsync.core.dao import Torrent
from seedboxsync_front.apis import Resource

api = Namespace('uploads', description='Operations related to uploaded torrents management')


# ==========================
# Models
# ==========================
upload_model = api.model('Upload', {
    'id': fields.Integer(required=True, description="Unique identifier of the uploaded torrent", example=99),
    'name': fields.String(required=True, description="Torrent file name", example="Justo.torrent"),
    'announce': fields.String(required=False, description="Announce URL or tracker information from the torrent file",
                              example="https://serversecret.com/anounce"),
    'sent': fields.DateTime(dt_format='iso8601', required=True, description="Timestamp when the torrent was uploaded"),
})
upload_list_envelope = Resource.build_envelope_model(api, 'UploadList', upload_model)
upload_envelope = Resource.build_envelope_model(api, 'Upload', upload_model, False)


# ==========================
# Request parser
# ==========================
parser = reqparse.RequestParser()
parser.add_argument(
    'limit',
    type=int,
    required=False,
    default=50,
    help='Maximum number of items to return (min=5, max=1000)',
    location='args'
)


# ==========================
# Endpoints
# ==========================
@api.route('')
class UploadsList(Resource):
    """
    Endpoint to manage uploaded torrents.

    Provides a list of uploaded torrents with optional limit on the number of items returned.
    """

    @api.doc('list_uploads')  # type: ignore[misc]
    @api.expect(parser)  # type: ignore[misc]
    @api.marshal_with(upload_list_envelope, code=200, description="List of uploaded torrents")  # type: ignore[misc]
    def get(self) -> dict[str, Any]:
        """
        Retrieve the most recent uploaded torrents.

        Query Parameters:
        - limit: Maximum number of torrents to return (default=50)
        """
        args = parser.parse_args()
        limit = self.set_limit(args.get('limit'))

        # Fetch torrents ordered by upload timestamp (most recent first)
        query = Torrent.select(
            Torrent.id,
            Torrent.name,
            Torrent.sent
        ).limit(limit).order_by(Torrent.sent.desc())

        return self.build_envelope(list(query.dicts()), 'Upload', 200)


@api.route('/<int:id>')
@api.response(404, 'Upload not found')
@api.param('id', 'The upload identifier')
class Uploads(Resource):
    """
    Endpoint for managing upload.

    Provides upload operations.
    """

    @api.doc('get_upload')  # type: ignore[misc]
    @api.marshal_with(upload_envelope, code=200, description="Upload element")  # type: ignore[misc]
    def get(self, id: int) -> dict[str, Any]:
        """
        Retrieve a upload.
        """
        try:
            result = Torrent.select(
                Torrent.id,
                Torrent.name,
                Torrent.sent
            ).where(Torrent.id == id).dicts().get()
        except Torrent.DoesNotExist:
            api.abort(404, "Upload {} doesn't exist".format(id))

        return self.build_envelope(result, 'Upload', 200)
