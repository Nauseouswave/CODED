# loan calculator

# Easy Part

income = float(input("What's your income? "))

expenses = float(input("What are your expenses? "))

dti = expenses / income

savings = income - expenses

print(f"""Your DTI is: {dti:.2f}
Your savings are: {savings:.2f}""")

if dti < 0.35:
    print("Eligible for a loan.")

else:
    print("Not eligible for a loan.")

# Medium Part

if dti < 0.3 or income > expenses:
    print("It's looking great!")
elif income < expenses and dti < 0.35:
    print("Financial status is good.")
else:
    print("You need to improve your financial situation.. :(")

# Hard Part

def calculate_dti(income, expenses=0):
    return 300 / income

def assess_status(dti):
    if dti < 0.3:
        return "Low Risk"
    elif dti >= 0.3 and dti <= 0.45:
        return "Medium Risk"
    elif dti > 0.45:
        return "High Risk"

print(f"Your DTI is: {calculate_dti(income, expenses):.2f}")
print(f"Your risk status is: {assess_status(calculate_dti(income, expenses))}")

# Bonus Part

# 1. Used 300 instead of expenses
# 2. Rounded the numbers to 2 decimal places