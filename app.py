from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from openai import OpenAI
import base64
import json
import os

app = Flask(__name__)

# Load API key from environment variable (NEVER commit API keys!)
# Set with: $env:OPENAI_API_KEY = "your-key-here" (PowerShell)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = """
You are a friendly, concise voice assistant.
Answer naturally and briefly like a real human.
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Streaming endpoint: returns Server-Sent Events with tokens AND parallel audio chunks"""
    data = request.get_json() or {}
    user_text = data.get("text", "").strip()

    if not user_text:
        return jsonify({"error": "Empty input"}), 400

    def generate():
        try:
            print(f"📥 Received: {user_text}")
            
            # Stream tokens from OpenAI in real-time
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
                stream=True  # 🔥 Enable streaming!
            )

            full_response = ""
            sentence_buffer = ""
            sentence_count = 0
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    sentence_buffer += token
                    
                    # Send each token immediately for text display
                    yield f"data: {json.dumps({'token': token})}\n\n"
                    
                    # Check if we completed a sentence (., !, ?, or newline)
                    if any(punct in token for punct in ['.', '!', '?', '\n']):
                        sentence = sentence_buffer.strip()
                        if len(sentence) > 3:  # Only generate TTS for meaningful sentences
                            sentence_count += 1
                            print(f"🎤 Generating TTS for sentence {sentence_count}: {sentence[:50]}...")
                            
                            try:
                                # Generate TTS for this sentence in parallel
                                tts_response = client.audio.speech.create(
                                    model="tts-1",
                                    voice="alloy",
                                    input=sentence,
                                )
                                audio_bytes = tts_response.read()
                                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                                
                                # Send audio chunk immediately (parallel streaming!)
                                yield f"data: {json.dumps({
                                    'audio_chunk': audio_b64, 
                                    'audio_mime': 'audio/mpeg',
                                    'chunk_id': sentence_count
                                })}\n\n"
                                print(f"✅ TTS chunk {sentence_count} sent!")
                                
                            except Exception as tts_error:
                                print(f"⚠️ TTS failed for chunk: {tts_error}")
                            
                            sentence_buffer = ""  # Reset for next sentence
            
            print(f"✅ AI replied: {full_response}")
            
            # If there's remaining text that didn't end with punctuation
            if sentence_buffer.strip():
                try:
                    tts_response = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=sentence_buffer.strip(),
                    )
                    audio_bytes = tts_response.read()
                    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                    yield f"data: {json.dumps({'audio_chunk': audio_b64, 'audio_mime': 'audio/mpeg'})}\n\n"
                except Exception as tts_error:
                    print(f"⚠️ TTS failed: {tts_error}")
            
            # Signal end of stream
            yield "data: [DONE]\n\n"

        except Exception as e:
            print(f"❌ Error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')



if __name__ == "__main__":
    app.run(debug=True)
