import tkinter as tk
import random

# Map choices to emojis
emoji_map = {
    "Rock": "✊",
    "Paper": "📄",
    "Scissors": "✂️"
}

def play(player_choice):
    global player_score, computer_score

    computer_choice = random.choice(moves)
    # Display computer choice with emoji
    computer_label.config(text=f"Computer chose: {emoji_map[computer_choice]} {computer_choice}")

    # Determine winner
    if player_choice == computer_choice:
        result = "It's a Tie! 🤝"
        color = "orange"
    elif (player_choice == "Rock" and computer_choice == "Scissors") or \
         (player_choice == "Paper" and computer_choice == "Rock") or \
         (player_choice == "Scissors" and computer_choice == "Paper"):
        result = "You Win! 🎉"
        color = "green"
        player_score += 1
    else:
        result = "You Lose! 😢"
        color = "red"
        computer_score += 1

    # Show player's choice with emoji as well
    result_label.config(text=f"{emoji_map[player_choice]} {result}", fg=color)
    update_scores()

def update_scores():
    player_score_label.config(text=f"You: {player_score}")
    computer_score_label.config(text=f"Computer: {computer_score}")

def reset_scores():
    global player_score, computer_score
    player_score = 0
    computer_score = 0
    update_scores()
    computer_label.config(text="Computer chose: ")
    result_label.config(text="")

# Main window
root = tk.Tk()
root.title("Rock Paper Scissors")
root.geometry("400x350")
root.resizable(False, False)

# Game state
player_score = 0
computer_score = 0
moves = ["Rock", "Paper", "Scissors"]

# GUI widgets
instruction = tk.Label(root, text="Choose your move:", font=("Arial", 14))
instruction.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Buttons with emojis
rock_btn = tk.Button(button_frame, text="✊ Rock", width=10, command=lambda: play("Rock"))
rock_btn.grid(row=0, column=0, padx=5)

paper_btn = tk.Button(button_frame, text="📄 Paper", width=10, command=lambda: play("Paper"))
paper_btn.grid(row=0, column=1, padx=5)

scissors_btn = tk.Button(button_frame, text="✂️ Scissors", width=10, command=lambda: play("Scissors"))
scissors_btn.grid(row=0, column=2, padx=5)

computer_label = tk.Label(root, text="Computer chose: ", font=("Arial", 12))
computer_label.pack(pady=5)

result_label = tk.Label(root, text="", font=("Arial", 16, "bold"))
result_label.pack(pady=5)

score_frame = tk.Frame(root)
score_frame.pack(pady=10)

player_score_label = tk.Label(score_frame, text="You: 0", font=("Arial", 12))
player_score_label.grid(row=0, column=0, padx=20)

computer_score_label = tk.Label(score_frame, text="Computer: 0", font=("Arial", 12))
computer_score_label.grid(row=0, column=1, padx=20)

reset_btn = tk.Button(root, text="Reset Scores", width=15, command=reset_scores)
reset_btn.pack(pady=10)

root.mainloop()