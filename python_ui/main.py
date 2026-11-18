import tkinter as tk
from simulator import BrailleSimulator

root = tk.Tk()
root.title("OAT Lab UI - Braille Simulator")

app = BrailleSimulator(root)

root.mainloop()
