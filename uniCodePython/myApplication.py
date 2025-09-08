import streamlit as st

st.title("Money Management App")

st.header("Money Manager")
st.subheader("Track your expenses and income easily")

st.write("Welcome to the Money Management App! Here you can track your expenses and income effortlessly.")

st.divider()

name = st.text_input("Enter your name:")

operation = st.selectbox("Deposit or Withdraw:", ["Deposit", "Withdraw"])

amount = st.number_input("Enter amount:", min_value=0)

pos = st.selectbox("Type of Payment:", ["Apple Pay", "Knet", "Cash", "Credit Card"])

st.divider()

if st.button("Submit"):
    st.divider()
    if operation == "Deposit":
        st.success("Transaction recorded successfully!")
    else:
        st.error("Transaction recorded successfully!")
    st.write(f"Hello {name}, you have chosen to {operation}.")
    st.write(f"Amount: {amount}")
    st.write(f"Payment Method: {pos}")
    st.balloons()

st.logo("kfhLogo.png")