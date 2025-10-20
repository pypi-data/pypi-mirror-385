import random as r
from . import animation as a

def main():
    # List of words to choose from
    someWords = '''apple banana mango strawberry  
    orange grape pineapple apricot lemon coconut watermelon 
    cherry papaya berry peach lychee muskmelon'''

    # Choose a random word from the list
    someWords = someWords.split()
    word = someWords[r.randint(0, len(someWords)-1)]
    mylen = len(word)
    guessedword = ["_"] * mylen
    chances = 8

    # Print initial message
    print(f"Start guessing the word letter by letter \n You will get {chances} tries to find the word")

    # Print initial state of guessed word
    for i in range(mylen):
        print(guessedword[i], end=" ")
    print()

    playing, guessed = True, False                                

    while playing and chances != 0:
        guess = input("Enter your guess: ")
        correct, playing = False, False

        # Check if the guessed letter is correct
        for i in range(mylen):
            if guess == word[i]:
                guessedword[i] = guess
                print(guess, end=" ")
                correct = True
            else:
                print(guessedword[i], end=" ")
                playing = True

        if correct:
            print("\n\nGood Guess!")
        else:
            chances -= 1
            print(f"\n\nWrong Guess, {chances} left")
        a.hang_animation(chances)

        # Check if all letters have been guessed
        if "_" not in guessedword:
            guessed = True
            break

    if guessed:
        print(f"You have successfully guessed {word}")
    else:
        print(f"\n\nYou are out of Chances\n The Word was {word}")

if __name__ == '__main__':
    main()