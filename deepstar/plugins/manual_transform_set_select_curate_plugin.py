from deepstar.plugins.flask_apps \
    .transform_set_select_curate_flask_app \
    .transform_set_select_curate_flask_app \
    import TransformSetSelectCurateFlaskApp


class ManualTransformSetSelectCuratePlugin:
    """
    This class implements the ManualTransformSetSelectCuratePlugin class.
    """

    name = 'manual'

    def transform_set_select_curate(self, transform_set_id, opts):
        """
        This method serves a manual transform set curation UI.

        :param int transform_set_id: The transform set ID.
        :param dict opts: The dict of options.
        :rtype: None
        """

        TransformSetSelectCurateFlaskApp(transform_set_id).run()
