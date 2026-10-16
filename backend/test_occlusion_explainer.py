import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "j-hartmann/emotion-english-distilroberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

def explain_prediction(text, top_label_idx):
    words = text.split()
    if len(words) <= 1:
        return []
    
    # Baseline prob
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        base_prob = F.softmax(model(**inputs).logits, dim=-1)[0, top_label_idx].item()
    
    signals = []
    # Test removing each word
    stopwords = {"i", "am", "a", "an", "the", "and", "or", "to", "of", "in", "it", "is", "my", "by", "for"}
    for i, word in enumerate(words):
        clean_word = "".join(c for c in word if c.isalnum())
        if clean_word.lower() in stopwords:
            continue
        occluded = " ".join([w for j, w in enumerate(words) if j != i])
        occ_inputs = tokenizer(occluded, return_tensors="pt", truncation=True)
        with torch.no_grad():
            occ_prob = F.softmax(model(**occ_inputs).logits, dim=-1)[0, top_label_idx].item()
        drop = max(0.0, base_prob - occ_prob)
        signals.append({"word": clean_word, "drop": drop})
    
    signals.sort(key=lambda x: x["drop"], reverse=True)
    # Normalize weights
    max_drop = max([s["drop"] for s in signals], default=1.0)
    for s in signals:
        s["weight"] = round(s["drop"] / max_drop, 2) if max_drop > 0 else 0.5
    return signals[:4]

test_s = "I am angry and frustrated by work."
inputs = tokenizer(test_s, return_tensors="pt")
with torch.no_grad():
    logits = model(**inputs).logits
    top_idx = torch.argmax(logits, dim=-1).item()

print("Occlusion explanation for:", test_s)
print("Top emotion:", model.config.id2label[top_idx])
print("Attributed signals:", explain_prediction(test_s, top_idx))
