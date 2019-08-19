import os

from flask import Flask, jsonify, make_response, render_template, request, \
    send_from_directory
from flask_restful import abort, Api, Resource

from deepstar.filesystem.frame_file import FrameFile
from deepstar.filesystem.frame_set_sub_dir import FrameSetSubDir
from deepstar.models.frame_model import FrameModel


class FrameSetSelectCurateFlaskApp:
    """
    This class implements the FrameSetSelectCurateFlaskApp.
    """

    def __init__(self, frame_set_id):
        """
        This method initializes an instance of the FrameSetSelectCurateFlaskApp
        class.

        :param int frame_set_id: The frame set ID.
        :rtype: None
        """

        path = os.path.dirname(os.path.realpath(__file__))

        self._app = Flask(self.__class__.__name__,
                          template_folder=path + '/templates',
                          static_folder=path + '/static')

        self._api = Api(self._app)

        class IndexResource(Resource):
            def get(self):
                return make_response(
                    render_template('index.html', frame_set_id=frame_set_id))

        self._api.add_resource(IndexResource, '/')

        class FrameCollectionResource(Resource):
            def get(self, frame_set_id):
                if 'offset' in request.args:
                    offset = int(request.args['offset'])
                else:
                    offset = 0

                if 'length' in request.args:
                    length = int(request.args['length'])
                else:
                    length = 100

                result = FrameModel().list(frame_set_id, length=length,
                                           offset=offset)
                if result is None:
                    abort(404)

                return jsonify(result)

        route = '/frame_sets/<int:frame_set_id>/frames/'
        self._api.add_resource(FrameCollectionResource, route)

        class FrameResource(Resource):
            def get(self, frame_set_id, frame_id):
                return send_from_directory(FrameSetSubDir.path(frame_set_id),
                                           FrameFile.name(frame_id, 'jpg',
                                                          '192x192'))

            def put(self, frame_set_id, frame_id):
                frame_model = FrameModel()

                result = frame_model.update(frame_id,
                                            request.get_json()['rejected'])
                if result is False:
                    abort(404)

                result = frame_model.select(frame_id)
                if result is None:
                    abort(404)

                return jsonify(result)

        route = '/frame_sets/<int:frame_set_id>/frames/<int:frame_id>'
        self._api.add_resource(FrameResource, route)

    @property
    def api(self):
        """
        This method returns the flask_restful api instance.

        :rtype: flask_restful.Api
        """

        return self._api

    def run(self):
        """
        This method runs the flask app.

        :rtype: None
        """

        self._app.run(host='0.0.0.0', debug=False)
