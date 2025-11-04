import tkinter as tk
from tkinter import messagebox
import random

# -----------------------------
# Global Variables
# -----------------------------
current_player = "X"
board = [" " for _ in range(9)]
buttons = []
scoreboard = {"X": 0, "O": 0, "Computer": 0, "Draws": 0}
vs_computer = True  # default mode

# -----------------------------
# Game Functions
# -----------------------------
def check_winner():
    """Return 'X', 'O', 'Draw', or None."""
    win_conditions = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
        (0, 4, 8), (2, 4, 6)              # diagonals
    ]
    for a, b, c in win_conditions:
        if board[a] == board[b] == board[c] != " ":
            return board[a]

    if " " not in board:
        return "Draw"
    return None


def handle_click(index):
    """Handle when a button is clicked."""
    global current_player

    if board[index] != " ":
        return  # ignore click on filled cell

    board[index] = current_player
    buttons[index].config(text=current_player, state="disabled")

    winner = check_winner()

    if winner:
        end_game(winner)
        return

    # Switch player
    current_player = "O" if current_player == "X" else "X"
    status_label.config(text=f"Player {current_player}'s turn")

    if vs_computer and current_player == "O":
        root.after(700, computer_move)  # delay AI move for natural effect


def computer_move():
    """Simple random AI move."""
    global current_player

    empty_positions = [i for i, val in enumerate(board) if val == " "]
    if not empty_positions:
        return

    move = random.choice(empty_positions)
    board[move] = "O"
    buttons[move].config(text="O", state="disabled")

    winner = check_winner()
    if winner:
        end_game(winner)
    else:
        current_player = "X"
        status_label.config(text=f"Player {current_player}'s turn")


def end_game(winner):
    """Handle game end and update scoreboard."""
    if winner == "Draw":
        messagebox.showinfo("Game Over", "It's a Draw 🤝")
        scoreboard["Draws"] += 1
    elif vs_computer and winner == "O":
        messagebox.showinfo("Game Over", "🤖 Computer Wins!")
        scoreboard["Computer"] += 1
    else:
        messagebox.showinfo("Game Over", f"🎉 Player {winner} Wins!")
        scoreboard[winner] += 1

    update_scoreboard()
    reset_board()


def reset_board():
    """Reset board for next game."""
    global board, current_player
    board = [" " for _ in range(9)]
    current_player = "X"
    status_label.config(text="Player X's turn")
    for button in buttons:
        button.config(text=" ", state="normal")


def update_scoreboard():
    """Update scoreboard labels."""
    score_label.config(
        text=f"X: {scoreboard['X']}   O: {scoreboard['O']}   🤖: {scoreboard['Computer']}   Draws: {scoreboard['Draws']}"
    )


def toggle_mode():
    """Switch between 2-player and computer mode."""
    global vs_computer
    vs_computer = not vs_computer
    mode_button.config(
        text="Mode: Vs Computer" if vs_computer else "Mode: 2 Players"
    )
    reset_board()


# -----------------------------
# UI Setup
# -----------------------------
root = tk.Tk()
root.title("Tic Tac Toe 🎮")
root.geometry("340x460")
root.resizable(False, False)
root.configure(bg="#f8f9fa")

title_label = tk.Label(root, text="Tic Tac Toe", font=("Poppins", 22, "bold"), bg="#f8f9fa", fg="#333")
title_label.pack(pady=10)

status_label = tk.Label(root, text="Player X's turn", font=("Poppins", 14), bg="#f8f9fa", fg="#555")
status_label.pack(pady=5)

# Create game board (3x3 buttons)
frame = tk.Frame(root, bg="#f8f9fa")
frame.pack(pady=10)

for i in range(9):
    btn = tk.Button(
        frame,
        text=" ",
        font=("Poppins", 18, "bold"),
        width=5,
        height=2,
        bg="#ffffff",
        fg="#333",
        relief="ridge",
        bd=2,
        command=lambda i=i: handle_click(i)
    )
    btn.grid(row=i//3, column=i%3, padx=5, pady=5)
    buttons.append(btn)

# Scoreboard display
score_label = tk.Label(root, text="", font=("Poppins", 12, "bold"), bg="#f8f9fa", fg="#444")
score_label.pack(pady=10)
update_scoreboard()

# Buttons for reset and mode
btn_frame = tk.Frame(root, bg="#f8f9fa")
btn_frame.pack(pady=10)

reset_button = tk.Button(btn_frame, text="🔄 Reset", font=("Poppins", 12, "bold"),
                         bg="#4CAF50", fg="white", width=10, command=reset_board)
reset_button.grid(row=0, column=0, padx=10)

mode_button = tk.Button(btn_frame, text="Mode: Vs Computer", font=("Poppins", 12, "bold"),
                        bg="#2196F3", fg="white", width=15, command=toggle_mode)
mode_button.grid(row=0, column=1, padx=10)

# Run the window
root.mainloop()
