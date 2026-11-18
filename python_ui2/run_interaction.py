from braille_ui import Event, Input, build_sim_device

HELP = """
OAT LAB UI - INTERACTIVE SIMULATOR

Commands:

f             Forward button
b             Backward button
m             Microphone / select button
say <text>    Simulate spoken answer
v <0-100>     Volume slider
d <number>    Rotate dial
?             Show help
q             Quit
"""


def main():
    dev = build_sim_device()
    print(HELP)

    last_trace = 0

    while True:
        # Print new device feedback.
        for kind, message in dev.trace[last_trace:]:
            print(f"[{kind}] {message}")

        last_trace = len(dev.trace)

        try:
            line = input(f"\n[{dev.mode.name}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not line:
            continue

        command, _, argument = line.partition(" ")
        command = command.lower()

        try:
            if command == "q":
                break

            elif command == "?":
                print(HELP)

            elif command == "f":
                dev.handle(Event(Input.FORWARD))

            elif command == "b":
                dev.handle(Event(Input.BACKWARD))

            elif command == "m":
                dev.handle(Event(Input.MIC))

            elif command == "say":
                dev.handle(Event(Input.SPEECH, payload=argument))

            elif command == "v":
                dev.handle(Event(Input.SLIDER, int(argument)))

            elif command == "d":
                dev.handle(Event(Input.DIAL, int(argument)))

            else:
                print("Unknown command. Type ? for help.")

        except ValueError:
            print("Enter a valid number.")


if __name__ == "__main__":
    main()
