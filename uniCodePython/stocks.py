import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('stock_prices.csv')

print(data.head())

print(data.tail())

X1 = data['Day']

Y1 = data['Price']

plt.plot(X1, Y1)

plt.title("Stock Prices Over 30 Days")

plt.xlabel("Day")
plt.ylabel("USD")

plt.show()

X2 = data['Day']

Y2 = data['Volume']

plt.bar(X2, Y2, color='green')

plt.title("Trading Volume Over 30 Days")

plt.xlabel("Day")
plt.ylabel("Volume")

plt.show()

total_volume = data['Volume'].sum()
print(f"Total trading volume over 30 days: {total_volume}")