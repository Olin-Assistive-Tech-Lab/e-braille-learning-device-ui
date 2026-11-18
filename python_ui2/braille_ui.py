from dataclasses import dataclass
from enum import Enum, auto

BRAILLE = {
    "a": (1,),
    "b": (1, 2),
    "c": (1, 4),
    "d": (1, 4, 5),
    "e": (1, 5),
    "f": (1, 2, 4),
    "g": (1, 2, 4, 5),
    "h": (1, 2, 5),
    "i": (2, 4),
    "j": (2, 4, 5),
    "k": (1, 3),
    "l": (1, 2, 3),
    "m": (1, 3, 4),
    "n": (1, 3, 4, 5),
    "o": (1, 3, 5),
    "p": (1, 2, 3, 4),
    "q": (1, 2, 3, 4, 5),
    "r": (1, 2, 3, 5),
    "s": (2, 3, 4),
    "t": (2, 3, 4, 5),
    "u": (1, 3, 6),
    "v": (1, 2, 3, 6),
    "w": (2, 4, 5, 6),
    "x": (1, 3, 4, 6),
    "y": (1, 3, 4, 5, 6),
    "z": (1, 3, 5, 6),
    " ": (),
}

CELL_COUNT = 8


def text_to_cells(text):
    """Convert text into six-bit Braille cell values."""
    cells = []

    for char in text.lower():
        mask = 0

        for dot in BRAILLE.get(char, ()):
            mask |= 1 << (dot - 1)

        cells.append(mask)

    return cells


class Input(Enum):
    FORWARD = auto()
    BACKWARD = auto()
    MIC = auto()
    SPEECH = auto()
    DIAL = auto()
    SLIDER = auto()


class Mode(Enum):
    MENU = auto()
    LESSON = auto()
    READER = auto()


class LessonState(Enum):
    PRESENT = auto()
    LISTENING = auto()


@dataclass
class Event:
    input: Input
    value: int = 0
    payload: str = ""


LESSONS = [
    {"title": "First Words", "words": ["cab", "bad"]},
    {"title": "Beginner Letters", "words": ["a", "b", "c", "d", "e"]},
]

DOCUMENTS = {"Story": "a bad cab had a bad bag"}


