from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from openrun.api.schemas import ChatRequest
from openrun.core.state import get_global_state
from openrun.api.dependencies import verify_api_key
from openrun.model.inference import generate_response, stream_response
import time
import uuid
import os

router = APIRouter()

# HTML template for the built-in web playground
PLAYGROUND_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRun Playground</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .bg-app { background: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 100%); background-attachment: fixed; }
        
        .markdown-body pre { background-color: #0f172a; color: #e2e8f0; padding: 1rem; border-radius: 0.75rem; overflow-x: auto; margin: 1rem 0; box-shadow: inset 0 0 0 1px #334155; position: relative; }
        .markdown-body code { background-color: rgba(255,255,255,0.08); border-radius: 0.25rem; padding: 0.2em 0.4em; }
        .markdown-body pre code { background-color: transparent; padding: 0; }
        .message-content { white-space: pre-wrap; line-height: 1.6; }
        
        .copy-button { position: absolute; top: 0.5rem; right: 0.5rem; background: #334155; border: none; color: #cbd5e1; padding: 0.25rem 0.5rem; border-radius: 0.375rem; font-size: 0.75rem; cursor: pointer; opacity: 0; transition: all 0.2s; }
        .markdown-body pre:hover .copy-button { opacity: 1; }
        .copy-button:hover { background: #475569; color: #fff; }

        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }

        .typing-indicator { display: inline-flex; align-items: center; gap: 4px; height: 24px; padding: 0 4px; }
        .dot { width: 6px; height: 6px; background-color: #94a3b8; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.5; } 40% { transform: scale(1); opacity: 1; } }
    </style>
</head>
<body class="bg-app text-gray-100 h-screen flex flex-col antialiased">
    
    <!-- Top Nav -->
    <header class="bg-slate-900/60 backdrop-blur-md border-b border-slate-800 px-6 py-3.5 flex justify-between items-center shadow-sm z-20 flex-shrink-0 sticky top-0">
        <div class="flex items-center gap-3">
            <div class="h-9 w-9 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                    <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 5.522 4.477 10 10 10s10-4.478 10-10C22 6.477 17.522 2 12 2zm1.25 15.5a1.25 1.25 0 11-2.5 0 1.25 1.25 0 012.5 0zm-.8-2.6a1 1 0 01-1-.87L11.4 8h1.2l-.05 6.03a1 1 0 01-.1.37z" clip-rule="evenodd" />
                </svg>
            </div>
            <div>
                <h1 class="text-lg font-bold text-white tracking-tight">OpenRun <span class="text-indigo-400 font-medium">Chat</span></h1>
                <div class="text-[11px] text-slate-400 font-medium flex items-center gap-1.5 mt-0.5">
                    <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]"></span>
                    Running: <span id="model-name-display" class="text-slate-300 font-mono">Loading...</span>
                </div>
            </div>
        </div>
        
        <div class="flex items-center gap-4 bg-slate-800/50 p-1.5 rounded-xl border border-slate-700/50 shadow-inner">
            <div class="flex flex-col items-end px-3">
                <input type="password" id="api-key" placeholder="API Key (Optional)..." class="bg-slate-900 border hidden sm:block border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 outline-none w-56 font-mono placeholder-slate-500 transition-all">
            </div>
            
            <div class="h-6 w-px bg-slate-700 hidden sm:block"></div>
            
            <button id="clear-btn" class="text-slate-400 hover:text-rose-400 transition-colors p-2 rounded-lg hover:bg-slate-800" title="Clear Chat">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
            </button>
        </div>
    </header>

    <!-- Chat Area -->
    <main id="chat-container" class="flex-1 overflow-y-auto p-4 sm:p-8 space-y-8 scroll-smooth pb-40">
        <!-- Empty State -->
        <div id="empty-state" class="h-full flex flex-col items-center justify-center text-slate-500 space-y-6 animate-fade-in relative z-0">
            <div class="h-20 w-20 bg-slate-800 rounded-[2rem] flex items-center justify-center border border-slate-700 shadow-2xl shadow-indigo-500/10 mb-2 rotate-3 hover:rotate-0 transition-transform duration-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
            </div>
            <h2 class="text-2xl font-semibold text-slate-200">How can I help you today?</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl w-full mt-8">
                <button class="suggestion-btn text-left p-5 rounded-2xl border border-slate-700/60 bg-slate-800/40 hover:bg-slate-800 hover:border-slate-600 transition-all group backdrop-blur-sm shadow-md">
                    <div class="font-semibold text-slate-200 mb-1 group-hover:text-indigo-400 transition-colors">Write a Python script</div>
                    <div class="text-sm text-slate-400">to scrape data from a website</div>
                </button>
                <button class="suggestion-btn text-left p-5 rounded-2xl border border-slate-700/60 bg-slate-800/40 hover:bg-slate-800 hover:border-slate-600 transition-all group backdrop-blur-sm shadow-md">
                    <div class="font-semibold text-slate-200 mb-1 group-hover:text-indigo-400 transition-colors">Explain quantum computing</div>
                    <div class="text-sm text-slate-400">as if I am 5 years old</div>
                </button>
            </div>
        </div>
    </main>

    <!-- Input Footer -->
    <div class="fixed bottom-0 left-0 w-full bg-gradient-to-t from-slate-950 via-slate-900/90 to-transparent pt-12 pb-6 px-4 sm:px-6 pointer-events-none z-20">
        <div class="max-w-4xl mx-auto relative pointer-events-auto">
            
            <div id="error-toast" class="absolute -top-14 left-1/2 -translate-x-1/2 bg-rose-500/90 text-white px-5 py-2.5 rounded-xl text-sm shadow-xl shadow-rose-500/20 border border-rose-400 opacity-0 transition-all duration-300 pointer-events-none flex items-center gap-2 font-medium backdrop-blur-md translate-y-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <span id="error-msg"></span>
            </div>
            
            <!-- Stop Generating -->
            <div class="flex justify-center w-full absolute -top-16 pointer-events-none">
                <button id="stop-btn" class="hidden pointer-events-auto bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-300 text-xs font-semibold px-4 py-2 rounded-full shadow-lg transition-all items-center gap-2 backdrop-blur-md">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-rose-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd" />
                    </svg>
                    Stop generating
                </button>
            </div>

            <!-- Text Box -->
            <div class="relative bg-slate-800/80 backdrop-blur-xl rounded-3xl border border-slate-700/80 shadow-2xl focus-within:border-indigo-500/50 focus-within:ring-4 focus-within:ring-indigo-500/10 transition-all flex flex-col pb-12">
                <textarea id="message-input" rows="1" class="w-full bg-transparent text-slate-100 placeholder-slate-500 px-5 pt-5 pb-2 rounded-3xl focus:outline-none resize-none max-h-48 overflow-y-auto leading-relaxed text-[15px]" placeholder="Message OpenRun..." autofocus></textarea>
                
                <div class="absolute bottom-3 right-3 flex items-center gap-2">
                    <label class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-400 bg-slate-900/50 rounded-lg pointer-events-auto hover:bg-slate-700 transition cursor-pointer border border-slate-700/50">
                        <input type="checkbox" id="stream-toggle" class="rounded bg-slate-800 border-slate-600 text-indigo-500 focus:ring-offset-slate-900 focus:ring-indigo-500 cursor-pointer w-3.5 h-3.5" checked>
                        Stream
                    </label>
                    <button id="send-btn" class="bg-indigo-500 hover:bg-indigo-400 text-white h-9 w-9 rounded-[10px] flex items-center justify-center transition-all disabled:opacity-40 disabled:hover:bg-indigo-500 disabled:cursor-not-allowed transform active:scale-95 shadow-md shadow-indigo-500/20" disabled>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-0.5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="text-center mt-3 text-[11px] font-medium text-slate-500">
                OpenRun LLM API Server · OpenAI Compatible Output
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        const API_URL = '/v1/chat/completions';
        const HEALTH_URL = '/';
        
        let messages = [];
        let isGenerating = false;
        let abortController = null;
        
        const chatContainer = document.getElementById('chat-container');
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        const stopBtn = document.getElementById('stop-btn');
        const clearBtn = document.getElementById('clear-btn');
        const emptyState = document.getElementById('empty-state');
        const apiKeyInput = document.getElementById('api-key');
        const streamToggle = document.getElementById('stream-toggle');
        const errorToast = document.getElementById('error-toast');
        const errorMsg = document.getElementById('error-msg');
        const modelNameDisplay = document.getElementById('model-name-display');

        async function fetchHealth() {
            try {
                const res = await fetch(HEALTH_URL);
                if (res.ok) {
                    const data = await res.json();
                    modelNameDisplay.textContent = data.model || "Unknown";
                }
            } catch (e) {
                modelNameDisplay.textContent = "Offline";
                modelNameDisplay.classList.add("text-rose-400");
                modelNameDisplay.parentElement.querySelector('span').classList.replace("bg-emerald-400", "bg-rose-500");
            }
        }
        fetchHealth();

        marked.setOptions({ breaks: true, gfm: true });

        // Syntax highlighting injector for copy buttons
        const renderCode = (code, language) => {
            return `<pre><button class="copy-button" onclick="navigator.clipboard.writeText(this.parentElement.querySelector('code').innerText); this.innerText='Copied!'; setTimeout(()=>this.innerText='Copy', 2000);">Copy</button><code>${code.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`;
        };
        const renderer = new marked.Renderer();
        renderer.code = renderCode;
        marked.use({ renderer });

        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const text = btn.querySelector('.font-semibold').textContent + ' ' + btn.querySelector('.text-sm').textContent;
                messageInput.value = text;
                messageInput.focus();
                adjustTextareaHeight();
                messageInput.dispatchEvent(new Event('input'));
            });
        });

        function adjustTextareaHeight() {
            messageInput.style.height = 'auto';
            messageInput.style.height = Math.min(messageInput.scrollHeight, 200) + 'px';
        }

        messageInput.addEventListener('input', () => {
            adjustTextareaHeight();
            sendBtn.disabled = messageInput.value.trim() === '';
        });

        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!sendBtn.disabled && !isGenerating) sendMessage();
            }
        });

        sendBtn.addEventListener('click', sendMessage);
        
        stopBtn.addEventListener('click', () => {
            if (abortController) {
                abortController.abort();
                isGenerating = false;
                setUIGenerationState(false);
                const lastMsg = chatContainer.lastElementChild;
                if (lastMsg && lastMsg.dataset.role === 'assistant') {
                    const contentDiv = lastMsg.querySelector('.message-content');
                    if (contentDiv.querySelector('.typing-indicator')) {
                         contentDiv.querySelector('.typing-indicator').remove();
                    }
                }
            }
        });

        clearBtn.addEventListener('click', () => {
            if (isGenerating) return;
            messages = [];
            Array.from(chatContainer.children).forEach(child => { if (child.id !== 'empty-state') child.remove(); });
            emptyState.style.display = 'flex';
        });

        function showError(msg) {
            errorMsg.textContent = msg;
            errorToast.classList.remove('opacity-0', 'translate-y-2');
            setTimeout(() => { errorToast.classList.add('opacity-0', 'translate-y-2'); }, 4000);
        }
        
        function setUIGenerationState(generating) {
            isGenerating = generating;
            sendBtn.disabled = generating || messageInput.value.trim() === '';
            messageInput.disabled = generating;
            
            if (generating) {
                stopBtn.classList.remove('hidden');
                sendBtn.innerHTML = `<svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>`;
            } else {
                stopBtn.classList.add('hidden');
                sendBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-0.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd" /></svg>`;
                messageInput.focus();
            }
        }

        function createMessageElement(role, content) {
            const div = document.createElement('div');
            // Stylized bubbles handling
            const isUser = role === 'user';
            div.className = `flex gap-4 max-w-4xl mx-auto w-full group animate-fade-in ${isUser ? 'flex-row-reverse' : ''}`;
            div.dataset.role = role;
            
            const avatar = document.createElement('div');
            avatar.className = `w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center text-white text-xs shadow-md mt-1 ${isUser ? 'bg-indigo-500 ring-2 ring-indigo-500/20' : 'bg-slate-800 border border-slate-600'}`;
            
            if (isUser) {
                avatar.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" /></svg>`;
            } else {
                avatar.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-emerald-400" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 5.522 4.477 10 10 10s10-4.478 10-10C22 6.477 17.522 2 12 2zm1.25 15.5a1.25 1.25 0 11-2.5 0 1.25 1.25 0 012.5 0zm-.8-2.6a1 1 0 01-1-.87L11.4 8h1.2l-.05 6.03a1 1 0 01-.1.37z" clip-rule="evenodd" /></svg>`;
            }
            
            const contentContainer = document.createElement('div');
            // Bubble wrapping
            contentContainer.className = `flex flex-col max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`;
            
            const textBubble = document.createElement('div');
            textBubble.className = `px-5 py-3.5 rounded-3xl ${isUser ? 'bg-indigo-500 text-white rounded-br-sm shadow-indigo-500/10' : 'bg-slate-800 border border-slate-700/60 rounded-bl-sm shadow-sm'}`;
            
            const textDiv = document.createElement('div');
            textDiv.className = `message-content markdown-body text-[15px] ${isUser ? '!text-white' : 'text-slate-200'}`;
            
            if (isUser) {
                textDiv.textContent = content;
            } else if (content === '') {
                textDiv.innerHTML = '<div class="typing-indicator"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';
            } else {
                textDiv.innerHTML = marked.parse(content);
            }
            
            textBubble.appendChild(textDiv);
            contentContainer.appendChild(textBubble);
            
            div.appendChild(avatar);
            div.appendChild(contentContainer);
            
            return { element: div, textDiv };
        }

        async function sendMessage() {
            const text = messageInput.value.trim();
            if (!text) return;
            
            messageInput.value = '';
            adjustTextareaHeight();
            emptyState.style.display = 'none';
            setUIGenerationState(true);
            
            const { element: userElement } = createMessageElement('user', text);
            chatContainer.appendChild(userElement);
            messages.push({ role: 'user', content: text });
            
            const { element: botElement, textDiv: botTextDiv } = createMessageElement('assistant', '');
            chatContainer.appendChild(botElement);
            
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            
            const isStreaming = streamToggle.checked;
            abortController = new AbortController();
            const apiKey = apiKeyInput.value.trim();
            const headers = {
                'Content-Type': 'application/json',
                ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
            };
            
            try {
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({ messages, stream: isStreaming }),
                    signal: abortController.signal
                });
                
                if (!response.ok) {
                    let errMsg = `HTTP ${response.status}`;
                    try { errMsg = (await response.json()).detail || errMsg; } catch(e) {}
                    botTextDiv.innerHTML = `<span class="text-rose-400 font-medium">Error: ${errMsg}</span>`;
                    messages.pop();
                    setUIGenerationState(false);
                    showError(errMsg);
                    return;
                }
                
                botTextDiv.innerHTML = '';
                let fullResponseText = "";
                
                if (isStreaming) {
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder('utf-8');
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        
                        const chunk = decoder.decode(value, { stream: true });
                        const lines = chunk.split('\\n');
                        
                        for (const line of lines) {
                            if (line.startsWith('data: ') && line !== 'data: [DONE]') {
                                try {
                                    const data = JSON.parse(line.slice(6));
                                    fullResponseText += data.choices[0]?.delta?.content || '';
                                    botTextDiv.innerHTML = marked.parse(fullResponseText);
                                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'auto' });
                                } catch (e) {}
                            }
                        }
                    }
                } else {
                    const data = await response.json();
                    fullResponseText = data.choices[0]?.message?.content || '';
                    botTextDiv.innerHTML = marked.parse(fullResponseText);
                }
                messages.push({ role: 'assistant', content: fullResponseText });
                
            } catch (err) {
                if (err.name !== 'AbortError') {
                    botTextDiv.innerHTML = `<span class="text-rose-400 font-medium">Failed to connect.</span>`;
                    showError("Connection failed");
                    messages.pop(); 
                }
            } finally {
                if (isGenerating) setUIGenerationState(false);
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }
        }
    </script>
</body>
</html>
"""

@router.get("/chat", response_class=HTMLResponse)
async def chat_playground(request: Request):
    """
    Returns the built-in HTML/JS web playground for local or remote usage.
    """
    return PLAYGROUND_HTML

@router.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
async def chat_completions(request: ChatRequest):
    state = get_global_state()
    
    # Precedence: config.model > request.model > "openrun"
    model_name = getattr(state.config, "model", None) or request.model or "openrun"
    
    # Extract messages directly
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    if request.stream:
        return StreamingResponse(
            stream_response(messages),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"}
        )

    # Call inference layer
    response_text = generate_response(messages)
    
    # Calculate token usage (exact if tokenizer available, else approximate)
    prompt_tokens = 0
    completion_tokens = 0
    
    if hasattr(state, "adapter") and hasattr(state.adapter, "tokenizer") and hasattr(state.adapter.tokenizer, "encode"):
        prompt_tokens = sum(len(state.adapter.tokenizer.encode(m["content"])) for m in messages)
        completion_tokens = len(state.adapter.tokenizer.encode(response_text))
    else:
        # 1 word ~ 1.3 tokens heuristic
        prompt_tokens = int(sum(len(m["content"].split()) * 1.3 for m in messages))
        completion_tokens = int(len(response_text.split()) * 1.3)
        
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }
    }
