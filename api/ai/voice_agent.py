import os
import asyncio
import websockets
import pyaudio
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Audio parameters
RATE = 24000
CHUNK = 1024

audio = pyaudio.PyAudio()

input_stream = audio.open(
    format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK
)

output_stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True)


async def send_audio(ws):
    while True:
        data = input_stream.read(CHUNK, exception_on_overflow=False)
        await ws.send(data)


async def receive_audio(ws):
    async for message in ws:
        event = json.loads(message)
        if event.get("type") == "audio.delta":
            output_stream.write(bytes(event["audio"]))


async def run_voice_agent():
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1",
    }

    async with websockets.connect(url, extra_headers=headers) as ws:
        await ws.send(
            json.dumps(
                {
                    "type": "session.update",
                    "session": {
                        "voice": "nova",
                        "modalities": ["audio"],
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16",
                    },
                }
            )
        )

        await asyncio.gather(send_audio(ws), receive_audio(ws))


if __name__ == "__main__":
    asyncio.run(run_voice_agent())
