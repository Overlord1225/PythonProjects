import random

words = '''python java javascript c++ c# object programming machine learning
           data structure algorithm artificial intelligence internet computer
           technology network security datatype variable function class language
           string list tuple set dictionary integer float boolean array hangmanian'''.split()

def main():
    print("Welcome to Hangman!")
    secret_word = random.choice(words)
    guessed_letters = set()
    remaining_letters = len(secret_word)
    max_attempts = 7
    wrong_attempts = 0

    # Show initial blanks
    print(" ".join("_" for _ in secret_word))
    print()

    while remaining_letters > 0 and wrong_attempts < max_attempts:
        guess = input("Guess a letter: ").lower().strip()

        # Input validation
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter.")
            continue

        if guess in guessed_letters:
            print("You already guessed that letter. Try again.")
            continue

        guessed_letters.add(guess)

        if guess in secret_word:
            count = secret_word.count(guess)
            remaining_letters -= count
            print("Good guess!")
        else:
            wrong_attempts += 1
            print(f"Wrong guess! {max_attempts - wrong_attempts} attempts left.")

        # Show current word state
        display = [letter if letter in guessed_letters else "_" for letter in secret_word]
        print(" ".join(display))
        print()

    if remaining_letters == 0:
        print("Congratulations! You've guessed the word:", secret_word)
    else:
        print("You lost! The word was:", secret_word)

if __name__ == "__main__":
    main()