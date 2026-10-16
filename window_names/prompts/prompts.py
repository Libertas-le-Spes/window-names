from .command_prompt import CommandPrompt

PROMPTS = [
    CommandPrompt("omarchy-menu-input", "{question}", "--width", "500"),
    CommandPrompt("zenity", "--entry", "--title=Rename window", "--text={question}"),
    CommandPrompt("kdialog", "--title", "Rename window", "--inputbox", "{question}"),
]


def first_available(prompts: list = PROMPTS):
    return next(prompt for prompt in prompts if prompt.is_available())
