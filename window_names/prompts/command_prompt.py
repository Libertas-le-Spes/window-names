import shutil
import subprocess


class CommandPrompt:
    def __init__(self, program: str, *arguments: str):
        self._program = program
        self._arguments = arguments

    def is_available(self) -> bool:
        return shutil.which(self._program) is not None

    def ask(self, question: str) -> str | None:
        command = [self._program, *(argument.format(question=question) for argument in self._arguments)]
        answer = subprocess.run(command, capture_output=True, text=True)
        return answer.stdout.strip() if answer.returncode == 0 else None
