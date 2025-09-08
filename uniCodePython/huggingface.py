from transformers import pipeline

classifier = pipeline(
    "text-classification", 
    model="j-hartmann/emotion-english-distilroberta-base"
    )

sentence = "I am scared of spiders."

result = classifier(sentence)
print(result)