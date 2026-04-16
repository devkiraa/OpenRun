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
    <title>OpenRun Web Playground</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .markdown-body pre { background-color: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; margin-top: 0.5rem; margin-bottom: 0.5rem; font-family: monospace; }
        .markdown-body code { background-color: rgba(27,31,35,0.05); border-radius: 3px; padding: 0.2em 0.4em; }
        .markdown-body pre code { background-color: transparent; padding: 0; }
        .message-content { white-space: pre-wrap; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; line-height: 1.5; }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #6b7280; }
        @keyframes blink { 0% { opacity: 0.2; } 20% { opacity: 1; } 100% { opacity: 0.2; } }
        .recording span { animation-name: blink; animation-duration: 1.4s; animation-iteration-count: infinite; animation-fill-mode: both; font-size: 24px; line-height: 10px;}
        .recording span:nth-child(2) { animation-delay: 0.2s; }
        .recording span:nth-child(3) { animation-delay: 0.4s; }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 h-screen flex flex-col font-sans">
    
    <!-- Top Bar -->
    <header class="bg-gray-800 border-b border-gray-700 px-6 py-3 flex justify-between items-center shadow-sm z-10 flex-shrink-0">
        <div class="flex items-center gap-3">
            <div class="h-8 w-8 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
                </svg>
            </div>
            <div>
                <h1 class="text-lg font-bold text-gray-50 tracking-wide">OpenRun <span class="text-cyan-400">Playground</span></h1>
                <div class="text-xs text-gray-400 font-medium flex items-center gap-1.5">
                    <span class="h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]"></span>
                    Connected: <span id="model-name-display" class="text-gray-300 font-mono text-[10px] bg-gray-700 px-1 py-0.5 rounded">Loading...</span>
                </div>
            </div>
        </div>
        
        <div class="flex items-center gap-4 bg-gray-900/50 p-1.5 rounded-lg border border-gray-700/50">
            <div class="flex flex-col items-end px-2">
                <label for="api-key" class="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-0.5">API Key (Optional)</label>
                <input type="password" id="api-key" placeholder="sk-..." class="bg-gray-800 border hidden lg:block border-gray-700 text-gray-200 text-xs rounded px-2.5 py-1 focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500 outline-none w-48 font-mono placeholder-gray-600 transition-all">
            </div>
            
            <div class="h-6 w-px bg-gray-700 hidden sm:block"></div>
            
            <button id="clear-btn" class="text-gray-400 hover:text-red-400 transition-colors p-1.5 rounded hover:bg-gray-800" title="Clear Chat">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
            </button>
        </div>
    </header>

    <!-- Chat Container -->
    <main id="chat-container" class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scroll-smooth pb-32">
        <!-- Initial empty state -->
        <div id="empty-state" class="h-full flex flex-col items-center justify-center text-gray-500 space-y-4 animate-fade-in relative z-0">
            <div class="h-16 w-16 bg-gray-800 rounded-2xl flex items-center justify-center border border-gray-700 shadow-xl mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
            </div>
            <h2 class="text-xl font-medium text-gray-300">How can I help you today?</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full mt-8 opacity-70">
                <button class="suggestion-btn text-left p-4 rounded-xl border border-gray-700 bg-gray-800/50 hover:bg-gray-800 transition-all hover:border-gray-600 group">
                    <div class="font-medium text-gray-300 mb-1 group-hover:text-cyan-400 transition-colors">Write a Python script</div>
                    <div class="text-sm text-gray-500">to scrape data from a website</div>
                </button>
                <button class="suggestion-btn text-left p-4 rounded-xl border border-gray-700 bg-gray-800/50 hover:bg-gray-800 transition-all hover:border-gray-600 group">
                    <div class="font-medium text-gray-300 mb-1 group-hover:text-cyan-400 transition-colors">Explain quantum computing</div>
                    <div class="text-sm text-gray-500">as if I am 5 years old</div>
                </button>
            </div>
        </div>
    </main>

    <!-- Bottom Input Area -->
    <div class="absolute bottom-0 left-0 w-full bg-gradient-to-t from-gray-900 via-gray-900 to-transparent pt-10 pb-6 px-4 sm:px-6">
        <div class="max-w-4xl mx-auto relative">
            <div id="error-toast" class="absolute -top-12 left-1/2 -translate-x-1/2 bg-red-500/90 text-white px-4 py-2 rounded-lg text-sm shadow-lg border border-red-400 opacity-0 transition-opacity pointer-events-none flex items-center gap-2 font-medium backdrop-blur-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <span id="error-msg"></span>
            </div>
            
            <!-- Stop Generation Button -->
            <div class="flex justify-center w-full absolute -top-14 pointer-events-none">
                <button id="stop-btn" class="hidden pointer-events-auto bg-gray-800 hover:bg-gray-700 border border-gray-600 text-gray-300 text-xs px-4 py-1.5 rounded-full shadow-lg transition-all items-center gap-2 backdrop-blur-sm shadow-black/50">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd" />
                    </svg>
                    Stop generating
                </button>
            </div>

            <div class="relative bg-gray-800 rounded-2xl border border-gray-700 shadow-2xl focus-within:border-gray-500 focus-within:ring-1 focus-within:ring-gray-500 transition-all flex flex-col pb-12">
                <textarea id="message-input" rows="1" class="w-full bg-transparent text-gray-100 placeholder-gray-500 px-4 py-4 rounded-2xl focus:outline-none resize-none max-h-48 overflow-y-auto leading-relaxed" placeholder="Message OpenRun..." autofocus></textarea>
                
                <div class="absolute bottom-2.5 right-2 sm:right-3 flex items-center gap-1.5">
                    <label class="flex items-center gap-1.5 px-2 py-1.5 text-xs text-gray-400 bg-gray-900/50 rounded pointer-events-auto hover:bg-gray-700 transition cursor-pointer border border-gray-700/50">
                        <input type="checkbox" id="stream-toggle" class="rounded bg-gray-800 border-gray-600 text-cyan-500 focus:ring-offset-gray-900 focus:ring-cyan-600 cursor-pointer w-3 h-3" checked>
                        Stream
                    </label>
                    <button id="send-btn" class="bg-white hover:bg-gray-200 text-gray-900 h-8 w-8 rounded-lg flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed transform active:scale-95 shadow-md shadow-white/10" disabled>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-0.5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="text-center mt-2.5 text-[10px] text-gray-500">
                OpenRun API Server • Local Execution
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        // Use relative path for all API calls to automatically support Cloudflare Tunnels and ngrok!
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

        // Fetch global state to get model name
        async function fetchHealth() {
            try {
                const res = await fetch(HEALTH_URL);
                if (res.ok) {
                    const data = await res.json();
                    modelNameDisplay.textContent = data.model || "Unknown";
                }
            } catch (e) {
                modelNameDisplay.textContent = "Offline";
                modelNameDisplay.classList.add("text-red-400");
                modelNameDisplay.parentElement.querySelector('span').classList.replace("bg-green-500", "bg-red-500");
            }
        }
        fetchHealth();

        // Configure marked.js to use Tailwind typography styling basically
        marked.setOptions({
            breaks: true,
            gfm: true
        });

        // Setup suggestion buttons
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const text = btn.querySelector('.font-medium').textContent + ' ' + btn.querySelector('.text-sm').textContent;
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
                
                // Add aborted message
                const lastMsg = chatContainer.lastElementChild;
                if (lastMsg && lastMsg.dataset.role === 'assistant') {
                    const contentDiv = lastMsg.querySelector('.message-content');
                    if (contentDiv.querySelector('.recording')) {
                         contentDiv.querySelector('.recording').remove();
                    }
                    if (contentDiv.innerHTML.trim() === '') {
                        contentDiv.innerHTML = '<em class="text-gray-500">Generation stopped.</em>';
                    }
                }
            }
        });

        clearBtn.addEventListener('click', () => {
            if (isGenerating) return;
            messages = [];
            
            // Remove all chat messages
            const children = Array.from(chatContainer.children);
            children.forEach(child => {
                if (child.id !== 'empty-state') {
                    child.remove();
                }
            });
            
            emptyState.style.display = 'flex';
        });

        function showError(msg) {
            errorMsg.textContent = msg;
            errorToast.classList.remove('opacity-0');
            setTimeout(() => {
                errorToast.classList.add('opacity-0');
            }, 5000);
        }
        
        function setUIGenerationState(generating) {
            isGenerating = generating;
            sendBtn.disabled = generating || messageInput.value.trim() === '';
            messageInput.disabled = generating;
            
            if (generating) {
                stopBtn.classList.remove('hidden');
                setTimeout(() => stopBtn.classList.remove('opacity-0'), 10);
                
                // Replace send button icon with a spinner
                sendBtn.innerHTML = `<svg class="animate-spin h-5 w-5 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>`;
            } else {
                stopBtn.classList.add('hidden');
                
                // Restore send button icon
                sendBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-0.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd" /></svg>`;
                messageInput.focus();
            }
        }

        function createMessageElement(role, content) {
            const div = document.createElement('div');
            div.className = `flex gap-4 max-w-4xl mx-auto w-full group animate-fade-in px-4 py-2 rounded-xl border border-transparent hover:bg-gray-800/30 transition-colors ${role === 'user' ? '' : 'bg-gray-800/20'}`;
            div.dataset.role = role;
            
            const avatar = document.createElement('div');
            avatar.className = `w-8 h-8 flex-shrink-0 rounded flex items-center justify-center text-white text-xs font-bold shadow-sm ${role === 'user' ? 'bg-indigo-500' : 'bg-gradient-to-br from-emerald-400 to-cyan-500'}`;
            
            if (role === 'user') {
                avatar.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" /></svg>`;
            } else {
                avatar.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" /></svg>`;
            }
            
            const contentContainer = document.createElement('div');
            contentContainer.className = 'flex-1 min-w-0 pt-1 pb-2';
            
            const nameDiv = document.createElement('div');
            nameDiv.className = 'font-semibold text-xs text-gray-400 mb-1 tracking-wide uppercase flex items-center gap-2';
            if (role === 'user') {
                nameDiv.textContent = 'You';
            } else {
                nameDiv.innerHTML = `Model <span class="bg-gray-700 px-1.5 py-px rounded text-[9px] text-gray-300 normal-case tracking-normal">${modelNameDisplay.textContent}</span>`;
            }
            
            const textDiv = document.createElement('div');
            textDiv.className = 'message-content markdown-body text-[15px]';
            
            if (role === 'user') {
                textDiv.textContent = content; // Safe against XSS for user input
            } else if (content === '') {
                textDiv.innerHTML = '<span class="recording font-bold text-gray-500 tracking-widest text-lg h-5 inline-block"><span>.</span><span>.</span><span>.</span></span>';
            } else {
                textDiv.innerHTML = marked.parse(content);
            }
            
            contentContainer.appendChild(nameDiv);
            contentContainer.appendChild(textDiv);
            div.appendChild(avatar);
            div.appendChild(contentContainer);
            
            return { element: div, textDiv };
        }

        async function sendMessage() {
            const text = messageInput.value.trim();
            if (!text) return;
            
            // UI Updates
            messageInput.value = '';
            adjustTextareaHeight();
            emptyState.style.display = 'none';
            setUIGenerationState(true);
            
            // Add user message to UI
            const { element: userElement } = createMessageElement('user', text);
            chatContainer.appendChild(userElement);
            
            // Add to message history
            messages.push({ role: 'user', content: text });
            
            // Prepare assistant response element
            const { element: botElement, textDiv: botTextDiv } = createMessageElement('assistant', '');
            chatContainer.appendChild(botElement);
            
            // Scroll to bottom
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
            
            // Setup fetch
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
                    body: JSON.stringify({
                        messages: messages,
                        stream: isStreaming
                    }),
                    signal: abortController.signal
                });
                
                if (!response.ok) {
                    let errMsg = `Error ${response.status}`;
                    try {
                        const errJson = await response.json();
                        errMsg = errJson.detail || errMsg;
                    } catch(e) {}
                    
                    botTextDiv.innerHTML = `<span class="text-red-400 font-medium">${errMsg}</span>`;
                    messages.pop(); // Remove user message from history on error
                    setUIGenerationState(false);
                    showError(errMsg);
                    return;
                }
                
                // Remove the recording animation
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
                                    const delta = data.choices[0]?.delta?.content || '';
                                    fullResponseText += delta;
                                    botTextDiv.innerHTML = marked.parse(fullResponseText);
                                    
                                    // Keep trailing space scrolled
                                    window.scrollTo({
                                        top: document.body.scrollHeight,
                                        behavior: 'auto'
                                    });
                                } catch (e) {
                                    // Parse error on incomplete chunk
                                }
                            }
                        }
                    }
                } else {
                    const data = await response.json();
                    fullResponseText = data.choices[0]?.message?.content || '';
                    botTextDiv.innerHTML = marked.parse(fullResponseText);
                }
                
                // Add to history
                messages.push({ role: 'assistant', content: fullResponseText });
                
            } catch (err) {
                if (err.name === 'AbortError') {
                    // Handled entirely by the stop button click
                } else {
                    botTextDiv.innerHTML = `<span class="text-red-400 font-medium">Failed to connect to the OpenRun Server.</span>`;
                    showError("Connection failed");
                    messages.pop(); 
                }
            } finally {
                if (isGenerating) {
                    setUIGenerationState(false);
                }
            }
            
            // Final scroll
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
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
