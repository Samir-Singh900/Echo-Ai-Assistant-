import os
import re
from flask import Flask, jsonify, render_template_string, request

# --- SAFE IMPORTS ---
try:
    from flask_cors import CORS
    cors_installed = True
except ImportError:
    cors_installed = False

try:
    from groq import Groq
    groq_installed = True
except ImportError:
    groq_installed = False

app = Flask(__name__)
if cors_installed:
    CORS(app)

# --- CONFIGURATION ---
API_KEY = "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"

# --- THE ULTIMATE UI: REDESIGNED & MODERN ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ECHO | Samir Singh</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* --- CORE VARIABLES --- */
        :root {
            --primary: #00f2ff;
            --secondary: #bd00ff;
            --bg-deep: #05050a;
            --glass: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.1);
        }

        body {
            background-color: var(--bg-deep);
            color: white;
            font-family: 'Outfit', sans-serif;
            margin: 0;
            overflow-x: hidden;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* --- BACKGROUND ANIMATION --- */
        #bg-canvas { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; }

        /* --- UI ELEMENTS --- */

        /* 1. GLASS PANEL (The Chat Area) */
        .glass-panel {
            background: rgba(10, 10, 20, 0.6);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            box-shadow: 0 0 40px rgba(0, 242, 255, 0.05);
            border-radius: 24px;
            transition: 0.3s ease;
        }

        /* 2. THE REACTOR (The Button) */
        .reactor-container {
            position: relative;
            width: 140px;
            height: 140px;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: transform 0.2s;
            margin: 20px 0;
        }
        .reactor-container:active { transform: scale(0.95); }

        .reactor-core {
            width: 80px; height: 80px;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, #2a2a35, #000);
            border: 2px solid rgba(255,255,255,0.1);
            position: relative;
            z-index: 10;
            display: flex; justify-content: center; align-items: center;
            box-shadow: 0 0 20px rgba(0,0,0,0.5), inset 0 0 20px rgba(0,0,0,0.8);
            transition: 0.3s;
        }

        .reactor-glow {
            position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 140px; height: 140px;
            border-radius: 50%;
            background: conic-gradient(from 0deg, transparent 0%, var(--primary) 20%, transparent 40%);
            animation: rotate 4s linear infinite;
            opacity: 0.5;
            filter: blur(10px);
        }

        /* STATUS STATES */
        /* Listening: Red Pulse */
        .listening .reactor-core { border-color: #ff2a6d; box-shadow: 0 0 30px #ff2a6d; }
        .listening .reactor-glow { background: conic-gradient(from 0deg, transparent, #ff2a6d, transparent); animation: rotate 1s linear infinite; opacity: 1; }
        .listening i { color: #ff2a6d; animation: pulse-text 0.5s infinite alternate; }

        /* Speaking: Green/Cyan Ripple */
        .speaking .reactor-core { border-color: #05ff00; box-shadow: 0 0 30px #05ff00; }
        .speaking .reactor-glow { background: conic-gradient(from 0deg, transparent, #05ff00, transparent); animation: rotate 2s linear infinite; opacity: 0.8; }

        /* 3. TYPOGRAPHY & CODE */
        .response-text {
            font-family: 'Outfit', sans-serif;
            font-size: 1.1rem;
            line-height: 1.7;
            color: #e2e8f0;
        }
        .code-block {
            font-family: 'JetBrains Mono', monospace;
            background: rgba(0,0,0,0.4);
            border-radius: 8px;
            padding: 2px 6px;
            color: var(--primary);
            font-size: 0.9em;
        }

        /* 4. FOOTER DOCK */
        .dock {
            position: fixed; bottom: 30px;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(15px);
            padding: 12px 30px;
            border-radius: 50px;
            border: 1px solid rgba(255,255,255,0.1);
            display: flex; align-items: center; gap: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            z-index: 50;
        }
        .dock-divider { width: 1px; height: 24px; background: rgba(255,255,255,0.2); }
        .dock-link {
            font-size: 1.2rem;
            color: rgba(255,255,255,0.7);
            transition: 0.3s;
            position: relative;
        }
        .dock-link:hover { color: var(--primary); transform: translateY(-3px); }
        .dock-link::after {
            content: ''; position: absolute; bottom: -8px; left: 50%; transform: translateX(-50%);
            width: 0; height: 4px; background: var(--primary); border-radius: 2px; transition: 0.3s;
        }
        .dock-link:hover::after { width: 100%; }

        /* ANIMATIONS */
        @keyframes rotate { 100% { transform: translate(-50%, -50%) rotate(360deg); } }
        @keyframes pulse-text { from { opacity: 0.5; } to { opacity: 1; } }
        @keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    </style>
</head>
<body>

    <canvas id="bg-canvas"></canvas>

    <header class="w-full max-w-4xl flex justify-between items-center p-8 z-10 animate-[fade-in_1s_ease-out]">
        <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/50 flex items-center justify-center shadow-[0_0_15px_rgba(0,242,255,0.3)]">
                <i class="fas fa-wave-square text-cyan-400 text-xl"></i>
            </div>
            <div>
                <h1 class="text-3xl font-bold tracking-tight text-white">ECHO <span class="text-cyan-400">AI</span></h1>
                <p class="text-xs text-gray-400 tracking-widest uppercase">Personal Assistant</p>
            </div>
        </div>
        <div class="hidden md:flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
            <div class="w-2 h-2 bg-green-500 rounded-full shadow-[0_0_10px_#22c55e]"></div>
            <span class="text-xs font-bold text-gray-300">SYSTEM ONLINE</span>
        </div>
    </header>

    <main class="w-full max-w-2xl flex flex-col items-center gap-8 px-6 z-10 mt-4 pb-32">

        <div class="reactor-container" id="reactor" onclick="toggleListening()">
            <div class="reactor-glow"></div>
            <div class="reactor-core">
                <i id="core-icon" class="fas fa-microphone text-2xl text-gray-300 transition-colors"></i>
            </div>
        </div>

        <p id="status-text" class="text-cyan-400 text-sm font-mono tracking-widest uppercase animate-pulse">Tap Mic to Speak</p>

        <div class="glass-panel w-full p-1 min-h-[200px] relative group">
            <div class="flex justify-between items-center px-6 py-4 border-b border-white/5">
                <div class="flex gap-2">
                    <div class="w-3 h-3 rounded-full bg-red-500/50"></div>
                    <div class="w-3 h-3 rounded-full bg-yellow-500/50"></div>
                    <div class="w-3 h-3 rounded-full bg-green-500/50"></div>
                </div>
                <button onclick="copyResponse()" class="text-xs text-gray-400 hover:text-cyan-400 transition-colors flex items-center gap-2">
                    <i class="fas fa-copy"></i> <span id="copy-label">COPY</span>
                </button>
            </div>

            <div class="p-6">
                <div id="output-text" class="response-text text-gray-200">
                    Hello, How can I assist you today?
                </div>
            </div>

            <div class="absolute inset-0 rounded-24px bg-gradient-to-r from-cyan-500/0 via-cyan-500/5 to-purple-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
        </div>

    </main>

    <div class="dock">
        <div class="flex flex-col">
            <span class="text-sm font-bold text-white leading-none">Samir Singh</span>
            <span class="text-[10px] text-gray-400 uppercase leading-none mt-1">Creator</span>
        </div>

        <div class="dock-divider"></div>

        <a href="mailto:samirsingh98794@gmail.com" class="dock-link" title="Email"><i class="fas fa-envelope"></i></a>
        <a href="https://github.com/Samir-Singh900" target="_blank" class="dock-link" title="GitHub"><i class="fab fa-github"></i></a>
        <a href="https://www.linkedin.com/in/samir-singh-927637328/" target="_blank" class="dock-link" title="LinkedIn"><i class="fab fa-linkedin"></i></a>
    </div>

    <script>
        // --- 1. STARFIELD BACKGROUND ---
        const canvas = document.getElementById('bg-canvas');
        const ctx = canvas.getContext('2d');
        let width, height;

        function resize() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        const stars = Array.from({ length: 100 }, () => ({
            x: Math.random() * width,
            y: Math.random() * height,
            size: Math.random() * 1.5,
            speed: Math.random() * 0.2 + 0.1,
            opacity: Math.random()
        }));

        function animateBg() {
            ctx.fillStyle = '#05050a';
            ctx.fillRect(0, 0, width, height);

            stars.forEach(star => {
                ctx.fillStyle = `rgba(255, 255, 255, ${star.opacity})`;
                ctx.beginPath();
                ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
                ctx.fill();

                star.y -= star.speed;
                if (star.y < 0) star.y = height;
            });
            requestAnimationFrame(animateBg);
        }
        animateBg();

        // --- 2. COPY FUNCTION ---
        function copyResponse() {
            const text = document.getElementById('output-text').innerText;
            navigator.clipboard.writeText(text).then(() => {
                const label = document.getElementById('copy-label');
                label.innerText = "COPIED!";
                setTimeout(() => label.innerText = "COPY", 2000);
            });
        }

        // --- 3. SPEECH LOGIC ---
        const reactor = document.getElementById('reactor');
        const coreIcon = document.getElementById('core-icon');
        const statusText = document.getElementById('status-text');
        const outputText = document.getElementById('output-text');
        const synth = window.speechSynthesis;
        let voices = [];
        let recognition;

        window.speechSynthesis.onvoiceschanged = () => { voices = synth.getVoices(); };

        function speak(text, langCode) {
            if (synth.speaking) synth.cancel();
            if(text.length > 500) return;

            const u = new SpeechSynthesisUtterance(text);
            u.lang = langCode || 'en-US';

            // Prefer a Google voice or a female voice for "Assistant" vibe
            let voice = voices.find(v => v.name.includes("Google") && v.lang.startsWith("en")) || voices[0];
            if(voice) u.voice = voice;

            setVisuals('speaking');
            u.onend = () => setVisuals('idle');
            synth.speak(u);
        }

        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';

            recognition.onstart = () => setVisuals('listening');
            recognition.onend = () => { if(reactor.classList.contains('listening')) setVisuals('idle'); };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                statusText.innerText = "PROCESSING...";
                outputText.innerHTML = '<span class="animate-pulse">Analyzing request...</span>';
                processCommand(transcript);
            };
        } else {
            outputText.innerText = "Browser not supported. Please use Chrome.";
        }

        function toggleListening() {
            if (reactor.classList.contains('listening')) recognition.stop();
            else recognition.start();
        }

        function setVisuals(state) {
            reactor.classList.remove('listening', 'speaking');
            if(state !== 'idle') reactor.classList.add(state);

            if(state === 'idle') {
                coreIcon.className = "fas fa-microphone text-2xl text-gray-300";
                statusText.innerText = "Tap Orb to Speak";
            } else if(state === 'listening') {
                coreIcon.className = "fas fa-wave-square text-2xl text-white";
                statusText.innerText = "Listening...";
            } else if(state === 'speaking') {
                coreIcon.className = "fas fa-volume-up text-2xl text-white";
                statusText.innerText = "Echo is speaking...";
            }
        }

        async function processCommand(cmd) {
            try {
                const res = await fetch('/process', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ command: cmd })
                });
                const data = await res.json();

                // Typewriter effect logic could go here, but for now direct insert
                outputText.innerHTML = data.display_text;

                if(data.action_type === 'OPEN_URL') {
                    window.open(data.action_data, '_blank');
                }

                speak(data.spoken_text, data.lang_code);

            } catch (e) {
                statusText.innerText = "ERROR";
                outputText.innerText = "Connection lost. Please check server.";
            }
        }
    </script>
</body>
</html>
"""

# --- SMART BACKEND LOGIC ---
client = None
if groq_installed:
    try: client = Groq(api_key=API_KEY)
    except: pass

@app.route('/')
def home(): return render_template_string(HTML_UI)

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json(silent=True) or {}
    cmd = data.get('command', '')

    # SYSTEM PROMPT
    system_instruction = """
    You are ECHO, the personal AI assistant of Samir Singh.

    Response Rules:
    1. Keep [SPEAK] concise and conversational.
    2. Put detailed info and Code in [DISPLAY].
    3. Use HTML inside [DISPLAY] for formatting: <br>, <b>bold</b>, and for code use:
       <div class="code-block">code here</div>

    Format:
    [LANG:en-US]
    [SPEAK: Short audio summary]
    [DISPLAY: HTML formatted visual response]
    [ACTION:TYPE|DATA]
    """

    spoken_text = "I am ready, Samir."
    display_text = "System Online. Awaiting instructions."
    lang_code = "en-US"
    action_type = None
    action_data = None

    if client:
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": cmd}],
                max_tokens=500
            )
            raw = completion.choices[0].message.content.strip()

            # Parse Tags
            m = re.search(r'\[LANG:(.*?)\]', raw)
            if m: lang_code = m.group(1).strip()

            m = re.search(r'\[SPEAK:(.*?)\]', raw, re.DOTALL)
            if m: spoken_text = m.group(1).strip()

            m = re.search(r'\[DISPLAY:(.*?)\]', raw, re.DOTALL)
            if m: display_text = m.group(1).strip()
            else: display_text = raw # Fallback if AI forgets tags

            m = re.search(r'\[ACTION:(.*?)\|(.*?)\]', raw)
            if m:
                a_type = m.group(1).strip()
                if a_type == "OPEN": action_type = "OPEN_URL"
                action_data = m.group(2).strip()

        except Exception as e:
            display_text = f"Error: {str(e)}"

    return jsonify({
        "spoken_text": spoken_text,
        "display_text": display_text,
        "lang_code": lang_code,
        "action_type": action_type,
        "action_data": action_data
    })

if __name__ == '__main__':
    app.run(debug=True)