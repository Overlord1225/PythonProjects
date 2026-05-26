import time
import random
import json
import os
from texts import sample_texts

SCORE_FILE = "highscores.json"

def load_scores():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    return {"wpm": 0, "acc": 0.0}

def save_scores(scores):
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f)

def run_test():
    original = random.choice(sample_texts)
    print("\nType this:\n" + original + "\n")
    input("Press Enter to start...")
    start = time.time()
    typed = input("\n> ")
    elapsed = time.time() - start

    # WPM
    words = len(original.split())
    wpm = round(words / (elapsed / 60)) if elapsed > 0 else 0

    # Accuracy
    total_chars = max(len(original), len(typed))
    correct = sum(1 for i, c in enumerate(typed) if i < len(original) and c == original[i])
    acc = round((correct / total_chars) * 100, 2)

    print(f"\nWPM: {wpm} | Accuracy: {acc}% | Time: {elapsed:.1f}s")
    return wpm, acc

def main():
    scores = load_scores()
    while True:
        wpm, acc = run_test()
        updated = False
        if wpm > scores["wpm"]:
            scores["wpm"] = wpm
            updated = True
        if acc > scores["acc"]:
            scores["acc"] = acc
            updated = True
        if updated:
            save_scores(scores)
            print("✨ New high score! ✨")
        print(f"Best so far: {scores['wpm']} WPM / {scores['acc']}% accuracy")
        if input("\nPlay again? (y/n): ").lower() != "y":
            break
    print("Keep practicing!")

if __name__ == "__main__":
    main()