# hangman_gui.py
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import string

# -----------------------------
# Config / Word list (editable)
# -----------------------------
WORDS = [
    "PYTHON", "DEVELOPER", "HANGMAN", "COMPUTER", "PROGRAMMING",
    "ALGORITHM", "FUNCTION", "VARIABLE", "STRUCTURE", "NETWORK",
    "DATABASE", "FRAMEWORK", "INTERFACE", "PACKAGE", "MODULE"
]
MAX_WRONG = 6  # number of allowed wrong guesses

# -----------------------------
# Hangman GUI application
# -----------------------------
class HangmanGame:
    def __init__(self, master):
        self.master = master
        master.title("Hangman — Tkinter Edition")
        master.resizable(False, False)

        # Game variables
        self.word = ""
        self.guessed = set()
        self.wrong = 0

        # Top frame: canvas + controls
        top = tk.Frame(master)
        top.pack(padx=10, pady=6)

        # Canvas for hangman drawing
        self.canvas = tk.Canvas(top, width=240, height=300, bg="white", highlightthickness=1, highlightbackground="#999")
        self.canvas.grid(row=0, column=0, rowspan=4, padx=(0,10))

        # Right side controls
        tk.Label(top, text="Word:", font=("Helvetica", 10, "bold")).grid(row=0, column=1, sticky="w")
        self.word_var = tk.StringVar(master)
        self.word_label = tk.Label(top, textvariable=self.word_var, font=("Consolas", 20))
        self.word_label.grid(row=1, column=1, sticky="w", pady=(0,10))

        self.status_var = tk.StringVar(master)
        self.status_label = tk.Label(top, textvariable=self.status_var, font=("Helvetica", 10))
        self.status_label.grid(row=2, column=1, sticky="w")

        # Add custom word entry + button
        add_frame = tk.Frame(top)
        add_frame.grid(row=3, column=1, sticky="w", pady=(8,0))
        self.new_word_entry = tk.Entry(add_frame, width=16)
        self.new_word_entry.grid(row=0, column=0)
        add_btn = tk.Button(add_frame, text="Add Word", command=self.add_word)
        add_btn.grid(row=0, column=1, padx=(6,0))

        # Middle frame: alphabet buttons
        mid = tk.Frame(master)
        mid.pack(padx=10)
        self.letter_buttons = {}
        row = 0
        col = 0
        for ch in string.ascii_uppercase:
            b = tk.Button(mid, text=ch, width=4, command=lambda c=ch: self.guess_letter(c))
            b.grid(row=row, column=col, padx=2, pady=2)
            self.letter_buttons[ch] = b
            col += 1
            if col >= 9:
                col = 0
                row += 1

        # Bottom frame: controls
        bottom = tk.Frame(master)
        bottom.pack(pady=8)
        new_btn = tk.Button(bottom, text="New Game", command=self.new_game)
        new_btn.grid(row=0, column=0, padx=6)
        hint_btn = tk.Button(bottom, text="Hint", command=self.show_hint)
        hint_btn.grid(row=0, column=1, padx=6)
        quit_btn = tk.Button(bottom, text="Quit", command=master.quit)
        quit_btn.grid(row=0, column=2, padx=6)

        # start
        self.new_game()

    # -----------------------------
    # Game control methods
    # -----------------------------
    def new_game(self):
        """Start a new game."""
        self.word = random.choice(WORDS).upper()
        self.guessed = set()
        self.wrong = 0
        self.update_display()
        self.status_var.set(f"Wrong: {self.wrong} / {MAX_WRONG}")
        # re-enable all alphabet buttons
        for b in self.letter_buttons.values():
            b.configure(state=tk.NORMAL)
        self.canvas.delete("all")
        self.draw_scaffold()

    def add_word(self):
        """Add a new word from entry to the word list."""
        w = self.new_word_entry.get().strip().upper()
        if not w.isalpha():
            messagebox.showwarning("Invalid", "Only letters are allowed.")
            return
        if w in WORDS:
            messagebox.showinfo("Info", f"'{w}' is already in the list.")
            return
        WORDS.append(w)
        self.new_word_entry.delete(0, tk.END)
        messagebox.showinfo("Added", f"Added '{w}' to the word list.")

    def show_hint(self):
        """Provide a simple hint: reveal one unguessed letter (costs one wrong guess)."""
        unguessed = [c for c in set(self.word) if c not in self.guessed]
        if not unguessed:
            messagebox.showinfo("Hint", "No hints available.")
            return
        choice = random.choice(unguessed)
        # reveal the letter (but count as a wrong guess to keep balance)
        self.guess_letter(choice, from_hint=True)

    # -----------------------------
    # Guess processing and display
    # -----------------------------
    def guess_letter(self, ch, from_hint=False):
        """Process a guessed letter."""
        ch = ch.upper()
        # disable the button (if it's a real click)
        if ch in self.letter_buttons:
            self.letter_buttons[ch].configure(state=tk.DISABLED)
        # If already guessed, ignore
        if ch in self.guessed:
            return
        self.guessed.add(ch)
        if ch in self.word:
            # correct guess
            self.update_display()
            if self.check_win():
                self.end_game(win=True)
        else:
            # wrong guess
            # if from hint, still counts as a wrong in this implementation
            self.wrong += 1
            self.status_var.set(f"Wrong: {self.wrong} / {MAX_WRONG}")
            self.draw_hangman_step(self.wrong)
            if self.wrong >= MAX_WRONG:
                self.end_game(win=False)

    def update_display(self):
        """Update the shown word with underscores and guessed letters."""
        display = " ".join([c if c in self.guessed else "_" for c in self.word])
        self.word_var.set(display)

    def check_win(self):
        """Return True if player guessed all letters."""
        return all(c in self.guessed for c in self.word)

    def end_game(self, win):
        """Handle end of game: show message and disable alphabet."""
        for b in self.letter_buttons.values():
            b.configure(state=tk.DISABLED)
        if win:
            self.status_var.set("You win! 🎉")
            messagebox.showinfo("Victory!", f"Congratulations — you guessed '{self.word}'!")
        else:
            self.status_var.set("You lost. 💀")
            # reveal the full word
            self.word_var.set(" ".join(self.word))
            messagebox.showinfo("Game Over", f"Out of guesses. The word was: {self.word}")

    # -----------------------------
    # Drawing the scaffold & hangman
    # -----------------------------
    def draw_scaffold(self):
        """Draw the static part of the gallows."""
        c = self.canvas
        # base
        c.create_line(20, 280, 200, 280, width=3)
        # vertical post
        c.create_line(60, 280, 60, 40, width=3)
        # horizontal beam
        c.create_line(60, 40, 150, 40, width=3)
        # short drop
        c.create_line(150, 40, 150, 70, width=3)

    def draw_hangman_step(self, step):
        """
        Draw hangman parts in order:
         1: head
         2: body
         3: left arm
         4: right arm
         5: left leg
         6: right leg
        """
        c = self.canvas
        if step == 1:
            # head (circle)
            c.create_oval(130, 70, 170, 110, width=2, tag="part")
        elif step == 2:
            # body
            c.create_line(150, 110, 150, 180, width=2, tag="part")
        elif step == 3:
            # left arm
            c.create_line(150, 120, 120, 150, width=2, tag="part")
        elif step == 4:
            # right arm
            c.create_line(150, 120, 180, 150, width=2, tag="part")
        elif step == 5:
            # left leg
            c.create_line(150, 180, 130, 230, width=2, tag="part")
        elif step == 6:
            # right leg
            c.create_line(150, 180, 170, 230, width=2, tag="part")
        else:
            # anything more: draw eyes / rope shake
            pass

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = HangmanGame(root)
    root.mainloop()