class Device:
    """Simple simulation of user-facing device behavior."""

    def __init__(self):
        self.mode = Mode.MENU
        self.state = LessonState.PRESENT

        self.menu = []
        self.selection = 0

        self.lesson = None
        self.word_index = 0
        self.score = 0
        self.attempts = 0
        self.max_attempts = 2

        self.reader_text = ""
        self.reader_position = 0

        self.cells = []
        self.volume = 50
        self.listening = False

        self.trace = []

    def output(self, kind, message):
        """Record feedback for the GUI and terminal."""
        self.trace.append((kind, str(message)))

    def speak(self, message):
        self.output("VOICE", message)

    def cue(self, name):
        """Simulate audio and haptic feedback."""
        cues = {
            "navigate": (None, "tap"),
            "select": ("select", "tap"),
            "correct": ("correct", "success"),
            "wrong": ("wrong", "error"),
            "reward": ("reward", "success"),
            "listen": ("listen", "tap"),
            "edge": (None, "error"),
        }

        tone, haptic = cues[name]

        if tone:
            self.output("TONE", tone)

        if haptic:
            self.output("HAPTIC", haptic)

    def show_text(self, text):
        self.cells = text_to_cells(text[:CELL_COUNT])
        self.output("BRAILLE", text[:CELL_COUNT])

    def clear_cells(self):
        self.cells = []
        self.output("BRAILLE", "(cleared)")

    def boot(self):
        self.menu = [("lesson", lesson["title"], lesson) for lesson in LESSONS]

        self.menu += [("document", title, text) for title, text in DOCUMENTS.items()]

        self.speak("Braille device ready.")
        self.announce_menu()

    def announce_menu(self):
        kind, title, _ = self.menu[self.selection]
        self.speak(f"{kind}: {title}")

    def start_lesson(self, lesson):
        self.mode = Mode.LESSON
        self.lesson = lesson
        self.word_index = 0
        self.score = 0
        self.attempts = 0
        self.state = LessonState.PRESENT

        self.speak(f"Lesson: {lesson['title']}")
        self.speak("Feel the Braille, press MIC, " "then say the word.")

        self.present_word()

    def present_word(self):
        self.state = LessonState.PRESENT
        self.show_text(self.lesson["words"][self.word_index])

    def next_word(self):
        self.word_index += 1
        self.attempts = 0

        if self.word_index >= len(self.lesson["words"]):
            self.finish_lesson()
        else:
            self.present_word()

    def finish_lesson(self):
        total = len(self.lesson["words"])

        self.clear_cells()
        self.speak(f"Lesson complete. You got " f"{self.score} of {total}.")
        self.cue("reward")

        self.mode = Mode.MENU
        self.announce_menu()

    def evaluate_answer(self, answer):
        target = self.lesson["words"][self.word_index]

        self.listening = False
        self.output("MIC", "stopped")

        # Echo recognized speech in Braille.
        self.show_text(answer)

        if answer.strip().lower() == target.lower():
            self.score += 1
            self.cue("correct")
            self.speak("Correct!")
            self.next_word()
        else:
            self.attempts += 1
            self.cue("wrong")

            if self.attempts >= self.max_attempts:
                self.speak(f"The word was {target}.")
                self.next_word()
            else:
                self.speak("Not quite. Feel it again and retry.")
                self.present_word()

    def open_reader(self, text):
        self.mode = Mode.READER
        self.reader_text = text
        self.reader_position = 0

        self.speak("E-reader opened.")
        self.render_reader()

    def render_reader(self):
        text = self.reader_text[
            self.reader_position : self.reader_position + CELL_COUNT
        ]
        self.show_text(text)

    def scroll_reader(self, steps):
        last = max(0, len(self.reader_text) - 1)

        new_position = max(0, min(last, self.reader_position + steps))

        if new_position == self.reader_position:
            self.cue("edge")
            return

        self.reader_position = new_position
        self.cue("navigate")
        self.render_reader()

    def handle(self, event):
        """Process one physical-device input."""

        if event.input == Input.SLIDER:
            self.volume = max(0, min(100, event.value))
            self.output("VOLUME", f"{self.volume}%")
            return

        if self.mode == Mode.MENU:
            if event.input == Input.FORWARD:
                self.selection = (self.selection + 1) % len(self.menu)

                self.cue("navigate")
                self.announce_menu()

            elif event.input == Input.BACKWARD:
                self.selection = (self.selection - 1) % len(self.menu)

                self.cue("navigate")
                self.announce_menu()

            elif event.input == Input.MIC:
                kind, _, item = self.menu[self.selection]
                self.cue("select")

                if kind == "lesson":
                    self.start_lesson(item)
                else:
                    self.open_reader(item)

        elif self.mode == Mode.LESSON:
            if event.input == Input.MIC:
                if self.state == LessonState.PRESENT:
                    self.state = LessonState.LISTENING
                    self.listening = True

                    self.cue("listen")
                    self.output("MIC", "listening")

            elif event.input == Input.SPEECH:
                if self.state == LessonState.LISTENING:
                    self.evaluate_answer(event.payload)

            elif event.input == Input.FORWARD:
                if self.state == LessonState.PRESENT:
                    self.cue("navigate")
                    self.next_word()

            elif event.input == Input.BACKWARD:
                if self.state == LessonState.PRESENT:
                    if self.word_index > 0:
                        self.word_index -= 1
                        self.attempts = 0
                        self.cue("navigate")
                        self.present_word()
                    else:
                        self.cue("edge")

        elif self.mode == Mode.READER:
            if event.input == Input.DIAL:
                self.scroll_reader(event.value)

            elif event.input == Input.BACKWARD:
                self.clear_cells()
                self.mode = Mode.MENU
                self.speak("Returning to menu.")
                self.announce_menu()


def build_sim_device():
    device = Device()
    device.boot()
    return device
