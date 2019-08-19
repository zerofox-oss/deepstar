import os

from flask import Flask, jsonify, make_response, render_template, request, \
    send_from_directory
from flask_restful import abort, Api, Resource

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel


class TransformSetSelectCurateFlaskApp:
    """
    This class implements the TransformSetSelectCurateFlaskApp.
    """

    def __init__(self, transform_set_id):
        """
        This method initializes an instance of the
        TransformSetSelectCurateFlaskApp class.

        :param int transform_set_id: The transform set ID.
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
                    render_template('index.html',
                                    transform_set_id=transform_set_id))

        self._api.add_resource(IndexResource, '/')

        class TransformCollectionResource(Resource):
            def get(self, transform_set_id):
                if 'offset' in request.args:
                    offset = int(request.args['offset'])
                else:
                    offset = 0

                if 'length' in request.args:
                    length = int(request.args['length'])
                else:
                    length = 100

                result = TransformModel().list(transform_set_id, length=length,
                                               offset=offset)
                if result is None:
                    abort(404)

                return jsonify(result)

        route = '/transform_sets/<int:transform_set_id>/transforms/'
        self._api.add_resource(TransformCollectionResource, route)

        class TransformResource(Resource):
            def get(self, transform_set_id, transform_id):
                return send_from_directory(
                    TransformSetSubDir.path(transform_set_id),
                    TransformFile.name(transform_id, 'jpg'))

            def put(self, transform_set_id, transform_id):
                transform_model = TransformModel()

                result = transform_model.update(
                    transform_id, rejected=request.get_json()['rejected'])
                if result is False:
                    abort(404)

                result = transform_model.select(transform_id)
                if result is None:
                    abort(404)

                return jsonify(result)

        route = '/transform_sets/<int:transform_set_id>/transforms/<int:transform_id>'  # noqa
        self._api.add_resource(TransformResource, route)

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
