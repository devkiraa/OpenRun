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
import asyncio
import threading
from openrun.models.registry import PREDEFINED_MODELS

router = APIRouter()

# Concurrency limiter: max 1 inference at a time to prevent GPU OOM crashes
_inference_semaphore = asyncio.Semaphore(1)

# HTML template for the built-in web playground
PLAYGROUND_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRun Studio</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: #ffffff;
            color: #0f172a;
            letter-spacing: -0.011em;
        }

        input, select, button, textarea {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            letter-spacing: -0.011em;
        }

        /* High-End Markdown Typography for Chat Session Aesthetics */
        .markdown-body {
            line-height: 1.625;
            font-size: 15px;
            color: #334155;
        }

        .markdown-body p {
            margin-top: 0;
            margin-bottom: 0.85rem;
        }

        .markdown-body p:last-child {
            margin-bottom: 0;
        }

        .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4 {
            font-weight: 700;
            color: #0f172a;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            line-height: 1.35;
        }

        .markdown-body h1 { font-size: 1.4rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.3rem; }
        .markdown-body h2 { font-size: 1.25rem; }
        .markdown-body h3 { font-size: 1.1rem; }
        .markdown-body h4 { font-size: 1rem; }

        .markdown-body strong {
            color: #0f172a;
            font-weight: 700;
        }

        .markdown-body ul, .markdown-body ol {
            margin-top: 0;
            margin-bottom: 1rem;
            padding-left: 1.5rem;
        }

        .markdown-body ul { list-style-type: disc; }
        .markdown-body ol { list-style-type: decimal; }
        .markdown-body li { margin-bottom: 0.35rem; }

        .markdown-body li::marker {
            color: #3b82f6;
            font-weight: 600;
        }

        .markdown-body blockquote {
            margin: 1rem 0;
            padding: 0.5rem 1rem;
            color: #64748b;
            border-left: 4px solid #cbd5e1;
            background: #f8fafc;
            border-radius: 0 8px 8px 0;
        }

        .markdown-body a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }

        .markdown-body a:hover {
            text-decoration: underline;
        }

        .markdown-body table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 14px;
        }

        .markdown-body th, .markdown-body td {
            border: 1px solid #e2e8f0;
            padding: 8px 12px;
            text-align: left;
        }

        .markdown-body th {
            background-color: #f1f5f9;
            font-weight: 600;
            color: #1e293b;
        }

        .markdown-body tr:nth-child(even) {
            background-color: #f8fafc;
        }

        .markdown-body hr {
            height: 1px;
            background-color: #e2e8f0;
            border: none;
            margin: 1.5rem 0;
        }

        .markdown-body pre { 
            background-color: #0f172a; 
            color: #e2e8f9; 
            padding: 1.25rem; 
            border-radius: 12px; 
            overflow-x: auto; 
            margin: 1rem 0; 
            position: relative; 
            border: 1px solid #1e293b;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }

        .markdown-body code { 
            background-color: #f1f5f9; 
            color: #2563eb;
            border-radius: 6px; 
            padding: 0.2em 0.4em; 
            font-size: 85%;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-weight: 500;
        }

        .markdown-body pre code { 
            background-color: transparent; 
            color: inherit;
            padding: 0; 
            border-radius: 0;
            font-size: 13.5px;
            line-height: 1.5;
        }

        .message-content { 
            white-space: pre-wrap; 
            line-height: 1.7; 
        }

        .copy-button { 
            position: absolute; 
            top: 0.6rem; 
            right: 0.6rem; 
            background: #1e293b; 
            border: 1px solid #334155; 
            color: #94a3b8; 
            padding: 0.3rem 0.6rem; 
            border-radius: 6px; 
            font-size: 0.75rem; 
            cursor: pointer; 
            opacity: 0; 
            transition: all 0.2s; 
        }
        .markdown-body pre:hover .copy-button { 
            opacity: 1; 
        }
        .copy-button:hover { 
            background: #334155; 
            color: #ffffff; 
        }

        /* Premium minimal scrollbar */
        ::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(15, 23, 42, 0.08);
            border-radius: 9999px;
            transition: background 0.2s;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(15, 23, 42, 0.2);
        }

        .typing-indicator { 
            display: inline-flex; 
            align-items: center; 
            gap: 4px; 
            height: 24px; 
            padding: 0 4px; 
        }
        .dot { 
            width: 6px; 
            height: 6px; 
            background-color: #94a3b8; 
            border-radius: 50%; 
            animation: bounce 1.4s infinite ease-in-out both; 
        }
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 
            0%, 80%, 100% { transform: scale(0); opacity: 0.4; } 
            40% { transform: scale(1); opacity: 1; } 
        }

        .animate-fade-in {
            animation: fadeIn 0.25s ease-out forwards;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Sidebar collapse support */
        #sidebar.collapsed {
            width: 0px;
            min-width: 0px;
            opacity: 0;
            overflow: hidden;
            border-right-width: 0px;
            pointer-events: none;
        }
    </style>
