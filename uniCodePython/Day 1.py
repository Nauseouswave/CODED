# Day 1: Input, Variables, and Data Types, this is a simple program that takes user input and displays it back.

userName = input("Enter your name: ")

print("Hello " + userName)

age = int(input("Enter your age: "))

degree = input("Enter your degree: ")

print(f"Your age # {age}")

print(f"Your degree is {degree}")

favoriteFood = input("Enter your favorite food: ")

favoriteColor = input("Enter your favorite color: ")

summary = f"""
Hello, your name is {userName}, 
you're {age} years old, you study {degree}, 
your favorite food is {favoriteFood}, 
and most likely you wear {favoriteColor}.
"""

print(summary)
