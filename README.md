# NEXA Local AI Voice

Project AI lokal dengan chat, voice input (faster-whisper), LLM lokal (Ollama), dan voice output (pyttsx3).

## Windows
1. Install Python 3.11+.
2. Install Ollama.
3. Jalankan `ollama pull llama3.2:3b`.
4. Buka CMD di folder project.
5. `pip install -r requirements.txt`
6. `python -m uvicorn server:app --host 0.0.0.0 --port 8000`
7. Buka `http://127.0.0.1:8000`.

## Ganti model
Contoh: `ollama pull qwen2.5:3b`
Lalu set environment `LOCAL_AI_MODEL=qwen2.5:3b` sebelum menjalankan server.

## Catatan
Model Whisper akan diunduh saat pertama kali dipakai. Semua chat AI diproses lokal melalui Ollama setelah model tersedia. TTS memakai suara yang tersedia di OS.
