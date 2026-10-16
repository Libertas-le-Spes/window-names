import subprocess


def ask_in_menu(prompt: str) -> str | None:
    answer = subprocess.run(["omarchy-menu-input", prompt, "--width", "500"], capture_output=True, text=True)
    return answer.stdout.strip() if answer.returncode == 0 else None
