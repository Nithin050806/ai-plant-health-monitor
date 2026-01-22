import streamlit as st
from roboflow import Roboflow
import cv2
import numpy as np
from PIL import Image
import os
import subprocess

# ============================
# 🔴 API KEY (ONLY ROBOFLOW)
# ============================
ROBOFLOW_API_KEY =  "LSQsyYZodgnRME8qs8Ex"

# ============================
# ROBOTFLOW SETUP
# ============================
rf = Roboflow(api_key=ROBOFLOW_API_KEY)
project = rf.workspace().project("ai-pest-detection-and-health-monitoring-kyl8o")
model = project.version(1).model   

# ============================
# PAGE CONFIG + BRANDING
# ============================
st.set_page_config(page_title="AI Plant Health Monitor", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #2ecc71;'>🌿 AI Pest Detection & Smart Treatment Advisor</h1>
    <h4 style='text-align: center; color: gray;'>Built by <b> HACK SYNDICATE.EXE </b> – <b>Powered by NIMBUZ CLOUD </b></h4>
    <hr>
""", unsafe_allow_html=True)

st.write("Detect plant diseases and get AI-powered treatment advice in English & Tamil.")

# ============================
# MODE SELECTOR
# ============================
mode = st.radio("Choose Input Mode:", ["📷 Webcam", "🖼️ Upload Image"])

# ============================
# 🧠 LOCAL AI — ENGLISH ADVICE
# ============================
def get_english_advice(disease_name):
    prompt = f"""
You are an agricultural expert.
The detected plant disease is: {disease_name}.

Provide:
1. Simple explanation
2. Causes
3. Recommended pesticide (with dosage)
4. Organic treatment
5. Prevention tips

Keep it farmer-friendly and concise.
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.stdout is None or result.stdout.strip() == "":
            return "⚠️ AI returned empty response. Try again."

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return """
⚠️ AI took too long.

Basic Advice:
* Remove infected leaves  
* Avoid overhead watering  
* Improve air circulation  
* Use recommended fungicide  
* Monitor daily  
"""

    except Exception as e:
        return "⚠️ Local AI error: " + str(e)


# ============================
# 🧠 LOCAL AI — FAST TAMIL TRANSLATION (NULL SAFE)
# ============================
def translate_to_tamil(english_text):
    prompt = f"Translate this into simple Tamil:\n{english_text}"

    try:
        result = subprocess.run(
            ["ollama", "run", "phi"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=45
        )

        if result.stdout is None or result.stdout.strip() == "":
            return "⚠️ தமிழில் மொழிபெயர்க்க முடியவில்லை. மீண்டும் முயற்சிக்கவும்."

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return "⚠️ மொழிபெயர்ப்பு நேரம் அதிகமாக எடுத்துக் கொண்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."

    except Exception as e:
        return "⚠️ Tamil translation error: " + str(e)


# ============================
# FUNCTION: RUN DETECTION
# ============================
def run_detection(image_np, temp_path):
    cv2.imwrite(temp_path, cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
    result = model.predict(temp_path, confidence=20, overlap=30).json()
    predictions = result.get("predictions", [])
    return predictions


# ============================
# WEBCAM MODE
# ============================
if mode == "📷 Webcam":
    st.info("Allow camera → Show leaf → Click capture → AI analyzes disease")

    camera_image = st.camera_input("📸 Take a picture")

    if camera_image is not None:
        image = Image.open(camera_image).convert("RGB")
        st.image(image, caption="Captured Image", width=500)

        img_np = np.array(image)
        temp_path = "webcam.jpg"

        with st.spinner("🔍 Detecting disease..."):
            predictions = run_detection(img_np, temp_path)

        if predictions:
            pred = predictions[0]
            disease_name = pred["class"]
            confidence = round(pred["confidence"] * 100, 2)

            st.success(f"🦠 Detected: {disease_name} ({confidence}%)")

            with st.spinner("🤖 Generating treatment advice..."):
                english_advice = get_english_advice(disease_name)

            with st.spinner("🌐 Translating to Tamil..."):
                tamil_advice = translate_to_tamil(english_advice)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("## 🇬🇧 English Advice")
                st.write(english_advice)

            with col2:
                st.markdown("## 🇮🇳 தமிழ் ஆலோசனை")
                st.write(tamil_advice)

        else:
            st.warning("⚠️ No disease detected. Leaf may be stressed or nutrient-deficient.")

        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============================
# UPLOAD IMAGE MODE
# ============================
else:
    uploaded_file = st.file_uploader("📤 Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", width=500)

        img_np = np.array(image)
        temp_path = "temp.jpg"

        with st.spinner("🔍 Detecting disease..."):
            predictions = run_detection(img_np, temp_path)

        if predictions:
            pred = predictions[0]
            disease_name = pred["class"]
            confidence = round(pred["confidence"] * 100, 2)

            st.success(f"🦠 Detected: {disease_name} ({confidence}%)")

            with st.spinner("🤖 Generating treatment advice..."):
                english_advice = get_english_advice(disease_name)

            with st.spinner("🌐 Translating to Tamil..."):
                tamil_advice = translate_to_tamil(english_advice)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("## 🇬🇧 English Advice")
                st.write(english_advice)

            with col2:
                st.markdown("## 🇮🇳 தமிழ் ஆலோசனை")
                st.write(tamil_advice)

        else:
            st.warning("⚠️ No disease detected. Leaf may be stressed or nutrient-deficient.")

        if os.path.exists(temp_path):
            os.remove(temp_path)