import AppKit
from PyObjCTools.TestSupport import TestCase, min_os_level, min_sdk_level
import objc


class TestNSToolbarHelper(AppKit.NSObject):
    def toolbar_itemForItemIdentifier_willBeInsertedIntoToolbar_(self, a, b, c):
        return 1

    def toolbar_itemIdentifier_canBeInsertedAtIndex_(self, a, b, c):
        return


class TestNSToolbar(TestCase):
    def test_typed_enum(self):
        self.assertIsTypedEnum(AppKit.NSToolbarItemIdentifier, str)
        self.assertIsTypedEnum(AppKit.NSToolbarUserInfoKey, str)

    def test_enum_types(self):
        self.assertIsEnumType(AppKit.NSToolbarDisplayMode)
        self.assertIsEnumType(AppKit.NSToolbarSizeMode)

    def testConstants(self):
        self.assertEqual(AppKit.NSToolbarDisplayModeDefault, 0)
        self.assertEqual(AppKit.NSToolbarDisplayModeIconAndLabel, 1)
        self.assertEqual(AppKit.NSToolbarDisplayModeIconOnly, 2)
        self.assertEqual(AppKit.NSToolbarDisplayModeLabelOnly, 3)

        self.assertEqual(AppKit.NSToolbarSizeModeDefault, 0)
        self.assertEqual(AppKit.NSToolbarSizeModeRegular, 1)
        self.assertEqual(AppKit.NSToolbarSizeModeSmall, 2)

        self.assertIsInstance(AppKit.NSToolbarWillAddItemNotification, str)
        self.assertIsInstance(AppKit.NSToolbarDidRemoveItemNotification, str)

    @min_os_level("13.0")
    def testConstants13_0(self):
        self.assertIsInstance(AppKit.NSToolbarItemKey, str)

    @min_os_level("15.0")
    def testConstants15_0(self):
        self.assertIsInstance(AppKit.NSToolbarNewIndexKey, str)

    def testMethods(self):
        self.assertResultIsBOOL(AppKit.NSToolbar.isVisible)
        self.assertArgIsBOOL(AppKit.NSToolbar.setVisible_, 0)
        self.assertResultIsBOOL(AppKit.NSToolbar.customizationPaletteIsRunning)
        self.assertResultIsBOOL(AppKit.NSToolbar.showsBaselineSeparator)
        self.assertArgIsBOOL(AppKit.NSToolbar.setShowsBaselineSeparator_, 0)
        self.assertResultIsBOOL(AppKit.NSToolbar.allowsUserCustomization)
        self.assertArgIsBOOL(AppKit.NSToolbar.setAllowsUserCustomization_, 0)
        self.assertResultIsBOOL(AppKit.NSToolbar.autosavesConfiguration)
        self.assertArgIsBOOL(AppKit.NSToolbar.setAutosavesConfiguration_, 0)

    @min_os_level("10.10")
    def testMethods10_10(self):
        self.assertResultIsBOOL(AppKit.NSToolbar.allowsExtensionItems)
        self.assertArgIsBOOL(AppKit.NSToolbar.setAllowsExtensionItems_, 0)

    @min_os_level("15.0")
    def testMethods15_0(self):
        self.assertResultIsBOOL(AppKit.NSToolbar.allowsDisplayModeCustomization)
        self.assertArgIsBOOL(AppKit.NSToolbar.setAllowsDisplayModeCustomization_, 0)

    @min_sdk_level("10.6")
    def testProtocolObjects(self):
        self.assertProtocolExists("NSToolbarDelegate")

    def testProtocols(self):
        self.assertArgIsBOOL(
            TestNSToolbarHelper.toolbar_itemForItemIdentifier_willBeInsertedIntoToolbar_,
            2,
        )

        self.assertResultIsBOOL(
            TestNSToolbarHelper.toolbar_itemIdentifier_canBeInsertedAtIndex_
        )
        self.assertArgHasType(
            TestNSToolbarHelper.toolbar_itemIdentifier_canBeInsertedAtIndex_,
            2,
            objc._C_NSInteger,
        )
