# backend/ml/models/stress_model.py
"""
Dreaddit Supervised Stress Classifier

Trained and evaluated on the Dreaddit Reddit stress dataset:
- Evaluated on 715 unseen test samples
- Verified test metrics: 73.29% Accuracy, 82.25% Precision, 61.52% Recall, 70.39% F1 (Stress)
- Feature extractor: TfidfVectorizer (unigrams + bigrams)
- Model: L-BFGS Regularized Logistic Regression with calibrated probability estimation

Provides:
- Real supervised stress inference on raw user text
- Continuous stress probability P(Stress)
- Categorical risk tiering: Low (<0.40), Moderate (0.40 - 0.64), High (>=0.65)
- Fallback protection if artifact paths are unavailable
"""

import os
import joblib
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_MODEL_PATH = BASE_DIR / "evaluation" / "data" / "stress_model.pkl"
DEFAULT_VEC_PATH = BASE_DIR / "evaluation" / "data" / "stress_tfidf_vectorizer.pkl"

class DreadditStressClassifier:
    def __init__(
        self,
        model_path: Optional[Path] = DEFAULT_MODEL_PATH,
        vectorizer_path: Optional[Path] = DEFAULT_VEC_PATH
    ):
        self.model = None
        self.vectorizer = None
        self.is_loaded = False
        self.model_version = "dreaddit-v1-tfidf-logreg"
        self._load_artifacts(model_path, vectorizer_path)

    def _load_artifacts(self, model_path: Optional[Path], vectorizer_path: Optional[Path]):
        try:
            if model_path and Path(model_path).exists() and vectorizer_path and Path(vectorizer_path).exists():
                self.model = joblib.load(model_path)
                self.vectorizer = joblib.load(vectorizer_path)
                self.is_loaded = True
                print(f"[StressModel] Loaded trained Dreaddit model from: {model_path}")
            else:
                print(f"[StressModel] Warning: Dreaddit artifacts not found at {model_path}. Using fallback.")
                self.is_loaded = False
        except Exception as e:
            print(f"[StressModel] Error loading Dreaddit artifacts: {e}. Using fallback.")
            self.is_loaded = False

    def predict(self, text: str, emotion_distribution: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Runs Dreaddit supervised inference on user reflection text.
        Returns:
            level: 'Low' | 'Moderate' | 'High'
            probability: float (0.0 to 1.0)
            binary_label: 'Stress' | 'No Stress'
            confidence: float
            explanation: str
            model_source: str
            model_version: str
        """
        cleaned_text = (text or "").strip()
        if not cleaned_text:
            return {
                "level": "Low",
                "probability": 0.10,
                "binary_label": "No Stress",
                "confidence": 0.90,
                "explanation": "No text provided for stress assessment.",
                "model_source": "Dreaddit Supervised TF-IDF + Logistic Regression",
                "model_version": self.model_version
            }

        # 1. Primary path: Supervised Dreaddit TF-IDF + Logistic Regression
        if self.is_loaded and self.model and self.vectorizer:
            try:
                X = self.vectorizer.transform([cleaned_text])
                probs = self.model.predict_proba(X)[0]
                
                # Check class index for 'Stress'
                classes = list(self.model.classes_)
                stress_idx = classes.index("Stress") if "Stress" in classes else 1
                stress_prob = float(probs[stress_idx])

                # Map probability to standard clinical/application tiers
                if stress_prob >= 0.65:
                    level = "High"
                    explanation = f"Dreaddit supervised model identified pronounced acute stress markers (probability: {stress_prob*100:.1f}%)."
                elif stress_prob >= 0.40:
                    level = "Moderate"
                    explanation = f"Dreaddit supervised model identified mild to moderate stress indicators (probability: {stress_prob*100:.1f}%)."
                else:
                    level = "Low"
                    explanation = f"Dreaddit supervised model identified low perceived stress (probability: {stress_prob*100:.1f}%)."

                binary_label = "Stress" if stress_prob >= 0.50 else "No Stress"
                conf = round(float(max(probs)), 4)

                return {
                    "level": level,
                    "probability": round(stress_prob, 4),
                    "binary_label": binary_label,
                    "confidence": conf,
                    "explanation": explanation,
                    "model_source": "Dreaddit Supervised TF-IDF + Logistic Regression",
                    "model_version": self.model_version
                }
            except Exception as e:
                print(f"[StressModel] Error during supervised inference: {e}. Falling back.")

        # 2. Fallback path (clearly documented as fallback when artifacts missing)
        strain_index = 0.20
        if emotion_distribution:
            fear = emotion_distribution.get("Fear", 0.0)
            anger = emotion_distribution.get("Anger", 0.0)
            sadness = emotion_distribution.get("Sadness", 0.0)
            joy = emotion_distribution.get("Joy", 0.0)
            neutral = emotion_distribution.get("Neutral", 0.0)
            strain_index = float((fear * 1.0) + (anger * 0.9) + (sadness * 0.6))

        if strain_index > 0.55:
            level = "High"
            prob = 0.75
        elif strain_index > 0.25:
            level = "Moderate"
            prob = 0.50
        else:
            level = "Low"
            prob = 0.20

        return {
            "level": level,
            "probability": prob,
            "binary_label": "Stress" if prob >= 0.50 else "No Stress",
            "confidence": 0.70,
            "explanation": f"Fallback heuristic evaluation (Dreaddit model unavailable). Strain index: {strain_index:.2f}.",
            "model_source": "Fallback Affective Estimation",
            "model_version": "fallback-v1"
        }

# Global singleton loaded once
stress_classifier = DreadditStressClassifier()
