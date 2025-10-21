import AppKit
from PyObjCTools.TestSupport import TestCase, min_sdk_level


class TestNSTextViewportLayoutControllerHelper(AppKit.NSObject):
    def viewportBoundsForTextViewportLayoutController_(self, a):
        return 1


class TestNSTextViewportLayoutController(TestCase):
    @min_sdk_level("12.0")
    def test_protocols(self):
        self.assertProtocolExists("NSTextViewportLayoutControllerDelegate")

    def test_methods(self):
        self.assertResultHasType(
            TestNSTextViewportLayoutControllerHelper.viewportBoundsForTextViewportLayoutController_,
            AppKit.NSRect.__typestr__,
        )
