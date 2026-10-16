import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from spellchecker import SpellChecker

model_name = "j-hartmann/emotion-english-distilroberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

spell = SpellChecker()

sentences = [
    "I am angry and frustrated by work.",
    "I am ngry and frustated by work.",
    "I am not happy today.",
    "I am furious about what happened.",
    "I am scared about my exams.",
    "I feel completely hopeless and sad.",
    "I can't believe it, this is amazing!",
    "I had pizza for lunch.",
    "i am loving the day today"
]

label_map = {
    "anger": "Anger",
    "disgust": "Disgust",
    "fear": "Fear",
    "joy": "Joy",
    "neutral": "Neutral",
    "sadness": "Sadness",
    "surprise": "Surprise"
}

for s in sentences:
    # Generic spell normalization on unknown words
    words = s.split()
    corrected_words = []
    for w in words:
        clean = "".join(c for c in w if c.isalpha())
        if clean and clean.lower() not in spell:
            corr = spell.correction(clean.lower())
            corrected_words.append(corr if corr else w)
        else:
            corrected_words.append(w)
    norm_text = " ".join(corrected_words)

    inputs = tokenizer(norm_text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = F.softmax(logits, dim=-1)[0].tolist()

    dist = {label_map[model.config.id2label[i]]: round(probs[i], 4) for i in range(len(probs))}
    top_emo = max(dist, key=dist.get)
    top_conf = dist[top_emo]
    print(f"Input: \"{s}\"")
    print(f"  -> Top: {top_emo} ({top_conf*100:.1f}%) | Dist: {dist}\n")
