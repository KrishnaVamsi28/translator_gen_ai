# 🌐 Scalable AI Translation System with Adaptive Engine Selection

### 📌 Overview

This project is a multilingual translation system built using Gemini API (Primary Engine) and LibreTranslate (Fallback Engine).
It is designed to ensure high availability, fault tolerance, and automated failover in case of API rate limits or service failure.

The system integrates automation logic to maintain uninterrupted translation functionality under constrained conditions.

---

### 🚀 Features

🔹 AI-based translation using Gemini API

🔹 Automatic fallback to LibreTranslate

🔹 Intelligent engine selection mechanism

🔹 API rate-limit monitoring

🔹 Graceful degradation under service limits

🔹 Translation history tracking

🔹 TXT file upload support

🔹 Download translated output

🔹 Real-time dashboard (Streamlit UI)

---

### 🏗 System Architecture

The system follows a modular architecture:

User Interface Layer (Streamlit Dashboard)

Translation Controller (Decision Layer)

Rate Limit Monitoring Module

Primary Engine – Gemini API

Secondary Engine – LibreTranslate

Logging and Response Processing Module

The Translation Controller automatically selects the appropriate engine based on availability and usage limits.

---

### 🛠 Technologies Used

Python

Streamlit

Google Generative AI (Gemini API)

LibreTranslate REST API

Requests Library

dotenv

---

### ⚙ Installation & Setup

1️⃣ Clone the Repository

git clone <repository-link>

cd project-folder

2️⃣ Create Virtual Environment

python -m venv myenv

myenv\Scripts\activate   # Windows

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Add Gemini API Key

Create a .env file:

GOOGLE_API_KEY=your_api_key_here

5️⃣ Run the Application

streamlit run app.py

---

### 🔄 Failover Mechanism

The system uses Gemini API as the primary translation engine.
If any of the following conditions occur:

API rate limit exceeded

Network failure

Service unavailability

The system automatically switches to LibreTranslate to maintain operational continuity.

---

### 📊 Rate Limit Monitoring

The system tracks API usage and prevents abrupt failures by:

Counting translation requests

Checking predefined usage thresholds

Triggering fallback when limits are reached

---

### 🎯 Project Objectives

Develop a multilingual translation system

Implement intelligent failover

Ensure fault tolerance

Monitor API usage limits

Maintain operational continuity

Design modular automation-oriented architecture

---
