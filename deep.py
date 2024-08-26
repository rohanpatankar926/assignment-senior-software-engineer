from fastapi import WebSocket
import asyncio
from deepgram import (
    LiveOptions,
    LiveTranscriptionEvents,
    DeepgramClient,
)

options = LiveOptions(model="nova-2", smart_format=True)


async def Process_audio(main_socket: WebSocket, deepgram: DeepgramClient):
    async def send_transcript(text):
        await main_socket.send_text(text)

    def on_message(self, result, **kwargs):
        transcript = result.channel.alternatives[0].transcript
        asyncio.run(send_transcript(transcript))

    dg_connection = deepgram.listen.live.v("1")
    dg_connection.start(options)
    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

    return dg_connection
