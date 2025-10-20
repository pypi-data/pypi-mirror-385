#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import mimetypes
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from http_handler_js import get_javascript_code  # Import the JS code function

mimetypes.init()
mimetypes.add_type('image/avif', '.avif')
mimetypes.add_type('video/quicktime', '.mov')
mimetypes.add_type('audio/mp4', '.m4a')
mimetypes.add_type('audio/flac', '.flac')
mimetypes.add_type('audio/aac', '.aac')
mimetypes.add_type('audio/opus', '.opus')


class CropHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if self.server.verbose:
            super().log_message(format, *args)

    def _get_media_type_info(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()

        supported_image_exts = [
            ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg", ".ico", ".avif", ".tiff", ".tif", ".heic", ".heif", ".jxl"
        ]
        
        supported_video_exts = [
            ".mp4", ".webm", ".ogv", ".mov"
        ]
        
        supported_audio_exts = [
            ".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".opus"
        ]

        cache_buster = int(time.time())
        media_tag = ""
        media_type = ""
        controls_html = ""

        if ext in supported_image_exts:
            media_tag = f'<img id="media" src="/file?v={cache_buster}" onload="initializeCrop()" draggable="false" alt="Media file" />'
            media_type = "image"
        elif ext in supported_video_exts:
            media_tag = f'<video id="media" preload="metadata" src="/file?v={cache_buster}" onloadedmetadata="initializeCrop()" draggable="false"></video>'
            media_type = "video"
            controls_html = '''
<div class="video-controls" id="videoControls">
  <button id="playPause" class="control-btn" title="Play/Pause">▶️</button>
  <div class="progress-container">
    <span id="currentTime">0:00</span>
    <input type="range" id="seekBar" class="seek-bar" min="0" max="100" value="0" step="any">
    <span id="duration">0:00</span>
  </div>
  <select id="playbackSpeed" class="control-select" title="Playback Speed">
    <option value="0.5">0.5x</option>
    <option value="0.75">0.75x</option>
    <option value="1" selected>1x</option>
    <option value="1.25">1.25x</option>
    <option value="1.5">1.5x</option>
    <option value="1.75">1.75x</option>
    <option value="2">2x</option>
  </select>
  <div class="volume-container">
    <button id="muteBtn" class="control-btn" title="Mute/Unmute">🔊</button>
    <input type="range" id="volumeBar" class="volume-bar" min="0" max="100" value="100" step="1" title="Volume">
  </div>
</div>'''
        elif ext in supported_audio_exts:
            media_tag = f'<audio id="media" controls preload="metadata" src="/file?v={cache_buster}" onloadedmetadata="initializeCrop()"></audio>'
            media_type = "audio"
            controls_html = ""
        else:
            media_tag = '<div id="unsupported"><div class="unsupported-content"><div class="unsupported-icon">📁</div><div class="unsupported-text">Format not supported for preview</div><div class="unsupported-subtext">You can still set crop coordinates (default size: 500x300)</div></div></div>'
            media_type = "unsupported"
        
        return ext, media_tag, media_type, controls_html

    def do_GET(self):
        path = urlparse(self.path).path
        ext, media_tag, media_type, controls_html = self._get_media_type_info(self.server.media_file)

        if path == "/":
            media_wrapper_start = '<div id="media-wrapper">'
            crop_div = '<div id="crop" class="crop-box" style="left:50px;top:50px;width:200px;height:150px;" tabindex="0" role="img" aria-label="Crop selection area"><div class="resize-handle nw"></div><div class="resize-handle ne"></div><div class="resize-handle sw"></div><div class="resize-handle se"></div><div class="resize-handle n"></div><div class="resize-handle s"></div><div class="resize-handle w"></div><div class="resize-handle e"></div></div>'
            
            if media_type in ["image", "video", "unsupported"]:
                media_section = media_wrapper_start + media_tag + crop_div + '</div>' + controls_html
            else:
                media_section = media_wrapper_start + media_tag + '</div>' + controls_html 
            
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MediaCrop - Visual FFmpeg Crop Tool</title>
  <style>
    * {{ 
      box-sizing: border-box; 
      margin: 0; 
      padding: 0;
    }}
    
    :root {{
      --primary: #00ff41;
      --primary-hover: #00cc33;
      --primary-dark: #00aa2a;
      --bg-main: #0f0f0f;
      --bg-panel: #1a1a1a;
      --bg-control: #252525;
      --border: #333;
      --border-light: #444;
      --text-main: #ffffff;
      --text-muted: #aaa;
      --text-dim: #666;
      --shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
      --shadow-heavy: 0 8px 32px rgba(0, 0, 0, 0.6);
      --radius: 8px;
      --radius-large: 12px;
      --primary-rgb: 0, 255, 65;
    }}
    
    .light-theme {{
        --primary: #008000;
        --primary-hover: #006400;
        --primary-dark: #004d00;
        --bg-main: #f0f0f0;
        --bg-panel: #ffffff;
        --bg-control: #e0e0e0;
        --border: #ccc;
        --border-light: #ddd;
        --text-main: #1a1a1a;
        --text-muted: #555;
        --text-dim: #888;
        --shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        --shadow-heavy: 0 8px 32px rgba(0, 0, 0, 0.15);
        --primary-rgb: 0, 128, 0;
    }}
    
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      background: var(--bg-main);
      color: var(--text-main);
      user-select: none;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      transition: background-color 0.3s, color 0.3s;
    }}

    .header-bar {{
      background: var(--bg-panel);
      border-bottom: 1px solid var(--border);
      padding: 12px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
      height: 60px;
    }}
    
    .header-controls {{
        display: flex;
        align-items: center;
        gap: 20px;
    }}

    #themeToggle {{
        background: var(--bg-control);
        border: 1px solid var(--border);
        color: var(--text-main);
        font-size: 20px;
        line-height: 1;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }}
    
    #themeToggle:hover {{
        background: var(--border);
        box-shadow: 0 0 10px rgba(var(--primary-rgb), 0.3);
    }}

    .app-title {{
      font-size: 18px;
      font-weight: 600;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .app-title::before {{
      content: '✂️';
      font-size: 20px;
    }}

    .file-info {{
      display: flex;
      align-items: center;
      gap: 15px;
      font-size: 13px;
      color: var(--text-muted);
    }}

    .file-detail {{
      display: flex;
      align-items: center;
      gap: 5px;
    }}

    .file-detail-label {{
      color: var(--text-dim);
    }}

    .file-detail-value {{
      color: var(--text-main);
      font-weight: 500;
    }}

    .main-content {{
      display: flex;
      flex: 1;
      min-height: 0;
    }}

    .sidebar {{
      width: 280px;
      background: var(--bg-panel);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }}

    .sidebar-section {{
      border-bottom: 1px solid var(--border);
      padding: 20px;
    }}

    .sidebar-section:last-child {{
      border-bottom: none;
      flex: 1;
    }}

    .section-title {{
      font-size: 14px;
      font-weight: 600;
      color: var(--text-main);
      margin-bottom: 15px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .section-title::before {{
      font-size: 16px;
    }}

    .section-title.aspect::before {{ content: '📐'; }}
    .section-title.tools::before {{ content: '🔧'; }}
    .section-title.info::before {{ content: '📊'; }}

    .form-group {{
      margin-bottom: 15px;
    }}

    .form-group:last-child {{
      margin-bottom: 0;
    }}

    .form-label {{
      display: block;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-muted);
      margin-bottom: 6px;
    }}

    .form-select, .form-input, .form-button {{
      width: 100%;
      padding: 10px 12px;
      background: var(--bg-control);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      color: var(--text-main);
      font-size: 13px;
      transition: all 0.2s ease;
    }}

    .form-select:focus, .form-input:focus {{
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 30%, transparent);
    }}

    .form-input {{
      text-align: center;
      font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
    }}

    .custom-ratio {{
      display: none;
      grid-template-columns: 1fr auto 1fr;
      gap: 8px;
      align-items: center;
      margin-top: 8px;
    }}

    .custom-ratio.visible {{
      display: grid;
    }}

    .ratio-separator {{
      color: var(--text-muted);
      font-weight: 500;
    }}

    .form-button {{
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: #000;
      font-weight: 600;
      cursor: pointer;
      border: none;
      transition: all 0.2s ease;
    }}

    .form-button:hover {{
      background: linear-gradient(135deg, var(--primary-hover), var(--primary));
      transform: translateY(-1px);
      box-shadow: 0 4px 12px color-mix(in srgb, var(--primary) 50%, transparent);
    }}

    .form-button:active {{
      transform: translateY(0);
    }}
    
    .light-theme .form-button {{
        color: #ffffff;
    }}
    
    .light-theme .form-button:hover {{
        color: #ffffff;
    }}
    
    #saveButton {{
      background: linear-gradient(135deg, #4CAF50, #45a049) !important;
      color: #ffffff !important;
    }}

    .button-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}

    .button-grid .form-button {{
      font-size: 12px;
      padding: 8px 10px;
    }}

    .info-stats {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .info-stat {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
    }}

    .info-stat-label {{
      color: var(--text-muted);
    }}

    .info-stat-value {{
      color: var(--primary);
      font-weight: 600;
      font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
    }}

    .media-viewer {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 30px;
      position: relative;
      background: radial-gradient(circle at center, var(--bg-panel) 0%, var(--bg-main) 100%);
      min-height: 0;
      overflow: auto; 
      scrollbar-width: auto;
      scrollbar-color: var(--primary) var(--bg-control);
    }}
    
    .media-viewer::-webkit-scrollbar {{
      width: 20px;
      height: 20px;
    }}

    .media-viewer::-webkit-scrollbar-track {{
      background: var(--bg-control);
    }}

    .media-viewer::-webkit-scrollbar-thumb {{
      background-color: var(--primary);
      border-radius: 8px;
      border: 4px solid var(--bg-control);
    }}

    .media-viewer::-webkit-scrollbar-thumb:hover {{
      background-color: var(--primary-hover);
    }}

    #container {{
      position: relative;
      border: 2px solid var(--border-light);
      border-radius: var(--radius-large);
      background: #000;
      box-shadow: var(--shadow-heavy);
      display: inline-block;
    }}
    
    .light-theme #container {{
        background: #333;
    }}

    #media-wrapper {{
        position: relative;
        display: inline-block;
        line-height: 0;
    }}

    img, video, audio {{
      display: block;
      max-width: none;
      user-select: none;
      -webkit-user-drag: none;
      -moz-user-drag: none;
      -o-user-drag: none;
      user-drag: none;
      { "controls: none;" if media_type == "video" else "" } 
    }}

    #unsupported {{
      width: 500px;
      height: 300px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }}

    .unsupported-content {{
      text-align: center;
      padding: 40px;
    }}

    .unsupported-icon {{
      font-size: 48px;
      margin-bottom: 16px;
    }}

    .unsupported-text {{
      font-size: 18px;
      color: var(--text-main);
      margin-bottom: 8px;
      font-weight: 500;
    }}

    .unsupported-subtext {{
      font-size: 14px;
      color: var(--text-muted);
    }}

    .crop-box {{
      border: 2px dashed var(--primary);
      position: absolute;
      z-index: 50;
      box-sizing: border-box;
      min-width: 30px;
      min-height: 30px;
      cursor: grab;
      background: color-mix(in srgb, var(--primary) 15%, transparent); 
      box-shadow: 
        0 0 0 9999px color-mix(in srgb, var(--bg-main) 70%, transparent),
        inset 0 0 0 1px color-mix(in srgb, var(--primary) 30%, transparent);
      transition: box-shadow 0.2s ease;
    }}
    
    .light-theme .crop-box {{
        box-shadow: 
            0 0 0 9999px rgba(0, 0, 0, 0.4),
            inset 0 0 0 1px color-mix(in srgb, var(--primary) 50%, transparent);
    }}

    .crop-box:hover {{
      box-shadow: 
        0 0 0 9999px color-mix(in srgb, var(--bg-main) 75%, transparent),
        inset 0 0 0 1px color-mix(in srgb, var(--primary) 50%, transparent),
        0 0 20px color-mix(in srgb, var(--primary) 40%, transparent);
    }}

    .crop-box.dragging {{
      cursor: grabbing;
      box-shadow: 
        0 0 0 9999px color-mix(in srgb, var(--bg-main) 80%, transparent),
        inset 0 0 0 1px color-mix(in srgb, var(--primary) 70%, transparent),
        0 0 25px color-mix(in srgb, var(--primary) 60%, transparent);
    }}
    
    .light-theme .crop-box:hover, .light-theme .crop-box.dragging {{
        box-shadow: 
            0 0 0 9999px rgba(0, 0, 0, 0.5), 
            inset 0 0 0 1px color-mix(in srgb, var(--primary) 70%, transparent),
            0 0 25px color-mix(in srgb, var(--primary) 60%, transparent);
    }}


    .crop-box.show-grid::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-image: 
        linear-gradient(to right, color-mix(in srgb, var(--primary) 30%, transparent) 1px, transparent 1px),
        linear-gradient(to bottom, color-mix(in srgb, var(--primary) 30%, transparent) 1px, transparent 1px);
      background-size: 33.33% 33.33%;
      pointer-events: none;
    }}

    .resize-handle {{
      position: absolute;
      background: var(--primary);
      width: 16px;
      height: 16px;
      border: 2px solid var(--bg-main);
      border-radius: 50%;
      z-index: 51;
      transition: all 0.2s ease;
      transform: translate(-50%, -50%);
    }}
    
    .light-theme .resize-handle {{
        border: 2px solid var(--bg-panel);
    }}


    .resize-handle:hover {{
      background: #fff;
      transform: translate(-50%, -50%) scale(1.3);
      box-shadow: 0 0 8px color-mix(in srgb, var(--primary) 50%, transparent);
    }}
    
    .light-theme .resize-handle:hover {{
        background: #000;
        box-shadow: 0 0 8px color-mix(in srgb, var(--primary) 70%, transparent);
    }}

    .resize-handle.nw {{ top: 0; left: 0; cursor: nwse-resize; }}
    .resize-handle.ne {{ top: 0; right: 0; cursor: ne-resize; transform: translate(50%, -50%); }}
    .resize-handle.sw {{ bottom: 0; left: 0; cursor: sw-resize; transform: translate(-50%, 50%); }}
    .resize-handle.se {{ bottom: 0; right: 0; cursor: se-resize; transform: translate(50%, 50%); }}
    .resize-handle.n {{ top: 0; left: 50%; cursor: n-resize; }}
    .resize-handle.s {{ bottom: 0; left: 50%; cursor: s-resize; transform: translate(-50%, 50%); }}
    .resize-handle.w {{ left: 0; top: 50%; cursor: w-resize; }}
    .resize-handle.e {{ right: 0; top: 50%; cursor: e-resize; transform: translate(50%, -50%); }}

    .video-controls {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 20px;
      background: var(--bg-control);
      border-top: 1px solid var(--border-light);
      gap: 10px;
      flex-shrink: 0;
    }}

    .control-btn {{
      background: none;
      border: none;
      color: var(--text-main);
      font-size: 18px;
      cursor: pointer;
      padding: 5px;
      border-radius: var(--radius);
      transition: background 0.2s ease;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .control-btn:hover {{
      background: var(--border);
    }}

    .progress-container {{
      flex: 1;
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }}

    #currentTime, #duration {{
      font-size: 12px;
      color: var(--text-muted);
      min-width: 40px;
      font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
    }}

    .seek-bar {{
      flex: 1;
      height: 4px;
      background: var(--border);
      border-radius: 2px;
      outline: none;
      -webkit-appearance: none;
      cursor: pointer;
    }}

    .seek-bar::-webkit-slider-thumb {{
      -webkit-appearance: none;
      appearance: none;
      width: 12px;
      height: 12px;
      background: var(--primary);
      border-radius: 50%;
      cursor: pointer;
    }}

    .seek-bar::-moz-range-thumb {{
      width: 12px;
      height: 12px;
      background: var(--primary);
      border-radius: 50%;
      cursor: pointer;
      border: none;
    }}

    .control-select {{
      background: var(--bg-control);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 5px 8px;
      border-radius: var(--radius);
      font-size: 12px;
      cursor: pointer;
    }}

    .volume-container {{
      display: flex;
      align-items: center;
      gap: 5px;
      min-width: 100px;
    }}

    .volume-bar {{
      width: 80px;
      height: 4px;
      background: var(--border);
      border-radius: 2px;
      outline: none;
      -webkit-appearance: none;
      cursor: pointer;
    }}

    .volume-bar::-webkit-slider-thumb {{
      -webkit-appearance: none;
      appearance: none;
      width: 12px;
      height: 12px;
      background: var(--primary);
      border-radius: 50%;
      cursor: pointer;
    }}

    .volume-bar::-moz-range-thumb {{
      width: 12px;
      height: 12px;
      background: var(--primary);
      border-radius: 50%;
      cursor: pointer;
      border: none;
    }}

    .loading {{
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: var(--bg-panel);
      padding: 30px 40px;
      border-radius: var(--radius-large);
      box-shadow: var(--shadow-heavy);
      z-index: 1000;
      text-align: center;
    }}

    .spinner {{
      width: 32px;
      height: 32px;
      border: 3px solid var(--border);
      border-top: 3px solid var(--primary);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 15px;
    }}

    @keyframes spin {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}

    .loading-text {{
      font-size: 16px;
      font-weight: 500;
      color: var(--text-main);
    }}

    .help-modal {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      backdrop-filter: blur(4px);
    }}

    .help-content {{
      background: var(--bg-panel);
      border-radius: var(--radius-large);
      padding: 30px;
      max-width: 400px;
      box-shadow: var(--shadow-heavy);
      border: 1px solid var(--border);
    }}

    .help-title {{
      font-size: 20px;
      font-weight: 600;
      color: var(--primary);
      margin-bottom: 20px;
      text-align: center;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }}

    .help-title::before {{
      content: '⌨️';
      font-size: 24px;
    }}

    .help-shortcuts {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 25px;
    }}

    .help-shortcut {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 14px;
    }}

    .help-shortcut-desc {{
      color: var(--text-muted);
    }}

    .help-shortcut-key {{
      background: var(--bg-control);
      color: var(--primary);
      padding: 4px 8px;
      border-radius: 4px;
      font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
      font-size: 12px;
      font-weight: 600;
    }}

    .help-close {{
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: #000;
      border: none;
      padding: 12px 24px;
      border-radius: var(--radius);
      font-weight: 600;
      cursor: pointer;
      width: 100%;
      transition: all 0.2s ease;
    }}
    
    .light-theme .help-close {{
        color: #ffffff;
    }}


    .help-close:hover {{
      background: linear-gradient(135deg, var(--primary-hover), var(--primary));
      transform: translateY(-1px);
    }}

    .context-menu {{
      position: fixed;
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 8px 0;
      z-index: 300;
      display: none;
      box-shadow: var(--shadow);
      min-width: 180px;
    }}

    .context-item {{
      padding: 12px 16px;
      cursor: pointer;
      font-size: 14px;
      transition: background 0.2s ease;
      color: var(--text-main);
    }}

    .context-item:hover {{
      background: var(--bg-control);
      color: var(--primary);
    }}

    .floating-preview {{
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 200px;
      height: 180px;
      min-width: 150px;
      min-height: 120px;
      max-width: 90vw;
      max-height: 90vh;
      background: var(--bg-panel);
      border: 1px solid var(--border-light);
      border-radius: var(--radius);
      box-shadow: var(--shadow-heavy);
      z-index: 500;
      display: none; /* Initially hidden */
      flex-direction: column;
      overflow: hidden;
      transition: width 0.3s ease, height 0.3s ease, opacity 0.3s;
    }}

    .preview-header {{
      background: var(--bg-control);
      padding: 6px 10px;
      cursor: move;
      font-size: 12px;
      font-weight: 500;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-shrink: 0;
    }}

    .preview-header .preview-size {{
        font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
        color: var(--text-main);
    }}

    .preview-canvas-wrapper {{
      flex-grow: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      background: repeating-conic-gradient(var(--bg-main) 0% 25%, var(--bg-control) 0% 50%) 50% / 20px 20px;
      overflow: hidden;
      min-height: 0;
      cursor: pointer;
    }}

    #previewCanvas {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      image-rendering: pixelated;
    }}
    
    .preview-resize-handle {{
        position: absolute;
        width: 12px;
        height: 12px;
        background: var(--primary);
        border: 1px solid var(--bg-main);
        border-radius: 3px;
        z-index: 501;
        opacity: 0;
        transition: opacity 0.2s;
    }}

    .floating-preview:hover .preview-resize-handle {{
        opacity: 1;
    }}

    .p-nw {{ top: -1px; left: -1px; cursor: nwse-resize; }}
    .p-ne {{ top: -1px; right: -1px; cursor: nesw-resize; }}
    .p-sw {{ bottom: -1px; left: -1px; cursor: nesw-resize; }}
    .p-se {{ bottom: -1px; right: -1px; cursor: nwse-resize; }}
    .p-n {{ top: -1px; left: 50%; transform: translateX(-50%); cursor: ns-resize; }}
    .p-s {{ bottom: -1px; left: 50%; transform: translateX(-50%); cursor: ns-resize; }}
    .p-w {{ top: 50%; left: -1px; transform: translateY(-50%); cursor: ew-resize; }}
    .p-e {{ top: 50%; right: -1px; transform: translateY(-50%); cursor: ew-resize; }}

    .preview-close-btn {{
        display: none;
        position: absolute;
        top: 15px;
        right: 15px;
        width: 40px;
        height: 40px;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        font-size: 24px;
        line-height: 38px;
        text-align: center;
        cursor: pointer;
        z-index: 502;
        transition: transform 0.2s, background 0.2s;
    }}

    .preview-close-btn:hover {{
        background: rgba(0, 0, 0, 0.8);
        transform: scale(1.1);
    }}
    
    .floating-preview.fullscreen {{
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        max-width: 100vw;
        max-height: 100vh;
        border-radius: 0;
        z-index: 2000;
        transition: none;
    }}

    .floating-preview.fullscreen .preview-header,
    .floating-preview.fullscreen .preview-resize-handle {{
        display: none;
    }}
    
    .floating-preview.fullscreen .preview-close-btn {{
        display: block;
    }}
    
    .floating-preview.fullscreen .preview-canvas-wrapper {{
        background: #000;
    }}

    .notification {{
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: var(--bg-panel);
      color: var(--text-main);
      padding: 25px 35px;
      border-radius: var(--radius-large);
      z-index: 2100;
      box-shadow: var(--shadow-heavy);
      border: 1px solid var(--primary);
      text-align: center;
      max-width: 400px;
      animation: fadeInOut 3s forwards;
    }}

    .notification-title {{
      font-size: 18px;
      font-weight: 600;
      color: var(--primary);
      margin-bottom: 15px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }}

    .notification-title::before {{
      content: '✅';
      font-size: 20px;
    }}

    .notification-code {{
      background: var(--bg-control);
      padding: 12px 16px;
      border-radius: var(--radius);
      font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
      font-size: 14px;
      color: var(--primary);
      margin: 15px 0;
      border: 1px solid var(--border);
      overflow-x: auto;
    }}

    .notification-subtitle {{
      font-size: 13px;
      color: var(--text-muted);
    }}
    
    @keyframes fadeInOut {{
        0% {{ opacity: 0; transform: translate(-50%, -50%) scale(0.9); }}
        10% {{ opacity: 1; transform: translate(-50%, -50%) scale(1); }}
        90% {{ opacity: 1; transform: translate(-50%, -50%) scale(1); }}
        100% {{ opacity: 0; transform: translate(-50%, -50%) scale(0.9); }}
    }}

    @media (max-width: 1024px) {{
      .sidebar {{
        width: 250px;
      }}
      
      #container {{
        max-width: calc(100vw - 270px);
      }}
    }}

    @media (max-width: 768px) {{
      .header-bar {{
        flex-direction: column;
        height: auto;
        padding: 12px 15px;
        gap: 10px;
        flex-shrink: 0;
      }}
      
      .file-info {{
        gap: 10px;
        font-size: 12px;
      }}
      
      .main-content {{
        flex-direction: column;
      }}
      
      .sidebar {{
        width: 100%;
        border-right: none;
        border-bottom: 1px solid var(--border);
        flex-direction: row;
        overflow-x: auto;
        padding: 0;
        flex-shrink: 0;
        scrollbar-width: thin;
        scrollbar-color: var(--primary) var(--bg-control);
      }}

      .sidebar::-webkit-scrollbar {{
        height: 6px;
      }}
      .sidebar::-webkit-scrollbar-track {{
        background: var(--bg-control);
      }}
      .sidebar::-webkit-scrollbar-thumb {{
        background-color: var(--primary);
        border-radius: 6px;
      }}
      
      .sidebar-section {{
        min-width: 220px;
        border-right: 1px solid var(--border);
        border-bottom: none;
        flex-shrink: 0;
      }}
      
      .sidebar-section:last-child {{
        border-right: none;
      }}

      .media-viewer {{
        flex: 1;
        min-height: 0;
      }}
      
      #container {{
        max-width: 100%;
        max-height: 100%;
      }}

      .resize-handle {{
        width: 22px;
        height: 22px;
      }}

      .video-controls {{
        padding: 10px 15px;
        gap: 5px;
      }}

      .control-btn {{
        width: 35px;
        height: 35px;
        font-size: 16px;
      }}

      .progress-container {{
        gap: 5px;
      }}

      #currentTime, #duration {{
        min-width: 35px;
        font-size: 11px;
      }}

      .volume-container {{
        min-width: 80px;
      }}

      .volume-bar {{
        width: 60px;
      }}
    }}

    .smooth-transition {{
      transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .visually-hidden {{
      position: absolute;
      width: 1px;
      height: 1px;
      margin: -1px;
      padding: 0;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }}
  </style>
</head>
<body class="dark-theme"> <div class="loading" id="loadingIndicator">
    <div class="spinner"></div>
    <div class="loading-text">Loading media...</div>
  </div>

  <div class="header-bar">
    <div class="app-title">MediaCrop - Visual FFmpeg Crop Tool</div>
    <div class="header-controls">
      <button id="themeToggle" title="Toggle Dark/Light Theme">☀️</button>
      <div class="file-info">
        <div class="file-detail">
          <span class="file-detail-label">Format:</span>
          <span class="file-detail-value">{ext.upper().replace('.', '')}</span>
        </div>
        <div class="file-detail">
          <span class="file-detail-label">Type:</span>
          <span class="file-detail-value">{media_type.title()}</span>
        </div>
        <div class="file-detail">
          <span class="file-detail-label">Size:</span>
          <span class="file-detail-value" id="fileSizeInfo">Loading...</span>
        </div>
      </div>
    </div>
  </div>

  <div class="main-content">
    <div class="sidebar">
      <div class="sidebar-section">
        <div class="section-title aspect">Aspect Ratio</div>
        
        <div class="form-group">
          <label class="form-label" for="aspect">Preset</label>
          <select id="aspect" class="form-select">
            <option value="free">Free Form</option>
            <option value="1:1">1:1 (Square)</option>
            <option value="4:3">4:3 (Standard)</option>
            <option value="16:9">16:9 (Widescreen)</option>
            <option value="9:16">9:16 (Portrait)</option>
            <option value="3:2">3:2 (Photo)</option>
            <option value="5:4">5:4 (Large Format)</option>
            <option value="21:9">21:9 (Ultrawide)</option>
            <option value="2.35:1">2.35:1 (Cinemascope)</option>
            <option value="2.39:1">2.39:1 (Anamorphic)</option>
            <option value="original">Original</option>
            <option value="custom">Custom Ratio</option>
          </select>
        </div>
        
        <div class="custom-ratio" id="customRatio">
          <input type="text" id="customW" class="form-input" value="16" placeholder="W" inputmode="numeric">
          <div class="ratio-separator">:</div>
          <input type="text" id="customH" class="form-input" value="9" placeholder="H" inputmode="numeric">
        </div>
      </div>

      <div class="sidebar-section">
        <div class="section-title tools">Quick Tools</div>
        
        <div class="form-group">
          <div class="button-grid">
            <button class="form-button" onclick="toggleGrid()" title="Toggle Rule-of-Thirds Grid (G)">📐 Grid</button>
            <button class="form-button" onclick="centerCrop()" title="Center the Crop Box (C)">🎯 Center</button>
            <button class="form-button" onclick="resetCropSize()" title="Reset Crop Box Size & Position">🔄 Reset</button>
            <button class="form-button" onclick="toggleHelp()" title="Show Keyboard Shortcuts (?)">❓ Help</button>
          </div>
        </div>
        
        <div class="form-group">
          <button id="saveButton" class="form-button" onclick="saveCrop()" style="background: linear-gradient(135deg, #4CAF50, #45a049); font-size: 14px; padding: 12px;">
            💾 Save Coordinates
          </button>
        </div>
      </div>

      <div class="sidebar-section">
        <div class="section-title info">Crop Info</div>
        
        <div class="info-stats">
          <div class="info-stat">
            <span class="info-stat-label">Natural Res:</span>
            <span class="info-stat-value" id="naturalResInfo">N/A</span>
          </div>
          <div class="info-stat">
            <span class="info-stat-label">Position:</span>
            <span class="info-stat-value" id="positionInfo">(0, 0)</span>
          </div>
          <div class="info-stat">
            <span class="info-stat-label">Size:</span>
            <span class="info-stat-value" id="sizeInfo">200×150</span>
          </div>
          <div class="info-stat">
            <span class="info-stat-label">Ratio:</span>
            <span class="info-stat-value" id="ratioInfo">4:3</span>
          </div>
          <div class="info-stat">
            <span class="info-stat-label">Zoom:</span>
            <span class="info-stat-value" id="zoomInfo">100%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="media-viewer">
      <div id="container">
        {media_section}
      </div>
    </div>
  </div>

  <div class="help-modal" id="helpModal">
    <div class="help-content">
      <div class="help-title">Keyboard Shortcuts</div>
      <div class="help-shortcuts">
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Move crop box</span>
          <span class="help-shortcut-key">Arrow Keys</span>
        </div>
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Fine adjustment</span>
          <span class="help-shortcut-key">Shift + Arrows</span>
        </div>
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Zoom In/Out Media</span>
          <span class="help-shortcut-key">Mouse Wheel</span>
        </div>
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Center crop box</span>
          <span class="help-shortcut-key">C</span>
        </div>
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Toggle grid</span>
          <span class="help-shortcut-key">G</span>
        </div>
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Save coordinates</span>
          <span class="help-shortcut-key">Enter</span>
        </div>
        <div class="help-shortcut">
          <span class="help-shortcut-desc">Close help</span>
          <span class="help-shortcut-key">Esc</span>
        </div>
      </div>
      <button class="help-close" onclick="toggleHelp()">Got it!</button>
    </div>
  </div>

  <div class="context-menu" id="contextMenu">
    <div class="context-item" onclick="centerCrop()">🎯 Center Crop Box</div>
    <div class="context-item" onclick="toggleGrid()">📐 Toggle Grid</div>
    <div class="context-item" onclick="resetCropSize()">🔄 Reset Size</div>
    <div class="context-item" onclick="saveCrop()">💾 Save Coordinates</div>
  </div>

  <div id="floatingPreview" class="floating-preview">
    <div class="preview-header">
      <span class="preview-title">Live Preview</span>
      <span class="preview-size" id="previewSizeInfo"></span>
    </div>
    <div class="preview-canvas-wrapper">
        <canvas id="previewCanvas"></canvas>
    </div>
    <div class="preview-resize-handle p-nw"></div><div class="preview-resize-handle p-ne"></div>
    <div class="preview-resize-handle p-sw"></div><div class="preview-resize-handle p-se"></div>
    <div class="preview-resize-handle p-n"></div><div class="preview-resize-handle p-s"></div>
    <div class="preview-resize-handle p-w"></div><div class="preview-resize-handle p-e"></div>
    <button class="preview-close-btn" id="previewCloseBtn" title="Close Fullscreen">&times;</button>
  </div>

  <script src="/main.js"></script>
</body>
</html>"""
            
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        elif path == "/main.js":
            js_content = get_javascript_code(media_type, ext)
            self.send_response(200)
            self.send_header("Content-type", "application/javascript; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(js_content.encode("utf-8"))

        elif path == "/file":
            try:
                if not os.path.exists(self.server.media_file) or not os.access(self.server.media_file, os.R_OK):
                    self.send_error(404, f"File not found or not readable: {self.server.media_file}")
                    return

                file_size = os.path.getsize(self.server.media_file)
                mime_type = mimetypes.guess_type(self.server.media_file)[0] or 'application/octet-stream'

                range_header = self.headers.get('Range')
                if range_header:
                    try:
                        range_header = range_header.strip().lower().replace('bytes=', '')
                        
                        if ',' in range_header:
                             self.send_error(416)
                             return
                             
                        start_str, end_str = range_header.split('-')
                        start = int(start_str) if start_str else 0
                        end = int(end_str) if end_str else file_size - 1
                        
                        if start < 0 or end < start or end >= file_size:
                            self.send_response(416)
                            self.send_header('Content-Range', f'bytes */{file_size}')
                            self.end_headers()
                            return
                        
                        length = end - start + 1
                        self.send_response(206)
                        self.send_header('Content-type', mime_type)
                        self.send_header('Accept-Ranges', 'bytes')
                        self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
                        self.send_header('Content-Length', str(length))
                        self.send_header("Last-Modified", self.date_time_string(os.path.getmtime(self.server.media_file)))
                        self.end_headers()

                        with open(self.server.media_file, 'rb') as f:
                            f.seek(start)
                            remaining = length
                            chunk_size = 65536
                            while remaining > 0:
                                chunk = f.read(min(remaining, chunk_size))
                                if not chunk: break
                                self.wfile.write(chunk)
                                remaining -= len(chunk)
                    except ValueError:
                        self.send_error(400, "Invalid Range header format")
                else:
                    self.send_response(200)
                    self.send_header("Content-type", mime_type)
                    self.send_header("Content-Length", str(file_size))
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Last-Modified", self.date_time_string(os.path.getmtime(self.server.media_file)))
                    self.end_headers()
                    
                    with open(self.server.media_file, 'rb') as f:
                        chunk_size = 1024 * 1024
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk: break
                            self.wfile.write(chunk)
                            
            except FileNotFoundError:
                self.send_error(404, f"File not found: {self.server.media_file}")
            except PermissionError:
                self.send_error(403, f"Permission denied: {self.server.media_file}")
            except BrokenPipeError:
                if self.server.verbose: self.log_message("Client disconnected (Broken Pipe).")
            except Exception as e:
                self.send_error(500, f"File error: {str(e)}")
                
        else:
            self.send_error(404, "Not Found")

    def do_HEAD(self):
        if urlparse(self.path).path == "/file":
            try:
                if not os.path.exists(self.server.media_file) or not os.access(self.server.media_file, os.R_OK):
                    self.send_error(404, "File not found or not readable")
                    return
                
                file_size = os.path.getsize(self.server.media_file)
                mime_type = mimetypes.guess_type(self.server.media_file)[0] or 'application/octet-stream'
                
                self.send_response(200)
                self.send_header("Content-Length", str(file_size))
                self.send_header("Content-Type", mime_type)
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Last-Modified", self.date_time_string(os.path.getmtime(self.server.media_file)))
                self.end_headers()
            except Exception as e:
                self.send_error(500, f"Error getting file info: {str(e)}")
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/save":
            try:
                length = int(self.headers.get("Content-Length", 0))
                if length > 10000:
                    self.send_error(413, "Payload too large")
                    return
                    
                body = self.rfile.read(length)
                data = json.loads(body.decode("utf-8"))
                
                required_fields = ['w', 'h', 'x', 'y']
                for field in required_fields:
                    if field not in data or not isinstance(data[field], (int, float)) or data[field] < 0:
                        self.send_error(400, f"Invalid or missing {field} parameter")
                        return
                
                w = int(data['w'])
                h = int(data['h'])
                x = int(data['x'])
                y = int(data['y'])

                input_file_path = self.server.media_file
                path_part, ext_part = os.path.splitext(input_file_path)
                
                i = 1
                while True:
                    output_file_name = f"{path_part}_crop_{w}x{h}_{i}{ext_part}"
                    if not os.path.exists(output_file_name):
                        break
                    i += 1
                
                if data.get('mediaType') == 'video':
                    ffmpeg_command = f'\nffmpeg -i "{input_file_path}" -vf "crop={w}:{h}:{x}:{y}" -c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 192k "{output_file_name}"\n'
                elif data.get('mediaType') == 'image':
                    ffmpeg_command = f'\nffmpeg -i "{input_file_path}" -vf "crop={w}:{h}:{x}:{y}" -q:v 1 "{output_file_name}"\n'
                else:
                    ffmpeg_command = f'\nffmpeg -i "{input_file_path}" -vf "crop={w}:{h}:{x}:{y}" -c:v libx264 -preset veryfast -crf 23 -c:a copy "{output_file_name}"\n'

                print(ffmpeg_command)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                
                self.wfile.write(json.dumps({
                    "success": True,
                    "message": "Crop parameters saved successfully",
                    "crop_filter": f"crop={w}:{h}:{x}:{y}",
                    "timestamp": self.date_time_string()
                }).encode("utf-8"))
                
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON data in request body")
            except KeyError as e:
                self.send_error(400, f"Missing required field: {e}")
            except Exception as e:
                print(f"Server POST Error: {e}")
                self.send_error(500, f"Server error: {str(e)}")
        else:
            self.send_error(404, "Not Found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Range")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()