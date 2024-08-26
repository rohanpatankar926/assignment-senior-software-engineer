# README

## Overview
This FastAPI application provides two main functionalities: **Text-to-Speech (TTS)** and **Speech-to-Text (STT)** using OpenAI and Deepgram services. The app is designed to convert text to speech and stream the audio, as well as convert audio received via WebSocket to text in real-time.

## Features
- **Text-to-Speech (TTS)**
  - Converts text input into speech using OpenAI's TTS service.
  - Streams audio in real-time.

- **Speech-to-Text (STT)**
  - Receives audio data through WebSocket.
  - Converts received audio to text using Deepgram's STT service.

## Dependencies
- FastAPI
- Uvicorn
- OpenAI Python client
- Loguru for logging
- Deepgram Python SDK
- Python `dotenv` for environment variables management

## Setup

1. **Install Required Packages:**
   ```bash
   pip install fastapi uvicorn openai loguru deepgram-python python-dotenv
Environment Variables:
Create a .env file in the project directory and add your API keys:
makefile
Copy code
OPENAI_API_KEY=<your-openai-api-key>
DEEPGRAM_API_KEY=<your-deepgram-api-key>
TOKEN_HEADER=<your-secure-token>
Running the Application
```
To start the FastAPI server, run the following command:

bash
Copy code
uvicorn main:app --port 8080 --host 0.0.0.0 --workers 3
API Endpoints

1. Text-to-Speech (TTS)
Endpoint: /tts
Method: GET
Query Parameters:
text: Text to convert to speech.
Headers:
Authorization: Bearer token required.
Response: Streams the generated speech as an audio file.
2. Speech-to-Text (STT)
Endpoint: /ws/stt
Method: WebSocket
Functionality: Converts streamed audio to text in real-time.

## Security

Authentication: The application uses HTTP Bearer Token authentication for securing the /tts endpoint.
Logging

Logs are managed using Loguru, providing detailed logs for debugging and monitoring purposes.
Error Handling

Comprehensive error handling is implemented to manage HTTP exceptions and WebSocket disconnections gracefully.
