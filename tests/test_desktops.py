import threading
import time
import unittest
from unittest import mock

from tests.fake_i3 import FakeI3
from window_names.desktops.desktops import running_desktop
from window_names.desktops.i3 import I3
from window_names.desktops.i3_ipc import I3Ipc
from window_names.desktops.sway import Sway
from window_names.desktops.x11 import X11

SWAY_TREE = {
    "id": 1, "type": "root", "nodes": [{
        "id": 3, "type": "workspace", "nodes": [
            {"id": 7, "type": "con", "name": "onplia – Program.cs", "app_id": None, "pid": 4100,
             "window_properties": {"class": "jetbrains-rider"}, "focused": False, "nodes": []},
            {"id": 8, "type": "con", "name": "~/src", "app_id": "foot", "pid": 4200, "focused": True, "nodes": []},
        ],
        "floating_nodes": [{"id": 9, "type": "floating_con", "name": "Chat", "app_id": "chrome-chat.google.com__-Default", "pid": 4300, "nodes": []}],
    }],
}

I3_TREE = {
    "id": 1, "type": "root", "nodes": [{
        "id": 3, "type": "workspace", "nodes": [
            {"id": 7, "type": "con", "name": "notes", "window": 0x1a00007, "window_properties": {"class": "Gedit"}, "focused": True, "nodes": []},
        ],
    }],
}


class SwayTest(unittest.TestCase):
    def setUp(self):
        self.wm = FakeI3(SWAY_TREE)
        with mock.patch.dict("os.environ", {"SWAYSOCK": self.wm.path}):
            self.sway = Sway()

    def test_every_app_window_is_found_with_its_class_title_and_process(self):
        found = [(w.id, w.app_class, w.title, w.pid) for w in self.sway.windows()]
        self.assertCountEqual(found, [
            ("7", "jetbrains-rider", "onplia – Program.cs", 4100),
            ("8", "foot", "~/src", 4200),
            ("9", "chrome-chat.google.com__-Default", "Chat", 4300),
        ])

    def test_the_focused_window_is_the_active_one(self):
        self.assertEqual(self.sway.active_window().id, "8")

    def test_text_becomes_the_windows_title_format_once(self):
        self.sway.show_text("7", 'Rider — "onplia"')
        self.sway.show_text("7", 'Rider — "onplia"')
        self.assertEqual(self.wm.commands, ['[con_id=7] title_format "Rider — \\"onplia\\""'])

    def test_waiting_ends_early_when_a_window_changes(self):
        self.sway.wait(0.01)
        threading.Timer(0.1, self.wm.send_event).start()
        started = time.monotonic()
        self.sway.wait(5)
        self.assertLess(time.monotonic() - started, 2)


class MarkupTest(unittest.TestCase):
    def sway_with(self, config):
        wm = FakeI3(SWAY_TREE, config)
        with mock.patch.dict("os.environ", {"SWAYSOCK": wm.path}):
            Sway().show_text("7", "Music & <Search>")
        return wm.commands[0]

    def test_sway_with_a_plain_font_shows_the_text_as_it_is(self):
        self.assertEqual(self.sway_with("font monospace 10\n"), '[con_id=7] title_format "Music & <Search>"')

    def test_sway_with_a_pango_font_gets_markup_escaped(self):
        self.assertEqual(self.sway_with("font pango:monospace 10\n"), '[con_id=7] title_format "Music &amp; &lt;Search&gt;"')

    def test_i3_always_gets_markup_escaped(self):
        wm = FakeI3(I3_TREE)
        with mock.patch.dict("os.environ", {"I3SOCK": wm.path}):
            I3(mock.Mock()).show_text("7", "Music & Search")
        self.assertEqual(wm.commands, ['[con_id=7] title_format "Music &amp; Search"'])


class I3Test(unittest.TestCase):
    def test_i3_is_found_through_its_root_window_property_without_i3sock(self):
        wm = FakeI3(I3_TREE)
        xprop = mock.Mock()
        xprop.root_strings.return_value = [wm.path]
        xprop.pid_of.return_value = 1
        with mock.patch.dict("os.environ", {"DISPLAY": ":0"}, clear=True):
            self.assertEqual(I3(xprop).windows()[0].title, "notes")
        xprop.root_strings.assert_called_with("I3_SOCKET_PATH")

    def test_i3_asks_x11_for_the_process(self):
        wm = FakeI3(I3_TREE)
        xprop = mock.Mock()
        xprop.pid_of.return_value = 5150
        with mock.patch.dict("os.environ", {"I3SOCK": wm.path}):
            window = I3(xprop).windows()[0]
        xprop.pid_of.assert_called_with("0x1a00007")
        self.assertEqual((window.id, window.app_class, window.title, window.pid), ("7", "Gedit", "notes", 5150))


class FakeXprop:
    def __init__(self):
        self.titles = {"0x1": "bash: ~/src"}
        self.sets = []

    def client_ids(self):
        return list(self.titles)

    def active_id(self):
        return "0x1"

    def strings_of(self, window_id, name):
        return {"WM_CLASS": ["xterm", "XTerm"], "_NET_WM_NAME": [self.titles[window_id]]}.get(name, [])

    def pid_of(self, window_id):
        return 77

    def set_title(self, window_id, text):
        self.sets.append(text)
        self.titles[window_id] = text
        return True


class X11Test(unittest.TestCase):
    def setUp(self):
        self.xprop = FakeXprop()
        self.x11 = X11(self.xprop, sleep=lambda seconds: None)

    def test_the_app_keeps_its_own_title_after_the_name_is_shown(self):
        self.x11.windows()
        self.x11.show_text("0x1", "Terminal — ~/src")
        window = self.x11.windows()[0]
        self.assertEqual((window.app_class, window.title, window.pid), ("XTerm", "bash: ~/src", 77))

    def test_the_name_is_set_again_when_the_app_overwrites_it(self):
        self.x11.windows()
        self.x11.show_text("0x1", "Terminal — ~/src")
        self.x11.windows()
        self.x11.show_text("0x1", "Terminal — ~/src")
        self.xprop.titles["0x1"] = "bash: ~/other"
        self.assertEqual(self.x11.windows()[0].title, "bash: ~/other")
        self.x11.show_text("0x1", "Terminal — ~/other")
        self.assertEqual(self.xprop.sets, ["Terminal — ~/src", "Terminal — ~/other"])


class PickingTheDesktopTest(unittest.TestCase):
    def test_the_first_running_desktop_is_used(self):
        class NotHere:
            @staticmethod
            def is_running():
                return False

        class Here:
            @staticmethod
            def is_running():
                return True

        self.assertIsInstance(running_desktop([NotHere, Here]), Here)

    def test_no_supported_desktop_is_explained(self):
        class NotHere:
            @staticmethod
            def is_running():
                return False

        with self.assertRaises(SystemExit) as stopped:
            running_desktop([NotHere])
        self.assertIn("Hyprland, Sway, i3 and X11", str(stopped.exception))
