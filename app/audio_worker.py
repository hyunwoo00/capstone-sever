import json
from flask_socketio import SocketIO
from app.yamnet import model_output
import numpy as np
from redis import Redis

# Redis 연결
r = Redis(host='redis', port='6379', db=0)

# 여기도 똑같은 Redis를 바라보게 설정
# write_only=True는 수신은 안 하고 발신만 하겠다는 최적화 옵션.
external_socketio = SocketIO(message_queue='redis://redis:6379/0', write_only=True)

def audio_worker():
    while True:
        _, json_data = r.blpop("audio_queue")   # BLOCKING POP
        data = json.loads(json_data)
        
        sid = data["sid"]
        audio_data = data["audio_data"]

        label, category = process_audio(audio_data)

        external_socketio.emit('audio_response', {"label": label, "category": category}, room = sid)
        

def process_audio(data):
    #전처리
    wav = np.array(data, dtype=np.float32)

    #yamnet 모델 실행
    label, category = model_output(wav)

    return label, category

if __name__ == "__main__":
    audio_worker()
