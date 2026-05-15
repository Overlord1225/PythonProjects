import random

print("Welcome to the Number Guessing Game!")

number_to_guess = random.randint(1, 100)
attempts = 7

while attempts > 0:
    guess = int(input("Enter your guess (between 1 and 100): "))
    
    if guess < number_to_guess:
        print("Too low! Try again.")
    elif guess > number_to_guess:
        print("Too high! Try again.")
    else:
        print(f"Congratulations! You've guessed the number {number_to_guess} correctly!")
        break
    
    attempts -= 1
    if attempts == 0:
        print(f"Game Over! The number was {number_to_guess}.")
    print(f"You have {attempts} attempts left.")
     