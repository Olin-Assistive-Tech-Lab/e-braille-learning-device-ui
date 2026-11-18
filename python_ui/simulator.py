import tkinter as tk
from tkinter import simpledialog

from braille import get_braille
from lessons import LESSONS, BOOK_TEXT


class BrailleSimulator:
    """Medium-fidelity simulator for OAT Lab UI."""

    def __init__(self, root):
        self.root = root
        self.root.geometry("750x800")
        self.root.configure(bg="#e8edf2")

        # Device interaction variables
        self.mode = "menu"
        self.menu_index = 0
        self.lesson_index = 0
        self.question_index = 0
        self.attempts = 0

        self.dots = set()

        self.book_index = 0
        self.volume = 5
        self.bluetooth = False
        self.battery = 85

        self.build_interface()
        self.bind_keys()
        self.update_display()

    # -----------------------------------
    # BUILD LAPTOP SIMULATOR INTERFACE
    # -----------------------------------

    def build_interface(self):
        tk.Label(
            self.root, text="OAT LAB UI", font=("Arial", 24, "bold"), bg="#e8edf2"
        ).pack(pady=12)

        self.status = tk.Label(self.root, text="", font=("Arial", 11), bg="#e8edf2")
        self.status.pack()

        self.instruction = tk.Label(
            self.root, text="", font=("Arial", 17, "bold"), bg="#e8edf2", wraplength=650
        )
        self.instruction.pack(pady=20)

        # Jumbo six-dot Braille cell
        self.braille_frame = tk.Frame(self.root, bg="#d1dce6", padx=35, pady=25)
        self.braille_frame.pack(pady=10)

        self.dot_buttons = {}

        for dot in range(1, 7):
            row = (dot - 1) % 3
            col = 0 if dot <= 3 else 1

            button = tk.Button(
                self.braille_frame,
                text=str(dot),
                font=("Arial", 18, "bold"),
                width=5,
                height=2,
                command=lambda d=dot: self.toggle_dot(d),
            )

            button.grid(row=row, column=col, padx=15, pady=10)

            self.dot_buttons[dot] = button

        # Physical-style control buttons
        controls = tk.Frame(self.root, bg="#e8edf2")
        controls.pack(pady=15)

        buttons = [
            ("DIAL UP", self.dial_up),
            ("SELECT", self.select),
            ("DIAL DOWN", self.dial_down),
            ("BACK", self.back),
            ("CLEAR", self.clear_dots),
            ("HINT", self.hint),
            ("MIC", self.microphone),
            ("E-READER", self.open_reader),
            ("VOL -", lambda: self.change_volume(-1)),
            ("VOL +", lambda: self.change_volume(1)),
            ("BLUETOOTH", self.toggle_bluetooth),
        ]

        for i, (label, command) in enumerate(buttons):
            tk.Button(controls, text=label, width=14, height=2, command=command).grid(
                row=i // 3, column=i % 3, padx=5, pady=5
            )

        self.feedback = tk.Label(
            self.root,
            text="",
            font=("Arial", 12),
            bg="#ffffff",
            wraplength=650,
            height=3,
        )

        self.feedback.pack(fill="x", padx=25, pady=10)

    # -----------------------------------
    # KEYBOARD CONTROLS
    # -----------------------------------

    def bind_keys(self):
        for dot in range(1, 7):
            self.root.bind(str(dot), lambda event, d=dot: self.toggle_dot(d))

        self.root.bind("<Up>", lambda event: self.dial_up())

        self.root.bind("<Down>", lambda event: self.dial_down())

        self.root.bind("<Return>", lambda event: self.select())

        self.root.bind("<Escape>", lambda event: self.back())

        self.root.bind("<space>", lambda event: self.clear_dots())

        self.root.bind("h", lambda event: self.hint())

        self.root.bind("m", lambda event: self.microphone())

        self.root.bind("r", lambda event: self.open_reader())

        self.root.bind("b", lambda event: self.toggle_bluetooth())

        self.root.bind("<plus>", lambda event: self.change_volume(1))

        self.root.bind("<minus>", lambda event: self.change_volume(-1))

    # -----------------------------------
    # BRAILLE DOT INTERACTION
    # -----------------------------------

    def toggle_dot(self, dot):
        """Raise or lower a Braille dot."""
        if self.mode == "reader":
            return

        if dot in self.dots:
            self.dots.remove(dot)
        else:
            self.dots.add(dot)

        self.update_dots()

    def update_dots(self):
        """Update visual appearance of dots."""
        for dot, button in self.dot_buttons.items():
            if dot in self.dots:
                button.configure(bg="#3678c8", fg="white", relief="raised")
            else:
                button.configure(bg="#ffffff", fg="black", relief="flat")

    def clear_dots(self):
        """Clear all raised Braille dots."""
        if self.mode == "reader":
            return

        self.dots.clear()
        self.update_dots()

    # -----------------------------------
    # AUDIO AND HAPTIC SIMULATION
    # -----------------------------------

    def feedback_message(self, audio, vibration="None"):
        """Show simulated audio and vibration."""
        self.feedback.configure(text=(f"AUDIO: {audio}\n" f"HAPTIC: {vibration}"))

    # -----------------------------------
    # DISPLAY CURRENT DEVICE STATE
    # -----------------------------------

    def update_display(self):
        connection = "Connected" if self.bluetooth else "Disconnected"

        self.status.configure(
            text=(
                f"Battery: {self.battery}%  |  "
                f"Bluetooth: {connection}  |  "
                f"Volume: {self.volume}"
            )
        )

        if self.mode == "menu":
            name = LESSONS[self.menu_index]["name"]

            self.instruction.configure(
                text=(
                    "LESSON MENU\n" f"> {name}\n" "Turn dial to browse. Press Select."
                )
            )

        elif self.mode == "lesson":
            questions = LESSONS[self.lesson_index]["letters"]

            target = questions[self.question_index]

            self.instruction.configure(
                text=(
                    f"LESSON: "
                    f"{LESSONS[self.lesson_index]['name']}\n"
                    f"Make the Braille letter: {target}\n"
                    "Press Select to check."
                )
            )

        elif self.mode == "reader":
            letter = BOOK_TEXT[self.book_index]

            self.instruction.configure(
                text=(
                    "E-READER MODE\n"
                    f"Current letter: {letter}\n"
                    "Turn dial to move through text."
                )
            )

        self.update_dots()

    # -----------------------------------
    # ROTARY DIAL
    # -----------------------------------

    def dial_up(self):
        """Simulate rotating dial upward."""
        if self.mode == "menu":
            self.menu_index = (self.menu_index - 1) % len(LESSONS)

        elif self.mode == "reader":
            self.book_index = max(0, self.book_index - 1)
            self.show_reader_letter()

        self.update_display()

    def dial_down(self):
        """Simulate rotating dial downward."""
        if self.mode == "menu":
            self.menu_index = (self.menu_index + 1) % len(LESSONS)

        elif self.mode == "reader":
            self.book_index = min(len(BOOK_TEXT) - 1, self.book_index + 1)
            self.show_reader_letter()

        self.update_display()

    # -----------------------------------
    # LESSON INTERACTION
    # -----------------------------------

    def select(self):
        """Select a lesson or check an answer."""
        if self.mode == "menu":
            self.lesson_index = self.menu_index
            self.question_index = 0
            self.attempts = 0
            self.mode = "lesson"

            self.clear_dots()

            self.feedback_message("Lesson started. Make the requested letter.")

        elif self.mode == "lesson":
            self.check_answer()

        self.update_display()

    def check_answer(self):
        """Check the user's Braille answer."""
        questions = LESSONS[self.lesson_index]["letters"]

        target = questions[self.question_index]
        correct_dots = get_braille(target)

        if self.dots == correct_dots:
            self.feedback_message("Correct! Great job!", "Short vibration")

            self.question_index += 1
            self.attempts = 0
            self.clear_dots()

            if self.question_index >= len(questions):
                self.mode = "menu"

                self.feedback_message("Lesson complete!", "Two short vibrations")

        else:
            self.attempts += 1

            if self.attempts >= 3:
                self.feedback_message(
                    f"The correct dots for {target} " f"are {sorted(correct_dots)}.",
                    "Long vibration",
                )

                self.attempts = 0

            else:
                self.feedback_message("Not quite. Try again.", "Short vibration")

    def hint(self):
        """Give a simple lesson hint."""
        if self.mode == "lesson":
            questions = LESSONS[self.lesson_index]["letters"]

            target = questions[self.question_index]
            dots = get_braille(target)

            self.feedback_message(f"Hint: {target} uses " f"{len(dots)} raised dots.")
        else:
            self.feedback_message("Start a lesson to request a hint.")

    # -----------------------------------
    # MICROPHONE SIMULATION
    # -----------------------------------

    def microphone(self):
        """Simulate speech recognition using typing."""
        answer = simpledialog.askstring(
            "Microphone Simulation", "Type what the user says:", parent=self.root
        )

        if not answer:
            return

        answer = answer.strip().upper()

        if self.mode == "lesson":
            questions = LESSONS[self.lesson_index]["letters"]

            target = questions[self.question_index]

            if answer == target:
                self.dots = get_braille(target)
                self.check_answer()
                self.update_display()
            else:
                self.feedback_message(
                    f"Speech recognized: {answer}. " "Incorrect answer.",
                    "Short vibration",
                )
        else:
            self.feedback_message(f"Speech recognized: {answer}")

    # -----------------------------------
    # E-READER SIMULATION
    # -----------------------------------

    def open_reader(self):
        """Open the sample e-reader."""
        self.mode = "reader"
        self.book_index = 0

        self.show_reader_letter()

        self.feedback_message("E-reader opened.")

        self.update_display()

    def show_reader_letter(self):
        """Show the current e-reader character."""
        letter = BOOK_TEXT[self.book_index]
        self.dots = get_braille(letter)
        self.update_dots()

    # -----------------------------------
    # OTHER PHYSICAL CONTROLS
    # -----------------------------------

    def back(self):
        """Return to the lesson menu."""
        self.mode = "menu"
        self.clear_dots()

        self.feedback_message("Returned to lesson menu.")

        self.update_display()

    def change_volume(self, amount):
        """Adjust simulated audio volume."""
        self.volume = max(0, min(10, self.volume + amount))

        self.feedback_message(f"Volume set to {self.volume}.")

        self.update_display()

    def toggle_bluetooth(self):
        """Simulate Bluetooth connection."""
        self.bluetooth = not self.bluetooth

        self.feedback_message(
            "Bluetooth connected." if self.bluetooth else "Bluetooth disconnected."
        )

        self.update_display()
