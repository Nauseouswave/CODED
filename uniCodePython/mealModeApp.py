import streamlit as st
import requests
from transformers import pipeline

# إعداد الصفحة
st.title("🍽️ Meal Mood App")
st.write("Tell us how you're feeling, and we'll suggest a meal for you!")

# تحميل النموذج (مع التخزين المؤقت)
def load_emotion_model():
    return pipeline(
        "text-classification", 
        model="j-hartmann/emotion-english-distilroberta-base"
    )

def get_random_meal():
    response = requests.get("https://www.themealdb.com/api/json/v1/1/random.php")
    meal = response.json()
    return meal

emotion_food_dict = {
    "joy": "Pizza",
    "sadness": "Ice Cream", 
    "anger": "Spicy Curry"
}

emotion_classifier = load_emotion_model()
meal = get_random_meal()

st.subheader("Today's Random Meal:")
st.write(f"🍽️ {meal['meals'][0]['strMeal']}")

user_feeling = st.text_input("How are you feeling today? (in English):")

if user_feeling:
    result = emotion_classifier(user_feeling)
    emotion = result[0]["label"]
    
    st.subheader(f"Your emotion is: {emotion}")
    
    if emotion == "joy":
        st.success("Great! You're happy!")
        st.write(f"🍕 Suggested meal: {emotion_food_dict['joy']}")
    elif emotion == "sadness":
        st.info("Cheer up!")
        st.write(f"🍦 Suggested meal: {emotion_food_dict['sadness']}")
    elif emotion == "anger":
        st.warning("Calm down!")
        st.write(f"🌶️ Suggested meal: {emotion_food_dict['anger']}")
    else:
        st.write(f"You're feeling {emotion}")
        st.write("Here's a random meal for you!")
        st.write(f"🍽️ Suggested meal: {meal['meals'][0]['strMeal']}")
