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
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'></path><polyline points='3.27 6.96 12 12.01 20.73 6.96'></polyline><line x1='12' y1='22.08' x2='12' y2='12'></line></svg>">

    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        border: "hsl(var(--border))",
                        input: "hsl(var(--input))",
                        ring: "hsl(var(--ring))",
                        background: "hsl(var(--background))",
                        foreground: "hsl(var(--foreground))",
                        primary: {
                            DEFAULT: "hsl(var(--primary))",
                            foreground: "hsl(var(--primary-foreground))",
                        },
                        secondary: {
                            DEFAULT: "hsl(var(--secondary))",
                            foreground: "hsl(var(--secondary-foreground))",
                        },
                        destructive: {
                            DEFAULT: "hsl(var(--destructive))",
                            foreground: "hsl(var(--destructive-foreground))",
                        },
                        muted: {
                            DEFAULT: "hsl(var(--muted))",
                            foreground: "hsl(var(--muted-foreground))",
                        },
                        accent: {
                            DEFAULT: "hsl(var(--accent))",
                            foreground: "hsl(var(--accent-foreground))",
                        },
                        popover: {
                            DEFAULT: "hsl(var(--popover))",
                            foreground: "hsl(var(--popover-foreground))",
                        },
                        card: {
                            DEFAULT: "hsl(var(--card))",
                            foreground: "hsl(var(--card-foreground))",
                        },
                    },
                    borderRadius: {
                        lg: "var(--radius)",
                        md: "calc(var(--radius) - 2px)",
                        sm: "calc(var(--radius) - 4px)",
                    },
                    fontFamily: {
                        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
                        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
                    },
                    animation: {
                        "accordion-down": "accordion-down 0.2s ease-out",
                        "accordion-up": "accordion-up 0.2s ease-out",
                    },
                }
            }
        }
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Code Highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    
    <!-- Styles -->
    <style>
        :root {
            --background: 0 0% 100%;
            --foreground: 222.2 84% 4.9%;
            --card: 0 0% 100%;
            --card-foreground: 222.2 84% 4.9%;
            --popover: 0 0% 100%;
            --popover-foreground: 222.2 84% 4.9%;
            --primary: 221.2 83.2% 53.3%;
            --primary-foreground: 210 40% 98%;
            --secondary: 210 40% 96.1%;
            --secondary-foreground: 222.2 47.4% 11.2%;
            --muted: 210 40% 96.1%;
            --muted-foreground: 215.4 16.3% 46.9%;
            --accent: 210 40% 96.1%;
            --accent-foreground: 222.2 47.4% 11.2%;
            --destructive: 0 84.2% 60.2%;
            --destructive-foreground: 210 40% 98%;
            --border: 214.3 31.8% 91.4%;
            --input: 214.3 31.8% 91.4%;
            --ring: 221.2 83.2% 53.3%;
            --radius: 0.5rem;
        }
        .dark {
            --background: 222.2 84% 4.9%;
            --foreground: 210 40% 98%;
            --card: 222.2 84% 4.9%;
            --card-foreground: 210 40% 98%;
            --popover: 222.2 84% 4.9%;
            --popover-foreground: 210 40% 98%;
            --primary: 217.2 91.2% 59.8%;
            --primary-foreground: 222.2 47.4% 11.2%;
            --secondary: 217.2 32.6% 17.5%;
            --secondary-foreground: 210 40% 98%;
            --muted: 217.2 32.6% 17.5%;
            --muted-foreground: 215 20.2% 65.1%;
            --accent: 217.2 32.6% 17.5%;
            --accent-foreground: 210 40% 98%;
            --destructive: 0 62.8% 30.6%;
            --destructive-foreground: 210 40% 98%;
            --border: 217.2 32.6% 17.5%;
            --input: 217.2 32.6% 17.5%;
            --ring: 224.3 76.3% 48%;
        }

        body {
            background-color: hsl(var(--background));
            color: hsl(var(--foreground));
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: hsl(var(--muted)); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: hsl(var(--muted-foreground)); }

        /* Shadcn Button styles */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
            border-radius: calc(var(--radius) - 2px);
            font-size: 0.875rem;
            font-weight: 500;
            transition-property: color, background-color, border-color;
            transition-duration: 150ms;
            height: 2.25rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .btn:disabled { opacity: 0.5; pointer-events: none; }
        .btn-primary { background-color: hsl(var(--primary)); color: hsl(var(--primary-foreground)); }
        .btn-primary:hover { background-color: hsl(var(--primary) / 0.9); }
        .btn-outline { border: 1px solid hsl(var(--input)); background-color: hsl(var(--background)); }
        .btn-outline:hover { background-color: hsl(var(--accent)); color: hsl(var(--accent-foreground)); }
        .btn-ghost { background-color: transparent; }
        .btn-ghost:hover { background-color: hsl(var(--accent)); color: hsl(var(--accent-foreground)); }
        .btn-icon { height: 2.25rem; width: 2.25rem; padding: 0; }
        
        .input-ring:focus-within {
            outline: 2px solid transparent;
            outline-offset: 2px;
            box-shadow: 0 0 0 2px hsl(var(--background)), 0 0 0 4px hsl(var(--ring));
        }

        /* Markdown Prose Styles */
        .prose p { margin-bottom: 1rem; line-height: 1.6; }
        .prose p:last-child { margin-bottom: 0; }
        .prose strong { font-weight: 600; color: hsl(var(--foreground)); }
        .prose ul { list-style-type: disc; padding-left: 1.5rem; margin-bottom: 1rem; }
        .prose ol { list-style-type: decimal; padding-left: 1.5rem; margin-bottom: 1rem; }
        .prose a { color: hsl(var(--primary)); text-decoration: underline; text-underline-offset: 4px; }
        .prose h1, .prose h2, .prose h3, .prose h4 { font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem; color: hsl(var(--foreground)); }
        .prose h1 { font-size: 1.5rem; }
        .prose h2 { font-size: 1.25rem; border-bottom: 1px solid hsl(var(--border)); padding-bottom: 0.25rem; }
        .prose h3 { font-size: 1.125rem; }
        .prose blockquote { border-left: 4px solid hsl(var(--border)); padding-left: 1rem; font-style: italic; color: hsl(var(--muted-foreground)); margin-bottom: 1rem; }
        
        /* Inline Code */
        .prose code:not(pre code) {
            background-color: hsl(var(--secondary));
            color: hsl(var(--secondary-foreground));
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
            font-size: 0.875em;
            font-family: inherit;
        }

        /* Code Blocks */
        .prose pre {
            background-color: #282c34; /* Atom One Dark bg */
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            margin-top: 1rem;
            margin-bottom: 1rem;
            overflow-x: auto;
            position: relative;
        }
        .prose pre code {
            display: block;
            padding: 1rem;
            color: #abb2bf;
            font-size: 0.875em;
            line-height: 1.5;
            background: transparent;
            border: none;
        }
        
        .code-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #21252b;
            padding: 0.5rem 1rem;
            border-bottom: 1px solid #181a1f;
            font-size: 0.75rem;
            color: #9ca3af;
            border-top-left-radius: var(--radius);
            border-top-right-radius: var(--radius);
        }
        
        .copy-code-btn {
            background: transparent;
            border: none;
            color: #9ca3af;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.25rem;
            transition: color 0.2s;
        }
        .copy-code-btn:hover { color: #e5e7eb; }

        /* Typing indicator */
        .typing-indicator { display: inline-flex; align-items: center; gap: 4px; height: 24px; }
        .typing-indicator .dot { width: 6px; height: 6px; background-color: hsl(var(--muted-foreground)); border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
        .typing-indicator .dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }

        /* Layout */
        .sidebar-expanded { width: 260px; min-width: 260px; }
        .sidebar-collapsed { width: 0; min-width: 0; overflow: hidden; border: none; }
    </style>

    <!-- Dependencies -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.0.9/purify.min.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body class="h-screen w-full flex overflow-hidden selection:bg-primary/20 text-sm">

    <!-- SIDEBAR -->
    <aside id="sidebar" class="sidebar-expanded bg-card border-r border-border flex flex-col h-full transition-all duration-300 z-30 flex-shrink-0">
        <div class="p-4 flex items-center justify-between">
            <h2 class="font-semibold text-base flex items-center gap-2">
                <i data-lucide="box" class="w-5 h-5 text-primary"></i>
                OpenRun
            </h2>
            <button id="sidebar-toggle-close" class="btn btn-ghost btn-icon text-muted-foreground hover:text-foreground" title="Close Sidebar">
                <i data-lucide="panel-left-close" class="w-4 h-4"></i>
            </button>
        </div>
        
        <div class="px-3 pb-3">
            <button id="new-chat-btn" class="w-full btn btn-outline justify-start gap-2 text-foreground">
                <i data-lucide="plus" class="w-4 h-4"></i>
                New Chat
            </button>
        </div>
        
        <div class="px-3 pb-2">
            <div class="relative flex items-center bg-background border border-input rounded-md px-3 py-1.5 focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 focus-within:ring-offset-background transition-shadow">
                <i data-lucide="search" class="w-4 h-4 text-muted-foreground mr-2"></i>
                <input type="text" id="sidebar-search" placeholder="Search chats..." class="w-full bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none">
            </div>
        </div>

        <div class="flex-1 overflow-y-auto p-3 space-y-1" id="chats-list">
            <!-- Chats populated here -->
        </div>

        <div class="p-3 border-t border-border flex flex-col gap-1">
            <button id="open-settings-btn" class="w-full btn btn-ghost justify-start gap-2 text-muted-foreground hover:text-foreground">
                <i data-lucide="settings" class="w-4 h-4"></i>
                Settings
            </button>
            <button id="exit-btn" class="w-full btn btn-ghost justify-start gap-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10">
                <i data-lucide="power" class="w-4 h-4"></i>
                Shutdown
            </button>
        </div>
    </aside>

    <!-- MAIN APP -->
    <main class="flex-1 flex flex-col h-full bg-background relative min-w-0">
        <!-- HEADER -->
        <header class="h-14 border-b border-border flex items-center justify-between px-4 flex-shrink-0 bg-background/95 backdrop-blur z-20">
            <div class="flex items-center gap-3">
                <button id="sidebar-toggle-open" class="hidden btn btn-ghost btn-icon text-muted-foreground hover:text-foreground" title="Open Sidebar">
                    <i data-lucide="panel-left-open" class="w-4 h-4"></i>
                </button>
                
                <!-- Model Selector -->
                <div class="relative group/model">
                    <button id="model-select-trigger" class="btn btn-outline h-9 gap-2 shadow-sm bg-card">
                        <i data-lucide="cpu" class="w-4 h-4 text-primary"></i>
                        <span id="active-model-name-display" class="font-medium text-foreground">Loading...</span>
                        <i data-lucide="chevron-down" class="w-4 h-4 text-muted-foreground"></i>
                    </button>
                    
                    <div id="model-dropdown" class="hidden absolute top-full left-0 mt-1 w-64 bg-popover border border-border rounded-md shadow-md py-1 z-50">
                        <div class="px-3 py-1.5 text-xs font-medium text-muted-foreground border-b border-border mb-1">Models</div>
                        <div class="max-h-[300px] overflow-y-auto px-1" id="dropdown-model-list">
                            <!-- Models populated here -->
                        </div>
                    </div>
                </div>
                
                <!-- Server Status -->
                <div class="hidden sm:flex items-center gap-2 text-xs font-medium border-l border-border pl-3">
                    <span class="relative flex h-2.5 w-2.5" id="live-indicator-dot">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
                    </span>
                    <span id="model-load-status" class="text-green-500">Active</span>
                    <span class="text-muted-foreground mx-1">|</span>
                    <span id="live-metrics" class="text-muted-foreground font-mono">0.0 TPS</span>
                </div>
            </div>
            
            <div class="flex items-center gap-2">
                <!-- Theme Toggle -->
                <button id="theme-toggle" class="btn btn-ghost btn-icon text-muted-foreground hover:text-foreground">
                    <i data-lucide="sun" class="w-4 h-4 hidden dark:block"></i>
                    <i data-lucide="moon" class="w-4 h-4 block dark:hidden"></i>
                </button>
                <button id="clear-btn" class="btn btn-ghost btn-icon text-muted-foreground hover:text-destructive hover:bg-destructive/10" title="Clear Chat">
                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
            </div>
        </header>

        <!-- LOADER GATE -->
        <div id="model-gate" class="hidden absolute inset-0 bg-background/80 backdrop-blur-sm z-30 flex items-center justify-center p-6">
            <div class="max-w-md w-full border border-border rounded-xl bg-card shadow-lg p-6 flex flex-col items-center text-center">
                <i data-lucide="loader-2" class="w-8 h-8 text-primary animate-spin mb-4"></i>
                <h3 class="text-lg font-semibold text-foreground" id="gate-title">Starting Model Engine</h3>
                <p class="mt-2 text-sm text-muted-foreground" id="gate-desc">Please wait while the weights are loaded into memory.</p>
            </div>
        </div>

        <!-- CHAT AREA -->
        <div id="chat-container" class="flex-1 overflow-y-auto px-4 py-6 space-y-6 scroll-smooth flex flex-col relative w-full">
            
            <!-- Empty State -->
            <div id="empty-state" class="m-auto flex flex-col items-center justify-center max-w-2xl text-center">
                <div class="w-16 h-16 bg-secondary text-primary rounded-2xl flex items-center justify-center mb-6 shadow-sm border border-border">
                    <i data-lucide="sparkles" class="w-8 h-8"></i>
                </div>
                <h2 class="text-2xl font-semibold tracking-tight text-foreground mb-2">How can I help you today?</h2>
                <p class="text-muted-foreground mb-8 text-sm">Powered by OpenRun Local AI Engine</p>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl">
                    <button class="suggestion-btn btn btn-outline h-auto py-3 px-4 flex flex-col items-start gap-1 text-left bg-card hover:bg-accent/50 transition">
                        <span class="font-medium text-sm text-foreground">Explain quantum computing</span>
                        <span class="text-xs text-muted-foreground">in simple terms</span>
                    </button>
                    <button class="suggestion-btn btn btn-outline h-auto py-3 px-4 flex flex-col items-start gap-1 text-left bg-card hover:bg-accent/50 transition">
                        <span class="font-medium text-sm text-foreground">Write a Python script</span>
                        <span class="text-xs text-muted-foreground">to automate daily backups</span>
                    </button>
                    <button class="suggestion-btn btn btn-outline h-auto py-3 px-4 flex flex-col items-start gap-1 text-left bg-card hover:bg-accent/50 transition">
                        <span class="font-medium text-sm text-foreground">Brainstorm names</span>
                        <span class="text-xs text-muted-foreground">for a new tech startup</span>
                    </button>
                    <button class="suggestion-btn btn btn-outline h-auto py-3 px-4 flex flex-col items-start gap-1 text-left bg-card hover:bg-accent/50 transition">
                        <span class="font-medium text-sm text-foreground">Draft an email</span>
                        <span class="text-xs text-muted-foreground">to decline a meeting politely</span>
                    </button>
                </div>
            </div>
            
            <!-- Messages will be injected here -->
        </div>

        <!-- INPUT FOOTER -->
        <div class="p-4 bg-background border-t border-border relative z-20 w-full flex-shrink-0">
            <!-- Toasts -->
            <div id="error-toast" class="absolute -top-12 left-1/2 -translate-x-1/2 bg-destructive text-destructive-foreground px-4 py-2 rounded-md text-sm shadow-md opacity-0 pointer-events-none flex items-center gap-2 font-medium z-50 transition-all duration-300 translate-y-2">
                <i data-lucide="alert-circle" class="w-4 h-4"></i>
                <span id="error-msg"></span>
            </div>

            <!-- Stop Button -->
            <div class="absolute -top-14 left-1/2 -translate-x-1/2 z-30">
                <button id="stop-btn" class="hidden btn bg-background border border-border text-foreground hover:bg-muted shadow-sm rounded-full h-8 px-3 gap-2 text-xs">
                    <i data-lucide="square" class="w-3 h-3 fill-current text-destructive"></i>
                    Stop generating
                </button>
            </div>

            <div class="max-w-4xl mx-auto relative">
                <div class="input-ring bg-card border border-input rounded-xl shadow-sm flex flex-col transition-shadow">
                    <textarea id="message-input" rows="1" class="w-full bg-transparent text-foreground placeholder:text-muted-foreground px-4 py-3 focus:outline-none resize-none max-h-48 overflow-y-auto text-sm" placeholder="Message OpenRun..." autofocus></textarea>
                    
                    <div class="flex items-center justify-between px-3 pb-2 pt-1">
                        <div class="flex items-center gap-2">
                            <label class="flex items-center gap-1.5 cursor-pointer select-none text-xs text-muted-foreground hover:text-foreground transition">
                                <input type="checkbox" id="stream-toggle" class="rounded border-input text-primary focus:ring-primary w-3.5 h-3.5 bg-background" checked>
                                Stream
                            </label>
                        </div>
                        <button id="send-btn" class="btn btn-primary h-8 w-8 p-0 rounded-lg flex items-center justify-center transition-all disabled:opacity-50 disabled:bg-primary" disabled>
                            <i data-lucide="arrow-up" class="w-4 h-4"></i>
                        </button>
                    </div>
                </div>
                <div class="text-center mt-2 text-[10px] text-muted-foreground">
                    AI models can make mistakes. Verify important information.
                </div>
            </div>
        </div>
    </main>

    <!-- SETTINGS MODAL -->
    <div id="settings-modal" class="hidden fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-card rounded-lg border border-border shadow-lg max-w-sm w-full animate-accordion-down flex flex-col">
            <div class="p-4 border-b border-border flex justify-between items-center">
                <h3 class="text-base font-semibold flex items-center gap-2 text-foreground">
                    <i data-lucide="settings" class="w-4 h-4"></i>
                    Settings
                </h3>
                <button id="close-settings-modal" class="btn btn-ghost btn-icon h-7 w-7 text-muted-foreground hover:text-foreground">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>
            
            <div class="p-4 space-y-4">
                <div class="space-y-1.5">
                    <div class="flex justify-between items-center">
                        <label class="text-sm font-medium text-foreground">Hugging Face Token</label>
                        <a href="https://huggingface.co/settings/tokens" target="_blank" class="text-xs text-primary hover:underline flex items-center gap-1">
                            Get Token <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
                        </a>
                    </div>
                    <input type="password" id="hf-token" placeholder="hf_..." class="w-full bg-background border border-input text-foreground text-sm rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring">
                    <p class="text-xs text-muted-foreground">Required for gated models like Llama-3.</p>
                </div>

                <div class="space-y-1.5">
                    <label class="text-sm font-medium text-foreground">API Key</label>
                    <input type="password" id="api-key" placeholder="sk-..." class="w-full bg-background border border-input text-foreground text-sm rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-ring">
                    <p class="text-xs text-muted-foreground">If your OpenRun server requires authentication.</p>
                </div>
                
                <div class="bg-muted p-3 rounded-md text-xs text-muted-foreground flex items-start gap-2">
                    <i data-lucide="info" class="w-4 h-4 flex-shrink-0 mt-0.5"></i>
                    <p>Credentials are stored securely in your browser's local storage.</p>
                </div>
            </div>
            
            <div class="p-4 border-t border-border flex justify-end">
                <button id="save-settings-btn" class="btn btn-primary">Save Changes</button>
            </div>
        </div>
    </div>

    <!-- SCRIPTS -->
    <script>
        // Icons Initialization
        lucide.createIcons();

        // Theme Toggle
        const themeToggle = document.getElementById('theme-toggle');
        const html = document.documentElement;
        
        // Initial Theme
        if (localStorage.theme === 'dark') {
            html.classList.add('dark');
        } else {
            html.classList.remove('dark');
        }
        
        themeToggle.addEventListener('click', () => {
            html.classList.toggle('dark');
            if (html.classList.contains('dark')) {
                localStorage.theme = 'dark';
            } else {
                localStorage.theme = 'light';
            }
        });

        // Config & State
        const API_URL = '/v1/chat/completions';
        const HEALTH_URL = '/';
        const MODELS_CATALOG_URL = '/models/catalog';
        const MODEL_STATUS_URL = '/models/status';
        const MODEL_LOAD_URL = '/models/load';
        const CHATS_URL = '/v1/chats';
        const METRICS_LIVE_URL = '/v1/metrics/live';

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
        
        // Custom UI selectors
        const sidebar = document.getElementById('sidebar');
        const sidebarToggleClose = document.getElementById('sidebar-toggle-close');
        const sidebarToggleOpen = document.getElementById('sidebar-toggle-open');
        const sidebarSearch = document.getElementById('sidebar-search');
        const modelSelectTrigger = document.getElementById('model-select-trigger');
        const modelDropdown = document.getElementById('model-dropdown');
        const activeModelNameDisplay = document.getElementById('active-model-name-display');
        const openSettingsBtn = document.getElementById('open-settings-btn');
        const closeSettingsModal = document.getElementById('close-settings-modal');
        const settingsModal = document.getElementById('settings-modal');
        const saveSettingsBtn = document.getElementById('save-settings-btn');
        const exitBtn = document.getElementById('exit-btn');

        // Init localStorage credentials
        if (localStorage.getItem('openrun_api_key')) apiKeyInput.value = localStorage.getItem('openrun_api_key');
        if (localStorage.getItem('openrun_hf_token')) hfTokenInput.value = localStorage.getItem('openrun_hf_token');

        // Sidebar Toggle
        sidebarToggleClose.addEventListener('click', () => {
            sidebar.classList.remove('sidebar-expanded');
            sidebar.classList.add('sidebar-collapsed');
            sidebarToggleOpen.classList.remove('hidden');
        });
        sidebarToggleOpen.addEventListener('click', () => {
            sidebar.classList.remove('sidebar-collapsed');
            sidebar.classList.add('sidebar-expanded');
            sidebarToggleOpen.classList.add('hidden');
        });

        // Model Dropdown
        modelSelectTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            modelDropdown.classList.toggle('hidden');
            const icon = modelSelectTrigger.querySelector('[data-lucide="chevron-down"]');
            if (modelDropdown.classList.contains('hidden')) {
                icon.style.transform = '';
            } else {
                icon.style.transform = 'rotate(180deg)';
            }
        });
        document.addEventListener('click', (e) => {
            if (!modelDropdown.contains(e.target) && !modelSelectTrigger.contains(e.target)) {
                modelDropdown.classList.add('hidden');
                modelSelectTrigger.querySelector('[data-lucide="chevron-down"]').style.transform = '';
            }
        });

        // Settings Modal
        openSettingsBtn.addEventListener('click', () => settingsModal.classList.remove('hidden'));
        closeSettingsModal.addEventListener('click', () => settingsModal.classList.add('hidden'));
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

        // Setup Markdown Parser & Highlighter
        marked.setOptions({
            breaks: true,
            gfm: true,
            highlight: function(code, lang) {
                const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                return hljs.highlight(code, { language }).value;
            }
        });
        
        // Custom Renderer for Code Blocks
        const renderer = new marked.Renderer();
        renderer.code = function(code, language) {
            const validLanguage = hljs.getLanguage(language) ? language : 'plaintext';
            const highlighted = hljs.highlight(code, { language: validLanguage }).value;
            
            return \`
            <div class="my-4 rounded-md overflow-hidden border border-border bg-[#282c34] font-mono text-sm shadow-sm">
                <div class="code-header flex justify-between items-center px-3 py-1.5 bg-[#21252b] border-b border-[#181a1f] text-xs text-[#9ca3af]">
                    <span class="uppercase tracking-wider font-semibold">\${validLanguage}</span>
                    <button class="copy-code-btn flex items-center gap-1.5 hover:text-white transition-colors" onclick="copyCodeText(this)">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
                        <span>Copy</span>
                    </button>
                </div>
                <div class="p-3 overflow-x-auto">
                    <code class="hljs language-\${validLanguage}" style="background:transparent; padding:0;">\${highlighted}</code>
                </div>
            </div>\`;
        };
        marked.use({ renderer });

        window.copyCodeText = function(btn) {
            const preContainer = btn.closest('.code-header').nextElementSibling;
            const text = preContainer.querySelector('code').innerText;
            navigator.clipboard.writeText(text);
            const span = btn.querySelector('span');
            span.innerText = 'Copied!';
            setTimeout(() => span.innerText = 'Copy', 2000);
        };

        // Render Markdown securely
        function renderMarkdown(content) {
            if (!content) return '';
            try {
                // Stabilize incomplete code blocks during streaming
                const fenceCount = (content.match(/\`\`\`/g) || []).length;
                let stableContent = content;
                if (fenceCount % 2 === 1) {
                    stableContent += '\\n\`\`\`';
                }
                const rawHtml = marked.parse(stableContent);
                // Sanitize HTML
                return DOMPurify.sanitize(rawHtml, {
                    ADD_ATTR: ['target', 'onclick', 'data-lucide', 'class', 'style'],
                    ADD_TAGS: ['svg', 'path', 'rect', 'circle', 'line', 'polyline', 'polygon']
                });
            } catch (e) {
                console.error("Markdown parse error:", e);
                return content;
            }
        }

        // Fetch API
        async function fetchAPI(url, options = {}) {
            const apiKey = apiKeyInput.value.trim();
            const headers = {
                'Content-Type': 'application/json',
                ...(apiKey ? {'Authorization': \`Bearer \${apiKey}\`} : {}),
                ...options.headers
            };
            return fetch(url, { ...options, headers });
        }

        async function fetchModels() {
            try {
                const res = await fetchAPI(MODELS_CATALOG_URL);
                if (!res.ok) return;
                const data = await res.json();
                catalogModels = data.data || [];
                renderModelsDropdown();
            } catch (err) { console.error(err); }
        }

        function renderModelsDropdown() {
            const dropdown = document.getElementById('dropdown-model-list');
            dropdown.innerHTML = '';
            
            if (catalogModels.length === 0) {
                dropdown.innerHTML = \`<div class="px-3 py-2 text-center text-xs text-muted-foreground">No models</div>\`;
                return;
            }

            catalogModels.forEach(model => {
                const option = document.createElement('button');
                option.className = 'w-full text-left px-3 py-2 text-sm text-foreground hover:bg-accent hover:text-accent-foreground rounded-sm flex items-center justify-between transition group';
                
                option.innerHTML = \`
                    <div class="flex flex-col">
                        <span class="font-medium">\${model.id}</span>
                        <span class="text-[10px] text-muted-foreground">\${model.size || 'N/A'} • \${model.engine || 'N/A'}</span>
                    </div>
                \`;
                
                option.addEventListener('click', async () => {
                    activeModelId = model.id;
                    activeModelNameDisplay.textContent = model.id;
                    modelDropdown.classList.add('hidden');
                    modelSelectTrigger.querySelector('[data-lucide="chevron-down"]').style.transform = '';
                    await loadSelectedModelByName(model.id);
                });
                
                dropdown.appendChild(option);
            });
        }

        async function fetchHealth() {
            try {
                const res = await fetch(HEALTH_URL);
                if (res.ok) {
                    const data = await res.json();
                    if (data.model) {
                        modelReady = true;
                        modelLoadStatus.textContent = 'Active';
                        modelLoadStatus.className = 'text-green-500 font-medium';
                        document.getElementById('live-indicator-dot').classList.remove('hidden');
                        
                        // Select model in UI
                        const activeKey = data.model;
                        const modelBaseName = activeKey.split('/').pop() || activeKey;
                        activeModelId = activeKey;
                        activeModelNameDisplay.textContent = modelBaseName;
                        modelGate.classList.add('hidden');
                    } else {
                        modelReady = false;
                        modelLoadStatus.textContent = 'No Model';
                        modelLoadStatus.className = 'text-amber-500 font-medium';
                        showGateLoader("Active Service", "No LLM loaded. Please select one from the dropdown.");
                    }
                }
            } catch (e) {
                modelReady = false;
                modelLoadStatus.textContent = 'Offline';
                modelLoadStatus.className = 'text-destructive font-medium';
                document.getElementById('live-indicator-dot').classList.add('hidden');
                showGateLoader("Offline", "Local server is unreachable.");
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
            modelLoadStatus.className = 'text-primary font-medium animate-pulse';
            
            showGateLoader("Loading weights", \`Loading \${modelId} into memory...\`);
            updateSendButtonState();

            const payload = {
                model_key: modelId,
                hf_token: hfTokenInput.value.trim() || null
            };

            let res = await fetchAPI(MODEL_LOAD_URL, { method: 'POST', body: JSON.stringify(payload) }).catch(() => null);
            if (!res || res.status === 404) {
                res = await fetchAPI('/v1/models/load', { method: 'POST', body: JSON.stringify(payload) }).catch(() => null);
            }

            if (!res || !res.ok) {
                showError('Failed to load model.');
                fetchHealth();
                return;
            }

            if (modelStatusPoll) clearInterval(modelStatusPoll);
            modelStatusPoll = setInterval(pollModelStatus, 1500);
            await pollModelStatus();
        }

        async function pollModelStatus() {
            let res = await fetchAPI(MODEL_STATUS_URL).catch(() => null);
            if (!res || !res.ok) res = await fetchAPI('/v1/models/status').catch(() => null);
            if (!res || !res.ok) return;
            const status = await res.json();

            if (status.status === 'loading' || status.status === 'queued') {
                modelReady = false;
                const prog = status.progress ? \`(\${status.progress}%)\` : '';
                modelLoadStatus.textContent = \`Loading \${prog}\`;
                showGateLoader("Loading model", \`\${status.message || 'Queued'} \${prog}\`);
            } else if (status.status === 'ready' || status.loaded_model) {
                modelReady = true;
                modelLoadStatus.textContent = 'Active';
                modelLoadStatus.className = 'text-green-500 font-medium';
                if (modelStatusPoll) { clearInterval(modelStatusPoll); modelStatusPoll = null; }
                modelGate.classList.add('hidden');
                await fetchHealth();
            } else if (status.status === 'error') {
                modelReady = false;
                modelLoadStatus.textContent = 'Error';
                modelLoadStatus.className = 'text-destructive font-medium';
                showGateLoader("Load Failed", status.error || 'Failed to load weights.');
                if (modelStatusPoll) { clearInterval(modelStatusPoll); modelStatusPoll = null; }
            }
            updateSendButtonState();
        }

        // Chat Management
        function renderEmptyChats() {
            chatsList.innerHTML = \`
                <div class="py-6 text-center text-muted-foreground flex flex-col items-center">
                    <i data-lucide="message-square-off" class="w-6 h-6 mb-2 opacity-50"></i>
                    <p class="text-xs">No chats yet</p>
                </div>
            \`;
            lucide.createIcons();
        }

        async function fetchChats() {
            try {
                const res = await fetchAPI(CHATS_URL);
                if (!res.ok) { renderEmptyChats(); return; }
                const data = await res.json();
                const chats = data.data || [];

                chatsList.innerHTML = '';
                if (chats.length === 0) { renderEmptyChats(); return; }

                chats.forEach(chat => {
                    const isActive = chat.id === currentChatId;
                    const btn = document.createElement('div');
                    btn.className = \`group flex items-center justify-between px-3 py-2 rounded-md cursor-pointer transition text-sm \${isActive ? 'bg-accent text-accent-foreground font-medium' : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground'}\`;
                    
                    btn.innerHTML = \`
                        <div class="flex items-center gap-2 truncate">
                            <i data-lucide="message-square" class="w-4 h-4 flex-shrink-0"></i>
                            <span class="truncate">\${chat.title || 'Untitled'}</span>
                        </div>
                    \`;
                    btn.addEventListener('click', () => openChat(chat.id));
                    chatsList.appendChild(btn);
                });
                lucide.createIcons();
                
                if (!currentChatId && chats.length) {
                    await openChat(chats[0].id);
                }
            } catch (err) { renderEmptyChats(); }
        }

        async function createChat(title = 'New Chat') {
            const res = await fetchAPI(CHATS_URL, { method: 'POST', body: JSON.stringify({ title }) });
            if (!res.ok) return null;
            const data = await res.json();
            currentChatId = data.chat?.id || null;
            clearChatView();
            await fetchChats();
            return currentChatId;
        }

        async function openChat(chatId) {
            if (!chatId) return;
            const res = await fetchAPI(\`\${CHATS_URL}/\${chatId}\`);
            if (!res.ok) return;
            const data = await res.json();
            if (!data.ok) { showError('Failed to open chat'); return; }
            currentChatId = chatId;
            renderExistingMessages(data.chat?.messages || []);
            await fetchChats();
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
            if ((chatMessages || []).length > 0) emptyState.style.display = 'none';
            chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'auto' });
        }

        async function fetchLiveMetrics() {
            const res = await fetchAPI(METRICS_LIVE_URL).catch(() => null);
            if (!res || !res.ok) return;
            const data = await res.json();
            if (data.data) liveMetrics.textContent = \`\${data.data.tokens_per_sec || 0.0} TPS\`;
        }

        // Messaging Logic
        function updateSendButtonState() {
            sendBtn.disabled = isGenerating || messageInput.value.trim() === '' || !modelReady;
        }
        
        function adjustTextareaHeight() {
            messageInput.style.height = 'auto';
            messageInput.style.height = Math.min(messageInput.scrollHeight, 200) + 'px';
        }

        messageInput.addEventListener('input', () => { adjustTextareaHeight(); updateSendButtonState(); });
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!sendBtn.disabled && !isGenerating) sendMessage();
            }
        });

        sendBtn.addEventListener('click', sendMessage);
        newChatBtn.addEventListener('click', () => createChat('New Chat'));
        clearBtn.addEventListener('click', () => { if (!isGenerating) clearChatView(); });

        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const spans = btn.querySelectorAll('span');
                messageInput.value = spans[0].textContent + " " + spans[1].textContent;
                messageInput.focus();
                adjustTextareaHeight();
                updateSendButtonState();
            });
        });

        stopBtn.addEventListener('click', () => {
            if (abortController) {
                abortController.abort();
                setUIGenerationState(false);
                const lastMsg = chatContainer.lastElementChild;
                if (lastMsg && lastMsg.dataset.role === 'assistant') {
                    const ind = lastMsg.querySelector('.typing-indicator');
                    if (ind) ind.remove();
                }
            }
        });

        function showError(msg) {
            errorMsg.textContent = msg;
            errorToast.classList.remove('opacity-0', 'translate-y-2');
            setTimeout(() => errorToast.classList.add('opacity-0', 'translate-y-2'), 4000);
        }

        function setUIGenerationState(generating) {
            isGenerating = generating;
            messageInput.disabled = generating;
            if (generating) {
                stopBtn.classList.remove('hidden');
                sendBtn.innerHTML = \`<i data-lucide="loader-2" class="w-4 h-4 text-primary-foreground animate-spin"></i>\`;
            } else {
                stopBtn.classList.add('hidden');
                sendBtn.innerHTML = \`<i data-lucide="arrow-up" class="w-4 h-4 text-primary-foreground"></i>\`;
                messageInput.focus();
            }
            lucide.createIcons();
            updateSendButtonState();
        }

        function createMessageElement(role, content) {
            const isUser = role === 'user';
            const div = document.createElement('div');
            div.className = \`flex w-full mx-auto max-w-3xl gap-4 \${isUser ? 'flex-row-reverse' : ''} animate-accordion-down\`;
            div.dataset.role = role;
            
            const avatar = document.createElement('div');
            avatar.className = \`w-8 h-8 flex-shrink-0 rounded-md flex items-center justify-center shadow-sm \${isUser ? 'bg-primary text-primary-foreground' : 'bg-muted border border-border text-foreground'}\`;
            
            if (isUser) {
                avatar.innerHTML = \`<i data-lucide="user" class="w-4.5 h-4.5"></i>\`;
            } else {
                avatar.innerHTML = \`<i data-lucide="bot" class="w-4.5 h-4.5"></i>\`;
            }
            
            const contentContainer = document.createElement('div');
            contentContainer.className = \`flex flex-col flex-1 min-w-0 \${isUser ? 'items-end' : 'items-start'}\`;
            
            const textBubble = document.createElement('div');
            textBubble.className = \`px-4 py-3 rounded-2xl max-w-full \${isUser ? 'bg-primary text-primary-foreground rounded-tr-sm' : 'bg-card border border-border text-foreground rounded-tl-sm shadow-sm'}\`;
            
            const textDiv = document.createElement('div');
            textDiv.className = \`prose prose-sm dark:prose-invert max-w-none w-full break-words \${isUser ? 'text-primary-foreground prose-p:text-primary-foreground prose-headings:text-primary-foreground prose-strong:text-primary-foreground prose-a:text-primary-foreground' : ''}\`;
            
            if (isUser) {
                textDiv.textContent = content;
            } else if (content === '') {
                textDiv.innerHTML = '<div class="typing-indicator"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';
            } else {
                textDiv.innerHTML = renderMarkdown(content);
            }
            
            textBubble.appendChild(textDiv);
            contentContainer.appendChild(textBubble);
            div.appendChild(avatar);
            div.appendChild(contentContainer);
            
            // Re-init icons for dynamic content
            setTimeout(() => lucide.createIcons({ root: avatar }), 0);
            
            return { element: div, textDiv };
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
                if (dataLines.length) events.push(dataLines.join('\\n'));
            }
            return { events, remainder };
        }

        async function sendMessage() {
            const text = messageInput.value.trim();
            if (!text || !modelReady) return;
            
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
            
            try {
                const payload = { model: activeModelId || "openrun", messages, stream: isStreaming, chat_id: currentChatId };
                const response = await fetchAPI(API_URL, {
                    method: 'POST',
                    body: JSON.stringify(payload),
                    signal: abortController.signal
                });
                
                if (!response.ok) {
                    let errMsg = \`HTTP \${response.status}\`;
                    try { errMsg = (await response.json()).detail || errMsg; } catch(e) {}
                    botTextDiv.innerHTML = \`<span class="text-destructive font-medium">\${errMsg}</span>\`;
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
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        
                        sseBuffer += decoder.decode(value, { stream: true });
                        const parsed = parseSSEEvents(sseBuffer);
                        sseBuffer = parsed.remainder;
                        
                        for (const eventData of parsed.events) {
                            if (eventData === '[DONE]') continue;
                            try {
                                const data = JSON.parse(eventData);
                                const delta = data.choices?.[0]?.delta?.content || '';
                                if (delta) {
                                    fullResponseText += delta;
                                    botTextDiv.innerHTML = renderMarkdown(fullResponseText);
                                    chatContainer.scrollTo({ top: chatContainer.scrollHeight });
                                }
                                if (data.error?.message) showError(data.error.message);
                            } catch (e) {}
                        }
                    }
                    botTextDiv.innerHTML = renderMarkdown(fullResponseText);
                } else {
                    const data = await response.json();
                    fullResponseText = data.choices[0]?.message?.content || '';
                    botTextDiv.innerHTML = renderMarkdown(fullResponseText);
                }
                
                messages.push({ role: 'assistant', content: fullResponseText });
                await fetchChats();
                await fetchLiveMetrics();
                
            } catch (err) {
                if (err.name !== 'AbortError') {
                    botTextDiv.innerHTML = \`<span class="text-destructive font-medium">Connection failed</span>\`;
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
        }

        // Live Search
        sidebarSearch.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            Array.from(chatsList.children).forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(query)) item.style.display = 'flex';
                else item.style.display = 'none';
            });
        });

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
