import tempfile
import unittest
from pathlib import Path

from tests.fake_proc import add_process
from window_names.app_names import AppNames
from window_names.kinds.any_app import AnyApp
from window_names.kinds.claude_terminal import ClaudeTerminal
from window_names.kinds.jetbrains import JetBrains
from window_names.kinds.terminal import Terminal
from window_names.kinds.web_app import WebApp
from window_names.processes import Process
from window_names.window import Window


def window(app_class: str, title: str, pid: int = 0) -> Window:
    return Window(address="0x1", app_class=app_class, title=title, pid=pid)


class TerminalsTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.proc = self.root / "proc"
        self.project = Path.home() / "RiderProjects"
        self.terminal = Terminal(lambda pid: Process(pid, self.proc))

    def test_a_shell_reads_as_terminal_and_its_folder(self):
        add_process(self.proc, 10, "foot", self.root, children=[11])
        add_process(self.proc, 11, "bash", self.project, foreground=11)
        self.assertEqual(self.terminal.name(window("foot", "anything", 10)), "Terminal — ~/RiderProjects")

    def test_a_program_in_front_of_the_shell_gives_its_own_name_and_folder(self):
        add_process(self.proc, 10, "foot", self.root, children=[11])
        add_process(self.proc, 11, "bash", Path.home(), foreground=12)
        add_process(self.proc, 12, "nvim", self.project)
        self.assertEqual(self.terminal.name(window("foot", "anything", 10)), "nvim — ~/RiderProjects")

    def test_claude_shows_its_session_name_without_the_status_mark(self):
        add_process(self.proc, 10, "foot", self.root, children=[11])
        add_process(self.proc, 11, "bash", Path.home(), foreground=12)
        add_process(self.proc, 12, "claude", Path.home())
        claude = ClaudeTerminal(self.terminal)
        session = window("foot", "◑ Session window name display", 10)
        self.assertTrue(claude.matches(session))
        self.assertEqual(claude.name(session), "Claude Code — ~ · Session window name display")

    def test_claude_before_it_has_named_the_session(self):
        add_process(self.proc, 10, "foot", self.root, children=[11])
        add_process(self.proc, 11, "bash", Path.home(), foreground=12)
        add_process(self.proc, 12, "claude", Path.home())
        self.assertEqual(ClaudeTerminal(self.terminal).name(window("foot", "✳ Claude Code", 10)), "Claude Code — ~")

    def test_claude_is_not_claimed_when_a_shell_is_in_front(self):
        add_process(self.proc, 10, "foot", self.root, children=[11])
        add_process(self.proc, 11, "bash", Path.home(), foreground=11)
        self.assertFalse(ClaudeTerminal(self.terminal).matches(window("foot", "x", 10)))


class AppsTest(unittest.TestCase):
    def setUp(self):
        folder = Path(tempfile.mkdtemp())
        (folder / "jetbrains-rider.desktop").write_text("[Desktop Entry]\nName=Rider\nStartupWMClass=jetbrains-rider\n")
        (folder / "org.gnome.Nautilus.desktop").write_text("[Desktop Entry]\nName=Files\n")
        self.app_names = AppNames((folder,))

    def test_rider_shows_its_project(self):
        self.assertEqual(JetBrains(self.app_names).name(window("jetbrains-rider", "onplia – /address-comments")), "Rider — onplia")

    def test_rider_without_a_project_is_left_to_other_kinds(self):
        self.assertFalse(JetBrains(self.app_names).matches(window("jetbrains-rider", "Welcome to Rider")))

    def test_web_apps_show_their_site(self):
        cases = {
            "chrome-chat.google.com__u_2_app_home-Default": "chat.google.com",
            "chrome-github.com__-Default": "github.com",
            "chrome-www.example.org__-Default": "example.org",
        }
        for app_class, expected in cases.items():
            self.assertTrue(WebApp().matches(window(app_class, "page")))
            self.assertEqual(WebApp().name(window(app_class, "page")), expected)

    def test_any_other_app_shows_its_name_and_title(self):
        self.assertEqual(AnyApp(self.app_names).name(window("org.gnome.Nautilus", "Downloads")), "Files — Downloads")
        self.assertEqual(AnyApp(self.app_names).name(window("unknown-app", "")), "unknown-app")
