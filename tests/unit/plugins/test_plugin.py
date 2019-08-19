import unittest

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
from deepstar.plugins.overlay_transform_set_select_merge_plugin import \
    OverlayTransformSetSelectMergePlugin
from deepstar.plugins.overlay_image_transform_set_select_merge_plugin import \
    OverlayImageTransformSetSelectMergePlugin
from deepstar.plugins.pad_transform_set_select_extract_plugin import \
    PadTransformSetSelectExtractPlugin
from deepstar.plugins.plugin import Plugin
from deepstar.plugins.resize_transform_set_select_extract_plugin import \
    ResizeTransformSetSelectExtractPlugin
from deepstar.plugins.slice_transform_set_select_extract_plugin import \
    SliceTransformSetSelectExtractPlugin
from deepstar.plugins.transform_set_frame_set_select_extract_plugin import \
    TransformSetFrameSetSelectExtractPlugin


class TestPlugin(unittest.TestCase):
    """
    This class tests the Plugin class.
    """

    def test(self):
        class TestPlugin2:
            pass

        class TestCustomPlugin:
            map_ = {
                'test': {
                    'default': TestPlugin2
                }
            }

            @classmethod
            def get(cls, operation, plugin):
                if operation in TestCustomPlugin.map_:
                    if plugin in TestCustomPlugin.map_[operation]:
                        return TestCustomPlugin.map_[operation][plugin]

        class TestPlugin1(Plugin):
            @classmethod
            def custom_plugin(cls):
                return TestCustomPlugin

        plugin = TestPlugin1.get('video_select_extract', 'default')
        self.assertTrue(plugin == DefaultVideoSelectExtractPlugin)

        plugin = TestPlugin1.get('frame_set_select_curate', ManualFrameSetSelectCuratePlugin.name)  # noqa
        self.assertTrue(plugin == ManualFrameSetSelectCuratePlugin)

        plugin = TestPlugin1.get('frame_set_select_extract', MTCNNFrameSetSelectExtractPlugin.name)  # noqa
        self.assertTrue(plugin == MTCNNFrameSetSelectExtractPlugin)

        plugin = TestPlugin1.get('frame_set_select_extract', TransformSetFrameSetSelectExtractPlugin.name)  # noqa
        self.assertTrue(plugin == TransformSetFrameSetSelectExtractPlugin)

        plugin = TestPlugin1.get('transform_set_select_curate', ManualTransformSetSelectCuratePlugin.name)  # noqa
        self.assertTrue(plugin == ManualTransformSetSelectCuratePlugin)

        plugin = TestPlugin1.get('transform_set_select_curate', MaxBlurTransformSetSelectCuratePlugin.name)  # noqa
        self.assertTrue(plugin == MaxBlurTransformSetSelectCuratePlugin)

        plugin = TestPlugin1.get('transform_set_select_curate', MinSizeTransformSetSelectCuratePlugin.name)  # noqa
        self.assertTrue(plugin == MinSizeTransformSetSelectCuratePlugin)

        plugin = TestPlugin1.get('transform_set_select_extract', AdjustColorTransformSetSelectExtractPlugin.name)  # noqa
        self.assertTrue(plugin == AdjustColorTransformSetSelectExtractPlugin)

        plugin = TestPlugin1.get('transform_set_select_extract', CropTransformSetSelectExtractPlugin.name)  # noqa
        self.assertTrue(plugin == CropTransformSetSelectExtractPlugin)

        plugin = TestPlugin1.get('transform_set_select_extract', MaxSizeTransformSetSelectExtractPlugin.name)  # noqa
        self.assertTrue(plugin == MaxSizeTransformSetSelectExtractPlugin)

        plugin = TestPlugin1.get('transform_set_select_extract', PadTransformSetSelectExtractPlugin.name)  # noqa
        self.assertTrue(plugin == PadTransformSetSelectExtractPlugin)

        plugin = TestPlugin1.get('transform_set_select_extract', ResizeTransformSetSelectExtractPlugin.name)  # noqa
        self.assertTrue(plugin == ResizeTransformSetSelectExtractPlugin)

        plugin = TestPlugin1.get('transform_set_select_extract', SliceTransformSetSelectExtractPlugin.name)  # noqa
        self.assertTrue(plugin == SliceTransformSetSelectExtractPlugin)

        plugin = TestPlugin1.get('transform_set_select_merge', FadeTransformSetSelectMergePlugin.name)  # noqa
        self.assertTrue(plugin == FadeTransformSetSelectMergePlugin)

        plugin = TestPlugin1.get('transform_set_select_merge', OverlayTransformSetSelectMergePlugin.name)  # noqa
        self.assertTrue(plugin == OverlayTransformSetSelectMergePlugin)

        plugin = TestPlugin1.get('transform_set_select_merge', OverlayImageTransformSetSelectMergePlugin.name)  # noqa
        self.assertTrue(plugin == OverlayImageTransformSetSelectMergePlugin)

        plugin = TestPlugin1.get('test', 'default')
        self.assertTrue(plugin == TestPlugin2)

        plugin = TestPlugin1.get('test', 'test')
        self.assertIsNone(plugin)
