# Day 3

# Easy Part

transactions = [5, 10, 40, 30]

print(transactions)

transactions.append(40)

print(transactions)

# Medium Part

transactions[2] = 20

print(transactions)

transactions.pop(1)

print(transactions)

transactions.insert(3, 67)

print(transactions)

for i in transactions:
    print(i)

# Hard Part

operation = {
    "type": "Knet",
    "amount": 20
}

print(operation)

for type,amount in operation.items():
    print(f"The type is {type}\nThe amount is {amount}")

# Bonus Part

for i in range(len(transactions)):
    print(f"Transaction {i + 1}: {transactions[i]}")

tally = 0
for i in range(len(transactions)):
    tally += 1

print(f"Total Transactions: {tally}")