</head>
<body class="h-screen antialiased flex bg-white overflow-hidden select-none">

    <!-- 🤖 SIDEBAR -->
    <aside id="sidebar" class="w-[280px] bg-white border-r border-slate-100 flex flex-col h-full transition-all duration-300 ease-in-out z-30">
        <!-- Sidebar Header Actions -->
        <div class="flex items-center justify-between px-5 pt-5 pb-3">
            <button id="sidebar-toggle-btn" class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-50 rounded-lg transition" title="Close Sidebar">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                    <path d="M9 3v18" />
                </svg>
            </button>
            <button id="new-chat-btn" class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-50 rounded-lg transition" title="New Conversation">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
            </button>
        </div>

        <!-- Search Bar -->
        <div class="px-4 py-2">
            <div class="relative flex items-center bg-slate-50 border border-slate-200/80 rounded-xl px-3 py-1.5 focus-within:border-slate-300 focus-within:bg-white transition">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-slate-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input type="text" id="sidebar-search" placeholder="Search" class="w-full bg-transparent text-sm text-slate-700 placeholder-slate-400 focus:outline-none select-text">
            </div>
        </div>

        <!-- Scrollable Conversation List -->
        <div class="flex-1 overflow-y-auto px-2 py-3 space-y-0.5 select-text" id="chats-list">
            <!-- Populated via Javascript, falls back to mockup items if empty -->
        </div>

        <!-- Sidebar Bottom Action Controls -->
        <div class="border-t border-slate-100 p-3 flex items-center justify-around select-none">
            <button id="open-settings-btn" class="flex items-center justify-center gap-1.5 px-3 py-2 text-slate-400 hover:text-slate-700 hover:bg-slate-50 rounded-xl transition text-xs font-bold w-full" title="Server Configurations">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Settings
            </button>
            <button id="exit-btn" class="flex items-center justify-center gap-1.5 px-3 py-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-xl transition text-xs font-bold w-full" title="Stop OpenRun">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Shutdown
            </button>
        </div>
    </aside>

    <!-- 💬 MAIN CHAT AREA -->
    <main class="flex-1 flex flex-col h-full bg-white relative min-w-0">
        
        <!-- Floating Expand Sidebar Button -->
        <button id="sidebar-expand-btn" class="hidden absolute top-4 left-4 z-40 bg-white border border-slate-200/80 p-2 rounded-lg hover:bg-slate-50 hover:text-slate-800 text-slate-400 transition shadow-sm" title="Open Sidebar">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <path d="M9 3v18" />
            </svg>
        </button>

        <!-- Top Header Navigation -->
        <header class="h-16 border-b border-slate-100 flex items-center justify-between px-6 flex-shrink-0 relative z-20">
            <div class="flex items-center gap-2">
                <!-- Dropdown Model Trigger -->
                <div class="relative">
                    <button id="model-select-trigger" class="flex items-center gap-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200/60 rounded-xl px-3.5 py-1.5 text-xs font-bold text-slate-700 transition active:scale-[0.98]">
                        <span id="active-model-logo-container" class="inline-flex items-center">
                            <!-- Model Logo SVG -->
                            <svg class="w-4 h-4 text-emerald-600" viewBox="0 0 24 24" fill="currentColor">
                                <circle cx="12" cy="12" r="10" class="fill-emerald-500/10 stroke-emerald-500" stroke-width="1.5"/>
                                <path d="M12 6v12M6 12h12M7.75 7.75l8.5 8.5M7.75 16.25l8.5-8.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                            </svg>
                        </span>
                        <span id="active-model-name-display" class="font-sans">GPT-4o</span>
                        <svg class="w-3 h-3 text-slate-400 caret-icon transition-transform duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                        </svg>
                    </button>

                    <!-- Dropdown Models Popover Card -->
                    <div id="model-dropdown" class="hidden absolute left-0 mt-2 w-64 bg-white border border-slate-100 rounded-2xl shadow-xl py-2 z-50 animate-fade-in">
                        <div class="px-3.5 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-widest border-b border-slate-50 pb-2 mb-1.5">Model</div>
                        <div class="max-h-[320px] overflow-y-auto space-y-0.5 px-1" id="dropdown-model-list">
                            <!-- Populated dynamically from API -->
                        </div>
                    </div>
                </div>

                <!-- Sleek Active Server Status Display -->
                <div class="flex items-center gap-2 text-[11px] font-semibold text-slate-400 font-sans border-l border-slate-100 pl-3 ml-1 select-none">
                    <span class="flex h-2 w-2 relative" id="live-indicator-dot">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span id="model-load-status" class="truncate max-w-[130px] font-bold uppercase tracking-wider text-slate-500">Engine Active</span>
                    <span class="text-slate-200">|</span>
                    <span id="live-metrics" class="text-slate-400 font-mono">TPS: 0.0</span>
                </div>
            </div>

            <!-- Top Header Actions -->
            <div class="flex items-center gap-2">
                <button id="clear-btn" class="text-slate-400 hover:text-rose-500 p-2 rounded-lg hover:bg-slate-50 transition" title="Clear Chat History">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
            </div>
        </header>

        <!-- Blocking Model Loader Gate -->
        <section id="model-gate" class="hidden absolute inset-0 bg-white/95 backdrop-blur-sm z-30 flex items-center justify-center p-6 select-none animate-fade-in">
            <div class="max-w-md w-full border border-slate-100 rounded-2xl bg-white shadow-2xl p-8 text-center">
                <div class="h-12 w-12 mx-auto rounded-full bg-blue-50 flex items-center justify-center mb-4 border border-blue-100/60 text-blue-500">
                    <svg class="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                </div>
                <h3 class="text-base font-bold text-slate-800" id="gate-title">Booting Model Runtime</h3>
                <p class="mt-2 text-xs text-slate-400 leading-relaxed" id="gate-desc">Please wait while the active model resolves, or choose a model from the header selector to load it.</p>
            </div>
        </section>

        <!-- Dynamic Chat Container -->
        <main id="chat-container" class="flex-1 overflow-y-auto px-6 py-8 space-y-6 scroll-smooth select-text bg-[#fafafa]/40">
            <!-- Welcome Empty State -->
            <div id="empty-state" class="h-full flex flex-col items-center justify-center text-slate-400 space-y-5 animate-fade-in py-12 select-none">
                <div class="h-14 w-14 bg-white rounded-2xl flex items-center justify-center border border-slate-100 shadow-sm text-blue-500/95">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                </div>
                <h2 class="text-xl font-bold text-slate-800 font-sans tracking-tight">What can I build for you today?</h2>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-xl w-full pt-4 px-4">
                    <button class="suggestion-btn text-left p-4 rounded-xl border border-slate-200/80 bg-white hover:bg-slate-50 hover:border-slate-300 transition group shadow-sm flex flex-col justify-between h-24">
                        <span class="font-bold text-xs text-slate-700 group-hover:text-blue-600 transition-colors">Write a detailed layout plan</span>
                        <span class="text-[10px] text-slate-400">for boosting SaaS user engagement strategies</span>
                    </button>
                    <button class="suggestion-btn text-left p-4 rounded-xl border border-slate-200/80 bg-white hover:bg-slate-50 hover:border-slate-300 transition group shadow-sm flex flex-col justify-between h-24">
                        <span class="font-bold text-xs text-slate-700 group-hover:text-blue-600 transition-colors">Generate keyword research summary</span>
                        <span class="text-[10px] text-slate-400">for modern dark-mode landing pages</span>
                    </button>
                </div>
            </div>
        </main>

        <!-- Input Footer Panel -->
        <div id="chat-input-footer" class="bg-white px-6 pb-6 pt-3 flex-shrink-0 relative select-none">
            <div class="max-w-3xl mx-auto relative">
                
                <!-- Error Toast Notification -->
                <div id="error-toast" class="absolute -top-12 left-1/2 -translate-x-1/2 bg-rose-500 text-white px-4 py-2 rounded-xl text-xs shadow-xl border border-rose-400 opacity-0 transition-all duration-300 pointer-events-none flex items-center gap-2 font-bold z-50 translate-y-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                    <span id="error-msg"></span>
                </div>
                
                <!-- Stop Generation Button -->
                <div class="flex justify-center w-full absolute -top-14 pointer-events-none">
                    <button id="stop-btn" class="hidden pointer-events-auto bg-white hover:bg-slate-50 border border-slate-200/80 text-slate-700 text-xs font-bold px-4 py-2 rounded-full shadow-md transition items-center gap-2">
                        <span class="flex h-1.5 w-1.5 relative">
                            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                            <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-rose-500"></span>
                        </span>
                        Stop generation
                    </button>
                </div>

                <!-- Input Text Box -->
                <div class="relative bg-slate-50/50 border border-slate-200/90 rounded-2xl shadow-sm focus-within:border-slate-300 focus-within:bg-white focus-within:shadow-md transition duration-200 flex items-center py-2 px-4">
                    <textarea id="message-input" rows="1" class="w-full bg-transparent text-slate-800 placeholder-slate-400 pr-16 pl-1 py-2 focus:outline-none resize-none max-h-40 overflow-y-auto leading-relaxed text-sm select-text" placeholder="Send a message" autofocus></textarea>
                    
                    <div class="absolute right-3 flex items-center gap-2">
                        <!-- Stream Checkbox -->
                        <label class="flex items-center gap-1.5 px-2 py-1 text-[10px] font-bold text-slate-400 hover:text-slate-600 cursor-pointer select-none bg-slate-100 rounded-lg transition border border-slate-200/40">
                            <input type="checkbox" id="stream-toggle" class="rounded border-slate-300 text-blue-500 focus:ring-blue-500 cursor-pointer w-3 h-3" checked>
                            Stream
                        </label>
                        <button id="send-btn" class="bg-blue-600 hover:bg-blue-500 text-white h-8 w-8 rounded-xl flex items-center justify-center transition disabled:opacity-30 disabled:hover:bg-blue-600 disabled:cursor-not-allowed transform active:scale-95 shadow-md shadow-blue-500/10" disabled>
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5 ml-0.5" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="text-center mt-3 text-[10px] font-bold text-slate-300 uppercase tracking-widest leading-none">
                    AI models can make mistakes. Check important info.
                </div>
            </div>
        </div>
    </main>

    <!-- ⚙️ CONFIGURATIONS MODAL -->
    <div id="settings-modal" class="hidden fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl border border-slate-100 shadow-2xl max-w-sm w-full p-6 animate-fade-in flex flex-col">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-sm font-bold text-slate-800 flex items-center gap-1.5">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Server Configurations
                </h3>
                <button id="close-settings-modal" class="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-50 transition">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            
            <div class="space-y-4">
                <div>
                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">Hugging Face Token</label>
                    <input type="password" id="hf-token" placeholder="Optional token..." class="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-xl px-3.5 py-2.5 focus:border-blue-500 focus:bg-white outline-none font-mono transition select-text">
                </div>

                <div>
                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">API Password/Key</label>
                    <input type="password" id="api-key" placeholder="Optional auth key..." class="w-full bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-xl px-3.5 py-2.5 focus:border-blue-500 focus:bg-white outline-none font-mono transition select-text">
                </div>
                
                <div class="text-[10px] text-slate-400 leading-normal bg-slate-50 rounded-xl p-3 border border-slate-100 font-medium select-none">
                    🔒 Saved credentials will be saved in your browser and sent with server requests automatically.
                </div>

                <button id="save-settings-btn" class="w-full bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold py-3 rounded-xl transition active:scale-[0.98] shadow-lg shadow-blue-500/10">
                    Apply Configurations
                </button>
            </div>
        </div>
    </div>

    <!-- 📜 SCRIPTS -->
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

        // Brand Logos Collection
        const BRAND_LOGOS = {
            deepseek: `<svg class="w-4 h-4 text-emerald-600 mr-1.5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10" class="fill-emerald-500/10 stroke-emerald-500" stroke-width="1.5"/><path d="M12 6v12M6 12h12M7.75 7.75l8.5 8.5M7.75 16.25l8.5-8.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>`,
            llama: `<svg class="w-4 h-4 text-blue-500 mr-1.5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10" class="fill-blue-500/10 stroke-blue-500" stroke-width="1.5"/><path d="M8 10a2 2 0 100 4 2 2 0 000-4zm8 0a2 2 0 100 4 2 2 0 000-4z"/></svg>`,
            qwen: `<svg class="w-4 h-4 text-teal-600 mr-1.5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10" class="fill-teal-500/10 stroke-teal-500" stroke-width="1.5"/><path d="M12 9a3 3 0 110 6 3 3 0 010-6zm0-2a5 5 0 100 10 5 5 0 000-10z" fill-rule="evenodd" clip-rule="evenodd"/></svg>`,
            gemma: `<svg class="w-4 h-4 text-indigo-500 mr-1.5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10" class="fill-indigo-500/10 stroke-indigo-500" stroke-width="1.5"/><path d="M12 6c0 3.3 2.7 6 6 6-3.3 0-6 2.7-6 6 0-3.3-2.7-6-6-6 3.3 0 6-2.7 6-6z"/></svg>`,
            phi: `<svg class="w-4 h-4 text-purple-500 mr-1.5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10" class="fill-purple-500/10 stroke-purple-500" stroke-width="1.5"/><path d="M12 5c0 3.8 3.2 7 7 7-3.8 0-7 3.2-7 7 0-3.8-3.2-7-7-7 3.8 0 7-3.2 7-7z" /></svg>`,
            mistral: `<svg class="w-4 h-4 text-amber-500 mr-1.5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10" class="fill-amber-500/10 stroke-amber-500" stroke-width="1.5"/><path d="M7 8h2.5l2.5 4.5L14.5 8H17v8h-2.5v-4.5L12 16l-2.5-4.5V16H7z"/></svg>`,
            star: `<svg class="w-4 h-4 text-orange-500 mr-1.5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10" class="fill-orange-500/10 stroke-orange-500" stroke-width="1.5"/><path d="M12 7l1.2 3.2 3.3.3-2.5 2.2.8 3.3-2.8-2-2.8 2 .8-3.3-2.5-2.2 3.3-.3z"/></svg>`,
            custom: `<svg class="w-4 h-4 text-slate-500 mr-1.5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 9h6v6H9zM9 1v4M15 1v4M9 19v4M15 19v4M1 9h4M1 15h4M19 9h4M19 15h4"/></svg>`
        };

        function getModelBrandInfo(modelId) {
            const id = modelId.toLowerCase();
            if (id.includes('deepseek')) return { brand: 'DeepSeek', logo: BRAND_LOGOS.deepseek };
            if (id.includes('llama')) return { brand: 'Meta Llama', logo: BRAND_LOGOS.llama };
            if (id.includes('qwen')) return { brand: 'Qwen', logo: BRAND_LOGOS.qwen };
            if (id.includes('gemma')) return { brand: 'Google Gemma', logo: BRAND_LOGOS.gemma };
            if (id.includes('phi')) return { brand: 'Microsoft Phi', logo: BRAND_LOGOS.phi };
            if (id.includes('mistral')) return { brand: 'Mistral', logo: BRAND_LOGOS.mistral };
            if (id.includes('star') || id.includes('coder')) return { brand: 'StarCoder', logo: BRAND_LOGOS.star };
            return { brand: 'AI Model', logo: BRAND_LOGOS.custom };
        }

        let catalogModels = [];
        let messages = [];
        let isGenerating = false;
        let abortController = null;
        let modelReady = false;
        let modelStatusPoll = null;
        let currentChatId = null;
        let metricsPoll = null;
        let activeModelId = ''; 

        // Cache elements
        const chatContainer = document.getElementById('chat-container');
        const modelGate = document.getElementById('model-gate');
        const gateTitle = document.getElementById('gate-title');
        const gateDesc = document.getElementById('gate-desc');
        const chatInputFooter = document.getElementById('chat-input-footer');
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        const stopBtn = document.getElementById('stop-btn');
        const clearBtn = document.getElementById('clear-btn');
        const emptyState = document.getElementById('empty-state');
        const apiKeyInput = document.getElementById('api-key');
        const hfTokenInput = document.getElementById('hf-token');
        const modelLoadStatus = document.getElementById('model-load-status');
        const liveMetrics = document.getElementById('live-metrics');
        const chatsList = document.getElementById('chats-list');
        const newChatBtn = document.getElementById('new-chat-btn');
        const streamToggle = document.getElementById('stream-toggle');
        const errorToast = document.getElementById('error-toast');
        const errorMsg = document.getElementById('error-msg');
        
        // Custom redesigned selectors
        const sidebar = document.getElementById('sidebar');
        const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
        const sidebarExpandBtn = document.getElementById('sidebar-expand-btn');
        const sidebarSearch = document.getElementById('sidebar-search');
        const modelSelectTrigger = document.getElementById('model-select-trigger');
        const modelDropdown = document.getElementById('model-dropdown');
        const activeModelLogoContainer = document.getElementById('active-model-logo-container');
        const activeModelNameDisplay = document.getElementById('active-model-name-display');
        const openSettingsBtn = document.getElementById('open-settings-btn');
        const closeSettingsModal = document.getElementById('close-settings-modal');
        const settingsModal = document.getElementById('settings-modal');
        const saveSettingsBtn = document.getElementById('save-settings-btn');
        const exitBtn = document.getElementById('exit-btn');

        // Initialize localStorage credentials
        if (localStorage.getItem('openrun_api_key')) {
            apiKeyInput.value = localStorage.getItem('openrun_api_key');
        }
        if (localStorage.getItem('openrun_hf_token')) {
            hfTokenInput.value = localStorage.getItem('openrun_hf_token');
        }

        // Toggle Sidebar
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.add('collapsed');
            sidebarExpandBtn.classList.remove('hidden');
        });
        sidebarExpandBtn.addEventListener('click', () => {
            sidebar.classList.remove('collapsed');
            sidebarExpandBtn.classList.add('hidden');
        });

        // Toggle Model Dropdown Popover
        modelSelectTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            modelDropdown.classList.toggle('hidden');
            modelSelectTrigger.querySelector('.caret-icon').classList.toggle('rotate-180');
        });

        document.addEventListener('click', (e) => {
            if (!modelDropdown.contains(e.target) && !modelSelectTrigger.contains(e.target)) {
                modelDropdown.classList.add('hidden');
                modelSelectTrigger.querySelector('.caret-icon').classList.remove('rotate-180');
            }
        });

        // Toggle Settings Modal
        openSettingsBtn.addEventListener('click', () => {
            settingsModal.classList.remove('hidden');
        });
        closeSettingsModal.addEventListener('click', () => {
            settingsModal.classList.add('hidden');
        });
        saveSettingsBtn.addEventListener('click', () => {
            localStorage.setItem('openrun_api_key', apiKeyInput.value.trim());
            localStorage.setItem('openrun_hf_token', hfTokenInput.value.trim());
            settingsModal.classList.add('hidden');
            initPlayground();
        });

        exitBtn.addEventListener('click', () => {
            if (confirm("Stop OpenRun local servers?")) {
                fetch('/shutdown', { method: 'POST' }).catch(() => {});
                alert("OpenRun Shutdown command sent.");
            }
        });

        async function fetchModels() {
            try {
                const apiKey = apiKeyInput.value.trim();
                const headers = {
                    ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
                };
                const res = await fetch(MODELS_CATALOG_URL, { headers });
                if (!res.ok) return;
                const data = await res.json();
                catalogModels = data.data || [];
                renderModelsDropdown();
            } catch (err) {
                console.error("Failed to fetch models", err);
            }
        }

        function renderModelsDropdown() {
            const dropdown = document.getElementById('dropdown-model-list');
            dropdown.innerHTML = '';
            
            if (catalogModels.length === 0) {
                dropdown.innerHTML = `<div class="px-4 py-3 text-center text-xs font-semibold text-slate-400 select-none">No models available</div>`;
                return;
            }

            catalogModels.forEach(model => {
                const brandInfo = getModelBrandInfo(model.id);
                const option = document.createElement('div');
                option.className = 'model-option flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer hover:bg-slate-50 group transition';
                option.setAttribute('data-model-id', model.id);
                
                option.innerHTML = `
                    <div class="flex items-center min-w-0 pointer-events-none">
                        ${brandInfo.logo}
                        <span class="text-xs font-bold text-slate-700 truncate">${model.id}</span>
                    </div>
                    <div class="relative group\\/tooltip inline-flex items-center">
                        <svg class="w-3.5 h-3.5 text-slate-300 hover:text-slate-500 transition cursor-pointer" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M12 16v-4m0-4h.01"/>
                        </svg>
                        <div class="absolute bottom-full mb-2 right-0 bg-[#1e293b] text-white text-[10px] font-medium rounded-lg px-2.5 py-1.5 shadow-lg opacity-0 group-hover\\/tooltip:opacity-100 transition-opacity duration-150 pointer-events-none whitespace-normal w-52 z-50 leading-normal">
                            <div class="font-bold text-slate-200 truncate mb-0.5">${model.name || model.id}</div>
                            <div class="text-[9px] text-slate-400">Size: ${model.size || 'N/A'} • Context: ${model.context || 'N/A'}</div>
                            <div class="text-[9px] text-slate-400 mt-0.5">Engine: ${model.engine || 'N/A'} • Speed: ${model.speed || 'N/A'}</div>
                            <div class="absolute top-full right-1.5 -mt-1 border-4 border-transparent border-t-[#1e293b]"></div>
                        </div>
                    </div>
                `;
                
                option.addEventListener('click', async (e) => {
                    // Avoid tooltip triggers
                    if (e.target.closest('circle') || e.target.closest('path') || e.target.closest('.group\\\\/tooltip')) {
                        return;
                    }
                    
                    activeModelId = model.id;
                    activeModelNameDisplay.textContent = model.id;
                    activeModelLogoContainer.innerHTML = brandInfo.logo;
                    
                    modelDropdown.classList.add('hidden');
                    modelSelectTrigger.querySelector('.caret-icon').classList.remove('rotate-180');

                    await loadSelectedModelByName(model.id);
                });
                
                dropdown.appendChild(option);
            });
        }

        function updateModelAccessUI() {
            modelGate.classList.add('hidden');
        }

        function updateSendButtonState() {
            sendBtn.disabled = isGenerating || messageInput.value.trim() === '' || !modelReady;
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
            chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'auto' });
        }

        function renderEmptyChats() {
            chatsList.innerHTML = `
                <div class="px-4 py-8 text-center text-slate-400 select-none select-none">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mx-auto mb-2 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <div class="text-[11px] font-bold uppercase tracking-wider text-slate-300">No chats yet</div>
                    <div class="text-[10px] text-slate-400/80 mt-1">Start a conversation to begin</div>
                </div>
            `;
        }

        async function fetchChats() {
            try {
                const apiKey = apiKeyInput.value.trim();
                const headers = {
                    ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
                };
                const res = await fetch(CHATS_URL, { headers });
                if (!res.ok) {
                    renderEmptyChats();
                    return;
                }
                const data = await res.json();
                const chats = data.data || [];

                chatsList.innerHTML = '';
                if (chats.length === 0) {
                    renderEmptyChats();
                    return;
                }

                chats.forEach(chat => {
                    const btn = document.createElement('div');
                    const isActive = chat.id === currentChatId;
                    btn.className = `sidebar-item flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition select-none text-xs font-semibold ${isActive ? 'bg-slate-100 text-slate-800' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'}`;
                    btn.innerHTML = `
                        <div class="flex items-center min-w-0 flex-1 gap-2 pointer-events-none">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                            <span class="truncate pr-1">${chat.title || 'Untitled Chat'}</span>
                        </div>
                    `;
                    btn.addEventListener('click', () => openChat(chat.id));
                    chatsList.appendChild(btn);
                });

                if (!currentChatId && chats.length) {
                    await openChat(chats[0].id);
                }
            } catch (err) {
                renderEmptyChats();
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
            const res = await fetch(METRICS_LIVE_URL, { headers }).catch(() => null);
            if (!res || !res.ok) return;
            const data = await res.json();
            const m = data.data;
            if (!m) {
                liveMetrics.textContent = 'TPS: 0.0';
                return;
            }
            liveMetrics.textContent = `TPS: ${m.tokens_per_sec || 0.0}`;
        }

        async function fetchHealth() {
            try {
                const res = await fetch(HEALTH_URL);
                if (res.ok) {
                    const data = await res.json();
                    if (data.model) {
                        modelReady = true;
                        modelLoadStatus.textContent = 'Active';
                        modelLoadStatus.className = 'font-bold uppercase tracking-wider text-emerald-600';
                        document.getElementById('live-indicator-dot').classList.remove('hidden');
                        
                        // Try to select the matched active model in UI catalog
                        const activeKey = data.model;
                        let matchedOption = false;
                        for (const model of catalogModels) {
                            if (activeKey === model.id || activeKey === model.name || activeKey.includes(model.id) || model.id.includes(activeKey)) {
                                activeModelId = model.id;
                                activeModelNameDisplay.textContent = model.id;
                                const brandInfo = getModelBrandInfo(model.id);
                                activeModelLogoContainer.innerHTML = brandInfo.logo;
                                matchedOption = true;
                                break;
                            }
                        }
                        if (!matchedOption) {
                            // Custom loaded CLI model
                            const modelBaseName = activeKey.split('/').pop() || activeKey;
                            activeModelId = activeKey;
                            activeModelNameDisplay.textContent = modelBaseName;
                            const brandInfo = getModelBrandInfo(activeKey);
                            activeModelLogoContainer.innerHTML = brandInfo.logo;
                        }
                        updateModelAccessUI();
                    } else {
                        modelReady = false;
                        modelLoadStatus.textContent = 'No Model';
                        modelLoadStatus.className = 'font-bold uppercase tracking-wider text-amber-500';
                        showGateLoader("Active OpenRun Service", "No local LLM model loaded. Use the dropdown model selector above to automatically load a fast local reasoning engine.");
                    }
                }
            } catch (e) {
                modelReady = false;
                modelLoadStatus.textContent = 'Offline';
                modelLoadStatus.className = 'font-bold uppercase tracking-wider text-rose-500';
                document.getElementById('live-indicator-dot').classList.add('hidden');
                showGateLoader("OpenRun Offline", "The local server is offline or unreachable. Please launch the OpenRun serve process in your workspace terminal.");
            }
            updateSendButtonState();
        }

        function showGateLoader(title, desc) {
            modelGate.classList.remove('hidden');
            gateTitle.textContent = title;
            gateDesc.textContent = desc;
        }

        async function loadSelectedModelByName(modelId) {
            modelReady = false;
            modelLoadStatus.textContent = 'Loading...';
            modelLoadStatus.className = 'font-bold uppercase tracking-wider text-blue-500 animate-pulse';
            
            showGateLoader("Loading model weights", `Deploying and loading ${modelId.toUpperCase()} weights into VRAM. This process leverages backend optimizations for quick local inference.`);
            updateSendButtonState();

            const apiKey = apiKeyInput.value.trim();
            const headers = {
                'Content-Type': 'application/json',
                ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
            };
            const payload = {
                model_key: modelId,
                hf_token: hfTokenInput.value.trim() || null
            };

            let res = await fetch(MODEL_LOAD_URL, {
                method: 'POST',
                headers,
                body: JSON.stringify(payload)
            }).catch(() => null);

            if (!res || res.status === 404) {
                res = await fetch('/v1/models/load', {
                    method: 'POST',
                    headers,
                    body: JSON.stringify(payload)
                }).catch(() => null);
            }

            if (!res || !res.ok) {
                showError('Failed to start loading model on local host');
                fetchHealth();
                return;
            }

            if (modelStatusPoll) clearInterval(modelStatusPoll);
            modelStatusPoll = setInterval(pollModelStatus, 1500);
            await pollModelStatus();
        }

        async function pollModelStatus() {
            const apiKey = apiKeyInput.value.trim();
            const headers = {
                ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
            };
            let res = await fetch(MODEL_STATUS_URL, { headers }).catch(() => null);
            if (!res || !res.ok) res = await fetch('/v1/models/status', { headers }).catch(() => null);
            if (!res || !res.ok) return;
            const status = await res.json();

            if (status.status === 'loading' || status.status === 'queued') {
                modelReady = false;
                const stage = status.stage ? ` - ${status.stage}` : '';
                const prog = status.progress ? ` (${status.progress}%)` : '';
                modelLoadStatus.textContent = `Loading${prog}`;
                showGateLoader("Loading model weights", `Loading stage: ${status.message || 'Queued'} ${prog}${stage}. Preparing local pipeline.`);
            } else if (status.status === 'ready' || status.loaded_model) {
                modelReady = true;
                modelLoadStatus.textContent = 'Active';
                modelLoadStatus.className = 'font-bold uppercase tracking-wider text-emerald-600';
                if (modelStatusPoll) {
                    clearInterval(modelStatusPoll);
                    modelStatusPoll = null;
                }
                updateModelAccessUI();
                await fetchHealth();
            } else if (status.status === 'error') {
                modelReady = false;
                modelLoadStatus.textContent = 'Load Failed';
                modelLoadStatus.className = 'font-bold uppercase tracking-wider text-rose-500';
                showGateLoader("Load process crashed", `Error: ${status.error || 'Failed to download or load model weights.'}`);
                if (modelStatusPoll) {
                    clearInterval(modelStatusPoll);
                    modelStatusPoll = null;
                }
            }
            updateSendButtonState();
        }

        // Live search filter
        sidebarSearch.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            document.querySelectorAll('.sidebar-item').forEach(item => {
                const text = item.querySelector('span').textContent.toLowerCase();
                if (text.includes(query)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        });

        // Suggestion buttons click
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const text = btn.querySelector('.font-bold').textContent + " " + btn.querySelector('.text-[10px]').textContent;
                messageInput.value = text;
                messageInput.focus();
                adjustTextareaHeight();
                updateSendButtonState();
            });
        });

        function adjustTextareaHeight() {
            messageInput.style.height = 'auto';
            messageInput.style.height = Math.min(messageInput.scrollHeight, 180) + 'px';
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
        newChatBtn.addEventListener('click', async () => {
            await createChat('New Chat');
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
                stable += '\\n```';
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
            const parts = buffer.split('\\n\\n');
            const remainder = parts.pop() || '';

            for (const part of parts) {
                const dataLines = [];
                for (const line of part.split('\\n')) {
                    if (line.startsWith('data:')) {
                        dataLines.push(line.slice(5).trimStart());
                    }
                }
                if (dataLines.length) {
                    events.push(dataLines.join('\\n'));
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
                sendBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5 ml-0.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd" /></svg>`;
                messageInput.focus();
            }

            updateSendButtonState();
        }

        function createMessageElement(role, content) {
            const div = document.createElement('div');
            const isUser = role === 'user';
            div.className = `flex gap-4 max-w-3xl mx-auto w-full group animate-fade-in ${isUser ? 'flex-row-reverse' : ''}`;
            div.dataset.role = role;
            
            const avatar = document.createElement('div');
            avatar.className = `w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center text-xs font-semibold shadow-sm mt-0.5 ${isUser ? 'bg-blue-600 text-white ring-2 ring-blue-500/10' : 'bg-slate-50 border border-slate-200/60 text-slate-600'}`;
            
            if (isUser) {
                avatar.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" /></svg>`;
            } else {
                avatar.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>`;
            }
            
            const contentContainer = document.createElement('div');
            contentContainer.className = `flex flex-col max-w-[82%] ${isUser ? 'items-end' : 'items-start'}`;
            
            const textBubble = document.createElement('div');
            textBubble.className = `px-4.5 py-3.5 rounded-2xl ${isUser ? 'bg-slate-100 text-slate-800 rounded-tr-sm' : 'bg-white border border-slate-100 rounded-tl-sm shadow-sm'}`;
            
            const textDiv = document.createElement('div');
            textDiv.className = `message-content markdown-body text-[14px] text-slate-800`;
            
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
                showError('Active model runtime is loading. Please wait.');
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
            
            chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
            
            const isStreaming = streamToggle.checked;
            abortController = new AbortController();
            const apiKey = apiKeyInput.value.trim();
            const headers = {
                'Content-Type': 'application/json',
                ...(apiKey ? {'Authorization': `Bearer ${apiKey}`} : {})
            };
            
            try {
                const payload = {
                    model: activeModelId || "openrun",
                    messages,
                    stream: isStreaming,
                    chat_id: currentChatId
                };
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers,
                    body: JSON.stringify(payload),
                    signal: abortController.signal
                });
                
                if (!response.ok) {
                    let errMsg = `HTTP ${response.status}`;
                    try { errMsg = (await response.json()).detail || errMsg; } catch(e) {}
                    botTextDiv.innerHTML = `<span class="text-rose-500 font-semibold">Error: ${errMsg}</span>`;
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
                                    chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'auto' });
                                }
    
                                const reason = data.choices?.[0]?.finish_reason;
                                if (reason) {
                                    streamFinishReason = reason;
                                }
    
                                if (data.error?.message) {
                                    showError(data.error.message);
                                }
                            } catch (e) {
                                // keep buffering
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
                    botTextDiv.innerHTML = `<span class="text-rose-500 font-semibold">Failed to connect.</span>`;
                    showError("Connection failed");
                    messages.pop(); 
                }
            } finally {
                if (isGenerating) setUIGenerationState(false);
                chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
            }
        }

        async function initPlayground() {
            await fetchModels();
            await fetchHealth();
            await fetchChats();
            await fetchLiveMetrics();
            
            if (metricsPoll) clearInterval(metricsPoll);
            metricsPoll = setInterval(fetchLiveMetrics, 2000);
            
            marked.setOptions({ breaks: true, gfm: true });
            const renderCode = (code, language) => {
                return `<pre><button class="copy-button" onclick="navigator.clipboard.writeText(this.parentElement.querySelector('code').innerText); this.innerText='Copied!'; setTimeout(()=>this.innerText='Copy', 2000);">Copy</button><code>${code.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`;
            };
            const renderer = new marked.Renderer();
            renderer.code = renderCode;
            marked.use({ renderer });
        }

        initPlayground();
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
            quantize = state.config.quantize if state.config else None
            low_cpu_mem = state.config.low_cpu_mem if state.config else False
            adapter = HuggingFaceAdapter(model_name, quantize=quantize, low_cpu_mem=low_cpu_mem)
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
    # Acquire semaphore to prevent concurrent GPU inference (OOM protection)
    acquired = _inference_semaphore.locked()
    if acquired:
        # Another request is already running — check if we can wait briefly
        try:
            await asyncio.wait_for(_inference_semaphore.acquire(), timeout=120.0)
        except asyncio.TimeoutError:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "message": "Server is busy processing another request. Please retry shortly.",
                        "type": "server_busy",
                    }
                },
            )
    else:
        await _inference_semaphore.acquire()

    try:
        return await _run_chat_completions(request)
    finally:
        _inference_semaphore.release()


async def _run_chat_completions(request: ChatRequest):
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
