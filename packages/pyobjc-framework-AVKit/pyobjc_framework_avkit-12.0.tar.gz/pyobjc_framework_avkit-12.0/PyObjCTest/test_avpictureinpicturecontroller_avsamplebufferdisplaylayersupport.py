from PyObjCTools.TestSupport import TestCase, min_sdk_level
import AVKit


class TestAVPictureInPictureController_AVSampleBufferDisplayLayerSupportHelper(
    AVKit.NSObject
):
    def pictureInPictureController_setPlaying_(self, a, b):
        pass

    def pictureInPictureControllerTimeRangeForPlayback_(self, a):
        return 1

    def pictureInPictureControllerIsPlaybackPaused_(self, a):
        return 1

    def pictureInPictureController_didTransitionToRenderSize_(self, a, b):
        pass

    def pictureInPictureControllerShouldProhibitBackgroundAudioPlayback_(self, a):
        return 1

    def pictureInPictureController_skipInterval_completionHandler_(self, a, b, c):
        pass


class TestAVPictureInPictureController_AVSampleBufferDisplayLayerSupport(TestCase):
    @min_sdk_level("12.0")
    def testProtocols12_0(self):
        self.assertProtocolExists("AVPictureInPictureSampleBufferPlaybackDelegate")

    def test_methods(self):
        self.assertArgIsBOOL(
            TestAVPictureInPictureController_AVSampleBufferDisplayLayerSupportHelper.pictureInPictureController_setPlaying_,
            1,
        )
        self.assertResultHasType(
            TestAVPictureInPictureController_AVSampleBufferDisplayLayerSupportHelper.pictureInPictureControllerTimeRangeForPlayback_,  # noqa: B950
            b"{CMTimeRange={CMTime=qiIq}{CMTime=qiIq}}",
        )
        self.assertResultIsBOOL(
            TestAVPictureInPictureController_AVSampleBufferDisplayLayerSupportHelper.pictureInPictureControllerIsPlaybackPaused_
        )
        self.assertArgHasType(
            TestAVPictureInPictureController_AVSampleBufferDisplayLayerSupportHelper.pictureInPictureController_didTransitionToRenderSize_,  # noqa: B950
            1,
            b"{CMVideoDimensions=ii}",
        )
        self.assertArgHasType(
            TestAVPictureInPictureController_AVSampleBufferDisplayLayerSupportHelper.pictureInPictureController_skipInterval_completionHandler_,  # noqa: B950
            1,
            b"{CMTime=qiIq}",
        )
        self.assertArgIsBlock(
            TestAVPictureInPictureController_AVSampleBufferDisplayLayerSupportHelper.pictureInPictureController_skipInterval_completionHandler_,  # noqa: B950
            2,
            b"v",
        )
        self.assertResultIsBOOL(
            TestAVPictureInPictureController_AVSampleBufferDisplayLayerSupportHelper.pictureInPictureControllerShouldProhibitBackgroundAudioPlayback_  # noqa: B950
        )
