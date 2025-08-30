# Day 1: Input, Variables, and Data Types, this is a simple program that takes user info and displays it back.

# Easy Section

userName = input("Enter your name: ")

print("Hello " + userName)

# Medium Section

age = int(input("Enter your age: "))

degree = input("Enter your degree: ")

print(f"Your age # {age}")

print(f"Your degree is {degree}")

# Hard Section

favoriteFood = input("Enter your favorite food: ")

favoriteColor = input("Enter your favorite color: ")

print(f"Hello, your name is {userName}, you're {age} years old, you study {degree}, your favorite food is {favoriteFood}, and most likely you wear {favoriteColor}.")

# Bonus Section

summary = f"""
Hello, your name is {userName}, 
you're {age} years old, you study {degree}, 
your favorite food is {favoriteFood}, 
and most likely you wear {favoriteColor}.
"""

print(summary)
