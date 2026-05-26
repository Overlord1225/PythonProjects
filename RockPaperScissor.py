import random
from enum import Enum

class Move(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"

NUM_TO_MOVE = {
    "1": Move.ROCK,
    "2": Move.PAPER,
    "3": Move.SCISSORS,
}

def get_winner(player, computer):
    if player == computer:
        return "tie"
    if (player == Move.ROCK and computer == Move.SCISSORS) or \
       (player == Move.PAPER and computer == Move.ROCK) or \
       (player == Move.SCISSORS and computer == Move.PAPER):
        return "win"
    return "lose"

def get_user_move():
    while True:
        choice = input("Enter your choice (1=rock, 2=paper, 3=scissors) or 'q'/'quit' to exit: ").lower().strip()
        if choice in ("q", "quit"):
            return None
        if choice in NUM_TO_MOVE:
            return NUM_TO_MOVE[choice]
        print("Invalid choice. Please enter 1, 2, or 3.")

def ask_play_again():
    while True:
        answer = input("Play again? (yes/no/y/n): ").lower().strip()
        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n"):
            return False
        print("Please answer 'yes' or 'no'.")

def main():
    print("Welcome to Rock, Paper, Scissors!")
    scores = {"win": 0, "lose": 0, "tie": 0}

    while True:
        user_move = get_user_move()
        if user_move is None:
            print("Thanks for playing! Final scores:")
            break

        computer_move = random.choice(list(Move))
        print(f"Computer chose: {computer_move.value}")

        result = get_winner(user_move, computer_move)
        if result == "tie":
            print("It's a tie!")
        elif result == "win":
            print("You win!")
        else:
            print("You lose!")
        scores[result] += 1

        print(f"Scores → Wins: {scores['win']}, Losses: {scores['lose']}, Ties: {scores['tie']}")

        if not ask_play_again():
            print("Thanks for playing! Final scores:")
            break

    print(f"Wins: {scores['win']}, Losses: {scores['lose']}, Ties: {scores['tie']}")

if __name__ == "__main__":
    main()