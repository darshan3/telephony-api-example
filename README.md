# Information about messages exchanged between mesmer and telephony server

### Messages sent by mesmer server:

1. This message is send by us at the end of an audio stream stream.
The telephony server should send this message back to us after playing the audio.
```python
mark_message = {
    "event": "mark",
    "streamSid": self.stream_sid,
    "mark": {
        "name": "XXXX"
        }
    }
```

2. This message is send by us to send audio data to the telephony server.
```python
media_message = {
    'event': 'media',
    'streamSid': self.stream_sid,
    'media': {
        'payload': base64_audio
        }
    }
```

3. This message is send by us to clear the audio stream. 
On receiving this message, the telephony server should stop playing the audio and clear the audio buffer on their end.
It should send back all the pending mark messages.
```python
interrupt_message = {
    "event": "clear",
    "streamSid": self.stream_sid
    }
```

### Messages received from telephony server:

1. This is the first message sent by the telephony server to the mesmer server.
It is used to establish the connection.
```python
data = {
    "event": "connected"
}
```

2. This message is sent by the telephony server to the mesmer server to start the conversation.
It should contain the streamSid of the conversation.
```python
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
```

3. This message is sent by the telephony server to the mesmer server to send audio data.
It should contain the audio payload in base64 format.
```python
data = {
    'event': 'media',
    'streamSid': "XXXX",
    'media': {
        'timestamp': XX,
        'payload': base64_audio
        }
    }
```

4. This message is sent by the telephony server to the mesmer server to mark the end of the audio data.
It should contain the name of the mark.
```python
data = {
    "event": "mark",
    "streamSid": "XXXX",
    "mark": {
        "name": "XXXX"
        }
    }
```

5. This message is sent by the telephony server to the mesmer server to stop the conversation.
```python
data = {
    "event": "stop",
    "stop": {
        "streamSid": "XXXX",
        "callSid": "XXXX",
        "accountSid": "XXXX"
        }
    }
```