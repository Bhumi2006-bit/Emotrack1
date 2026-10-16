# backend/ml/models/emotion_model.py
"""
Calibrated Multi-Model 7-Class Emotion Classifier
Supports:
1. "ensemble": Validation-tuned weighted ensemble of RoBERTa+1D CNN (1.2), BERT-base (1.2), and DistilRoBERTa (0.8).
2. "roberta_cnn": Local fine-tuned RoBERTa + 1D CNN architecture.
3. "distilroberta": Zero-shot DistilRoBERTa baseline.

Includes robust graceful fallback to DistilRoBERTa if local weights are not accessible.
Features:
- PyTorch inference loaded ONCE at startup.
- Temperature scaling (T=1.15) for calibrated probability distributions.
- Information-theoretic Shannon entropy for uncertainty quantification (0.0 = certain, 1.0 = maximum ambiguity).
- Ambiguity margin detection (margin between Top-1 and Top-2 emotions).
- Sarcasm/indirect expression sensitivity markers.
- Model-agnostic label probability calculation for occlusion explainability.
- 100% backward-compatible return dictionary.
"""

import os
import re
import math
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

# Generic spelling normalization
try:
    from spellchecker import SpellChecker
    _spell = SpellChecker()
except ImportError:
    _spell = None

ALL_CLASSES = ["Anger", "Disgust", "Fear", "Joy", "Neutral", "Sadness", "Surprise"]
LABEL_MAP = {
    "anger": "Anger",
    "disgust": "Disgust",
    "fear": "Fear",
    "joy": "Joy",
    "neutral": "Neutral",
    "sadness": "Sadness",
    "surprise": "Surprise"
}
LABEL_TO_ID = {l: i for i, l in enumerate(ALL_CLASSES)}
ID_TO_LABEL = {i: l for i, l in enumerate(ALL_CLASSES)}
MAX_ENTROPY_7 = math.log2(7.0)  # ~2.80735 bits

_candidate_dirs = [
    Path("backend/research/goemotions_ekman_experiment/models_track_b"),
    Path(__file__).resolve().parent.parent.parent / "research" / "goemotions_ekman_experiment" / "models_track_b",
    Path("research/goemotions_ekman_experiment/models_track_b"),
]
BASE_CHECKPOINT_DIR = next((d for d in _candidate_dirs if d.exists()), _candidate_dirs[0])


class RobertaCNNClassifier(nn.Module):
    """
    Fine-Tuned RoBERTa with 1D Convolutional feature extractor and global max pooling.
    Trained on GoEmotions-Ekman Track B (Leakage-Controlled).
    """
    def __init__(self, model_name: str = "roberta-base", num_classes: int = 7, cnn_filters: int = 256, kernel_size: int = 3, dropout_rate: float = 0.2):
        super().__init__()
        self.roberta = AutoModel.from_pretrained(model_name)
        hidden_size = self.roberta.config.hidden_size
        self.conv1d = nn.Conv1d(
            in_channels=hidden_size,
            out_channels=cnn_filters,
            kernel_size=kernel_size,
            padding=kernel_size // 2
        )
        self.relu = nn.ReLU()
        self.global_pool = nn.AdaptiveMaxPool1d(1)
        self.dropout = nn.Dropout(dropout_rate)
        self.classifier = nn.Linear(cnn_filters, num_classes)

    def forward(self, input_ids, attention_mask):
        roberta_output = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        x = roberta_output.last_hidden_state.permute(0, 2, 1)  # (batch, hidden_dim, seq_len)
        x = self.conv1d(x)
        x = self.relu(x)
        x = self.global_pool(x).squeeze(-1)
        x = self.dropout(x)
        return self.classifier(x)


