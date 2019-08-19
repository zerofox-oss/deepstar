from deepstar.plugins.adjust_color_transform_set_select_extract_plugin import \
    AdjustColorTransformSetSelectExtractPlugin
from deepstar.plugins.crop_transform_set_select_extract_plugin import \
    CropTransformSetSelectExtractPlugin
from deepstar.plugins.default_video_select_extract_plugin import \
    DefaultVideoSelectExtractPlugin
from deepstar.plugins.fade_transform_set_select_merge_plugin import \
    FadeTransformSetSelectMergePlugin
from deepstar.plugins.manual_frame_set_select_curate_plugin import \
    ManualFrameSetSelectCuratePlugin
from deepstar.plugins.manual_transform_set_select_curate_plugin import \
    ManualTransformSetSelectCuratePlugin
from deepstar.plugins.max_blur_transform_set_select_curate_plugin import \
    MaxBlurTransformSetSelectCuratePlugin
from deepstar.plugins.max_size_transform_set_select_extract_plugin import \
    MaxSizeTransformSetSelectExtractPlugin
from deepstar.plugins.min_size_transform_set_select_curate_plugin import \
    MinSizeTransformSetSelectCuratePlugin
from deepstar.plugins.mtcnn_frame_set_select_extract_plugin import \
    MTCNNFrameSetSelectExtractPlugin
from deepstar.plugins.overlay_image_transform_set_select_merge_plugin import \
    OverlayImageTransformSetSelectMergePlugin
from deepstar.plugins.overlay_transform_set_select_merge_plugin import \
    OverlayTransformSetSelectMergePlugin
from deepstar.plugins.pad_transform_set_select_extract_plugin import \
    PadTransformSetSelectExtractPlugin
from deepstar.plugins.resize_transform_set_select_extract_plugin import \
    ResizeTransformSetSelectExtractPlugin
from deepstar.plugins.slice_transform_set_select_extract_plugin import \
    SliceTransformSetSelectExtractPlugin
from deepstar.plugins.transform_set_frame_set_select_extract_plugin import \
    TransformSetFrameSetSelectExtractPlugin
from deepstar.plugins.mesonet_video_select_detect_plugin import \
    MesoNetVideoSelectDetectPlugin
from deepstar.plugins.mouth_transform_set_select_extract_plugin import \
    MouthTransformSetSelectExtractPlugin

try:
    from deepstar.plugins.custom_plugin import CustomPlugin
except ImportError:
    pass


class Plugin:
    """
    This class implements the Plugin class.
    """

    _map = {
        'video_select_extract': {
            'default': DefaultVideoSelectExtractPlugin
        },
        'video_select_deploy': {
        },
        'video_select_detect': {
            MesoNetVideoSelectDetectPlugin.name:
                MesoNetVideoSelectDetectPlugin
        },
        'frame_set_select_curate': {
            ManualFrameSetSelectCuratePlugin.name:
                ManualFrameSetSelectCuratePlugin
        },
        'frame_set_select_extract': {
            MTCNNFrameSetSelectExtractPlugin.name:
                MTCNNFrameSetSelectExtractPlugin,
            TransformSetFrameSetSelectExtractPlugin.name:
                TransformSetFrameSetSelectExtractPlugin
        },
        'transform_set_select_curate': {
            ManualTransformSetSelectCuratePlugin.name:
                ManualTransformSetSelectCuratePlugin,
            MaxBlurTransformSetSelectCuratePlugin.name:
                MaxBlurTransformSetSelectCuratePlugin,
            MinSizeTransformSetSelectCuratePlugin.name:
                MinSizeTransformSetSelectCuratePlugin
        },
        'transform_set_select_extract': {
            AdjustColorTransformSetSelectExtractPlugin.name:
                AdjustColorTransformSetSelectExtractPlugin,
            CropTransformSetSelectExtractPlugin.name:
                CropTransformSetSelectExtractPlugin,
            MaxSizeTransformSetSelectExtractPlugin.name:
                MaxSizeTransformSetSelectExtractPlugin,
            PadTransformSetSelectExtractPlugin.name:
                PadTransformSetSelectExtractPlugin,
            ResizeTransformSetSelectExtractPlugin.name:
                ResizeTransformSetSelectExtractPlugin,
            SliceTransformSetSelectExtractPlugin.name:
                SliceTransformSetSelectExtractPlugin,
            MouthTransformSetSelectExtractPlugin.name:
                MouthTransformSetSelectExtractPlugin
        },
        'transform_set_select_merge': {
            FadeTransformSetSelectMergePlugin.name:
                FadeTransformSetSelectMergePlugin,
            OverlayTransformSetSelectMergePlugin.name:
                OverlayTransformSetSelectMergePlugin,
            OverlayImageTransformSetSelectMergePlugin.name:
                OverlayImageTransformSetSelectMergePlugin
        }
    }

    @classmethod
    def custom_plugin(cls):
        """
        This method returns CustomPlugin if defined.

        :rtype: CustomPlugin
        """

        try:
            return CustomPlugin
        except NameError:
            return None

    @classmethod
    def get(cls, operation, plugin='default'):
        """
        This method returns a plugin for an operation and name.

        :param str operation: The operation name.
        :param str plugin: The plugin name.
        :rtype: object
        """

        custom_plugin = cls.custom_plugin()
        if custom_plugin is not None:
            plugin_ = custom_plugin.get(operation, plugin)
            if plugin_ is not None:
                return plugin_

        if operation in Plugin._map:
            if plugin in Plugin._map[operation]:
                return Plugin._map[operation][plugin]

        return None
