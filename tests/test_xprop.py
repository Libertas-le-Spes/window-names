import unittest
from unittest import mock

from window_names.desktops.xprop import Xprop

OUTPUTS = {
    ("-root", "-notype", "_NET_CLIENT_LIST"): "_NET_CLIENT_LIST: window id # 0x1a00007, 0x2c00003\n",
    ("-root", "-notype", "_NET_ACTIVE_WINDOW"): "_NET_ACTIVE_WINDOW: window id # 0x2c00003\n",
    ("-id", "0x2c00003", "-notype", "WM_CLASS"): 'WM_CLASS = "gedit", "Gedit"\n',
    ("-id", "0x2c00003", "-notype", "_NET_WM_NAME"): '_NET_WM_NAME = "say \\"hi\\" — notes"\n',
    ("-id", "0x2c00003", "-notype", "_NET_WM_PID"): "_NET_WM_PID = 5150\n",
}


class XpropTest(unittest.TestCase):
    def setUp(self):
        self.xprop = Xprop()
        patcher = mock.patch.object(Xprop, "_run", staticmethod(lambda *arguments: OUTPUTS.get(arguments)))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_reads_windows_and_their_properties(self):
        self.assertEqual(self.xprop.client_ids(), ["0x1a00007", "0x2c00003"])
        self.assertEqual(self.xprop.active_id(), "0x2c00003")
        self.assertEqual(self.xprop.strings_of("0x2c00003", "WM_CLASS"), ["gedit", "Gedit"])
        self.assertEqual(self.xprop.strings_of("0x2c00003", "_NET_WM_NAME"), ['say "hi" — notes'])
        self.assertEqual(self.xprop.pid_of("0x2c00003"), 5150)

    def test_missing_properties_read_as_nothing(self):
        self.assertEqual(self.xprop.strings_of("0x1a00007", "WM_CLASS"), [])
        self.assertEqual(self.xprop.pid_of("0x1a00007"), 0)
