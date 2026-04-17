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
import threading
from openrun.models.registry import PREDEFINED_MODELS

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
        body {
            font-family: 'Inter', sans-serif;
            background: #f7f7f8;
            color: #202123;
        }

        input, select, button, textarea {
            font-family: 'Inter', sans-serif;
        }

        .app-shell {
            height: 100vh;
            display: grid;
            grid-template-columns: 250px 1fr;
            gap: 0;
        }

        .sidebar {
            border-right: 1px solid #e5e7eb;
            background: #ffffff;
            padding: 14px 10px;
            overflow: auto;
        }

        .sidebar-item {
            width: 100%;
            text-align: left;
            font-size: 12px;
            padding: 8px 10px;
            border-radius: 8px;
            color: #4b5563;
            margin-bottom: 4px;
            border: 1px solid transparent;
            transition: all 0.15s ease;
        }

        .sidebar-item:hover {
            background: #f9fafb;
            border-color: #e5e7eb;
            color: #111827;
        }

        .sidebar-item.active {
            background: #ecfeff;
            color: #0f766e;
            border-color: #99f6e4;
            font-weight: 600;
        }

        .main-area {
            display: flex;
            flex-direction: column;
            min-width: 0;
            background: #f8fafc;
        }

        .top-controls {
            display: grid;
            gap: 6px;
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 8px;
            min-width: 560px;
        }

        .top-controls-row {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .status-chip {
            font-size: 10px;
            color: #4b5563;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 9999px;
            padding: 2px 8px;
            white-space: nowrap;
        }

        .markdown-body pre { background-color: #f1f5f9; color: #0f172a; padding: 1rem; border-radius: 0.75rem; overflow-x: auto; margin: 1rem 0; box-shadow: inset 0 0 0 1px #dbe2ea; position: relative; }
        .markdown-body code { background-color: #eef2ff; border-radius: 0.25rem; padding: 0.2em 0.4em; }
        .markdown-body pre code { background-color: transparent; padding: 0; }
        .message-content { white-space: pre-wrap; line-height: 1.6; }

        .copy-button { position: absolute; top: 0.5rem; right: 0.5rem; background: #e2e8f0; border: none; color: #334155; padding: 0.25rem 0.5rem; border-radius: 0.375rem; font-size: 0.75rem; cursor: pointer; opacity: 0; transition: all 0.2s; }
        .markdown-body pre:hover .copy-button { opacity: 1; }
        .copy-button:hover { background: #cbd5e1; color: #0f172a; }

        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

        .typing-indicator { display: inline-flex; align-items: center; gap: 4px; height: 24px; padding: 0 4px; }
        .dot { width: 6px; height: 6px; background-color: #64748b; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.5; } 40% { transform: scale(1); opacity: 1; } }

        @media (max-width: 900px) {
            .app-shell { grid-template-columns: 1fr; }
            .sidebar { display: none; }
            .top-controls { min-width: 0; width: 100%; }
        }
    </style>
</head>
<body class="h-screen antialiased">
<div class="app-shell">
    <aside class="sidebar">
        <div class="text-sm font-semibold text-gray-900 mb-4 px-2">Playground</div>
        <button id="new-chat-btn" class="sidebar-item">+ New Chat</button>
        <div class="text-[10px] uppercase tracking-wide text-gray-400 mt-4 mb-2 px-2">My Chats</div>
        <div id="chats-list"></div>
    </aside>

    <div class="main-area">
    
    <!-- Top Nav -->
    <header class="bg-white border-b border-gray-200 px-5 py-3 flex justify-between items-center shadow-sm z-20 flex-shrink-0 sticky top-0">
        <div class="flex items-center gap-3">
            <div class="h-9 w-9 bg-gradient-to-br from-cyan-500 to-emerald-400 rounded-xl flex items-center justify-center shadow-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                    <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 5.522 4.477 10 10 10s10-4.478 10-10C22 6.477 17.522 2 12 2zm1.25 15.5a1.25 1.25 0 11-2.5 0 1.25 1.25 0 012.5 0zm-.8-2.6a1 1 0 01-1-.87L11.4 8h1.2l-.05 6.03a1 1 0 01-.1.37z" clip-rule="evenodd" />
                </svg>
            </div>
            <div>
                <h1 class="text-base font-semibold text-gray-900 tracking-tight">OpenRun <span class="text-cyan-600 font-semibold">Studio</span></h1>
                <div class="text-[11px] text-gray-500 font-medium flex items-center gap-1.5 mt-0.5">
                    <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                    Running: <span id="model-name-display" class="text-gray-700 font-mono">No model loaded</span>
                </div>
            </div>
        </div>
        
        <div class="top-controls">
            <div class="top-controls-row">
                <select id="model-select" class="bg-white border border-gray-300 text-gray-800 text-xs rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-cyan-500/30 focus:border-cyan-500 outline-none w-44 sm:w-56">
                    <option value="">Select model...</option>
                </select>

                <input type="password" id="hf-token" placeholder="HF token (optional)" class="bg-white border border-gray-300 text-gray-800 text-xs rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-cyan-500/30 focus:border-cyan-500 outline-none w-52 font-mono placeholder-gray-400 transition-all">

                <button id="load-model-btn" class="bg-cyan-500 hover:bg-cyan-400 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-all">
                    Load Model
                </button>

                <button id="clear-btn" class="text-gray-400 hover:text-rose-500 transition-colors p-2 rounded-lg hover:bg-gray-100" title="Clear Chat">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
            </div>

            <div class="top-controls-row">
                <input type="password" id="api-key" placeholder="API Key (Optional)..." class="bg-white border border-gray-300 text-gray-800 text-xs rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-cyan-500/30 focus:border-cyan-500 outline-none w-64 font-mono placeholder-gray-400 transition-all">
                <span id="model-load-status" class="status-chip">No model loaded</span>
                <span id="live-metrics" class="status-chip">Tokens: 0 | TPS: 0</span>
            </div>
        </div>

    </header>

    <section id="model-gate" class="flex-1 flex items-center justify-center p-6 sm:p-10 bg-[#f8fafc]">
        <div class="max-w-xl w-full rounded-2xl border border-cyan-100 bg-white shadow-sm p-6 sm:p-8 text-center">
            <div class="h-12 w-12 mx-auto rounded-xl bg-cyan-50 border border-cyan-100 flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 11c0-1.657 1.343-3 3-3s3 1.343 3 3v5H6v-5c0-1.657 1.343-3 3-3s3 1.343 3 3zm0 0V7m0 0a2 2 0 100-4 2 2 0 000 4z" />
                </svg>
            </div>
            <h2 class="text-xl sm:text-2xl font-semibold text-gray-900">Load a model to start chat</h2>
            <p class="mt-2 text-sm text-gray-600">Select a model from the top dropdown and click <span class="font-semibold text-cyan-700">Load Model</span>. The chat interface will unlock once the model is ready.</p>
        </div>
    </section>

    <!-- Chat Area -->
    <main id="chat-container" class="hidden flex-1 overflow-y-auto p-4 sm:p-8 space-y-6 scroll-smooth bg-[#f8fafc]">
        <!-- Empty State -->
        <div id="empty-state" class="h-full flex flex-col items-center justify-center text-gray-500 space-y-6 animate-fade-in relative z-0">
            <div class="h-20 w-20 bg-white rounded-[2rem] flex items-center justify-center border border-gray-200 shadow-sm mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
            </div>
            <h2 class="text-2xl font-semibold text-gray-900">How can I help you today?</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl w-full mt-8">
                <button class="suggestion-btn text-left p-5 rounded-2xl border border-gray-200 bg-white hover:bg-cyan-50 hover:border-cyan-200 transition-all group shadow-sm">
                    <div class="font-semibold text-gray-800 mb-1 group-hover:text-cyan-700 transition-colors">Write a Python script</div>
                    <div class="text-sm text-gray-500">to scrape data from a website</div>
                </button>
                <button class="suggestion-btn text-left p-5 rounded-2xl border border-gray-200 bg-white hover:bg-cyan-50 hover:border-cyan-200 transition-all group shadow-sm">
                    <div class="font-semibold text-gray-800 mb-1 group-hover:text-cyan-700 transition-colors">Explain quantum computing</div>
                    <div class="text-sm text-gray-500">as if I am 5 years old</div>
                </button>
            </div>
        </div>
    </main>

    <!-- Input Footer -->
    <div id="chat-input-footer" class="hidden border-t border-gray-200 bg-white/95 backdrop-blur-sm px-4 sm:px-6 py-4 pointer-events-auto">
        <div class="max-w-4xl mx-auto relative">
            
            <div id="error-toast" class="absolute -top-14 left-1/2 -translate-x-1/2 bg-rose-500/90 text-white px-5 py-2.5 rounded-xl text-sm shadow-xl border border-rose-400 opacity-0 transition-all duration-300 pointer-events-none flex items-center gap-2 font-medium backdrop-blur-md translate-y-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <span id="error-msg"></span>
            </div>
            
            <!-- Stop Generating -->
            <div class="flex justify-center w-full absolute -top-16 pointer-events-none">
                <button id="stop-btn" class="hidden pointer-events-auto bg-white hover:bg-gray-50 border border-gray-300 text-gray-700 text-xs font-semibold px-4 py-2 rounded-full shadow-sm transition-all items-center gap-2 backdrop-blur-md">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-rose-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd" />
                    </svg>
                    Stop generating
                </button>
            </div>

            <!-- Text Box -->
            <div class="relative bg-white rounded-2xl border border-gray-300 shadow-sm focus-within:border-cyan-500/60 focus-within:ring-2 focus-within:ring-cyan-500/20 transition-all flex flex-col pb-12">
                <textarea id="message-input" rows="1" class="w-full bg-transparent text-gray-900 placeholder-gray-500 px-5 pt-4 pb-2 rounded-2xl focus:outline-none resize-none max-h-48 overflow-y-auto leading-relaxed text-[15px]" placeholder="Send a message..." autofocus></textarea>
                
                <div class="absolute bottom-3 right-3 flex items-center gap-2">
                    <label class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-100 rounded-lg pointer-events-auto hover:bg-gray-200 transition cursor-pointer border border-gray-200">
                        <input type="checkbox" id="stream-toggle" class="rounded bg-white border-gray-300 text-cyan-500 focus:ring-offset-white focus:ring-cyan-500 cursor-pointer w-3.5 h-3.5" checked>
                        Stream
                    </label>
                    <button id="send-btn" class="bg-cyan-500 hover:bg-cyan-400 text-white h-9 w-9 rounded-[10px] flex items-center justify-center transition-all disabled:opacity-40 disabled:hover:bg-cyan-500 disabled:cursor-not-allowed transform active:scale-95 shadow-sm" disabled>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-0.5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="text-center mt-2 text-[11px] font-medium text-gray-500">
                OpenRun Studio | OpenAI-compatible backend |
                <a href="/v1/chat/completions" target="_blank" class="text-cyan-600 hover:underline">/v1/chat/completions</a> |
                <a href="/models" target="_blank" class="text-cyan-600 hover:underline">/models</a> |
                <a href="/v1/models" target="_blank" class="text-cyan-600 hover:underline">/v1/models</a> |
                <a href="/models/catalog" target="_blank" class="text-cyan-600 hover:underline">/models/catalog</a> |
                <a href="/v1/models/catalog" target="_blank" class="text-cyan-600 hover:underline">/v1/models/catalog</a> |
                <a href="/models/status" target="_blank" class="text-cyan-600 hover:underline">/models/status</a> |
                <a href="/v1/models/status" target="_blank" class="text-cyan-600 hover:underline">/v1/models/status</a> |
                <a href="/v1/chats" target="_blank" class="text-cyan-600 hover:underline">/v1/chats</a>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        const API_URL = '/v1/chat/completions';
        const HEALTH_URL = '/';
        const MODELS_URL = '/models';
        const MODELS_CATALOG_URL = '/models/catalog';
        const MODEL_STATUS_URL = '/models/status';
        const MODEL_LOAD_URL = '/models/load';
        const CHATS_URL = '/v1/chats';
        const METRICS_LIVE_URL = '/v1/metrics/live';
        
        let messages = [];
        let isGenerating = false;
        let abortController = null;
        let modelReady = false;
        let modelStatusPoll = null;
        let currentChatId = null;
        let metricsPoll = null;
        
        const chatContainer = document.getElementById('chat-container');
        const modelGate = document.getElementById('model-gate');
        const chatInputFooter = document.getElementById('chat-input-footer');
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        const stopBtn = document.getElementById('stop-btn');
        const clearBtn = document.getElementById('clear-btn');
        const emptyState = document.getElementById('empty-state');
        const apiKeyInput = document.getElementById('api-key');
        const hfTokenInput = document.getElementById('hf-token');
        const modelSelect = document.getElementById('model-select');
        const loadModelBtn = document.getElementById('load-model-btn');
        const modelLoadStatus = document.getElementById('model-load-status');
        const liveMetrics = document.getElementById('live-metrics');
        const chatsList = document.getElementById('chats-list');
        const newChatBtn = document.getElementById('new-chat-btn');
        const streamToggle = document.getElementById('stream-toggle');
        const errorToast = document.getElementById('error-toast');
        const errorMsg = document.getElementById('error-msg');
        const modelNameDisplay = document.getElementById('model-name-display');

        function updateModelAccessUI() {
            if (modelReady) {
                modelGate.classList.add('hidden');
                chatContainer.classList.remove('hidden');
                chatInputFooter.classList.remove('hidden');
                newChatBtn.disabled = false;
                newChatBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                return;
            }

            modelGate.classList.remove('hidden');
            chatContainer.classList.add('hidden');
            chatInputFooter.classList.add('hidden');
            newChatBtn.disabled = true;
            newChatBtn.classList.add('opacity-50', 'cursor-not-allowed');
        }

        function updateSendButtonState() {
            sendBtn.disabled = isGenerating || !modelReady || messageInput.value.trim() === '';
            updateModelAccessUI();
        }

        function clearChatView() {
            messages = [];
            Array.from(chatContainer.children).forEach(child => { if (child.id !== 'empty-state') child.remove(); });
            emptyState.style.display = 'flex';
        }

        function renderExistingMessages(chatMessages) {
            clearChatView();
            for (const msg of (chatMessages || [])) {
                const { element } = createMessageElement(msg.role, msg.content || '');
                chatContainer.appendChild(element);
            }
            if ((chatMessages || []).length > 0) {
                emptyState.style.display = 'none';
            }
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'auto' });
        }

        async function fetchChats() {
            try {
                const apiKey = apiKeyInput.value.trim();
                const headers = {
                    ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
                };
                const res = await fetch(CHATS_URL, { headers });
                if (!res.ok) {
                    showError(`Chats API error (${res.status})`);
                    return;
                }
                const data = await res.json();
                const chats = data.data || [];

                chatsList.innerHTML = '';
                chats.forEach(chat => {
                    const btn = document.createElement('button');
                    btn.className = `sidebar-item ${chat.id === currentChatId ? 'active' : ''}`;
                    btn.textContent = chat.title || 'Untitled Chat';
                    btn.title = chat.title || 'Untitled Chat';
                    btn.addEventListener('click', () => openChat(chat.id));
                    chatsList.appendChild(btn);
                });

                if (!currentChatId && chats.length) {
                    await openChat(chats[0].id);
                }
                updateModelAccessUI();
            } catch (err) {
                showError('Unable to fetch chats');
            }
        }

        async function createChat(title = 'New Chat') {
            const apiKey = apiKeyInput.value.trim();
            const headers = {
                'Content-Type': 'application/json',
                ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
            };
            const res = await fetch(CHATS_URL, {
                method: 'POST',
                headers,
                body: JSON.stringify({ title })
            });
            if (!res.ok) {
                showError('Failed to create chat');
                return null;
            }
            const data = await res.json();
            const chat = data.chat;
            currentChatId = chat?.id || null;
            clearChatView();
            await fetchChats();
            return currentChatId;
        }

        async function openChat(chatId) {
            if (!chatId) return;
            if (!modelReady) return;
            const apiKey = apiKeyInput.value.trim();
            const headers = {
                ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
            };
            const res = await fetch(`${CHATS_URL}/${chatId}`, { headers });
            if (!res.ok) return;
            const data = await res.json();
            if (!data.ok) {
                showError(data.error || 'Failed to open chat');
                return;
            }
            currentChatId = chatId;
            renderExistingMessages(data.chat?.messages || []);
            await fetchChats();
        }

        async function fetchLiveMetrics() {
            const apiKey = apiKeyInput.value.trim();
            const headers = {
                ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
            };
            const res = await fetch(METRICS_LIVE_URL, { headers });
            if (!res.ok) return;
            const data = await res.json();
            const m = data.data;
            if (!m) {
                liveMetrics.textContent = 'Tokens: 0 | TPS: 0';
                return;
            }
            liveMetrics.textContent = `Prompt: ${m.prompt_tokens} | Completion: ${m.completion_tokens} | TPS: ${m.tokens_per_sec}`;
        }

        async function fetchHealth() {
            try {
                const res = await fetch(HEALTH_URL);
                if (res.ok) {
                    const data = await res.json();
                    modelNameDisplay.textContent = data.model || "No model loaded";
                }
            } catch (e) {
                modelNameDisplay.textContent = "Offline";
                modelNameDisplay.classList.add("text-rose-400");
                modelNameDisplay.parentElement.querySelector('span').classList.replace("bg-emerald-400", "bg-rose-500");
            }
        }

        async function fetchModels() {
            try {
                const apiKey = apiKeyInput.value.trim();
                const headers = {
                    ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
                };
                // Always load available models from public catalog first.
                let catalogRes = await fetch(MODELS_CATALOG_URL);
                if (!catalogRes.ok) {
                    catalogRes = await fetch('/v1/models/catalog');
                }
                if (!catalogRes.ok) {
                    modelLoadStatus.textContent = 'Failed to fetch models';
                    showError(`Model catalog error (${catalogRes.status})`);
                    return;
                }
                const catalog = await catalogRes.json();

                // Enrich with loaded-state if available.
                let loadedMap = new Map();
                let loadingData = null;
                let stateRes = await fetch(MODELS_URL, { headers });
                if (!stateRes.ok) {
                    stateRes = await fetch('/v1/models', { headers });
                }
                if (stateRes.ok) {
                    const stateData = await stateRes.json();
                    loadingData = stateData.loading;
                    for (const m of (stateData.data || [])) {
                        loadedMap.set(m.id, !!m.loaded);
                    }
                }

                modelSelect.innerHTML = '<option value="">Select model...</option>';
                for (const item of catalog.data || []) {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.textContent = `${item.id} | ${item.size || 'N/A'} | Ctx ${item.context || 'N/A'} | ${item.speed || 'N/A'} | ${item.engine}`;
                    if (loadedMap.get(item.id)) {
                        option.selected = true;
                        modelReady = true;
                        modelLoadStatus.textContent = `Loaded: ${item.id}`;
                        modelNameDisplay.textContent = item.name || item.id;
                    }
                    modelSelect.appendChild(option);
                }

                if (loadingData?.status === 'loading' || loadingData?.status === 'queued') {
                    modelReady = false;
                    modelLoadStatus.textContent = `Loading ${formatLoadStatus(loadingData)}`;
                    loadModelBtn.disabled = true;
                    loadModelBtn.textContent = 'Loading...';
                    if (!modelStatusPoll) {
                        modelStatusPoll = setInterval(pollModelStatus, 1500);
                    }
                }

                updateSendButtonState();
            } catch (err) {
                modelLoadStatus.textContent = 'Failed to fetch models';
                showError('Unable to fetch model list');
            }
        }

        function formatLoadStatus(info) {
            const stage = info?.stage ? ` - ${info.stage}` : '';
            const progress = Number.isFinite(info?.progress) ? ` (${info.progress}%)` : '';
            const elapsed = Number.isFinite(info?.elapsed_seconds) ? ` - ${info.elapsed_seconds}s` : '';
            const message = info?.message ? ` - ${info.message}` : '';
            return `${info?.model_key || 'model'}${stage}${progress}${elapsed}${message}`;
        }

        async function pollModelStatus() {
            const apiKey = apiKeyInput.value.trim();
            const headers = {
                ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
            };
            let res = await fetch(MODEL_STATUS_URL, { headers });
            if (!res.ok) {
                res = await fetch('/v1/models/status', { headers });
            }
            if (!res.ok) {
                showError(`Model status API error (${res.status})`);
                return;
            }
            const status = await res.json();

            if (status.status === 'loading' || status.status === 'queued') {
                modelReady = false;
                modelLoadStatus.textContent = `Loading ${formatLoadStatus(status)}`;
                loadModelBtn.disabled = true;
                loadModelBtn.textContent = 'Loading...';
            } else if (status.status === 'ready') {
                modelReady = true;
                modelLoadStatus.textContent = `Loaded: ${status.model_key || status.loaded_model || 'model'} (${status.elapsed_seconds || 0}s)`;
                loadModelBtn.disabled = false;
                loadModelBtn.textContent = 'Load';
                if (modelStatusPoll) {
                    clearInterval(modelStatusPoll);
                    modelStatusPoll = null;
                }
                await fetchHealth();
                await fetchModels();
            } else if (status.status === 'error') {
                modelReady = false;
                modelLoadStatus.textContent = `Load failed: ${status.stage || 'failed'}`;
                loadModelBtn.disabled = false;
                loadModelBtn.textContent = 'Retry';
                if (status.error) showError(status.error);
                if (modelStatusPoll) {
                    clearInterval(modelStatusPoll);
                    modelStatusPoll = null;
                }
            }
            updateSendButtonState();
        }

        async function loadSelectedModel() {
            if (!modelSelect.value) {
                showError('Please select a model first');
                return;
            }

            const apiKey = apiKeyInput.value.trim();
            const headers = {
                'Content-Type': 'application/json',
                ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
            };
            const payload = {
                model_key: modelSelect.value,
                hf_token: hfTokenInput.value.trim() || null
            };

            let res = await fetch(MODEL_LOAD_URL, {
                method: 'POST',
                headers,
                body: JSON.stringify(payload)
            });
            if (res.status === 404) {
                res = await fetch('/v1/models/load', {
                    method: 'POST',
                    headers,
                    body: JSON.stringify(payload)
                });
            }

            const data = await res.json().catch(() => ({}));
            if (!res.ok || !data.ok) {
                showError(data.error || 'Failed to start loading model');
                return;
            }

            modelReady = false;
            modelLoadStatus.textContent = `Loading ${data.model_key} - queued (0%)`;
            updateSendButtonState();

            if (modelStatusPoll) clearInterval(modelStatusPoll);
            modelStatusPoll = setInterval(pollModelStatus, 1500);
            await pollModelStatus();
        }

        updateModelAccessUI();
        fetchHealth();
        fetchModels();
        fetchChats();
        fetchLiveMetrics();
        if (metricsPoll) clearInterval(metricsPoll);
        metricsPoll = setInterval(fetchLiveMetrics, 1500);

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
            updateSendButtonState();
        });

        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!sendBtn.disabled && !isGenerating) sendMessage();
            }
        });

        sendBtn.addEventListener('click', sendMessage);
        loadModelBtn.addEventListener('click', loadSelectedModel);
        newChatBtn.addEventListener('click', async () => {
            await createChat('New Chat');
            modelLoadStatus.textContent = 'New chat created';
        });
        apiKeyInput.addEventListener('change', async () => {
            await fetchModels();
            await fetchChats();
            await fetchLiveMetrics();
        });
        
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
            clearChatView();
            modelLoadStatus.textContent = 'Chat cleared';
        });

        function showError(msg) {
            errorMsg.textContent = msg;
            errorToast.classList.remove('opacity-0', 'translate-y-2');
            setTimeout(() => { errorToast.classList.add('opacity-0', 'translate-y-2'); }, 4000);
        }

        function stabilizePartialMarkdown(text) {
            if (!text) return '';
            let stable = text;
            const fenceCount = (stable.match(/```/g) || []).length;
            if (fenceCount % 2 === 1) {
                stable += '\n```';
            }
            return stable;
        }

        function renderStreamContent(textDiv, content, isFinal = false) {
            try {
                if (isFinal) {
                    textDiv.innerHTML = marked.parse(content || '');
                    return;
                }
                const stabilized = stabilizePartialMarkdown(content || '');
                textDiv.innerHTML = marked.parse(stabilized);
            } catch (_) {
                textDiv.textContent = content || '';
            }
        }

        function parseSSEEvents(buffer) {
            const events = [];
            const parts = buffer.split('\n\n');
            const remainder = parts.pop() || '';

            for (const part of parts) {
                const dataLines = [];
                for (const line of part.split('\n')) {
                    if (line.startsWith('data:')) {
                        dataLines.push(line.slice(5).trimStart());
                    }
                }
                if (dataLines.length) {
                    events.push(dataLines.join('\n'));
                }
            }

            return { events, remainder };
        }
        
        function setUIGenerationState(generating) {
            isGenerating = generating;
            messageInput.disabled = generating;
            
            if (generating) {
                stopBtn.classList.remove('hidden');
                sendBtn.innerHTML = `<svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>`;
            } else {
                stopBtn.classList.add('hidden');
                sendBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-0.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd" /></svg>`;
                messageInput.focus();
            }

            updateSendButtonState();
        }

        function createMessageElement(role, content) {
            const div = document.createElement('div');
            // Stylized bubbles handling
            const isUser = role === 'user';
            div.className = `flex gap-4 max-w-4xl mx-auto w-full group animate-fade-in ${isUser ? 'flex-row-reverse' : ''}`;
            div.dataset.role = role;
            
            const avatar = document.createElement('div');
            avatar.className = `w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center text-white text-xs shadow-sm mt-1 ${isUser ? 'bg-cyan-500 ring-2 ring-cyan-500/20' : 'bg-white border border-gray-300'}`;
            
            if (isUser) {
                avatar.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" /></svg>`;
            } else {
                avatar.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-cyan-600" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 5.522 4.477 10 10 10s10-4.478 10-10C22 6.477 17.522 2 12 2zm1.25 15.5a1.25 1.25 0 11-2.5 0 1.25 1.25 0 012.5 0zm-.8-2.6a1 1 0 01-1-.87L11.4 8h1.2l-.05 6.03a1 1 0 01-.1.37z" clip-rule="evenodd" /></svg>`;
            }
            
            const contentContainer = document.createElement('div');
            // Bubble wrapping
            contentContainer.className = `flex flex-col max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`;
            
            const textBubble = document.createElement('div');
            textBubble.className = `px-5 py-3.5 rounded-3xl ${isUser ? 'bg-cyan-500 text-white rounded-br-sm' : 'bg-white border border-gray-200 rounded-bl-sm shadow-sm'}`;
            
            const textDiv = document.createElement('div');
            textDiv.className = `message-content markdown-body text-[15px] ${isUser ? '!text-white' : 'text-gray-800'}`;
            
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
            if (!modelReady) {
                showError('Load a model first');
                return;
            }
            if (!currentChatId) {
                const created = await createChat('New Chat');
                if (!created) return;
            }
            
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
                    body: JSON.stringify({ messages, stream: isStreaming, chat_id: currentChatId }),
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
                    let sseBuffer = '';
                    let streamFinishReason = null;
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        
                        sseBuffer += decoder.decode(value, { stream: true });
                        const parsed = parseSSEEvents(sseBuffer);
                        sseBuffer = parsed.remainder;

                        for (const eventData of parsed.events) {
                            if (eventData === '[DONE]') {
                                continue;
                            }
                            try {
                                const data = JSON.parse(eventData);
                                const deltaContent = data.choices?.[0]?.delta?.content || '';
                                if (deltaContent) {
                                    fullResponseText += deltaContent;
                                    renderStreamContent(botTextDiv, fullResponseText, false);
                                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'auto' });
                                }

                                const reason = data.choices?.[0]?.finish_reason;
                                if (reason) {
                                    streamFinishReason = reason;
                                }

                                if (data.error?.message) {
                                    showError(data.error.message);
                                }
                            } catch (e) {
                                // keep buffering on partial/incomplete JSON frames
                            }
                        }
                    }

                    renderStreamContent(botTextDiv, fullResponseText, true);
                    if (streamFinishReason === 'cancelled') {
                        showError('Generation cancelled');
                    } else if (streamFinishReason === 'error') {
                        showError('Generation ended with an error');
                    }
                } else {
                    const data = await response.json();
                    fullResponseText = data.choices[0]?.message?.content || '';
                    botTextDiv.innerHTML = marked.parse(fullResponseText);
                }
                messages.push({ role: 'assistant', content: fullResponseText });
                await fetchChats();
                await fetchLiveMetrics();
                
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
    </div>
</div>
</body>
</html>
"""

@router.get("/chat", response_class=HTMLResponse)
async def chat_playground(request: Request):
    """
    Returns the built-in HTML/JS web playground for local or remote usage.
    """
    return PLAYGROUND_HTML


def _resolve_hf_token(optional_token: str | None = None) -> str | None:
    token = optional_token or os.getenv("HF_TOKEN")
    if token:
        return token

    try:
        from google.colab import userdata  # type: ignore
        token = userdata.get("HF_TOKEN")
    except Exception:
        token = None
    return token


def _set_loading_state(
    *,
    status: str,
    model_key: str | None = None,
    stage: str | None = None,
    message: str | None = None,
    progress: int | None = None,
    error: str | None = None,
):
    state = get_global_state()
    now = time.time()

    state.loading_status = status
    if model_key is not None:
        state.loading_model_key = model_key
    state.loading_stage = stage
    state.loading_message = message
    if progress is not None:
        state.loading_progress = max(0, min(100, int(progress)))
    state.loading_error = error

    if status in ("queued", "loading") and state.loading_started_at is None:
        state.loading_started_at = now
    if status in ("ready", "error", "idle"):
        if state.loading_started_at is None:
            state.loading_started_at = now
    state.loading_updated_at = now


def _loading_snapshot(state):
    elapsed = None
    if state.loading_started_at:
        elapsed = round(time.time() - state.loading_started_at, 1)

    return {
        "status": state.loading_status,
        "model_key": state.loading_model_key,
        "stage": state.loading_stage,
        "message": state.loading_message,
        "progress": state.loading_progress,
        "error": state.loading_error,
        "elapsed_seconds": elapsed,
        "updated_at": state.loading_updated_at,
    }


def _estimate_tokens(state, text: str) -> int:
    if not text:
        return 0
    if hasattr(state, "adapter") and state.adapter and hasattr(state.adapter, "tokenizer") and hasattr(state.adapter.tokenizer, "encode"):
        try:
            return len(state.adapter.tokenizer.encode(text))
        except Exception:
            pass
    return int(len(text.split()) * 1.3)


def _record_metrics(state, *, model_name: str, prompt_tokens: int, completion_tokens: int, duration_seconds: float, stream: bool, chat_id: str | None):
    total_tokens = prompt_tokens + completion_tokens
    tps = round((completion_tokens / duration_seconds), 2) if duration_seconds > 0 else 0.0
    metric = {
        "id": f"m-{uuid.uuid4().hex[:10]}",
        "created": int(time.time()),
        "model": model_name,
        "chat_id": chat_id,
        "stream": stream,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "duration_seconds": round(duration_seconds, 3),
        "tokens_per_sec": tps,
    }
    state.latest_metrics = metric
    state.metrics_history.append(metric)
    if len(state.metrics_history) > 200:
        state.metrics_history = state.metrics_history[-200:]

    state.metrics_totals["requests"] += 1
    state.metrics_totals["prompt_tokens"] += prompt_tokens
    state.metrics_totals["completion_tokens"] += completion_tokens
    state.metrics_totals["total_tokens"] += total_tokens
    state.metrics_totals["total_seconds"] += duration_seconds

    return metric


def _create_chat(state, title: str | None = None):
    chat_id = f"chat_{uuid.uuid4().hex[:10]}"
    now = int(time.time())
    chat = {
        "id": chat_id,
        "title": title or "New Chat",
        "created": now,
        "updated": now,
        "messages": [],
    }
    state.chats[chat_id] = chat
    state.chat_order.insert(0, chat_id)
    state.active_chat_id = chat_id
    return chat


def _chat_summary(chat: dict):
    return {
        "id": chat["id"],
        "title": chat["title"],
        "created": chat["created"],
        "updated": chat["updated"],
        "message_count": len(chat.get("messages", [])),
    }


def _load_selected_model(model_key: str, hf_token: str | None = None):
    state = get_global_state()
    _set_loading_state(
        status="loading",
        model_key=model_key,
        stage="preparing",
        message="Preparing model metadata",
        progress=5,
    )

    try:
        info = PREDEFINED_MODELS[model_key]
        engine = info.get("engine", "transformers")
        model_name = info["model"]

        if engine != "ollama":
            _set_loading_state(
                status="loading",
                model_key=model_key,
                stage="auth",
                message="Checking Hugging Face credentials",
                progress=12,
            )
            token = _resolve_hf_token(hf_token)
            if token:
                from huggingface_hub import login
                login(token)

        if engine == "transformers":
            _set_loading_state(
                status="loading",
                model_key=model_key,
                stage="initializing",
                message="Initializing Transformers adapter",
                progress=25,
            )
            from openrun.adapters.huggingface import HuggingFaceAdapter
            adapter = HuggingFaceAdapter(model_name)
        elif engine == "airllm":
            _set_loading_state(
                status="loading",
                model_key=model_key,
                stage="initializing",
                message="Initializing AirLLM adapter",
                progress=25,
            )
            from openrun.adapters.airllm import AirLLMAdapter
            adapter = AirLLMAdapter(model_name)
        else:
            _set_loading_state(
                status="loading",
                model_key=model_key,
                stage="connecting",
                message="Connecting to local Ollama runtime",
                progress=25,
            )
            from openrun.adapters.ollama import OllamaAdapter
            adapter = OllamaAdapter(model_name)

        _set_loading_state(
            status="loading",
            model_key=model_key,
            stage="loading_weights",
            message="Loading model weights into memory",
            progress=60,
        )

        adapter.load()
        state.adapter = adapter

        if state.config:
            state.config.model = model_name

        _set_loading_state(
            status="ready",
            model_key=model_key,
            stage="ready",
            message="Model ready for chat",
            progress=100,
            error=None,
        )
    except Exception as e:
        _set_loading_state(
            status="error",
            model_key=model_key,
            stage="failed",
            message="Model load failed",
            progress=100,
            error=str(e),
        )


@router.get("/models")
@router.get("/v1/models")
async def list_models():
    state = get_global_state()
    current_model = None
    if state.adapter and hasattr(state.adapter, "model_name"):
        current_model = state.adapter.model_name
    elif state.config and state.config.model:
        current_model = state.config.model

    data = []
    for key, info in PREDEFINED_MODELS.items():
        data.append({
            "id": key,
            "object": "model",
            "engine": info.get("engine", "transformers"),
            "name": info.get("model"),
            "size": info.get("size", "N/A"),
            "context": info.get("context", "N/A"),
            "speed": info.get("speed", "N/A"),
            "loaded": current_model == info.get("model"),
        })

    return {
        "object": "list",
        "data": data,
        "loading": _loading_snapshot(state),
    }


@router.get("/models/status")
@router.get("/v1/models/status")
async def model_loading_status():
    state = get_global_state()
    loaded_model = None
    if state.adapter and hasattr(state.adapter, "model_name"):
        loaded_model = state.adapter.model_name
    elif state.config:
        loaded_model = state.config.model

    return {
        **_loading_snapshot(state),
        "loaded_model": loaded_model,
    }


@router.get("/models/catalog")
@router.get("/v1/models/catalog")
async def model_catalog():
    data = []
    for key, info in PREDEFINED_MODELS.items():
        data.append({
            "id": key,
            "object": "model",
            "engine": info.get("engine", "transformers"),
            "name": info.get("model"),
            "size": info.get("size", "N/A"),
            "context": info.get("context", "N/A"),
            "speed": info.get("speed", "N/A"),
        })
    return {
        "object": "list",
        "data": data,
    }


@router.post("/models/load", dependencies=[Depends(verify_api_key)])
@router.post("/v1/models/load", dependencies=[Depends(verify_api_key)])
async def load_model_from_ui(payload: dict):
    model_key = (payload or {}).get("model_key")
    hf_token = (payload or {}).get("hf_token")

    if not model_key or model_key not in PREDEFINED_MODELS:
        return {
            "ok": False,
            "error": "Invalid model_key",
        }

    state = get_global_state()
    if state.loading_status == "loading":
        return {
            "ok": False,
            "error": "Another model is currently loading",
            "loading_model": state.loading_model_key,
        }

    _set_loading_state(
        status="queued",
        model_key=model_key,
        stage="queued",
        message="Queued for loading",
        progress=0,
        error=None,
    )

    thread = threading.Thread(target=_load_selected_model, args=(model_key, hf_token), daemon=True)
    thread.start()

    return {
        "ok": True,
        "status": "queued",
        "model_key": model_key,
        "stage": "queued",
        "message": "Queued for loading",
    }


@router.get("/v1/chats", dependencies=[Depends(verify_api_key)])
async def list_chats():
    state = get_global_state()
    chats = [_chat_summary(state.chats[cid]) for cid in state.chat_order if cid in state.chats]
    return {
        "object": "list",
        "data": chats,
        "active_chat_id": state.active_chat_id,
    }


@router.post("/v1/chats", dependencies=[Depends(verify_api_key)])
async def create_chat(payload: dict | None = None):
    state = get_global_state()
    title = (payload or {}).get("title")
    chat = _create_chat(state, title=title)
    return {"ok": True, "chat": chat}


@router.get("/v1/chats/{chat_id}", dependencies=[Depends(verify_api_key)])
async def get_chat(chat_id: str):
    state = get_global_state()
    chat = state.chats.get(chat_id)
    if not chat:
        return {"ok": False, "error": "Chat not found"}
    state.active_chat_id = chat_id
    return {"ok": True, "chat": chat}


@router.patch("/v1/chats/{chat_id}", dependencies=[Depends(verify_api_key)])
async def rename_chat(chat_id: str, payload: dict):
    state = get_global_state()
    chat = state.chats.get(chat_id)
    if not chat:
        return {"ok": False, "error": "Chat not found"}
    title = (payload or {}).get("title", "").strip()
    if title:
        chat["title"] = title[:80]
    chat["updated"] = int(time.time())
    return {"ok": True, "chat": chat}


@router.delete("/v1/chats/{chat_id}", dependencies=[Depends(verify_api_key)])
async def delete_chat(chat_id: str):
    state = get_global_state()
    if chat_id not in state.chats:
        return {"ok": False, "error": "Chat not found"}
    del state.chats[chat_id]
    state.chat_order = [cid for cid in state.chat_order if cid != chat_id]
    if state.active_chat_id == chat_id:
        state.active_chat_id = state.chat_order[0] if state.chat_order else None
    return {"ok": True}


@router.get("/v1/metrics/live", dependencies=[Depends(verify_api_key)])
async def live_metrics():
    state = get_global_state()
    return {
        "ok": True,
        "data": state.latest_metrics,
    }


@router.get("/v1/metrics/history", dependencies=[Depends(verify_api_key)])
async def metrics_history(limit: int = 20):
    state = get_global_state()
    safe_limit = max(1, min(200, int(limit)))
    return {
        "ok": True,
        "data": state.metrics_history[-safe_limit:],
    }


@router.get("/v1/metrics/summary", dependencies=[Depends(verify_api_key)])
async def metrics_summary():
    state = get_global_state()
    totals = state.metrics_totals
    avg_tps = round((totals["completion_tokens"] / totals["total_seconds"]), 2) if totals["total_seconds"] > 0 else 0.0
    return {
        "ok": True,
        "totals": totals,
        "avg_tokens_per_sec": avg_tps,
        "latest": state.latest_metrics,
    }

@router.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
async def chat_completions(request: ChatRequest):
    state = get_global_state()
    
    # Precedence: config.model > request.model > "openrun"
    model_name = getattr(state.config, "model", None) or request.model or "openrun"
    
    # Extract messages directly
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    prompt_tokens = sum(_estimate_tokens(state, m["content"]) for m in messages)

    chat_id = request.chat_id
    if chat_id:
        if chat_id not in state.chats:
            created_chat = _create_chat(state, title="New Chat")
            chat_id = created_chat["id"]
        state.active_chat_id = chat_id

    def _persist_chat_and_metrics(response_text: str, stream_mode: bool, duration_seconds: float, finish_reason: str = "stop"):
        completion_tokens = _estimate_tokens(state, response_text)
        metric = _record_metrics(
            state,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            duration_seconds=duration_seconds,
            stream=stream_mode,
            chat_id=chat_id,
        )
        if chat_id and chat_id in state.chats:
            user_messages = [
                {"role": "user", "content": m["content"]}
                for m in messages
                if m.get("role") == "user"
            ]
            chat = state.chats[chat_id]
            chat["messages"] = user_messages + [{"role": "assistant", "content": response_text}]
            chat["updated"] = int(time.time())
            if chat["title"] == "New Chat" and user_messages:
                chat["title"] = user_messages[0]["content"][:48] or "New Chat"
        return metric

    if request.stream:
        def _on_stream_complete(response_text: str, finish_reason: str, elapsed: float):
            _persist_chat_and_metrics(response_text, True, elapsed, finish_reason)

        return StreamingResponse(
            stream_response(messages, model_name=model_name, on_complete=_on_stream_complete),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    # Call inference layer
    started_at = time.time()
    response_text = generate_response(messages)
    completion_tokens = _estimate_tokens(state, response_text)
    metric = _persist_chat_and_metrics(response_text, False, time.time() - started_at)
        
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
        },
        "chat_id": chat_id,
        "metrics": metric,
    }
