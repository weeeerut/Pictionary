import tkinter as tk
import random
from tkinter import messagebox

class PictionaryApp:
    def __init__(self, root):
        # Initialize the app with root window
        self.root = root
        self.root.title("Pictionary - Draw N Guess")
        
        # Game settings
        self.time_limit = 10
        self.file_path = "words.txt"
        self.words = self.getWords(self.file_path)
        self.word = self.pickWord(self.words)

        # UI setup and event binding
        self.setup_ui()
        self.bind_events()

        # Start the timer
        self.root.after(1000, self.update_timer)

        # Drawing settings
        self.selected_color_button = None
        self.pen_color = "black"
        self.thickness = 1
        self.paths = []  # To store drawing paths
        self.current_path = []  # Current drawing path

    # ------------------------------ UI SETUP ------------------------------
    def setup_ui(self):
        # Set up the user interface with all buttons, canvas, and input fields
        # Drawing frame
        self.draw_frame = tk.Frame(self.root)
        self.draw_frame.grid(row=0, column=0, padx=10, pady=10)

        # Guess frame
        self.guess_frame = tk.Frame(self.root)
        self.guess_frame.grid(row=0, column=1, padx=10, pady=10)

        # Guess input box
        self.guess_box = tk.Entry(self.guess_frame)
        self.guess_box.grid(row=1,column=0, sticky="w")

        # Guess prompt label
        self.guess_label = tk.Label(self.guess_frame, text="Enter your guess: ")
        self.guess_label.grid(row=0,column=0, sticky="w")

        # Chat log to display guesses
        self.chat_log = tk.Text(self.guess_frame, width=30, height=30, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_log.grid(row=4, column=0, pady=10)

        # Result label (correct/incorrect)
        self.result_label = tk.Label(self.guess_frame, text="")
        self.result_label.grid(row=3, column=0, sticky="w")

        # Timer display
        self.time_label = tk.Label(self.draw_frame, text=str(self.time_limit))
        self.time_label.grid(row=0, column=0, sticky="w")

        # Word display (the word being drawn)
        self.wordLabel = tk.Label(self.draw_frame, text=self.word.capitalize(), fg="#000000")
        self.wordLabel.grid(row=0, column=1, sticky="e")

        # Drawing canvas
        self.canvas = tk.Canvas(self.draw_frame, width=500, height=500, bg="white")
        self.canvas.grid(row=1, column=0, columnspan=2, pady=10)

        # Instructions
        self.instructions = tk.Label(self.draw_frame, text="Left click to draw | Right click to erase | Press 'C' to clear")
        self.instructions.grid(row=2, column=0, columnspan=2, pady=10)

        # Color selection frame
        self.color_frame = tk.Frame(self.draw_frame)
        self.color_frame.grid(row=3, column=0, columnspan=2)

        # Color buttons (red, blue, etc.)
        colors = ["black", "red", "blue", "green", "purple", "orange"]
        for color in colors:
            btn = tk.Button(self.color_frame, bg=color, width=2)
            btn.config(command=lambda c=color, b=btn: self.set_pen_color(c, b))
            btn.pack(side="left", padx=2)

        # Thickness slider
        self.color_slider = tk.Scale(self.root, from_=1, to=10, orient=tk.HORIZONTAL, command=self.changeThickness)
        self.color_slider.set(3)
        self.color_slider.grid(row=1, column=1)

        # Undo button
        self.undo_button = tk.Button(self.draw_frame, text="Undo", command=self.undo)
        self.undo_button.grid(row=4, column=0, columnspan=2, pady=10)

    def bind_events(self):
        # Bind the drawing and interaction events to canvas and buttons
        # Mouse events for drawing and erasing
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.finish_draw)
        self.canvas.bind("<ButtonPress-3>", self.start_erase)
        self.canvas.bind("<B3-Motion>", self.erase)
        self.canvas.bind("<ButtonRelease-3>", self.finish_erase)

        # Clear canvas with 'C' key
        self.root.bind("<c>", self.clear_canvas)

        # Change cursor appearance on canvas hover
        self.canvas.bind("<Enter>", lambda e: self.canvas.config(cursor="plus"))
        self.canvas.bind("<Leave>", lambda e: self.canvas.config(cursor=""))

        # Guess submission with Enter key
        self.guess_box.bind("<Return>", lambda event: self.submitGuess())

    # ------------------------------ GAME LOGIC ------------------------------
    def submitGuess(self):
        # Submit the user's guess and check if it's correct
        text = self.guess_box.get()
        
        if text:
            self.update_chat_log(f"Guess: {text}")
        
        if text.lower().strip() == self.word:
            self.result_label.config(text="Correct!")
        else:
            self.result_label.config(text="Incorrect.")

    def update_chat_log(self, message):
        # Update the chat log with a new guess
        self.chat_log.config(state=tk.NORMAL)  # Allow editing the chat log
        self.chat_log.insert(tk.END, message + "\n")  # Add the new guess at the end
        self.chat_log.config(state=tk.DISABLED)  # Disable editing again

    # ------------------------------ DRAWING FUNCTIONS ------------------------------
    def start_draw(self, event):
        # Initialize the drawing process
        self.current_path = []
        self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        # Draw a line on the canvas as the mouse moves
        line = self.canvas.create_line(
            self.last_x, self.last_y, event.x, event.y,
            fill=self.pen_color, width=self.thickness, capstyle=tk.ROUND, smooth=tk.TRUE
        )
        self.current_path.append(line)
        self.last_x, self.last_y = event.x, event.y

    def finish_draw(self, event):
        # Finish the current drawing path
        if self.current_path:
            self.paths.append(self.current_path)
        self.current_path = []

    def start_erase(self, event):
        # Start erasing the drawing when the right mouse button is pressed
        self.current_path = []
        self.last_x, self.last_y = event.x, event.y

    def changeThickness(self, val):
        # Update the drawing pen thickness
        self.thickness = int(val)

    def set_pen_color(self, color, btn=None):
        # Change the pen color based on user selection
        self.pen_color = color

        if self.selected_color_button:
            self.selected_color_button.config(relief="raised", bd=1)

        if btn:
            btn.config(relief="sunken", bd=3)
            self.selected_color_button = btn

    def erase(self, event):
        # Erase the drawing by creating white lines over the previous ones
        line = self.canvas.create_line(
            self.last_x, self.last_y, event.x, event.y,
            fill="white", width=10, capstyle=tk.ROUND, smooth=tk.TRUE
        )
        self.current_path.append(line)
        self.last_x, self.last_y = event.x, event.y

    def finish_erase(self, event):
        # Finish the erase operation
        if self.current_path:
            self.paths.append(self.current_path)
        self.current_path = []

    def undo(self):
        # Undo the last drawing path if possible
        if self.paths:
            last_path = self.paths.pop()  # Remove the most recent path
            for line in last_path:
                self.canvas.delete(line)  # Delete each line in the path

    def clear_canvas(self, event=None):
        # Clear the canvas
        self.canvas.delete("all")

    # ------------------------------ TIMER FUNCTIONS ------------------------------
    def update_timer(self):
        #Update the game timer every second.
        if self.time_limit > 0:
            self.time_limit -= 1
            self.time_label.config(text=str(self.time_limit))
            self.root.after(1000, self.update_timer)  # Call every second
        else:
            self.result_label.config(text="Time's up!")
            self.guess_box.config(state=tk.DISABLED)  # Disable guessing after time's up
            messagebox.showinfo("Time's Up!", "You didn't guess the word in time.")  # Show messagebox

    # ------------------------------ UTILITY FUNCTIONS ------------------------------
    def getWords(self, file):
        # Load words from a file
        with open(file) as f:
            words = f.readlines()
        return words

    def pickWord(self, words):
        # Pick a random word from the list
        return random.choice(words).strip()

# Set up the application window
root = tk.Tk()

# Initialize the Pictionary app without networking or image handling
app = PictionaryApp(root)

# Run the main loop of the app
root.mainloop()
