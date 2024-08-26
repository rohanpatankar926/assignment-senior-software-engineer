import uvicorn
from fastapi.responses import StreamingResponse
import os
from builtins import str
from openai import OpenAI
from fastapi import FastAPI, Depends, HTTPException, status, WebSocketDisconnect, WebSocket
import os
from loguru import logger
from deep import Process_audio
from deepgram import DeepgramClientOptions, DeepgramClient
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import time
load_dotenv()

deepgram = DeepgramClient(
    api_key=os.getenv("DEEPGRAM_API_KEY"),
    config=DeepgramClientOptions(options={"keepalive": "true"}),
)
security = HTTPBearer()

app=FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != os.getenv("TOKEN_HEADER"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication token",
        )
    return token

@app.get("/tts")
async def stream_speech(
    text: str, token: str = Depends(get_token)
):
    try:
        start_time = time.time()
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
        )
        if response.response.status_code != 200:
            logger.error(f"TTS service error: {response.response.status_code} - {response.text}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Error communicating with TTS service."
            )
        byte_data = response.iter_bytes()
        async def generate():
            try:
                for chunk in byte_data:
                    yield chunk
            except Exception as e:
                logger.error(f"Error streaming audio data: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error streaming audio data."
                )
            finally:
                logger.info(f"TTS request processed in {time.time() - start_time:.2f} seconds")
        return StreamingResponse(generate(), media_type="audio/x-wav")
    except HTTPException as http_exc:
        logger.error(f"HTTP Exception: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )


@app.websocket("/ws/stt")
async def speech_to_text(websocket: WebSocket):
    await websocket.accept()
    try:
        deepgram_socket = await Process_audio(websocket, deepgram)
        while True:
            try:
                start_time=time.time()
                data = await websocket.receive_bytes()
                if not data:
                    logger.warning("Received empty data from websocket.")
                    break
                deepgram_socket.send(data)
            except WebSocketDisconnect:
                logger.info("WebSocket connection closed by client.")
                break
            except Exception as e:
                logger.error(f"Error processing audio data: {e}")
                break
            finally:
                logger.info(f"STT request processed in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
        await websocket.send_json({"status": "false", "message": "Something went wrong..."})
    finally:
        await websocket.close()
        logger.info("WebSocket connection closed.")

if __name__=="__main__":
    uvicorn.run(app=app)