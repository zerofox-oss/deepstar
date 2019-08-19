from deepstar.plugins.flask_apps \
    .frame_set_select_curate_flask_app.frame_set_select_curate_flask_app \
    import FrameSetSelectCurateFlaskApp


class ManualFrameSetSelectCuratePlugin:
    """
    This class implements the ManualFrameSetSelectCuratePlugin class.
    """

    name = 'manual'

    def frame_set_select_curate(self, frame_set_id, opts):
        """
        This method serves a manual frame set curation UI.

        :param int frame_set_id: The frame set ID.
        :param dict opts: The dict of options.
        :rtype: None
        """

        FrameSetSelectCurateFlaskApp(frame_set_id).run()
