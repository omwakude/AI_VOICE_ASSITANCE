# chatbot/intent_model.py
import os
import subprocess
import pandas as pd
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

# -----------------------------
# Setup logging
# -----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# -----------------------------
# Load commands and intents
# -----------------------------
csv_path = os.path.join(os.path.dirname(__file__), "commands.csv")
df = pd.read_csv(csv_path)
df['command'] = df['command'].str.strip()
df['intent'] = df['intent'].str.strip()

commands = df['command'].tolist()
labels = df['intent'].tolist()
command_to_intent = dict(zip(commands, labels))

# -----------------------------
# Train Random Forest classifier
# -----------------------------
rf = RandomForestClassifier(n_estimators=500, random_state=42)
model_clf = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('rf', rf)
])
model_clf.fit(commands, labels)
logging.info(f"Intent model trained: {len(commands)} commands and {len(set(labels))} intents.")

# -----------------------------
# Local command mapping
# -----------------------------
LOCAL_COMMANDS = {
    "open_notepad": "notepad.exe",
    "music_play": ["start", "wmplayer"],
    "open_calc": "calc.exe",
    "open_cmd": "start cmd",
    "open_powershell": "start powershell",
    "paint": "mspaint",
    "snipping_tool": "start ms-screenclip:",
    "explorer": "explorer.exe"
}

# -----------------------------
# Execute command
# -----------------------------
def execute_command(spoken_text: str) -> str:
    try:
        # Predict intent using Random Forest
        predicted_intent = model_clf.predict([spoken_text])[0].strip()
        confidence = 1.0
        if hasattr(model_clf.named_steps['rf'], "predict_proba"):
            predicted_probs = model_clf.predict_proba([spoken_text])[0]
            predicted_intent = model_clf.classes_[predicted_probs.argmax()]
            confidence = predicted_probs.max()

        logging.info(f"Random Forest predicted: '{predicted_intent}' with confidence {confidence:.2f}")

        if confidence >= 0.52:  # Only execute if high confidence
            command = LOCAL_COMMANDS.get(predicted_intent)
            if command:
                if isinstance(command, list):
                    subprocess.Popen(command, shell=True)
                else:
                    os.system(command)
                logging.info(f"Executed local command: '{predicted_intent}'")
                return f"Executed local command: '{predicted_intent}'."
        
        return f"Command not recognized or confidence too low ({confidence:.2f})."
    
    except Exception as e:
        logging.error(f"Execution error: {e}")
        return f"Error processing command: {e}"
