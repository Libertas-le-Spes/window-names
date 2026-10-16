import tempfile
import unittest
from pathlib import Path

from window_names.desktops.sent_texts import SentTexts
from window_names.given_names import GivenNames
from window_names.namer import Namer
from window_names.service import Service
from window_names.window import Window

WINDOW = Window(id="0xabc", app_class="foot", title="t", pid=1)


class Everything:
    def matches(self, window):
        return True

    def name(self, window):
        return "default"


class FakeDesktop:
    def __init__(self, windows):
        self.open = windows
        self.shown = []

    def windows(self):
        return self.open

    def show_text(self, window_id, text):
        self.shown.append((window_id, text))
        return True


class NamerTest(unittest.TestCase):
    def setUp(self):
        root = Path(tempfile.mkdtemp())
        self.by_hand = GivenNames(root / "hand")
        self.by_tools = GivenNames(root / "tools")
        self.namer = Namer([self.by_hand, self.by_tools], [Everything()])

    def test_hand_beats_tools_beats_default(self):
        self.assertEqual(self.namer.text_for(WINDOW), "default")
        self.by_tools.give(WINDOW.id, "Rider Main")
        self.assertEqual(self.namer.text_for(WINDOW), "Rider Main")
        self.by_hand.give(WINDOW.id, "My review")
        self.assertEqual(self.namer.text_for(WINDOW), "My review")

    def test_a_window_that_closes_loses_its_names(self):
        desktop = FakeDesktop([WINDOW])
        service = Service(desktop, self.namer)
        service.refresh()
        self.by_tools.give(WINDOW.id, "Rider Main")
        self.by_hand.give(WINDOW.id, "My review")
        desktop.open = []
        service.refresh()
        self.assertEqual(self.namer.text_for(WINDOW), "default")

    def test_every_open_window_is_offered_its_text(self):
        desktop = FakeDesktop([WINDOW])
        Service(desktop, self.namer).refresh()
        self.assertEqual(desktop.shown, [("0xabc", "default")])


class SentTextsTest(unittest.TestCase):
    def test_text_is_sent_once_and_again_after_it_changes_or_fails(self):
        sent, sent_texts = [], SentTexts()
        works = [False, True, True]
        sender = lambda window_id, text: sent.append(text) or works.pop(0)
        sent_texts.send("w", "Chat", sender)
        sent_texts.send("w", "Chat", sender)
        sent_texts.send("w", "Chat", sender)
        sent_texts.send("w", "GitLab", sender)
        self.assertEqual(sent, ["Chat", "Chat", "GitLab"])

    def test_a_closed_window_is_forgotten(self):
        sent, sent_texts = [], SentTexts()
        sender = lambda window_id, text: sent.append(text) or True
        sent_texts.send("w", "Chat", sender)
        sent_texts.keep_only(set())
        sent_texts.send("w", "Chat", sender)
        self.assertEqual(sent, ["Chat", "Chat"])
