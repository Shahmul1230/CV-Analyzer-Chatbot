# CV-Analyzer-Chatbot

An AI-powered CV Assistant that helps users improve their CV, check ATS-focused suggestions, match CV with job descriptions, prepare cover letters, improve LinkedIn profiles, and get interview preparation guidance.

## Live Website

Visit the deployed project here:

[CV Analyzer Chatbot Live Demo](https://cv-analyzer-chatbot-1.onrender.com/)

## Features

1. AI-powered CV improvement suggestions
2. ATS-focused CV analysis
3. PDF and DOCX CV upload support
4. Job description matching guidance
5. Cover letter and LinkedIn profile improvement help
6. Interview preparation support
7. Clean chat widget UI
8. FastAPI backend with frontend served from the same Render service

## Tech Stack

Frontend:
HTML, CSS, JavaScript

Backend:
FastAPI, Python, LangChain, LangGraph, Groq API

Deployment:
Render Web Service

## Project Structure

```text
CV-Analyzer-Chatbot/
├── backend/
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── requirements.txt
└── README.md
```

## How to Run Locally

1. Clone the repository

```bash
git clone https://github.com/Shahmul1230/CV-Analyzer-Chatbot.git
```

2. Go to the project folder

```bash
cd CV-Analyzer-Chatbot
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add your API key

```env
GROQ_API_KEY=your_groq_api_key
```

5. Run the project

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

6. Open in browser

```text
http://localhost:8000/
```

## Deployment

This project is deployed on Render as a single Web Service.

Render Start Command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

## Author

Developed by Shahmul Islam
