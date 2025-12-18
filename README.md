# Real-time Voice Agent Using OpenAI

A real-time voice chatbot with streaming responses using OpenAI's GPT-4o-mini and Text-to-Speech.

## Features

- 🎤 Real-time speech-to-text (browser Web Speech API)
- ⚡ Streaming responses (token-by-token display)
- 🔊 Parallel text-to-speech (sentence-by-sentence audio generation)
- 🔇 Automatic feedback loop prevention (mic stops during AI response)
- 🔄 Continuous conversation (mic auto-resumes after response)

## Setup

### 1. Install Dependencies

```bash
pip install flask openai
```

### 2. Set Your OpenAI API Key

**⚠️ IMPORTANT: Get a new API key from OpenAI (your previous one was exposed)**

1. Go to https://platform.openai.com/api-keys
2. **Revoke** the old key (ends with `...w8A`)
3. Create a new API key
4. Set it as an environment variable:

**PowerShell (Windows):**
```powershell
$env:OPENAI_API_KEY = "your-new-api-key-here"
```

**CMD (Windows):**
```cmd
set OPENAI_API_KEY=your-new-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your-new-api-key-here"
```

### 3. Run the App

```bash
python app.py
```

Then open http://127.0.0.1:5000 in **Chrome desktop**.

## Usage

1. Click **"🎙 Start / Stop Mic"**
2. Allow microphone permissions
3. Speak your question
4. After 0.7 seconds of silence, your question is sent automatically
5. AI responds with streaming text and voice
6. Mic auto-resumes for your next question

## Security

- ✅ API key is now loaded from environment variable
- ✅ `.gitignore` prevents committing secrets
- ⚠️ **Never commit API keys to git**
- ⚠️ **Revoke your old exposed API key immediately**

## Troubleshooting

### "Speech recognition not supported"
- Use **Chrome desktop** (not Firefox, not mobile)
- Other browsers don't support Web Speech API

### "Mic permission denied"
- Click the lock icon in address bar → Site settings → Microphone → Allow

### "No response from AI"
- Check that your `OPENAI_API_KEY` environment variable is set
- Check the terminal for error messages

## Architecture

- **Backend:** Flask + OpenAI API (streaming)
- **Frontend:** Vanilla JS + Web Speech API
- **Streaming:** Server-Sent Events for real-time token delivery
- **TTS:** Sentence-by-sentence parallel audio generation

## Performance

- **Text streaming:** ~100ms to first token
- **Voice streaming:** Starts speaking after first sentence (parallel)
- **Pause detection:** 0.7 seconds (configurable in `index.html`)

