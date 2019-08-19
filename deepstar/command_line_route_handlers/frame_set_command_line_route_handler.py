import glob
import os
import shutil

import cv2
import imutils

from deepstar.filesystem.frame_file import FrameFile
from deepstar.filesystem.frame_set_sub_dir import FrameSetSubDir
from deepstar.models.frame_model import FrameModel
from deepstar.models.frame_set_model import FrameSetModel
from deepstar.models.transform_set_model import TransformSetModel
from deepstar.plugins.plugin import Plugin
from deepstar.util.command_line_route_handler import CommandLineRouteHandler
from deepstar.util.command_line_route_handler_error import \
    CommandLineRouteHandlerError
from deepstar.util.debug import debug
from deepstar.util.parse import parse_range


class FrameSetCommandLineRouteHandler(CommandLineRouteHandler):
    """
    This class implements the FrameSetCommandLineRouteHandler class.
    """

    def list(self):
        """
        This method lists frame sets in the frame set collection.

        :rtype: None
        """

        result = FrameSetModel().list()

        debug(f'{len(result)} results', 3)
        debug('id | fk_videos', 3)
        debug('-------------', 3)

        for r in result:
            debug(f'{r[0]} | {r[1]}', 3)

    def select_curate_manual(self, frame_set_id, opts):
        """
        This method serves a manual frame set curation UI.

        :param int frame_set_id: The frame set ID.
        :param dict opts: The dict of options.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        result = FrameSetModel().select(frame_set_id)
        if result is None:
            raise CommandLineRouteHandlerError(
                f'Frame set with ID {frame_set_id:08d} not found')

        plugin = Plugin.get('frame_set_select_curate', 'manual')

        plugin().frame_set_select_curate(frame_set_id, opts)

    def select_extract(self, frame_set_ids, name, opts):
        """
        This method extracts portions of frames to transform sets.

        :param list(int) frame_set_ids: The frame set IDs.
        :param str name: The name of the frame set extraction plugin to use.
        :param dict opts: The dict of options.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        frame_set_model = FrameSetModel()

        for frame_set_id in frame_set_ids:
            result = frame_set_model.select(frame_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Frame set with ID {frame_set_id:08d} not found')

        plugin = Plugin.get('frame_set_select_extract', name)
        if plugin is None:
            raise CommandLineRouteHandlerError(
                f"'{name}' is not a valid frame set extraction plugin name")

        transform_set_model = TransformSetModel()

        for frame_set_id in frame_set_ids:
            transform_set_id = plugin().frame_set_select_extract(frame_set_id,
                                                                 opts)

            result = transform_set_model.select(transform_set_id)

            debug(f'transform_set_id={result[0]}, name={result[1]}, '
                  f'fk_frame_sets={result[2]}, '
                  f'fk_prev_transform_sets={result[3]}',
                  3)

    def delete(self, frame_set_ids):
        """
        This method deletes a frame set from the frame set collection.

        :param list(int) frame_set_ids: The frame set IDs.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        frame_set_model = FrameSetModel()

        for frame_set_id in frame_set_ids:
            result = frame_set_model.select(frame_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Frame set with ID {frame_set_id:08d} not found')

        for frame_set_id in frame_set_ids:
            frame_set_model.delete(frame_set_id)

            shutil.rmtree(FrameSetSubDir.path(frame_set_id))

            debug(f'Frame set {frame_set_id} was successfully deleted', 3)

    def select_clone(self, frame_set_ids):
        """
        This method clones frame sets to new frame sets.

        :param list(int) frame_set_ids: The frame set IDs.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        frame_set_model = FrameSetModel()

        for frame_set_id in frame_set_ids:
            result = frame_set_model.select(frame_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Frame set with ID {frame_set_id:08d} not found')

        for frame_set_id in frame_set_ids:
            result = frame_set_model.select(frame_set_id)

            self.select_merge([frame_set_id], result[1], rejected=True)

    def select_merge(self, frame_set_ids, video_id=None, rejected=False):
        """
        This method merges multiple frame sets into one frame set.

        :param list(int) frame_set_ids: The frame set IDs.
        :param int video_id: The video ID to which this frame set corresponds
             (if any). The default value is None.
        :param bool rejected: True if should include rejected frames else False
            if should not. The default value is False.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        frame_set_model = FrameSetModel()

        for frame_set_id in frame_set_ids:
            result = frame_set_model.select(frame_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Frame set with ID {frame_set_id:08d} not found')

        frame_set_id = frame_set_model.insert(video_id)

        p1 = FrameSetSubDir.path(frame_set_id)

        os.makedirs(p1)

        frame_model = FrameModel()
        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))

        for frame_set_id_ in frame_set_ids:
            offset = 0
            p2 = FrameSetSubDir.path(frame_set_id_)

            while True:
                frames = frame_model.list(frame_set_id_, length=length,
                                          offset=offset, rejected=rejected)

                if not frames:
                    break

                for frame in frames:
                    frame_id = frame_model.insert(frame_set_id, frame[2])

                    p3 = FrameFile.path(p2, frame[0], 'jpg')
                    p4 = FrameFile.path(p2, frame[0], 'jpg', '192x192')
                    p5 = FrameFile.path(p1, frame_id, 'jpg')
                    p6 = FrameFile.path(p1, frame_id, 'jpg', '192x192')

                    shutil.copy(p3, p5)
                    shutil.copy(p4, p6)

                    debug(f'Frame with ID {frame[0]:08d} and thumbnail at '
                          f'{p3} and {p4} merged as ID {frame_id:08d} at '
                          f'{p5} and {p6}', 4)

                offset += length

        debug(f'frame_set_id={frame_set_id}, fk_videos={video_id}', 3)

    def select_export_dir(self, frame_set_ids, target_dir, opts={}):
        """
        This method exports frame sets to a directory.

        :param list frame_set_ids: The list of frame set IDs to export.
        :param str target_dir: The directory to which to export the frame sets.
        :param dict opts: The dict of options.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        frame_set_model = FrameSetModel()

        for frame_set_id in frame_set_ids:
            result = frame_set_model.select(frame_set_id)
            if result is None:
                raise CommandLineRouteHandlerError(
                    f'Frame set with ID {frame_set_id:08d} not found')

        frame_model = FrameModel()
        length = int(os.environ.get('MODEL_LIST_LENGTH', '100'))
        count = 0

        for fid in frame_set_ids:
            offset = 0
            frame_set_path = FrameSetSubDir.path(fid)

            while True:
                results = frame_model.list(fid, length=length, offset=offset,
                                           rejected=False)

                if not results:
                    break

                for frame_id, _, _ in results:
                    file_path = FrameFile().path(frame_set_path, frame_id,
                                                 'jpg')
                    if 'format' in opts:
                        filename = opts['format'] % frame_id
                    else:
                        filename = os.path.basename(file_path)

                    target_path = os.path.join(target_dir, filename)
                    shutil.copy(file_path, target_path)
                    count += 1

                    debug(f'Frame with ID {frame_id:08d} at {file_path} '
                          f'exported to {target_path}', 4)

                offset += length

        debug(f'{count} frames were successfully exported to {target_dir}',
              3)

    def insert_images(self, images_path, opts):
        """
        This method inserts a frame set from a directory of images.

        :param str images_path: The path to the directory containing the images
            to insert.
        :param dict opts: The dict of options.
        :raises: CommandLineRouteHandlerError
        :rtype: None
        """

        if not os.path.isdir(images_path):
            raise CommandLineRouteHandlerError(
                f'The path at {images_path} is not a directory')

        frame_set_id = FrameSetModel().insert(None)

        p1 = FrameSetSubDir.path(frame_set_id)

        os.makedirs(p1)

        frame_model = FrameModel()

        for image_path in glob.glob(os.path.join(images_path, '*')):
            ext = os.path.splitext(image_path)[1].lower()

            if ext not in ['.jpg', '.png']:
                debug(f"Skipped image at {image_path} because it does not "
                      f"have a '.jpg' or '.png' file extension", 4)
                continue

            image = cv2.imread(image_path)

            frame_id = frame_model.insert(frame_set_id, 0)

            p2 = FrameFile.path(p1, frame_id, 'jpg')

            cv2.imwrite(p2, image, [cv2.IMWRITE_JPEG_QUALITY, 100])

            thumbnail = imutils.resize(image, width=192, height=192)

            p3 = FrameFile.path(p1, frame_id, 'jpg', '192x192')

            cv2.imwrite(p3, thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 100])

            debug(f'Image at {image_path} inserted with ID {frame_id:08d} at '
                  f'{p2} and {p3}', 4)

        debug(f'frame_set_id={frame_set_id}, fk_videos=None', 3)

    def usage(self):
        """
        This method prints usage.

        :rtype: None
        """

        path = os.path.join(
                   os.path.dirname(os.path.realpath(__file__)),
                   'frame_set_command_line_route_handler_usage.txt')

        with open(path, 'r') as file_:
            usage = file_.read()

        usage = usage.strip()

        debug(usage, 3)

    def handle(self, args, opts):
        """
        This method handles command line arguments for the frame set
        collection.

        :param list(str) args: The list of command line arguments.
        :param dict opts: The dict of options.
        :rtype: None
        """

        if args[1] == 'list':
            self.list()
        elif args[1] == 'select' and args[4] == 'curate' \
                and args[5] == 'manual':
            self.select_curate_manual(int(args[3]), opts)
        elif args[1] == 'select' and args[4] == 'extract':
            self.select_extract(parse_range(args[3]), args[5], opts)
        elif args[1] == 'delete':
            self.delete(parse_range(args[3]))
        elif args[1] == 'select' and args[4] == 'clone':
            self.select_clone(parse_range(args[3]))
        elif args[1] == 'select' and args[4] == 'merge':
            self.select_merge(parse_range(args[3]))
        elif args[1] == 'select' and args[4] == 'export' \
                and args[5] == 'dir':
            self.select_export_dir(parse_range(args[3]), args[6], opts)
        elif args[1] == 'insert' and args[3] == 'images':
            self.insert_images(args[4], opts)
        elif args[1] == 'usage':
            self.usage()
