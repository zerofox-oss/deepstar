import cv2


def create_one_video_file_from_one_image_file(image_path, video_path,
                                              frame_count=1):
    """
    This method creates one video file from one image file.

    :param str image_path: The path to the image file.
    :param str video_path: The path to the video file.
    :param int frame_count: The image is added frame_count number of times to
        the video. The default value is 1.
    :rtype: bool
    """

    image = cv2.imread(image_path)
    if image is None:
        return False

    height, width = image.shape[:2]

    vw = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30.0,
                         (width, height))
    if vw is None:
        return False

    try:
        for _ in range(0, frame_count):
            vw.write(image)
    finally:
        vw.release()

    return True


def create_one_video_file_from_many_image_files(image_paths, video_path):
    """
    This method creates one video file from many image files.

    :param function image_paths: The generator function that returns the paths
        to the image files.
    :param str video_path: The path to the video file.
    :rtype: bool
    """

    vw = None

    try:
        for image_path in image_paths():
            image = cv2.imread(image_path)
            if image is None:
                return False

            # Initialize VideoWriter based on dimensions of first image.
            if vw is None:
                height, width = image.shape[:2]

                vw = cv2.VideoWriter(video_path,
                                     cv2.VideoWriter_fourcc(*'mp4v'),
                                     30.0, (width, height))
                if vw is None:
                    return False

            vw.write(image)
    finally:
        if vw is not None:
            vw.release()

    return True