class TransformerEmotionClassifier:
    """
    Configurable Emotion Classifier supporting Ensemble, RoBERTa-CNN, and DistilRoBERTa
    with automatic graceful fallback.
    """
    def __init__(self, backend: Optional[str] = None, temperature: float = 1.25):
        self.temperature = temperature
        self.backend = (backend or os.environ.get("EMOTION_BACKEND", "ensemble")).lower().strip()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.fallback_active = False

        # DistilRoBERTa baseline model & tokenizer (always kept as guaranteed fallback)
        self.distil_tokenizer = None
        self.distil_model = None

        # RoBERTa + CNN model & tokenizer
        self.roberta_tokenizer = None
        self.roberta_model = None

        # BERT-base model & tokenizer
        self.bert_tokenizer = None
        self.bert_model = None

        # Ensemble weights tuned strictly on validation.csv (soft-voting)
        self.ensemble_weights = {
            "roberta": 1.0,
            "bert": 1.4,
            "distil": 0.8
        }

        self._initialize_backend()

    def _load_distilroberta(self) -> bool:
        try:
            name = "j-hartmann/emotion-english-distilroberta-base"
            logger.info(f"[EmotionModel] Loading DistilRoBERTa baseline: {name}...")
            self.distil_tokenizer = AutoTokenizer.from_pretrained(name)
            self.distil_model = AutoModelForSequenceClassification.from_pretrained(name)
            self.distil_model.to(self.device)
            self.distil_model.eval()
            return True
        except Exception as e:
            logger.error(f"[EmotionModel] Failed to load DistilRoBERTa: {e}")
            return False

    def _load_roberta_cnn(self) -> bool:
        try:
            ckpt_path = BASE_CHECKPOINT_DIR / "roberta_cnn" / "best_model.pt"
            if not ckpt_path.exists():
                logger.warning(f"[EmotionModel] Checkpoint not found at {ckpt_path}")
                return False
            logger.info(f"[EmotionModel] Loading RoBERTa+CNN from {ckpt_path}...")
            self.roberta_tokenizer = AutoTokenizer.from_pretrained("roberta-base")
            self.roberta_model = RobertaCNNClassifier(model_name="roberta-base", num_classes=7)
            state_dict = torch.load(ckpt_path, map_location=self.device)
            self.roberta_model.load_state_dict(state_dict)
            self.roberta_model.to(self.device)
            self.roberta_model.eval()
            return True
        except Exception as e:
            logger.warning(f"[EmotionModel] Could not load RoBERTa+CNN: {e}")
            return False

    def _load_bert_base(self) -> bool:
        try:
            ckpt_path = BASE_CHECKPOINT_DIR / "bert_base" / "best_model.pt"
            if not ckpt_path.exists():
                logger.warning(f"[EmotionModel] Checkpoint not found at {ckpt_path}")
                return False
            logger.info(f"[EmotionModel] Loading BERT-base from {ckpt_path}...")
            self.bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            self.bert_model = AutoModelForSequenceClassification.from_pretrained(
                "bert-base-uncased",
                num_labels=7,
                id2label=ID_TO_LABEL,
                label2id=LABEL_TO_ID
            )
            state_dict = torch.load(ckpt_path, map_location=self.device)
            self.bert_model.load_state_dict(state_dict)
            self.bert_model.to(self.device)
            self.bert_model.eval()
            return True
        except Exception as e:
            logger.warning(f"[EmotionModel] Could not load BERT-base: {e}")
            return False

    def _initialize_backend(self):
        """Initializes requested backend with graceful fallback."""
        success = False
        if self.backend == "ensemble":
            r_ok = self._load_roberta_cnn()
            b_ok = self._load_bert_base()
            d_ok = self._load_distilroberta()
            if r_ok and b_ok and d_ok:
                success = True
                self.active_backend = "ensemble"
                self.model_name = "Validation-Tuned Weighted Ensemble (RoBERTa 1.0 + BERT 1.4 + DistilRoBERTa 0.8, Soft-Voting)"
                print(f"[EmotionModel] Successfully loaded Weighted Ensemble backend.")
            else:
                logger.warning("[EmotionModel] One or more ensemble models failed to load. Falling back to DistilRoBERTa baseline.")
        elif self.backend == "roberta_cnn":
            if self._load_roberta_cnn():
                success = True
                self.active_backend = "roberta_cnn"
                self.model_name = "Fine-Tuned RoBERTa + 1D CNN (GoEmotions-Ekman Track B)"
                print(f"[EmotionModel] Successfully loaded RoBERTa+CNN backend.")

        # Fallback handling
        if not success:
            if not self.distil_model:
                self._load_distilroberta()
            self.active_backend = "distilroberta"
            self.fallback_active = (self.backend != "distilroberta")
            self.model_name = "j-hartmann/emotion-english-distilroberta-base"
            if self.fallback_active:
                print(f"[EmotionModel] Active fallback enabled -> using {self.model_name}.")
            else:
                print(f"[EmotionModel] Successfully loaded DistilRoBERTa baseline.")

        # Compatibility references for legacy tools
        if self.distil_model is not None:
            self.model = self.distil_model
            self.tokenizer = self.distil_tokenizer
        elif self.roberta_model is not None:
            self.model = self.roberta_model
            self.tokenizer = self.roberta_tokenizer
        else:
            self.model = self.bert_model
            self.tokenizer = self.bert_tokenizer
        self.is_loaded = True

    def normalize_spelling(self, text: str) -> str:
        """Domain-agnostic spelling correction for out-of-vocabulary typos."""
        if not _spell:
            return text
        words = text.split()
        corrected = []
        for w in words:
            clean = re.sub(r'[^a-zA-Z]', '', w)
            if clean and len(clean) > 2 and clean.lower() not in _spell:
                candidate = _spell.correction(clean.lower())
                if candidate:
                    corrected.append(w.lower().replace(clean.lower(), candidate))
                    continue
            corrected.append(w)
        return " ".join(corrected)

    def _infer_distil(self, text: str) -> Dict[str, float]:
        inputs = self.distil_tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        with torch.no_grad():
            logits = self.distil_model(**inputs).logits
            probs = F.softmax(logits / self.temperature, dim=-1)[0].tolist()
        dist = {}
        for idx, p in enumerate(probs):
            raw = self.distil_model.config.id2label.get(idx, str(idx)).lower()
            app_label = LABEL_MAP.get(raw, raw.capitalize())
            dist[app_label] = p
        return dist

    def _infer_roberta_cnn(self, text: str) -> Dict[str, float]:
        inputs = self.roberta_tokenizer(text, return_tensors="pt", truncation=True, max_length=128).to(self.device)
        with torch.no_grad():
            logits = self.roberta_model(inputs["input_ids"], inputs["attention_mask"])
            probs = F.softmax(logits / self.temperature, dim=-1)[0].tolist()
        return {ID_TO_LABEL[i]: p for i, p in enumerate(probs)}

    def _infer_bert_base(self, text: str) -> Dict[str, float]:
        inputs = self.bert_tokenizer(text, return_tensors="pt", truncation=True, max_length=128).to(self.device)
        with torch.no_grad():
            logits = self.bert_model(**inputs).logits
            probs = F.softmax(logits / self.temperature, dim=-1)[0].tolist()
        return {ID_TO_LABEL[i]: p for i, p in enumerate(probs)}

    def get_label_probability(self, text: str, target_label: str) -> float:
        """
        Model-agnostic evaluation of the probability for target_label.
        Used by occlusion explainability.
        """
        cleaned_text = (text or "").strip()
        if not cleaned_text:
            return round(1.0 / 7.0, 4)
        target_norm = LABEL_MAP.get(target_label.lower(), target_label.capitalize())

        if self.active_backend == "ensemble" and not self.fallback_active:
            r_dist = self._infer_roberta_cnn(cleaned_text)
            b_dist = self._infer_bert_base(cleaned_text)
            d_dist = self._infer_distil(cleaned_text)
            w_r = self.ensemble_weights["roberta"]
            w_b = self.ensemble_weights["bert"]
            w_d = self.ensemble_weights["distil"]
            total_w = w_r + w_b + w_d
            p = (w_r * r_dist.get(target_norm, 0.0) + w_b * b_dist.get(target_norm, 0.0) + w_d * d_dist.get(target_norm, 0.0)) / total_w
            return float(p)
        elif self.active_backend == "roberta_cnn" and not self.fallback_active:
            r_dist = self._infer_roberta_cnn(cleaned_text)
            return float(r_dist.get(target_norm, 0.0))
        else:
            d_dist = self._infer_distil(cleaned_text)
            return float(d_dist.get(target_norm, 0.0))

    def predict(self, text: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs tokenization, model inference, temperature-scaled softmax,
        and information-theoretic uncertainty estimation.
        """
        cleaned_text = (text or "").strip()
        if not cleaned_text:
            return {
                "primary_emotion": "Neutral",
                "confidence": 0.50,
                "secondary_emotion": "Joy",
                "secondary_confidence": 0.20,
                "margin": 0.30,
                "uncertainty_score": 0.85,
                "is_ambiguous": True,
                "distribution": {c: round(1.0 / 7.0, 4) for c in ALL_CLASSES},
                "normalized_text": None,
                "model_name": self.model_name,
                "backend_type": self.active_backend,
                "fallback_active": self.fallback_active
            }

        eval_text = f"{context.strip()} {cleaned_text}" if context and context.strip() else cleaned_text
        normalized_text = self.normalize_spelling(eval_text)

        # Compute distribution based on active backend
        if self.active_backend == "ensemble" and not self.fallback_active:
            r_dist = self._infer_roberta_cnn(normalized_text)
            b_dist = self._infer_bert_base(normalized_text)
            d_dist = self._infer_distil(normalized_text)
            w_r = self.ensemble_weights["roberta"]
            w_b = self.ensemble_weights["bert"]
            w_d = self.ensemble_weights["distil"]
            total_w = w_r + w_b + w_d
            raw_distribution = {
                c: (w_r * r_dist.get(c, 0.0) + w_b * b_dist.get(c, 0.0) + w_d * d_dist.get(c, 0.0)) / total_w
                for c in ALL_CLASSES
            }
        elif self.active_backend == "roberta_cnn" and not self.fallback_active:
            raw_distribution = self._infer_roberta_cnn(normalized_text)
        else:
            raw_distribution = self._infer_distil(normalized_text)

        # Normalize across 7 classes
        total_p = sum(raw_distribution.get(c, 0.0) for c in ALL_CLASSES) or 1.0
        distribution = {c: round(raw_distribution.get(c, 0.0) / total_p, 4) for c in ALL_CLASSES}

        # Sort for primary and secondary
        sorted_emotions = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        primary_emotion, confidence = sorted_emotions[0]
        secondary_emotion, secondary_confidence = sorted_emotions[1]

        # Calculate Shannon entropy (uncertainty in [0, 1])
        entropy = 0.0
        for p in distribution.values():
            if p > 1e-6:
                entropy -= p * math.log2(p)
        uncertainty_score = round(min(1.0, max(0.0, entropy / MAX_ENTROPY_7)), 4)

        # Ambiguity detection: margin between top-1 and top-2 is small (< 0.15) or high entropy
        margin = round(confidence - secondary_confidence, 4)
        is_ambiguous = bool(margin < 0.15 or uncertainty_score >= 0.70)

        # Detect potential sarcasm / mixed signals in text
        lower_raw = cleaned_text.lower()
        sarcasm_cues = ["actually", "sarcastic", "sarcasm", "went wrong", "ruined", "yeah right", "hate my life", "terrible day"]
        has_sarcasm_cue = any(cue in lower_raw for cue in sarcasm_cues)
        if has_sarcasm_cue and primary_emotion in ["Joy", "Neutral"]:
            is_ambiguous = True

        return {
            "primary_emotion": primary_emotion,
            "confidence": round(confidence, 4),
            "secondary_emotion": secondary_emotion,
            "secondary_confidence": round(secondary_confidence, 4),
            "margin": margin,
            "uncertainty_score": uncertainty_score,
            "is_ambiguous": is_ambiguous,
            "distribution": distribution,
            "normalized_text": normalized_text if normalized_text != cleaned_text else None,
            "model_name": self.model_name,
            "backend_type": self.active_backend,
            "fallback_active": self.fallback_active
        }


# Global singleton
emotion_classifier = TransformerEmotionClassifier()
