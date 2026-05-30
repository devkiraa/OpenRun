import sys
import time
import math

def animate_loading_status(stage: str, message: str, duration: float = 1.0):
    """
    Renders an organic, glowing braille loading spinner with a Sunset Ember pulse progress bar.
    Fails back safely to plain logs in non-interactive/notebook streams.
    """
    import os
    is_notebook = "google.colab" in sys.modules or "COLAB_GPU" in os.environ or "ipykernel" in sys.modules
    
    if not sys.stdout.isatty() or is_notebook:
        # Static fallback for non-TTY / notebook pipelines
        print(f"[{stage}] {message}...")
        return

    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    steps = int(duration / 0.05)
    
    start_time = time.time()
    try:
        for i in range(steps):
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break
                
            frame_idx = i % len(frames)
            spinner = frames[frame_idx]
            
            # Sunset Ember dynamic flowing gradient
            phase = i * 0.1
            r = int(210 + 45 * math.sin(phase))
            g = int(100 + 70 * math.cos(phase))
            b = int(15 + 15 * math.sin(phase))
            color = f"\033[38;2;{r};{g};{b}m"
            
            pct = min(100, int((i / steps) * 100))
            
            # Progress bar
            bar_len = 15
            filled = int((pct / 100) * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            
            # Output in-place
            sys.stdout.write(f"\r\033[K\033[90m[{stage}]\033[0m {color}{spinner}\033[0m {message}... {color}[{bar}] {pct}%\033[0m")
            sys.stdout.flush()
            time.sleep(0.05)
            
        # Completion line
        sys.stdout.write(f"\r\033[K\033[92m✔ [{stage}] {message} - Complete!\033[0m\n")
    finally:
        # Ensure cursor is always restored even on interrupts
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def draw_live_dashboard(port: int, api_key: str = None):
    """
    Renders a mathematically perfect, cleanly aligned console dashboard card.
    Uses standard ASCII characters to guarantee pixel-perfect column alignment across all terminal types.
    """
    from openrun.core.state import get_global_state
    from urllib.parse import quote
    
    state = get_global_state()
    model_name = "openrun"
    if state:
        if state.adapter and hasattr(state.adapter, 'model_name'):
            model_name = state.adapter.model_name
        elif state.config and state.config.model:
            model_name = state.config.model
            
    api_base_url = f"http://localhost:{port}/v1"
    endpoint = f"http://localhost:{port}/v1/chat/completions"
    docs = f"http://localhost:{port}/docs"
    
    # Construct Hosted Web Chat Share Link
    base_chat_domain = "https://openrun-web.vercel.app/"
    params = f"?url={quote(api_base_url)}&theme=dark"
    if model_name:
        params += f"&model={quote(model_name)}"
    if api_key:
        params += f"&key={quote(api_key)}"
    share_url = base_chat_domain + params
    
    # OSC 8 Clickable Link
    click_text = "Click to Open Web Chat"
    osc8_link = f"\033]8;;{share_url}\033\\{click_text}\033]8;;\033\\"
    
    # Theme colors (Sunset Ember / Amber Gold / Clean White)
    border = "\033[38;2;255;100;30m"
    header = "\033[38;2;210;170;15m"
    key_color = "\033[38;2;250;130;30m"
    text = "\033[97m"
    dim = "\033[90m"
    link_color = "\033[38;2;30;144;255m" # glowing dodger blue
    reset = "\033[0m"
    
    # Fixed 60-character inner content box width
    box_width = 60
    
    title_text = "  OPENRUN API RUNTIME IS LIVE & ACCEPTING REQUESTS"
    endpoint_label = "  • API Endpoint: "
    docs_label = "  • Swagger UI:   "
    chat_label = "  • Web Chat UI:  "
    key_label = "  • API Key:      "
    
    # Pad right side to ensure perfect border alignment
    title_row = title_text.ljust(box_width)
    endpoint_row = (endpoint_label + endpoint).ljust(box_width)
    docs_row = (docs_label + docs).ljust(box_width)
    
    if api_key:
        masked_key = api_key
        if len(api_key) > 20:
            masked_key = api_key[:8] + "..." + api_key[-8:]
        key_value = masked_key
        key_color_code = key_color
    else:
        key_value = "None (Public Access Mode)"
        key_color_code = dim

    # Format the key row while keeping alignment intact
    key_plain_str = key_label + key_value
    key_padded = key_plain_str.ljust(box_width)
    val_start = key_padded.find(key_value)
    key_row = key_padded[:val_start] + key_color_code + key_value + reset + key_padded[val_start + len(key_value):]

    import os
    is_notebook = "google.colab" in sys.modules or "COLAB_GPU" in os.environ or "ipykernel" in sys.modules

    # Format the Web Chat row using standard spaces for length calculation, then inject OSC 8 if not in a notebook
    if is_notebook:
        chat_value = "See Link Below"
        chat_plain_str = chat_label + f"[{chat_value}]"
        chat_padded = chat_plain_str.ljust(box_width)
        val_start = chat_padded.find(f"[{chat_value}]")
        chat_row = chat_padded[:val_start] + link_color + f"[{chat_value}]" + reset + chat_padded[val_start + len(f"[{chat_value}]"):]
    else:
        chat_plain_str = chat_label + f"[{click_text}]"
        chat_padded = chat_plain_str.ljust(box_width)
        val_start = chat_padded.find(f"[{click_text}]")
        chat_row = chat_padded[:val_start] + link_color + f"[{osc8_link}]" + reset + chat_padded[val_start + len(f"[{click_text}]"):]

    # Print dashboard box
    print(f"\n{border}┌────────────────────────────────────────────────────────────┐{reset}")
    print(f"{border}│{reset}{header}{title_row}{reset}{border}│{reset}")
    print(f"{border}├────────────────────────────────────────────────────────────┤{reset}")
    print(f"{border}│{reset}{text}{endpoint_row}{reset}{border}│{reset}")
    print(f"{border}│{reset}{text}{docs_row}{reset}{border}│{reset}")
    print(f"{border}│{reset}{text}{chat_row}{reset}{border}│{reset}")
    print(f"{border}│{reset}{text}{key_row}{reset}{border}│{reset}")
    print(f"{border}└────────────────────────────────────────────────────────────┘{reset}")
    
    # Print the raw link right below so they can copy it with one click
    print(f"👉 {text}Share / Copy Web Chat Link:{reset} {link_color}{share_url}{reset}\n")
