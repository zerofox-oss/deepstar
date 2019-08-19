import os
import shutil

from deepstar.filesystem.transform_file import TransformFile
from deepstar.filesystem.transform_set_sub_dir import TransformSetSubDir
from deepstar.models.transform_model import TransformModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.plugins.plugin import Plugin
from deepstar.util.command_line_route_handler import CommandLineRouteHandler
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError
from deepstar.util.debug import debug
from deepstar.util.parse import parse_range
from deepstar.util.video import create_one_video_file_from_many_image_files


class TransformSetCommandLineRouteHandler(CommandLineRouteHandler):
    """
    This class implements the FrameCommandLineRouteHandler class.
    """

    def list(self):
        """
        This method lists transform sets in the transform set collection.

        :rtype: None
        """

        result = TransformSetModel().list()

        debug(f'{len(result)} results', 3)
        debug('id | name | fk_frame_sets | fk_prev_transform_sets', 3)
        debug('--------------------------------------------------', 3)

        for r in result:
            debug(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}', 3)

    def select_extract(self, transform_set_ids, name, opts):
        """
        This method runs a transformation plugin over previously created
        transform sets.

        :param list(int) transform_set_id: The transform set IDs.
        :param str name: The name of the transform set extraction plugin to
            use.
        :param dict opts: The dict of options.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        transform_set_model = TransformSetModel()

        for transform_set_id in transform_set_ids:
            result = transform_set_model.select(transform_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Transform set with ID {transform_set_id:08d} not found')

        plugin = Plugin.get('transform_set_select_extract', name)
        if plugin is None:
            raise CommandLineRouteHandlerError(
                    f"'{name}' is not a valid transform set extraction "
                    f'plugin name')

        for transform_set_id in transform_set_ids:
            try:
                new_transform_set_id = plugin() \
                    .transform_set_select_extract(transform_set_id, opts)
            except ValueError as e:
                raise CommandLineRouteHandlerError(str(e))

            result = transform_set_model.select(new_transform_set_id)

            debug(f'transform_set_id={result[0]}, name={result[1]}, '
                  f'fk_frame_sets={result[2]}, '
                  f'fk_prev_transform_sets={result[3]}',
                  3)

    def select_curate_auto(self, transform_set_ids, name, opts):
        """
        This method automatically curates a transform set.

        :param list(int) transform_set_ids: The transform set IDs.
        :param dict opts: The dict of options.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        for transform_set_id in transform_set_ids:
            result = TransformSetModel().select(transform_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Transform set with ID {transform_set_id:08d} not found')

        plugin = Plugin.get('transform_set_select_curate', name)
        if plugin is None:
            raise CommandLineRouteHandlerError(
                    f"'{name}' is not a valid transform set curation "
                    f'plugin name')

        for transform_set_id in transform_set_ids:
            plugin = Plugin.get('transform_set_select_curate', name)

            try:
                plugin().transform_set_select_curate(transform_set_id, opts)
            except ValueError as e:
                raise CommandLineRouteHandlerError(str(e))

        debug('success', 3)

    def select_curate_manual(self, transform_set_id, opts):
        """
        This method serves a manual transform set curation UI.

        :param int transform_set_id: The transform set ID.
        :param dict opts: The dict of options.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        result = TransformSetModel().select(transform_set_id)
        if result is None:
            raise CommandLineRouteHandlerError(
                f'Transform set with ID {transform_set_id:08d} not found')

        plugin = Plugin.get('transform_set_select_curate', 'manual')

        plugin().transform_set_select_curate(transform_set_id, opts)

    def select_export_dir(self, transform_set_ids, target_dir, opts={}):
        """
        This method exports transform sets to a directory.

        :param list transform_set_ids: The list of transform set IDs.
        :param str target_dir: The directory to which to export the transform
            sets.
        :param dict opts: The dict of options.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        transform_set_model = TransformSetModel()

        for transform_set_id in transform_set_ids:
            result = transform_set_model.select(transform_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Transform set with ID {transform_set_id:08d} not found')

        if not os.path.isdir(target_dir):
            raise CommandLineRouteHandlerError(
                f'{target_dir} is not a directory')

        transform_model = TransformModel()
        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        count = 0

        for tid in transform_set_ids:
            offset = 0
            transform_set_path = TransformSetSubDir.path(tid)

            while True:
                results = transform_model.list(tid, length=length,
                                               offset=offset, rejected=False)

                if not results:
                    break

                for transform_id, _, _, _, _ in results:
                    file_path = TransformFile().path(transform_set_path,
                                                     transform_id, 'jpg')
                    if 'format' in opts:
                        filename = opts['format'] % transform_id
                    else:
                        filename = os.path.basename(file_path)

                    target_path = os.path.join(target_dir, filename)
                    shutil.copy(file_path, target_path)
                    count += 1

                    debug(f'Transform with ID {transform_id:08d} at '
                          f'{file_path} exported to {target_path}', 4)

                offset += length

        debug(f'{count} transforms were successfully exported to {target_dir}',
              3)

    def select_export_video(self, transform_set_ids, target_dir):
        """
        This method exports transform sets to videos.

        :param list transform_set_ids: The list of transform set IDs.
        :param str target_dir: The directory to which to export the videos.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        for transform_set_id in transform_set_ids:
            result = TransformSetModel().select(transform_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Transform set with ID {transform_set_id:08d} not found')

        if not os.path.isdir(target_dir):
            raise CommandLineRouteHandlerError(
                f'{target_dir} is not a directory')

        transform_model = TransformModel()
        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        count = 0

        for transform_set_id in transform_set_ids:
            video_path = os.path.join(target_dir,
                                      f'{transform_set_id:08X}.mp4')

            def image_paths():
                offset = 0
                p1 = TransformSetSubDir.path(transform_set_id)

                while True:
                    transforms = transform_model.list(transform_set_id,
                                                      length=length,
                                                      offset=offset,
                                                      rejected=False)

                    if not transforms:
                        break

                    for transform in transforms:
                        image_path = TransformFile.path(p1, transform[0],
                                                        'jpg')

                        yield image_path

                        debug(f'Transform with ID {transform[0]:08d} at '
                              f'{image_path} exported to {video_path}', 4)

                    offset += length

            ret = create_one_video_file_from_many_image_files(
                image_paths, video_path)
            if ret is False:
                raise CommandLineRouteHandlerError(
                    'An error occured while attempting to create one '
                    'video file from many image files')

            count += 1

            debug(f'Transform set with ID {transform_set_id:08d} exported to '
                  f'{video_path}', 4)

        debug(f'{count} videos were successfully exported to {target_dir}', 3)

    def select_clone(self, transform_set_ids):
        """
        This method clones transform sets to new transform sets.

        :param list(int) transform_set_ids: The transform set IDs.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        transform_set_model = TransformSetModel()

        for transform_set_id in transform_set_ids:
            result = transform_set_model.select(transform_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Transform set with ID {transform_set_id:08d} not found')

        for transform_set_id in transform_set_ids:
            result = transform_set_model.select(transform_set_id)

            self.select_merge([transform_set_id], name=result[1],
                              fk_frame_sets=result[2],
                              fk_prev_transform_sets=transform_set_id,
                              rejected=True)

    def select_merge(self, transform_set_ids, name='merge', fk_frame_sets=None,
                     fk_prev_transform_sets=None, rejected=False):
        """
        This method merges multiple transform sets into one transform set.

        :param list(int) transform_set_ids: The transform set IDs.
        :param str name: The merged transform set's name. The default value is
            'merge'.
        :param int fk_frame_sets: The frame set ID to which this transform set
            corresponds (if any). The default value is None.
        :param int fk_prev_transform_sets: The transform set ID the previous
            transform set in this series of transformations. The default value
            is None.
        :param bool rejected: True if should include rejected else False if
            should not. The default value is False.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        transform_set_model = TransformSetModel()

        for transform_set_id in transform_set_ids:
            result = transform_set_model.select(transform_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Transform set with ID {transform_set_id:08d} not found')

        transform_set_id = transform_set_model.insert(name, fk_frame_sets,
                                                      fk_prev_transform_sets)

        p1 = TransformSetSubDir.path(transform_set_id)

        os.makedirs(p1)

        transform_model = TransformModel()
        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))

        for transform_set_id_ in transform_set_ids:
            offset = 0
            p2 = TransformSetSubDir.path(transform_set_id_)

            while True:
                transforms = transform_model.list(transform_set_id_,
                                                  length=length,
                                                  offset=offset,
                                                  rejected=rejected)

                if not transforms:
                    break

                for transform in transforms:
                    transform_id = transform_model.insert(transform_set_id,
                                                          transform[2],
                                                          transform[3],
                                                          transform[4])

                    p3 = TransformFile.path(p2, transform[0], 'jpg')
                    p4 = TransformFile.path(p1, transform_id, 'jpg')

                    shutil.copy(p3, p4)

                    debug(f'Transform with ID {transform[0]:08d} at {p3} '
                          f'merged as ID {transform_id:08d} at {p4}', 4)

                offset += length

        result = transform_set_model.select(transform_set_id)

        debug(f'transform_set_id={result[0]}, name={result[1]}, '
              f'fk_frame_sets={result[2]}, fk_prev_transform_sets={result[3]}',
              3)

    def select_merge_non_default(self, transform_set_ids, name, opts):
        """
        This method merges multiple transform sets into one transform set.

        :param list(int) transform_set_ids: The transform set IDs.
        :param str name: The name of the transform set merge plugin
            to  use.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        transform_set_model = TransformSetModel()

        for transform_set_id in transform_set_ids:
            result = transform_set_model.select(transform_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Transform set with ID {transform_set_id:08d} not found')

        plugin = Plugin.get('transform_set_select_merge', name)
        if plugin is None:
            raise CommandLineRouteHandlerError(
                    f"'{name}' is not a valid transform set merge plugin name")

        try:
            new_transform_set_id = plugin().transform_set_select_merge(
                                       transform_set_ids, opts)
        except ValueError as e:
            raise CommandLineRouteHandlerError(str(e))

        result = transform_set_model.select(new_transform_set_id)

        debug(f'transform_set_id={result[0]}, name={result[1]}, '
              f'fk_frame_sets={result[2]}, '
              f'fk_prev_transform_sets={result[3]}',
              3)

    def delete(self, transform_set_ids):
        """
        This method deletes a transform set from the transform set collection.

        :param list(int) transform_set_ids: The transform set IDs.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        transform_set_model = TransformSetModel()

        for transform_set_id in transform_set_ids:
            result = transform_set_model.select(transform_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Transform set with ID {transform_set_id:08d} not found')

        for transform_set_id in transform_set_ids:
            transform_set_model.delete(transform_set_id)

            shutil.rmtree(TransformSetSubDir.path(transform_set_id))

            debug(f'Transform set {transform_set_id} was successfully deleted',
                  3)

    def usage(self):
        """
        This method prints usage.

        :rtype: None
        """

        path = os.path.join(
                   os.path.dirname(os.path.realpath(__file__)),
                   'transform_set_command_line_route_handler_usage.txt')

        with open(path, 'r') as file_:
            usage = file_.read()

        usage = usage.strip()

        debug(usage, 3)

    def handle(self, args, opts):
        """
        This method handles command line arguments for the transform set
        collection.

        :param list(str) args: The list of command line arguments.
        :param dict opts: The dict of options.
        :rtype: None
        """

        if args[1] == 'list':
            self.list()
        elif args[1] == 'select' and args[4] == 'extract':
            self.select_extract(parse_range(args[3]), args[5], opts)
        elif args[1] == 'select' and args[4] == 'curate':
            if args[5] == 'manual':
                self.select_curate_manual(int(args[3]), opts)
            else:
                self.select_curate_auto(parse_range(args[3]), args[5], opts)
        elif args[1] == 'select' and args[4] == 'export' \
                and args[5] == 'dir':
            self.select_export_dir(parse_range(args[3]), args[6], opts)
        elif args[1] == 'select' and args[4] == 'export' \
                and args[5] == 'video':
            self.select_export_video(parse_range(args[3]), args[6])
        elif args[1] == 'select' and args[4] == 'clone':
            self.select_clone(parse_range(args[3]))
        elif args[1] == 'select' and args[4] == 'merge':
            if len(args) == 6:
                self.select_merge_non_default(parse_range(args[3]), args[5],
                                              opts)
            else:
                self.select_merge(parse_range(args[3]))
        elif args[1] == 'delete':
            self.delete(parse_range(args[3]))
        elif args[1] == 'usage':
            self.usage()
