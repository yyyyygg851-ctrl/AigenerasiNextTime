import os, json, tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

MODEL=os.getenv('LOCAL_AI_MODEL','llama3.2:3b')
app=FastAPI(title='NEXA Local AI')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
SYSTEM='''Kamu adalah NEXA, asisten AI lokal. Jawab natural, jelas, dan membantu. Gunakan bahasa Indonesia kecuali pengguna meminta bahasa lain. Jangan mengklaim akses yang tidak tersedia.'''

def ollama_chat(message,history):
    import urllib.request
    payload={'model':MODEL,'stream':False,'messages':[{'role':'system','content':SYSTEM}]+history[-20:]+[{'role':'user','content':message}]}
    req=urllib.request.Request('http://127.0.0.1:11434/api/chat',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=180) as r:return json.loads(r.read().decode())['message']['content']

@app.get('/')
def index(): return FileResponse('index.html')
@app.get('/api/status')
def status():
    try:
        import urllib.request
        with urllib.request.urlopen('http://127.0.0.1:11434/api/tags',timeout=3) as r:d=json.loads(r.read().decode())
        return {'ok':True,'model':MODEL,'models':[x.get('name') for x in d.get('models',[])]}
    except Exception as e:return {'ok':False,'model':MODEL,'error':str(e)}
@app.post('/api/chat')
async def chat(data:dict):
    try:
        msg=(data.get('message') or '').strip()
        if not msg:return JSONResponse({'error':'Pesan kosong'},400)
        return {'answer':ollama_chat(msg,data.get('history') or []),'model':MODEL}
    except Exception as e:return JSONResponse({'error':str(e)},500)
@app.post('/api/transcribe')
async def transcribe(audio:UploadFile=File(...)):
    try:
        from faster_whisper import WhisperModel
        raw=await audio.read(); suffix=Path(audio.filename or 'voice.webm').suffix or '.webm'
        f=tempfile.NamedTemporaryFile(delete=False,suffix=suffix); f.write(raw); f.close()
        model=WhisperModel(os.getenv('WHISPER_MODEL','base'),device=os.getenv('WHISPER_DEVICE','cpu'),compute_type=os.getenv('WHISPER_COMPUTE','int8'))
        segments,_=model.transcribe(f.name,language='id',vad_filter=True)
        text=' '.join(s.text.strip() for s in segments).strip(); os.unlink(f.name)
        return {'text':text}
    except Exception as e:return JSONResponse({'error':str(e)},500)
@app.post('/api/speak')
async def speak(data:dict):
    text=(data.get('text') or '').strip()
    if not text:return JSONResponse({'error':'Teks kosong'},400)
    try:
        import pyttsx3
        f=tempfile.NamedTemporaryFile(delete=False,suffix='.wav'); f.close()
        engine=pyttsx3.init(); engine.setProperty('rate',175); engine.save_to_file(text,f.name); engine.runAndWait()
        audio=open(f.name,'rb').read(); os.unlink(f.name)
        return Response(audio,media_type='audio/wav')
    except Exception as e:return JSONResponse({'error':str(e)},500)
