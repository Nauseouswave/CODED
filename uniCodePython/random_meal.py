import requests
from transformers import pipeline

response = requests.get("https://www.themealdb.com/api/json/v1/1/random.php")

meal = response.json()

print(meal["meals"][0]["strMeal"])

emotion_classifier = pipeline(
    "text-classification", 
    model="j-hartmann/emotion-english-distilroberta-base"
    )

user_feeling = input("How are you feeling today? (in English): ")

result = emotion_classifier(user_feeling)
emotion = result[0]["label"]

print(f"Your emotion is: {emotion}")

emotion_food_dict = {
    "joy": "Pizza",
    "sadness": "Ice Cream", 
    "anger": "Spicy Curry"
}

if emotion == "joy":
    print("Great! You're happy!")
    print(f"Suggested meal: {emotion_food_dict['joy']}")
elif emotion == "sadness":
    print("Cheer up!")
    print(f"Suggested meal: {emotion_food_dict['sadness']}")
elif emotion == "anger":
    print("Calm down!")
    print(f"Suggested meal: {emotion_food_dict['anger']}")
else:
    print(f"""You're feeling {emotion}
    Here's a random meal for you!
    Suggested meal: {meal['meals'][0]['strMeal']}""")