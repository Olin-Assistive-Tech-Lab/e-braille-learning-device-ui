import tkinter as tk
from tkinter import ttk, simpledialog

from braille_ui import Event, Input, Mode, LessonState, build_sim_device, CELL_COUNT


class Simulator:
    def __init__(self, root):
        self.root = root
        self.dev = build_sim_device()

        self.root.title("OAT Lab UI - Device Simulator")
        self.root.geometry("1050x750")
        self.root.configure(bg="#e8edf2")

        self.build_interface()
        self.bind_keyboard()
        self.refresh()

    def build_interface(self):
        tk.Label(
            self.root, text="OAT LAB UI", font=("Arial", 26, "bold"), bg="#e8edf2"
        ).pack(pady=12)

        self.status = tk.Label(self.root, font=("Arial", 13), bg="#e8edf2")
        self.status.pack()

        self.description = tk.Label(
            self.root, font=("Arial", 15), bg="#e8edf2", wraplength=900
        )
        self.description.pack(pady=12)

        # Jumbo Braille display
        display = tk.Frame(self.root, bg="#d5dce5", padx=18, pady=22)
        display.pack(pady=12)

        self.dots = []

        for cell_index in range(CELL_COUNT):
            cell_frame = tk.Frame(display, bg="#d5dce5")
            cell_frame.grid(row=0, column=cell_index, padx=6)

            cell_dots = {}

            for dot in range(1, 7):
                row = (dot - 1) % 3
                col = 0 if dot <= 3 else 1

                dot_label = tk.Label(
                    cell_frame, text="●", font=("Arial", 19), width=2, bg="#d5dce5"
                )

                dot_label.grid(row=row, column=col, padx=1, pady=4)

                cell_dots[dot] = dot_label

            self.dots.append(cell_dots)

        # Device controls
        controls = tk.Frame(self.root, bg="#e8edf2")
        controls.pack(pady=18)

        buttons = [
            ("◀ BACKWARD (B)", self.backward),
            ("MIC / SELECT (M)", self.mic),
            ("FORWARD (F) ▶", self.forward),
            ("DIAL ◀ (←)", lambda: self.dial(-1)),
            ("DIAL ▶ (→)", lambda: self.dial(1)),
        ]

        for i, (name, action) in enumerate(buttons):
            tk.Button(controls, text=name, command=action, width=19, height=2).grid(
                row=i // 3, column=i % 3, padx=8, pady=8
            )

        # Volume slider
        volume_frame = tk.Frame(self.root, bg="#e8edf2")
        volume_frame.pack(pady=8)

        tk.Label(volume_frame, text="VOLUME", bg="#e8edf2").pack(side="left", padx=10)

        self.volume = ttk.Scale(
            volume_frame, from_=0, to=100, orient="horizontal", length=250
        )

        self.volume.set(50)
        self.volume.pack(side="left")

        tk.Button(volume_frame, text="SET", command=self.set_volume).pack(
            side="left", padx=10
        )

        # Simulated microphone response
        speech_frame = tk.Frame(self.root, bg="#e8edf2")
        speech_frame.pack(pady=8)

        tk.Button(speech_frame, text="TYPE SPOKEN ANSWER", command=self.speak).pack()

        # Audio and haptic feedback log
        tk.Label(
            self.root, text="DEVICE FEEDBACK", font=("Arial", 12, "bold"), bg="#e8edf2"
        ).pack(pady=(12, 4))

        self.log = tk.Text(self.root, height=9, width=95, state="disabled")
        self.log.pack(padx=20, pady=5)

        self.last_trace = 0

    def bind_keyboard(self):
        self.root.bind("f", lambda e: self.forward())
        self.root.bind("b", lambda e: self.backward())
        self.root.bind("m", lambda e: self.mic())
        self.root.bind("<Left>", lambda e: self.dial(-1))
        self.root.bind("<Right>", lambda e: self.dial(1))
        self.root.bind("<Return>", lambda e: self.speak())

    def send(self, event):
        self.dev.handle(event)
        self.refresh()

    def forward(self):
        self.send(Event(Input.FORWARD))

    def backward(self):
        self.send(Event(Input.BACKWARD))

    def mic(self):
        self.send(Event(Input.MIC))

    def dial(self, steps):
        self.send(Event(Input.DIAL, steps))

    def set_volume(self):
        value = int(float(self.volume.get()))
        self.send(Event(Input.SLIDER, value))

    def speak(self):
        if self.dev.mode != Mode.LESSON or self.dev.state != LessonState.LISTENING:
            self.dev.speak("Press MIC before speaking.")
            self.refresh()
            return

        answer = simpledialog.askstring(
            "Speech Input", "What did the learner say?", parent=self.root
        )

        if answer is not None:
            self.send(Event(Input.SPEECH, payload=answer))

    def refresh(self):
        self.status.configure(
            text=(f"MODE: {self.dev.mode.name}   |   " f"VOLUME: {self.dev.volume}%")
        )

        if self.dev.mode == Mode.MENU:
            _, title, _ = self.dev.menu[self.dev.selection]
            message = f"MENU: {title}\n" "Forward/Backward to browse. " "MIC to select."

        elif self.dev.mode == Mode.LESSON:
            message = (
                f"LESSON: {self.dev.lesson['title']}\n"
                f"Word {self.dev.word_index + 1} "
                f"of {len(self.dev.lesson['words'])}\n"
                "Feel the Braille and identify it."
            )

            if self.dev.listening:
                message += "\nMIC LISTENING..."

        else:
            message = (
                "E-READER\n"
                "Turn dial to scroll through text. "
                "BACKWARD returns to menu."
            )

        self.description.configure(text=message)

        # Render each six-dot Braille cell
        for i in range(CELL_COUNT):
            mask = self.dev.cells[i] if i < len(self.dev.cells) else 0

            for dot in range(1, 7):
                raised = bool(mask & (1 << (dot - 1)))

                self.dots[i][dot].configure(fg="#1769b3" if raised else "#b4bec8")

        # Add new feedback messages
        new_entries = self.dev.trace[self.last_trace :]
        self.last_trace = len(self.dev.trace)

        if new_entries:
            self.log.configure(state="normal")

            for kind, message in new_entries:
                self.log.insert("end", f"[{kind}] {message}\n")

            self.log.see("end")
            self.log.configure(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    Simulator(root)
    root.mainloop()
