from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import base64
import os
from mesmer import MesmerEngine
from common import MessageEvent

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
        title="mesmer-server",
        description="Mesmer server to expose websocket and interact with the telephony telephony server"
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections: list[WebSocket] = []

router = APIRouter(
    prefix="/api/v1"
)



@router.websocket("/call/{call_id}")
async def call_socket(websocket: WebSocket, call_id: str):
    await websocket.accept()
    active_connections.append(websocket)
    '''
    Messages send by engine:

    1. This message is send by us at the end of an audio stream stream.
    The telephony server should send this message back to us after playing the audio.
    mark_message = {
        "event": "mark",
        "streamSid": self.stream_sid,
        "mark": {
            "name": "XXXX"
            }
        }

    2. This message is send by us to send audio data to the telephony server.
    media_message = {
        'event': 'media',
        'streamSid': self.stream_sid,
        'media': {
            'payload': base64_audio
            }
        }

    3. This message is send by us to clear the audio stream. 
    On receiving this message, the telephony telephony server should stop playing the audio and clear the audio buffer on their end.
    It should send back all the pending mark messages.
    interrupt_message = {
        "event": "clear",
        "streamSid": self.stream_sid
        }

    '''
    mesmer_engine = MesmerEngine(call_id,
                                 on_message=lambda message: websocket.send_text(json.dumps(message)),
                                 on_close=lambda: websocket.close()) 
    try:
        while True:
            message = await websocket.receive_text()
            if message is None:
                continue
            else:
                try:
                    data = json.loads(message)
                except json.decoder.JSONDecodeError:
                    continue
                print(f"WS Message : {data}")
                match data["event"]:
                    case "connected":
                        '''
                        This is the first message sent by the telephony server to the mesmer server.
                        It is used to establish the connection.

                        data = {
                            "event": "connected"
                        }
                        '''
                        continue
                    case "start":
                        '''
                        This message is sent by the telephony server to the mesmer server to start the conversation.
                        It should contain the streamSid of the conversation.

                        data = {
                            "event": "start",
                            "start": {
                                "callSid": "XXXX",
                                "streamSid": "XXXX",
                                "accountSid": "XXXX",
                                "mediaFormat": { 
                                    "encoding": "audio/x-mulaw", 
                                    "sampleRate": 8000, 
                                    "channels": 1 
                                },
                            }
                        }
                        '''
                        stream_sid = data["start"]["streamSid"]
                        mesmer_engine.start(stream_sid)
                        continue
                    case "media":
                        '''
                        This message is sent by the telephony server to the mesmer server to send audio data.
                        It should contain the audio payload in base64 format.

                        data = {
                            'event': 'media',
                            'streamSid': "XXXX",
                            'media': {
                                'timestamp': XX,
                                'payload': base64_audio
                                }
                            }
                        '''
                        media = data["media"]
                        audio_chunk = base64.b64decode(media["payload"])
                        mesmer_engine.add_audio(MessageEvent("source-audio-chunk", audio_chunk))
                        continue
                    case "mark":
                        '''
                        This message is sent by the telephony server to the mesmer server to mark the end of the audio data.
                        It should contain the name of the mark.
                        
                        data = {
                            "event": "mark",
                            "streamSid": "XXXX",
                            "mark": {
                                "name": "XXXX"
                                }
                            }
                        '''
                        mark_name = data["mark"]["name"]
                        mesmer_engine.add_event(MessageEvent("sink-audio-end", mark_name))
                    case "stop":
                        '''
                        This message is sent by the telephony server to the mesmer server to stop the conversation.
                        
                        data = {
                            "event": "stop",
                            "stop": {
                                "streamSid": "XXXX",
                                "callSid": "XXXX",
                                "accountSid": "XXXX"
                                }
                            }
                        '''
                        break
                    case _:
                        print(f"WS Unknown: {message}")
    except WebSocketDisconnect:
        print("Websocket Disconnected")
        pass
    active_connections.remove(websocket)


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("MESMER_HOST"),
        port=os.getenv("MESMER_PORT"),
        reload=True,
        server_header=False,
        log_level="info",
    )