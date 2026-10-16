import tempfile
import unittest
from pathlib import Path

from window_names.given_names import GivenNames
from window_names.namer import Namer
from window_names.service import Service
from window_names.window import Window

WINDOW = Window(address="0xabc", app_class="foot", title="t", pid=1)


class Everything:
    def matches(self, window):
        return True

    def name(self, window):
        return "default"


class NamerTest(unittest.TestCase):
    def setUp(self):
        root = Path(tempfile.mkdtemp())
        self.by_hand = GivenNames(root / "hand")
        self.by_tools = GivenNames(root / "tools")
        self.namer = Namer([self.by_hand, self.by_tools], [Everything()])

    def test_hand_beats_tools_beats_default(self):
        self.assertEqual(self.namer.text_for(WINDOW), "default")
        self.by_tools.give(WINDOW.address, "Rider Main")
        self.assertEqual(self.namer.text_for(WINDOW), "Rider Main")
        self.by_hand.give(WINDOW.address, "My review")
        self.assertEqual(self.namer.text_for(WINDOW), "My review")

    def test_a_closed_window_loses_its_names(self):
        self.by_tools.give(WINDOW.address, "Rider Main")
        self.by_hand.give(WINDOW.address, "My review")
        service = Service(FakeHyprland([WINDOW]), self.namer)
        service.on_event("closewindow>>abc")
        self.assertEqual(self.namer.text_for(WINDOW), "default")


class FakeHyprland:
    def __init__(self, windows):
        self._windows = windows
        self.shown = []
        self.has_bars = True

    def windows(self):
        return self._windows

    def show_text(self, address, text):
        self.shown.append((address, text))
        return self.has_bars


class ServiceTest(unittest.TestCase):
    def test_text_is_sent_once_and_again_after_it_changes(self):
        names = GivenNames(Path(tempfile.mkdtemp()))
        hyprland = FakeHyprland([WINDOW])
        service = Service(hyprland, Namer([names], [Everything()]))
        service.refresh()
        service.refresh()
        names.give(WINDOW.address, "Chat")
        service.refresh()
        self.assertEqual(hyprland.shown, [("0xabc", "default"), ("0xabc", "Chat")])

    def test_text_is_retried_while_the_bars_are_not_loaded(self):
        hyprland = FakeHyprland([WINDOW])
        hyprland.has_bars = False
        service = Service(hyprland, Namer([], [Everything()]))
        service.refresh()
        hyprland.has_bars = True
        service.refresh()
        self.assertEqual(len(hyprland.shown), 2)
