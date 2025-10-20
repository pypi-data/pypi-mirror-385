# http_handler_js.py

def get_javascript_code(media_type, ext):
    """Returns the complete JavaScript code as a formatted string."""
    
    js_code = f"""
    const elements = {{
      media: document.getElementById("media"),
      container: document.getElementById("container"),
      crop: document.getElementById("crop"),
      aspectSelect: document.getElementById("aspect"),
      customRatio: document.getElementById("customRatio"),
      customW: document.getElementById("customW"),
      customH: document.getElementById("customH"),
      positionInfo: document.getElementById("positionInfo"),
      sizeInfo: document.getElementById("sizeInfo"),
      ratioInfo: document.getElementById("ratioInfo"),
      naturalResInfo: document.getElementById("naturalResInfo"),
      zoomInfo: document.getElementById("zoomInfo"),
      fileSizeInfo: document.getElementById("fileSizeInfo"),
      loadingIndicator: document.getElementById("loadingIndicator"),
      helpModal: document.getElementById("helpModal"),
      contextMenu: document.getElementById("contextMenu"),
      mediaWrapper: document.getElementById("media-wrapper"),
      mediaViewer: document.querySelector(".media-viewer"),
      themeToggle: document.getElementById("themeToggle"),
      body: document.body,
      floatingPreview: document.getElementById("floatingPreview"),
      previewCanvas: document.getElementById("previewCanvas"),
      previewCanvasWrapper: document.querySelector(".preview-canvas-wrapper"),
      previewHeader: document.querySelector(".preview-header"),
      previewSizeInfo: document.getElementById("previewSizeInfo"),
      previewCloseBtn: document.getElementById("previewCloseBtn"),
    }};

    const state = {{
      isDragging: false,
      isResizing: false,
      resizeDirection: '',
      startMouseX: 0,
      startMouseY: 0,
      startCropLeft: 0,
      startCropTop: 0,
      startCropWidth: 0,
      startCropHeight: 0,
      mediaWidth: 0,
      mediaHeight: 0,
      naturalWidth: 0,
      naturalHeight: 0,
      aspectMode: "free",
      aspectRatio: null,
      isInitialized: false,
      showGrid: false,
      isHelpVisible: false,
      currentTheme: 'dark',
      lastUpdate: 0,
      animationFrame: null,
      mediaType: "{media_type}",
      fileExtension: "{ext}",
      zoom: 1,
      isPinching: false,
      pinchType: '',
      pinchInitialDist: 0,
      pinchInitialZoom: 0,
      pinchInitialWidth: 0,
      pinchInitialHeight: 0,
      pinchInitialLeft: 0,
      pinchInitialTop: 0,
      pinchInitialMid: {{x: 0, y: 0}},
      pinchInitialRelX: 0,
      pinchInitialRelY: 0,
      pinchInitialScrollLeft: 0,
      pinchInitialScrollTop: 0,
      autoScrollActive: false,
      mouseX: 0,
      mouseY: 0,
      isPreviewPinching: false,
      previewPinchInitialDist: 0,
      previewPinchInitialWidth: 0,
      previewPinchInitialHeight: 0,
      holdTimer: null,
      isResizingPreview: false,
    }};
    
    function initializeTheme() {{
        const storedTheme = localStorage.getItem('theme') || 'dark'; 
        setTheme(storedTheme);
    }}
    
    function setTheme(theme) {{
        state.currentTheme = theme;
        elements.body.classList.remove('dark-theme', 'light-theme');
        elements.body.classList.add(theme + '-theme');
        localStorage.setItem('theme', theme);
        
        elements.themeToggle.innerHTML = theme === 'dark' ? '☀️' : '🌙'; 
        elements.themeToggle.title = theme === 'dark' ? 'Switch to Light Theme' : 'Switch to Dark Theme';
    }}

    function toggleTheme() {{
        const newTheme = state.currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    }}

    const utils = {{
      debounce(func, wait) {{
        let timeout;
        return function executedFunction(...args) {{
          const later = () => {{
            clearTimeout(timeout);
            func(...args);
          }};
          clearTimeout(timeout);
          timeout = setTimeout(later, wait);
        }};
      }},
      
      throttle(func, limit) {{
        let inThrottle;
        return function(...args) {{
          if (!inThrottle) {{
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
          }}
        }};
      }},
      
      getEventCoords(e) {{
        if (e.type.startsWith('touch')) {{
            if (e.touches && e.touches.length > 0) {{
                return {{
                    x: e.touches[0].clientX,
                    y: e.touches[0].clientY
                }};
            }}
            return {{x: e.clientX, y: e.clientY}};
        }}
        return {{
          x: e.clientX,
          y: e.clientY
        }};
      }},
      
      gcd(a, b) {{
        return b === 0 ? a : this.gcd(b, a % b);
      }},
      
      formatFileSize(bytes) {{
        const sizes = ['B', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
      }},
      
      lerp(start, end, factor) {{
        return start + (end - start) * factor;
      }},

      getDistance(t1, t2) {{
        return Math.sqrt(Math.pow(t2.clientX - t1.clientX, 2) + Math.pow(t2.clientY - t1.clientY, 2));
      }},

      getMidpoint(t1, t2) {{
        return {{
          x: (t1.clientX + t2.clientX) / 2,
          y: (t1.clientY + t1.clientY) / 2
        }};
      }},

      formatTime(seconds) {{
        if (isNaN(seconds) || seconds < 0) return '0:00';
        const totalSeconds = Math.floor(seconds);
        const hours = Math.floor(totalSeconds / 3600);
        const mins = Math.floor((totalSeconds % 3600) / 60);
        const secs = totalSeconds % 60;
        
        if (hours > 0) {{
          return `${{hours}}:${{mins.toString().padStart(2, '0')}}:${{secs.toString().padStart(2, '0')}}`;
        }}
        return `${{mins}}:${{secs.toString().padStart(2, '0')}}`;
      }}
    }};
    
    function updatePreview() {{
        if (!state.isInitialized || state.mediaType === 'unsupported' || !elements.floatingPreview) {{
            if (elements.floatingPreview) elements.floatingPreview.style.display = 'none';
            return;
        }}
        
        if (elements.floatingPreview.style.display === 'none') {{
            elements.floatingPreview.style.display = 'flex';
        }}
        
        const ctx = elements.previewCanvas.getContext('2d');

        if (state.mediaType === 'audio') {{
            const parentWrapper = elements.previewCanvas.parentElement;
            const width = parentWrapper.clientWidth;
            const height = parentWrapper.clientHeight;
            elements.previewCanvas.width = width;
            elements.previewCanvas.height = height;
            
            ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--bg-main').trim();
            ctx.fillRect(0, 0, width, height);
            
            ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-dim').trim();
            ctx.font = `${{Math.min(width, height) * 0.6}}px Arial`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('🎵', width / 2, height / 2);
            
            elements.previewSizeInfo.textContent = 'Audio';
            return;
        }}

        if (!elements.crop || !elements.media) return;

        const cropLeft = parseFloat(elements.crop.style.left) || 0;
        const cropTop = parseFloat(elements.crop.style.top) || 0;
        const cropWidth = parseFloat(elements.crop.style.width) || 0;
        const cropHeight = parseFloat(elements.crop.style.height) || 0;

        if (cropWidth < 1 || cropHeight < 1) return;

        const scaleX = state.naturalWidth / state.mediaWidth;
        const scaleY = state.naturalHeight / state.mediaHeight;
        const sourceX = cropLeft * scaleX;
        const sourceY = cropTop * scaleY;
        const sourceWidth = cropWidth * scaleX;
        const sourceHeight = cropHeight * scaleY;
        
        if (sourceWidth < 1 || sourceHeight < 1) return;

        elements.previewCanvas.width = Math.round(sourceWidth);
        elements.previewCanvas.height = Math.round(sourceHeight);

        ctx.clearRect(0, 0, elements.previewCanvas.width, elements.previewCanvas.height);
        try {{
            ctx.drawImage(elements.media, sourceX, sourceY, sourceWidth, sourceHeight, 0, 0, elements.previewCanvas.width, elements.previewCanvas.height);
        }} catch (e) {{
            console.error("Canvas drawImage error:", e);
        }}
        
        elements.previewSizeInfo.textContent = `${{Math.round(sourceWidth)}}x${{Math.round(sourceHeight)}}`;
    }}

    function startPreviewRenderLoop() {{
      if (state.animationFrame) cancelAnimationFrame(state.animationFrame);
      function renderLoop() {{
        updatePreview();
        state.animationFrame = requestAnimationFrame(renderLoop);
      }}
      renderLoop();
    }}

    function stopPreviewRenderLoop() {{
      if (state.animationFrame) {{
        cancelAnimationFrame(state.animationFrame);
        state.animationFrame = null;
      }}
    }}

    function initVideoControls() {{
      const video = elements.media;
      const controls = document.getElementById('videoControls');
      if (!video || !controls) return;

      const playPause = document.getElementById('playPause');
      const seekBar = document.getElementById('seekBar');
      const currentTimeEl = document.getElementById('currentTime');
      const durationEl = document.getElementById('duration');
      const playbackSpeed = document.getElementById('playbackSpeed');
      const muteBtn = document.getElementById('muteBtn');
      const volumeBar = document.getElementById('volumeBar');

      function togglePlayPause() {{
        if (video.paused) {{
          video.play().catch(e => console.log('Play error:', e));
        }} else {{
          video.pause();
        }}
      }}

      playPause.addEventListener('click', togglePlayPause);
      video.addEventListener('click', togglePlayPause);

      video.addEventListener('play', () => {{ playPause.textContent = '⏸️'; startPreviewRenderLoop(); }});
      video.addEventListener('pause', () => {{ playPause.textContent = '▶️'; stopPreviewRenderLoop(); }});
      video.addEventListener('ended', () => {{ playPause.textContent = '▶️'; stopPreviewRenderLoop(); video.currentTime = 0; }});

      let isSeeking = false;
      
      seekBar.addEventListener('mousedown', () => {{ isSeeking = true; if(!video.paused) stopPreviewRenderLoop(); }});
      seekBar.addEventListener('mouseup', () => {{ isSeeking = false; if (!video.paused) startPreviewRenderLoop(); }});
      
      seekBar.addEventListener('input', (e) => {{
        const time = (e.target.value / 100) * video.duration;
        if(isFinite(time)) video.currentTime = time;
        currentTimeEl.textContent = utils.formatTime(time);
        updatePreview();
      }});

      video.addEventListener('timeupdate', () => {{
        if (video.duration) {{
            if (!isSeeking) {{
                const value = (video.currentTime / video.duration) * 100;
                seekBar.value = value;
            }}
            currentTimeEl.textContent = utils.formatTime(video.currentTime);
        }}
      }});

      video.addEventListener('loadedmetadata', () => {{
        durationEl.textContent = utils.formatTime(video.duration);
        seekBar.max = 100;
        if (video.videoWidth && video.videoHeight) {{
            elements.naturalResInfo.textContent = `${{video.videoWidth}}×${{video.videoHeight}}`;
        }}
      }});

      playbackSpeed.addEventListener('change', (e) => {{
        video.playbackRate = parseFloat(e.target.value);
      }});

      volumeBar.addEventListener('input', (e) => {{
        video.volume = e.target.value / 100;
        video.muted = video.volume === 0;
        muteBtn.textContent = video.muted ? '🔇' : '🔊';
      }});

      muteBtn.addEventListener('click', () => {{
        video.muted = !video.muted;
        if (!video.muted && video.volume === 0) video.volume = 1;
        if(video.muted) {{ volumeBar.value = 0; }} else {{ volumeBar.value = video.volume * 100; }}
        muteBtn.textContent = video.muted ? '🔇' : '🔊';
      }});

      video.volume = 1;
      muteBtn.textContent = '🔊';
      playPause.textContent = '▶️';
    }}

    function initializeCrop() {{
      requestAnimationFrame(() => {{ 
        if (state.isInitialized) return;

        updateMediaDimensions();
        updateFileInfo();
        
        if (state.mediaType === 'image' || state.mediaType === 'video' || state.mediaType === 'unsupported') {{
            positionCropBox();
            updateCropInfo();
            setMediaZoom(1);
        }}
        
        if (state.mediaType === 'video') {{
          initVideoControls();
          elements.container.style.display = 'flex';
          elements.container.style.flexDirection = 'column';
          elements.mediaWrapper.style.flex = '1';
          elements.mediaWrapper.style.minHeight = '200px';
        }} else if (state.mediaType === 'audio') {{
            updatePreview();
        }}
        
        if (state.mediaType === 'image' && elements.media) {{
            elements.naturalResInfo.textContent = `${{elements.media.naturalWidth}}×${{elements.media.naturalHeight}}`;
        }}

        state.isInitialized = true;
        hideLoading();
        
        if (elements.crop) {{
            elements.crop.focus();
        }}
      }});
    }}

    function hideLoading() {{
      elements.loadingIndicator.style.display = 'none';
    }}

    function updateMediaDimensions() {{
        if (elements.media) {{
            state.mediaWidth = elements.media.offsetWidth;
            state.mediaHeight = elements.media.offsetHeight;
        }}
      
        if (state.mediaType === 'unsupported') {{
          state.mediaWidth = 500;
          state.mediaHeight = 300;
          state.naturalWidth = 500;
          state.naturalHeight = 300;
          elements.container.style.width = state.mediaWidth + 'px';
          elements.container.style.height = state.mediaHeight + 'px';
          elements.mediaWrapper.style.width = state.mediaWidth + 'px';
          elements.mediaWrapper.style.height = state.mediaHeight + 'px';
          return;
        }}
        
        if (!elements.media) return;
      
        if (elements.media.tagName === 'IMG') {{
          state.naturalWidth = elements.media.naturalWidth || state.mediaWidth;
          state.naturalHeight = elements.media.naturalHeight || state.mediaHeight;
        }} else if (elements.media.tagName === 'VIDEO') {{
          state.naturalWidth = elements.media.videoWidth || state.mediaWidth;
          state.naturalHeight = elements.media.videoHeight || state.mediaHeight;
        }} else if (elements.media.tagName === 'AUDIO') {{
            state.naturalWidth = 500; 
            state.naturalHeight = 50; 
            elements.container.style.width = 'fit-content';
            elements.container.style.height = 'auto';
            return;
        }} else {{
          state.naturalWidth = state.mediaWidth;
          state.naturalHeight = state.mediaHeight;
        }}
        
        if (elements.media) {{
            state.mediaWidth = elements.media.offsetWidth;
            state.mediaHeight = elements.media.offsetHeight;
        }}

        elements.naturalResInfo.textContent = `${{state.naturalWidth}}×${{state.naturalHeight}}`;
    }}

    function updateFileInfo() {{
      fetch('/file', {{ method: 'HEAD' }})
        .then(response => {{
          const contentLength = response.headers.get('content-length');
          if (contentLength) {{
            elements.fileSizeInfo.textContent = utils.formatFileSize(parseInt(contentLength));
          }} else {{
             elements.fileSizeInfo.textContent = 'N/A';
          }}
        }})
        .catch(() => {{
          elements.fileSizeInfo.textContent = 'Error';
        }});
    }}

    function positionCropBox() {{
      if (state.mediaWidth === 0 || state.mediaHeight === 0 || !elements.crop) return;
      
      const cropWidth = Math.min(200, state.mediaWidth * 0.4);
      const cropHeight = Math.min(150, state.mediaHeight * 0.3);
      
      const centerX = (state.mediaWidth - cropWidth) / 2;
      const centerY = (state.mediaHeight - cropHeight) / 2;
      
      setCropDimensions(centerX, centerY, cropWidth, cropHeight);
    }}

    function setCropDimensions(left, top, width, height, smooth = false) {{
      if (!elements.crop) return;
      
      width = Math.max(30, width);
      height = Math.max(30, height);
      
      left = Math.max(0, Math.min(left, state.mediaWidth - width));
      top = Math.max(0, Math.min(top, state.mediaHeight - height));
      
      width = Math.min(width, state.mediaWidth - left);
      height = Math.min(height, state.mediaHeight - top);
      
      const cropStyle = elements.crop.style;
      
      if (smooth) {{
        elements.crop.classList.add('smooth-transition');
        setTimeout(() => elements.crop.classList.remove('smooth-transition'), 150);
      }}
      
      cropStyle.left = Math.round(left) + 'px';
      cropStyle.top = Math.round(top) + 'px';
      cropStyle.width = Math.round(width) + 'px';
      cropStyle.height = Math.round(height) + 'px';
      
      updateCropInfo();
    }}

    function applyAspectRatio(width, height, maintainWidth = true) {{
      if (state.aspectMode === "free" || !state.aspectRatio || isNaN(state.aspectRatio)) {{
        return {{ width, height }};
      }}
      
      if (maintainWidth) {{
        height = Math.round(width / state.aspectRatio);
      }} else {{
        width = Math.round(height * state.aspectRatio);
      }}
      
      return {{ width, height }};
    }}

    function updateCropInfo() {{
      if (!elements.crop) return;
      const left = parseInt(elements.crop.style.left) || 0;
      const top = parseInt(elements.crop.style.top) || 0;
      const width = parseInt(elements.crop.style.width) || 0;
      const height = parseInt(elements.crop.style.height) || 0;
      
      elements.positionInfo.textContent = `(${{left}}, ${{top}})`;
      elements.sizeInfo.textContent = `${{width}}×${{height}}`;
      elements.zoomInfo.textContent = `${{Math.round(state.zoom * 100)}}%`;
      
      if (width && height) {{
        const gcd = utils.gcd(width, height);
        const ratioW = width / gcd;
        const ratioH = height / gcd;
        
        let ratioText = `${{ratioW}}:${{ratioH}}`;
        if (ratioW === ratioH) ratioText = "1:1";
        else if (Math.abs(ratioW/ratioH - 16/9) < 0.05) ratioText = "≈ 16:9";
        else if (Math.abs(ratioW/ratioH - 4/3) < 0.05) ratioText = "≈ 4:3";
        else if (Math.abs(ratioW/ratioH - 3/2) < 0.05) ratioText = "≈ 3:2";
        else {{
            const floatRatio = (width / height).toFixed(2);
            ratioText = `${{floatRatio}}:1`;
        }}
        
        elements.ratioInfo.textContent = ratioText;
      }}
      
      if (state.mediaType === 'image' || (state.mediaType === 'video' && elements.media.paused)) {{
        updatePreview();
      }}
    }}

    function setMediaZoom(newZoom) {{
      if (state.mediaType !== 'image' && state.mediaType !== 'video') return;
      newZoom = Math.max(0.1, Math.min(10, newZoom));
      
      const oldZoom = state.zoom;
      if (newZoom === oldZoom) return;

      const factor = newZoom / oldZoom;
      state.zoom = newZoom;
      
      if (elements.media && state.naturalWidth && state.naturalHeight) {{
        elements.media.style.width = (state.naturalWidth * newZoom) + 'px';
        elements.media.style.height = (state.naturalHeight * newZoom) + 'px';
      }}
      
      if (elements.crop) {{
        elements.crop.style.left = (parseFloat(elements.crop.style.left) * factor) + 'px';
        elements.crop.style.top = (parseFloat(elements.crop.style.top) * factor) + 'px';
        elements.crop.style.width = (parseFloat(elements.crop.style.width) * factor) + 'px';
        elements.crop.style.height = (parseFloat(elements.crop.style.height) * factor) + 'px';
      }}
      
      updateMediaDimensions();
      updateCropInfo();
    }}

    const dragHandlers = {{
      start(e) {{
        if (!elements.crop || e.target.classList.contains('resize-handle')) return;
        e.preventDefault();
        e.stopPropagation();
        
        if (e.type.startsWith('touch') && e.touches.length === 2) {{
          startPinch('crop', e);
          return;
        }} else if (e.type.startsWith('touch') && e.touches.length > 1) {{
          return;
        }}
        
        const coords = utils.getEventCoords(e);
        state.isDragging = true;
        state.startMouseX = coords.x;
        state.startMouseY = coords.y;
        state.startCropLeft = parseFloat(elements.crop.style.left) || 0;
        state.startCropTop = parseFloat(elements.crop.style.top) || 0;
        
        elements.crop.classList.add('dragging');
        
        document.addEventListener('mousemove', dragHandlers.move, {{ passive: false }});
        document.addEventListener('mouseup', dragHandlers.stop);
        document.addEventListener('touchmove', dragHandlers.move, {{ passive: false }});
        document.addEventListener('touchend', dragHandlers.stop);
        
        document.addEventListener('mousemove', updateMousePos);
        document.addEventListener('touchmove', updateMousePosTouch, {{ passive: false }});
        startAutoScroll();
      }},
      
      move: utils.throttle((e) => {{
        if (!state.isDragging) return;
        
        e.preventDefault();
        const coords = utils.getEventCoords(e);
        
        const deltaX = coords.x - state.startMouseX;
        const deltaY = coords.y - state.startMouseY;
        
        let newLeft = state.startCropLeft + deltaX;
        let newTop = state.startCropTop + deltaY;
        
        const currentWidth = parseFloat(elements.crop.style.width) || 0;
        const currentHeight = parseFloat(elements.crop.style.height) || 0;
        
        setCropDimensions(newLeft, newTop, currentWidth, currentHeight);
      }}, 16),
      
      stop() {{
        state.isDragging = false;
        if (elements.crop) elements.crop.classList.remove('dragging');
        
        document.removeEventListener('mousemove', dragHandlers.move);
        document.removeEventListener('mouseup', dragHandlers.stop);
        document.removeEventListener('touchmove', dragHandlers.move);
        document.removeEventListener('touchend', dragHandlers.stop);
        
        document.removeEventListener('mousemove', updateMousePos);
        document.removeEventListener('touchmove', updateMousePosTouch);
        stopAutoScroll();
      }}
    }};

    const resizeHandlers = {{
      start(e) {{
        e.preventDefault();
        e.stopPropagation();
        
        if (state.mediaType === 'audio' || !elements.crop) return;
        
        const coords = utils.getEventCoords(e);
        state.isResizing = true;
        state.resizeDirection = Array.from(e.target.classList).find(cls => cls !== 'resize-handle');
        state.startMouseX = coords.x;
        state.startMouseY = coords.y;
        
        state.startCropLeft = parseFloat(elements.crop.style.left) || 0;
        state.startCropTop = parseFloat(elements.crop.style.top) || 0;
        state.startCropWidth = parseFloat(elements.crop.style.width) || 0;
        state.startCropHeight = parseFloat(elements.crop.style.height) || 0;
        
        document.addEventListener('mousemove', resizeHandlers.move, {{ passive: false }});
        document.addEventListener('mouseup', resizeHandlers.stop);
        document.addEventListener('touchmove', resizeHandlers.move, {{ passive: false }});
        document.addEventListener('touchend', resizeHandlers.stop);
        
        document.addEventListener('mousemove', updateMousePos);
        document.addEventListener('touchmove', updateMousePosTouch, {{ passive: false }});
        startAutoScroll();
      }},
      
      move: utils.throttle((e) => {{
        if (!state.isResizing || !elements.crop) return;
        
        e.preventDefault();
        const coords = utils.getEventCoords(e);
        
        const deltaX = coords.x - state.startMouseX;
        const deltaY = coords.y - state.startMouseY;
        
        const {{ startCropLeft, startCropTop, startCropWidth, startCropHeight, resizeDirection, aspectRatio, aspectMode }} = state;

        let newLeft = startCropLeft;
        let newTop = startCropTop;
        let newWidth = startCropWidth;
        let newHeight = startCropHeight;

        if (resizeDirection.includes('e')) {{
            newWidth = startCropWidth + deltaX;
        }}
        if (resizeDirection.includes('w')) {{
            newWidth = startCropWidth - deltaX;
        }}
        if (resizeDirection.includes('s')) {{
            newHeight = startCropHeight + deltaY;
        }}
        if (resizeDirection.includes('n')) {{
            newHeight = startCropHeight - deltaY;
        }}

        if (aspectRatio && aspectMode !== "free") {{
            const isHorizontalHandle = resizeDirection.includes('e') || resizeDirection.includes('w');
            const isVerticalHandle = resizeDirection.includes('n') || resizeDirection.includes('s');

            if (isHorizontalHandle && !isVerticalHandle) {{
                newHeight = newWidth / aspectRatio;
            }} else if (isVerticalHandle && !isHorizontalHandle) {{
                newWidth = newHeight * aspectRatio;
            }} else {{ 
                const horizontalMovement = Math.abs(newWidth - startCropWidth);
                const verticalMovement = Math.abs(newHeight - startCropHeight);
                
                if (horizontalMovement > verticalMovement) {{
                    newHeight = newWidth / aspectRatio;
                }} else {{
                    newWidth = newHeight * aspectRatio;
                }}
            }}
        }}
        
        if (resizeDirection.includes('n')) {{
            newTop = startCropTop + (startCropHeight - newHeight);
        }}
        if (resizeDirection.includes('w')) {{
            newLeft = startCropLeft + (startCropWidth - newWidth);
        }}
        
        setCropDimensions(newLeft, newTop, newWidth, newHeight);
      }}, 16),
      
      stop() {{
        state.isResizing = false;
        
        document.removeEventListener('mousemove', resizeHandlers.move);
        document.removeEventListener('mouseup', resizeHandlers.stop);
        document.removeEventListener('touchmove', resizeHandlers.move);
        document.removeEventListener('touchend', resizeHandlers.stop);
        
        document.removeEventListener('mousemove', updateMousePos);
        document.removeEventListener('touchmove', updateMousePosTouch);
        stopAutoScroll();
      }}
    }};
    
    function handleMouseWheelZoom(e) {{
      if (state.mediaType === 'audio') return;
      e.preventDefault();

      const zoomFactor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
      const newZoom = state.zoom * zoomFactor;
      
      const viewer = elements.mediaViewer;
      const rect = viewer.getBoundingClientRect();
      
      const relativeX = e.clientX - rect.left;
      const relativeY = e.clientY - rect.top;

      const contentX = viewer.scrollLeft + relativeX;
      const contentY = viewer.scrollTop + relativeY;

      setMediaZoom(newZoom);

      const newContentX = contentX * (newZoom / state.zoom);
      const newContentY = contentY * (newZoom / state.zoom);

      viewer.scrollLeft = newContentX - relativeX;
      viewer.scrollTop = newContentY - relativeY;
    }}

    function startPinch(type, e) {{
      if (e.touches.length !== 2) return;
      if (type === 'media' && state.mediaType !== 'image' && state.mediaType !== 'video') return;
      
      state.isPinching = true;
      state.pinchType = type;
      state.pinchInitialDist = utils.getDistance(e.touches[0], e.touches[1]);
      
      if (type === 'crop') {{
        state.pinchInitialWidth = parseFloat(elements.crop.style.width);
        state.pinchInitialHeight = parseFloat(elements.crop.style.height);
        state.pinchInitialLeft = parseFloat(elements.crop.style.left);
        state.pinchInitialTop = parseFloat(elements.crop.style.top);
      }} else {{
        state.pinchInitialZoom = state.zoom;
        state.pinchInitialMid = utils.getMidpoint(e.touches[0], e.touches[1]);
        const viewerRect = elements.mediaViewer.getBoundingClientRect();
        state.pinchInitialRelX = state.pinchInitialMid.x - viewerRect.left;
        state.pinchInitialRelY = state.pinchInitialMid.y - viewerRect.top;
        state.pinchInitialScrollLeft = elements.mediaViewer.scrollLeft;
        state.pinchInitialScrollTop = elements.mediaViewer.scrollTop;
      }}
      document.addEventListener('touchmove', handlePinchMove, {{ passive: false }});
      document.addEventListener('touchend', handlePinchEnd);
    }}

    function handlePinchMove(e) {{
      if (!state.isPinching || e.touches.length !== 2) return;
      e.preventDefault();
      
      const newDist = utils.getDistance(e.touches[0], e.touches[1]);
      const factor = newDist / state.pinchInitialDist;
      
      if (state.pinchType === 'crop') {{
        let newWidth = state.pinchInitialWidth * factor;
        let newHeight = state.pinchInitialHeight * factor;
        
        const dims = applyAspectRatio(newWidth, newHeight);
        newWidth = dims.width;
        newHeight = dims.height;
        
        const deltaW = newWidth - state.pinchInitialWidth;
        const deltaH = newHeight - state.pinchInitialHeight;
        const newLeft = state.pinchInitialLeft - deltaW / 2;
        const newTop = state.pinchInitialTop - deltaH / 2;
        
        setCropDimensions(newLeft, newTop, newWidth, newHeight);
      }} else {{
        const newZoom = state.pinchInitialZoom * factor;
        const oldZoom = state.zoom;
        setMediaZoom(newZoom);
        
        const newFactor = newZoom / oldZoom;
        const viewer = elements.mediaViewer;
        
        viewer.scrollLeft = state.pinchInitialScrollLeft * newFactor + state.pinchInitialRelX * (newFactor - 1);
        viewer.scrollTop = state.pinchInitialScrollTop * newFactor + state.pinchInitialRelY * (newFactor - 1);
      }}
    }}

    function handlePinchEnd() {{
      state.isPinching = false;
      state.pinchType = '';
      document.removeEventListener('touchmove', handlePinchMove);
      document.removeEventListener('touchend', handlePinchEnd);
    }}
    
    function handleMediaTouchStart(e) {{
      if (e.touches.length === 2 && state.mediaType !== 'audio') {{
        e.preventDefault();
        startPinch('media', e);
      }}
    }}

    function updateMousePos(e) {{
      state.mouseX = e.clientX;
      state.mouseY = e.clientY;
    }}

    function updateMousePosTouch(e) {{
      if (e.touches.length > 0) {{
        state.mouseX = e.touches[0].clientX;
        state.mouseY = e.touches[0].clientY;
      }}
    }}

    function startAutoScroll() {{
      if (state.autoScrollActive) return;
      state.autoScrollActive = true;
      autoScrollLoop();
    }}

    function stopAutoScroll() {{
      state.autoScrollActive = false;
    }}

    function autoScrollLoop() {{
      if (!state.autoScrollActive) return;
      
      const viewer = elements.mediaViewer;
      const rect = viewer.getBoundingClientRect();
      const edgeSize = 50;
      const scrollSpeed = 10;
      
      let dx = 0, dy = 0;
      
      if (state.mouseX < rect.left + edgeSize) {{
        dx = -scrollSpeed * ((rect.left + edgeSize - state.mouseX) / edgeSize);
      }} else if (state.mouseX > rect.right - edgeSize) {{
        dx = scrollSpeed * ((state.mouseX - (rect.right - edgeSize)) / edgeSize);
      }}
      
      if (state.mouseY < rect.top + edgeSize) {{
        dy = -scrollSpeed * ((rect.top + edgeSize - state.mouseY) / edgeSize);
      }} else if (state.mouseY > rect.bottom - edgeSize) {{
        dy = scrollSpeed * ((state.mouseY - (rect.bottom - edgeSize)) / edgeSize);
      }}
      
      if (dx !== 0 || dy !== 0) {{
        viewer.scrollLeft += dx;
        viewer.scrollTop += dy;
        
        state.startMouseX -= dx;
        state.startMouseY -= dy;
        
        if (state.isDragging || state.isResizing) {{
            const fakeEvent = {{ clientX: state.mouseX, clientY: state.mouseY }};
            if (state.isDragging) {{
                dragHandlers.move(fakeEvent);
            }} else if (state.isResizing) {{
                resizeHandlers.move(fakeEvent);
            }}
        }}
      }}
      
      requestAnimationFrame(autoScrollLoop);
    }}

    function handleKeyboard(e) {{
      if (state.isHelpVisible && e.key === 'Escape') {{
        toggleHelp();
        return;
      }}
      
      if(elements.floatingPreview.classList.contains('fullscreen') && e.key === 'Escape') {{
          closePreviewFullscreen();
          return;
      }}
      
      if (state.isHelpVisible || state.mediaType === 'audio' || !elements.crop) return;
      
      const step = e.shiftKey ? 1 : 10;
      const currentLeft = parseFloat(elements.crop.style.left) || 0;
      const currentTop = parseFloat(elements.crop.style.top) || 0;
      const currentWidth = parseFloat(elements.crop.style.width) || 0;
      const currentHeight = parseFloat(elements.crop.style.height) || 0;
      
      let newLeft = currentLeft;
      let newTop = currentTop;
      
      switch (e.key) {{
        case 'ArrowLeft':
          e.preventDefault();
          newLeft = Math.max(0, currentLeft - step);
          break;
        case 'ArrowRight':
          e.preventDefault();
          newLeft = Math.min(state.mediaWidth - currentWidth, currentLeft + step);
          break;
        case 'ArrowUp':
          e.preventDefault();
          newTop = Math.max(0, currentTop - step);
          break;
        case 'ArrowDown':
          e.preventDefault();
          newTop = Math.min(state.mediaHeight - currentHeight, currentTop + step);
          break;
        case 'c': case 'C':
          e.preventDefault(); centerCrop(); break;
        case 'g': case 'G':
          e.preventDefault(); toggleGrid(); break;
        case 'Enter':
          if (document.activeElement === elements.crop) {{
            e.preventDefault(); saveCrop();
          }}
          break;
        default: return;
      }}
      
      if (newLeft !== currentLeft || newTop !== currentTop) {{
        setCropDimensions(newLeft, newTop, currentWidth, currentHeight, true);
        
        const viewer = elements.mediaViewer;
        const cropRect = elements.crop.getBoundingClientRect();
        const viewerRect = viewer.getBoundingClientRect();
        
        const scrollMargin = 50;
        
        if (cropRect.left < viewerRect.left + scrollMargin) {{
            viewer.scrollLeft -= step;
        }} else if (cropRect.right > viewerRect.right - scrollMargin) {{
            viewer.scrollLeft += step;
        }}
        
        if (cropRect.top < viewerRect.top + scrollMargin) {{
            viewer.scrollTop -= step;
        }} else if (cropRect.bottom > viewerRect.bottom - scrollMargin) {{
            viewer.scrollTop += step;
        }}
      }}
    }}

    function toggleGrid() {{
      state.showGrid = !state.showGrid;
      if(elements.crop) elements.crop.classList.toggle('show-grid', state.showGrid);
    }}

    function centerCrop() {{
      if (state.mediaType === 'audio' || !elements.crop) return;
      
      const currentWidth = parseFloat(elements.crop.style.width) || 0;
      const currentHeight = parseFloat(elements.crop.style.height) || 0;
      
      const centerX = (state.mediaWidth - currentWidth) / 2;
      const centerY = (state.mediaHeight - currentHeight) / 2;
      
      setCropDimensions(centerX, centerY, currentWidth, currentHeight, true);

      const viewer = document.querySelector('.media-viewer'); 
      viewer.scrollLeft = centerX + (currentWidth / 2) - (viewer.clientWidth / 2);
      viewer.scrollTop = centerY + (currentHeight / 2) - (viewer.clientHeight / 2);
    }}

    function resetCropSize() {{
      if (state.mediaType === 'audio' || !elements.crop) return;
      setMediaZoom(1);
      positionCropBox();
      elements.aspectSelect.value = "free";
      state.aspectMode = "free";
      state.aspectRatio = null;
      elements.customRatio.classList.remove('visible');
    }}

    function toggleHelp() {{
      state.isHelpVisible = !state.isHelpVisible;
      elements.helpModal.style.display = state.isHelpVisible ? 'flex' : 'none';
      if (!state.isHelpVisible && elements.crop) {{
        elements.crop.focus();
      }}
    }}

    function showContextMenu(e) {{
      if (state.mediaType === 'audio' || !elements.crop) return;
      e.preventDefault();
      const menu = elements.contextMenu;
      menu.style.display = 'block';
      let left = e.clientX;
      let top = e.clientY;
      if (left + menu.offsetWidth > window.innerWidth) left = window.innerWidth - menu.offsetWidth - 10;
      if (top + menu.offsetHeight > window.innerHeight) top = window.innerHeight - menu.offsetHeight - 10;
      
      menu.style.left = left + 'px';
      menu.style.top = top + 'px';
      
      document.addEventListener('click', hideContextMenu, {{ once: true }});
    }}

    function hideContextMenu() {{
      if (elements.contextMenu) {{
        elements.contextMenu.style.display = 'none';
      }}
    }}

    function handleAspectRatioChange(e) {{
      state.aspectMode = e.target.value;
      
      if (state.aspectMode === "custom") {{
        elements.customRatio.classList.add('visible');
        updateCustomAspectRatio();
      }} else {{
        elements.customRatio.classList.remove('visible');
        
        if (state.aspectMode === "free") {{
          state.aspectRatio = null;
        }} else if (state.aspectMode === "original") {{
          if (state.naturalWidth && state.naturalHeight) {{
            state.aspectRatio = state.naturalWidth / state.naturalHeight;
          }} else {{
            state.aspectRatio = null;
          }}
        }} else {{
          const parts = state.aspectMode.split(":");
          state.aspectRatio = parseFloat(parts[0]) / parseFloat(parts[1]);
        }}
        applyCurrentAspectRatio();
      }}
    }}

    function updateCustomAspectRatio() {{
      const w = parseFloat(elements.customW.value);
      const h = parseFloat(elements.customH.value);
      
      if (isNaN(w) || isNaN(h) || h === 0) {{
          state.aspectRatio = null;
          return;
      }}
      
      state.aspectRatio = w / h;
      if (state.aspectMode === "custom") {{
        applyCurrentAspectRatio();
      }}
    }}

    function applyCurrentAspectRatio() {{
      if (!state.aspectRatio || !state.isInitialized || state.mediaType === 'audio' || !elements.crop) return;
      
      const currentLeft = parseFloat(elements.crop.style.left) || 0;
      const currentTop = parseFloat(elements.crop.style.top) || 0;
      const currentWidth = parseFloat(elements.crop.style.width) || 0;
      
      const newHeight = Math.round(currentWidth / state.aspectRatio);
      
      if (newHeight > 30 && newHeight <= state.mediaHeight) {{
        setCropDimensions(currentLeft, currentTop, currentWidth, newHeight, true);
      }} else {{
        const currentHeight = parseFloat(elements.crop.style.height) || 0;
        const newWidth = Math.round(currentHeight * state.aspectRatio);
        setCropDimensions(currentLeft, currentTop, newWidth, currentHeight, true);
      }}
    }}

    function saveCrop() {{
      if (state.mediaType === 'audio' || !elements.crop) {{
        alert("Crop function is not applicable for this media type.");
        return;
      }}
      
      updateMediaDimensions();
      
      const left = parseFloat(elements.crop.style.left) || 0;
      const top = parseFloat(elements.crop.style.top) || 0;
      const width = parseFloat(elements.crop.style.width) || 0;
      const height = parseFloat(elements.crop.style.height) || 0;
      
      let scaleX = 1, scaleY = 1;
      
      if (state.naturalWidth && state.naturalHeight && state.mediaWidth && state.mediaHeight) {{
        scaleX = state.naturalWidth / state.mediaWidth;
        scaleY = state.naturalHeight / state.mediaHeight;
      }}
      
      const finalX = Math.round(left * scaleX);
      const finalY = Math.round(top * scaleY);
      const finalW = Math.round(width * scaleX);
      const finalH = Math.round(height * scaleY);
      
      fetch("/save", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ 
          x: finalX, y: finalY, w: finalW, h: finalH,
          scaleX: scaleX, scaleY: scaleY, mediaType: state.mediaType
        }})
      }})
      .then(response => {{
        if (response.ok) {{
          const notification = document.createElement('div');
          notification.className = 'notification';
          notification.innerHTML = `
            <div class="notification-title">Crop Saved Successfully!</div>
            <div class="notification-code">crop=${{finalW}}:${{finalH}}:${{finalX}}:${{finalY}}</div>
            <div class="notification-subtitle">FFmpeg command printed to terminal.</div>
          `;
          document.body.appendChild(notification);
          setTimeout(() => document.body.removeChild(notification), 3000);
        }} else {{
          response.json().then(data => alert("Error: " + (data.message || "Could not save crop parameters"))).catch(() => alert("Error: Could not save crop parameters"));
        }}
      }})
      .catch(error => {{
        alert("Network Error: " + error.message);
      }});
    }}

    const handleWindowResize = utils.debounce(() => {{
      if (!state.isInitialized) return;
      
      updateMediaDimensions();
      updateCropInfo();
      
      if (elements.crop) {{
        const left = parseFloat(elements.crop.style.left) || 0;
        const top = parseFloat(elements.crop.style.top) || 0;
        const width = parseFloat(elements.crop.style.width) || 0;
        const height = parseFloat(elements.crop.style.height) || 0;
        
        setCropDimensions(left, top, width, height, true);
      }}
    }}, 200);

    function openPreviewFullscreen() {{
        if (!elements.floatingPreview.classList.contains('fullscreen')) {{
            elements.floatingPreview.classList.add('fullscreen');
        }}
    }}
    
    function closePreviewFullscreen() {{
        if (elements.floatingPreview.classList.contains('fullscreen')) {{
            elements.floatingPreview.classList.remove('fullscreen');
        }}
    }}
    
    // --- Floating Preview Handlers ---
    const previewInteraction = {{
        isDragging: false,
        hasDragged: false,
        dragStartX: 0, dragStartY: 0,
        previewStartX: 0, previewStartY: 0,
        
        onMouseDown(e) {{
            e.preventDefault();
            this.isDragging = true;
            this.hasDragged = false;
            const coords = utils.getEventCoords(e);
            this.dragStartX = coords.x;
            this.dragStartY = coords.y;
            const rect = elements.floatingPreview.getBoundingClientRect();
            this.previewStartX = rect.left;
            this.previewStartY = rect.top;

            elements.floatingPreview.style.left = this.previewStartX + 'px';
            elements.floatingPreview.style.top = this.previewStartY + 'px';
            elements.floatingPreview.style.right = 'auto';
            elements.floatingPreview.style.bottom = 'auto';
            elements.floatingPreview.style.transition = 'none';

            document.addEventListener('mousemove', this.onMouseMove);
            document.addEventListener('mouseup', this.onMouseUp);
            document.addEventListener('touchmove', this.onMouseMove, {{ passive: false }});
            document.addEventListener('touchend', this.onMouseUp);
        }},

        onMouseMove(e) {{
            if (!previewInteraction.isDragging) return;
            const coords = utils.getEventCoords(e);
            const dx = coords.x - previewInteraction.dragStartX;
            const dy = coords.y - previewInteraction.dragStartY;
            
            if (!previewInteraction.hasDragged && Math.hypot(dx, dy) > 5) {{
                previewInteraction.hasDragged = true;
                if(state.holdTimer) clearTimeout(state.holdTimer);
            }}

            let newLeft = previewInteraction.previewStartX + dx;
            let newTop = previewInteraction.previewStartY + dy;
            const previewWidth = elements.floatingPreview.offsetWidth;
            const previewHeight = elements.floatingPreview.offsetHeight;
            newLeft = Math.max(0, Math.min(newLeft, window.innerWidth - previewWidth));
            newTop = Math.max(0, Math.min(newTop, window.innerHeight - previewHeight));
            elements.floatingPreview.style.left = newLeft + 'px';
            elements.floatingPreview.style.top = newTop + 'px';
        }},

        onMouseUp() {{
            this.isDragging = false;
            elements.floatingPreview.style.transition = '';
            document.removeEventListener('mousemove', this.onMouseMove);
            document.removeEventListener('mouseup', this.onMouseUp);
            document.removeEventListener('touchmove', this.onMouseMove);
            document.removeEventListener('touchend', this.onMouseUp);
        }},

        onContentMouseDown(e) {{
            if (e.target.classList.contains('preview-resize-handle')) return;
            state.holdTimer = setTimeout(() => {{
                if (!this.hasDragged) openPreviewFullscreen();
            }}, 700);
        }},
        
        onContentMouseUp(e) {{
            if(state.holdTimer) clearTimeout(state.holdTimer);
            if (!this.hasDragged && e.type !== 'touchend') {{ // Avoid double toggle on touch
                // elements.floatingPreview.classList.toggle('enlarged');
            }}
            this.hasDragged = false;
        }},
        
        bind(element, handler) {{
            return handler.bind(element);
        }}
    }};
    previewInteraction.onMouseDown = previewInteraction.bind(previewInteraction, previewInteraction.onMouseDown);
    previewInteraction.onMouseMove = previewInteraction.bind(previewInteraction, previewInteraction.onMouseMove);
    previewInteraction.onMouseUp = previewInteraction.bind(previewInteraction, previewInteraction.onMouseUp);
    previewInteraction.onContentMouseDown = previewInteraction.bind(previewInteraction, previewInteraction.onContentMouseDown);
    previewInteraction.onContentMouseUp = previewInteraction.bind(previewInteraction, previewInteraction.onContentMouseUp);
    
    const previewResizeHandlers = {{
        start(e) {{
            e.preventDefault();
            e.stopPropagation();
            if(state.holdTimer) clearTimeout(state.holdTimer);

            state.isResizingPreview = true;
            state.resizeDirection = Array.from(e.target.classList).find(cls => cls.startsWith('p-'));
            const coords = utils.getEventCoords(e);
            state.startMouseX = coords.x;
            state.startMouseY = coords.y;
            
            const rect = elements.floatingPreview.getBoundingClientRect();
            state.startCropLeft = rect.left;
            state.startCropTop = rect.top;
            state.startCropWidth = rect.width;
            state.startCropHeight = rect.height;

            elements.floatingPreview.style.transition = 'none';
            elements.floatingPreview.style.right = 'auto';
            elements.floatingPreview.style.bottom = 'auto';

            document.addEventListener('mousemove', this.move, {{ passive: false }});
            document.addEventListener('mouseup', this.stop, {{ once: true }});
            document.addEventListener('touchmove', this.move, {{ passive: false }});
            document.addEventListener('touchend', this.stop, {{ once: true }});
        }},
        
        move(e) {{
            if (!state.isResizingPreview) return;
            e.preventDefault();
            const coords = utils.getEventCoords(e);
            const deltaX = coords.x - state.startMouseX;
            const deltaY = coords.y - state.startMouseY;

            let newLeft = state.startCropLeft;
            let newTop = state.startCropTop;
            let newWidth = state.startCropWidth;
            let newHeight = state.startCropHeight;

            if (state.resizeDirection.includes('e')) newWidth = state.startCropWidth + deltaX;
            if (state.resizeDirection.includes('w')) {{
                newWidth = state.startCropWidth - deltaX;
                newLeft = state.startCropLeft + deltaX;
            }}
            if (state.resizeDirection.includes('s')) newHeight = state.startCropHeight + deltaY;
            if (state.resizeDirection.includes('n')) {{
                newHeight = state.startCropHeight - deltaY;
                newTop = state.startCropTop + deltaY;
            }}

            const minWidth = 150, minHeight = 120;
            if (newWidth < minWidth) {{
                if (state.resizeDirection.includes('w')) newLeft += newWidth - minWidth;
                newWidth = minWidth;
            }}
            if (newHeight < minHeight) {{
                if (state.resizeDirection.includes('n')) newTop += newHeight - minHeight;
                newHeight = minHeight;
            }}
            
            elements.floatingPreview.style.left = newLeft + 'px';
            elements.floatingPreview.style.top = newTop + 'px';
            elements.floatingPreview.style.width = newWidth + 'px';
            elements.floatingPreview.style.height = newHeight + 'px';
        }},
        
        stop() {{
            state.isResizingPreview = false;
            elements.floatingPreview.style.transition = '';
            document.removeEventListener('mousemove', this.move);
            document.removeEventListener('touchmove', this.move);
        }}
    }};
    previewResizeHandlers.start = previewResizeHandlers.start.bind(previewResizeHandlers);
    previewResizeHandlers.move = previewResizeHandlers.move.bind(previewResizeHandlers);
    previewResizeHandlers.stop = previewResizeHandlers.stop.bind(previewResizeHandlers);
    
    // --- New Pinch Zoom Handlers for Floating Preview ---
    function startPreviewPinch(e) {{
        if (!e.touches || e.touches.length !== 2) return;
        e.preventDefault();
        e.stopPropagation();

        if(state.holdTimer) clearTimeout(state.holdTimer);

        state.isPreviewPinching = true;
        state.previewPinchInitialDist = utils.getDistance(e.touches[0], e.touches[1]);

        const rect = elements.floatingPreview.getBoundingClientRect();
        state.previewPinchInitialWidth = rect.width;
        state.previewPinchInitialHeight = rect.height;

        elements.floatingPreview.style.transition = 'none';

        document.addEventListener('touchmove', handlePreviewPinchMove, {{ passive: false }});
        document.addEventListener('touchend', handlePreviewPinchEnd, {{ once: true }});
    }}

    function handlePreviewPinchMove(e) {{
        if (!state.isPreviewPinching || !e.touches || e.touches.length !== 2) return;
        e.preventDefault();

        const newDist = utils.getDistance(e.touches[0], e.touches[1]);
        if (state.previewPinchInitialDist <= 0) return;
        const factor = newDist / state.previewPinchInitialDist;

        let newWidth = state.previewPinchInitialWidth * factor;
        let newHeight = state.previewPinchInitialHeight * factor;

        const minWidth = 150;
        const minHeight = 120;
        const maxWidth = window.innerWidth * 0.95;
        const maxHeight = window.innerHeight * 0.95;

        newWidth = Math.max(minWidth, Math.min(newWidth, maxWidth));
        newHeight = Math.max(minHeight, Math.min(newHeight, maxHeight));

        elements.floatingPreview.style.width = newWidth + 'px';
        elements.floatingPreview.style.height = newHeight + 'px';
    }}

    function handlePreviewPinchEnd() {{
        if (!state.isPreviewPinching) return;
        state.isPreviewPinching = false;
        elements.floatingPreview.style.transition = '';
        document.removeEventListener('touchmove', handlePreviewPinchMove);
    }}

    function setupEventListeners() {{
      elements.themeToggle.addEventListener("click", toggleTheme);
      
      if (elements.crop) {{
        elements.crop.addEventListener("mousedown", dragHandlers.start);
        elements.crop.addEventListener("touchstart", dragHandlers.start, {{ passive: false }});
        elements.crop.addEventListener("contextmenu", showContextMenu);
        elements.crop.addEventListener("dblclick", centerCrop);
      
        document.querySelectorAll('.resize-handle').forEach(handle => {{
          handle.addEventListener("mousedown", resizeHandlers.start);
          handle.addEventListener("touchstart", resizeHandlers.start, {{ passive: false }});
        }});
      }}
      
      if (elements.mediaWrapper) {{
          elements.mediaWrapper.addEventListener("touchstart", handleMediaTouchStart, {{ passive: false }});
      }}
      
      if (elements.mediaViewer) {{
          elements.mediaViewer.addEventListener("wheel", handleMouseWheelZoom, {{ passive: false }});
      }}
      
      elements.aspectSelect.addEventListener("change", handleAspectRatioChange);
      elements.customW.addEventListener("input", utils.debounce(updateCustomAspectRatio, 300));
      elements.customH.addEventListener("input", utils.debounce(updateCustomAspectRatio, 300));
      
      document.addEventListener("keydown", handleKeyboard);
      
      window.addEventListener("resize", handleWindowResize);
      
      document.addEventListener("selectstart", e => {{
        if (state.isDragging || state.isResizing || state.isResizingPreview || previewInteraction.isDragging || state.isPreviewPinching) e.preventDefault();
      }});
      
      document.addEventListener("click", (e) => {{
        if (elements.contextMenu && !elements.contextMenu.contains(e.target)) {{
          hideContextMenu();
        }}
      }});

      elements.helpModal.addEventListener('click', (e) => {{
        if (e.target === elements.helpModal) {{
          toggleHelp();
        }}
      }});
      
      if (elements.floatingPreview) {{
        elements.previewHeader.addEventListener('mousedown', previewInteraction.onMouseDown);
        elements.previewHeader.addEventListener('touchstart', previewInteraction.onMouseDown, {{ passive: false }});
        
        const previewContentTouchStart = (e) => {{
            if (e.touches.length === 2) {{
                startPreviewPinch(e);
            }} else if (e.touches.length === 1) {{
                previewInteraction.onContentMouseDown(e);
            }}
        }};

        elements.previewCanvasWrapper.addEventListener('mousedown', previewInteraction.onContentMouseDown);
        elements.previewCanvasWrapper.addEventListener('mouseup', previewInteraction.onContentMouseUp);
        elements.previewCanvasWrapper.addEventListener('touchstart', previewContentTouchStart, {{ passive: false }});
        elements.previewCanvasWrapper.addEventListener('touchend', previewInteraction.onContentMouseUp);

        document.querySelectorAll('.preview-resize-handle').forEach(handle => {{
            handle.addEventListener('mousedown', previewResizeHandlers.start);
            handle.addEventListener('touchstart', previewResizeHandlers.start, {{ passive: false }});
        }});
        
        elements.previewCloseBtn.addEventListener('click', closePreviewFullscreen);
      }}
    }}

    document.addEventListener("DOMContentLoaded", function() {{
      initializeTheme();
      setupEventListeners();
      
      if (elements.media) {{
        if (elements.media.complete || elements.media.readyState >= 2) {{
          initializeCrop();
        }} else {{
          elements.media.addEventListener('loadedmetadata', initializeCrop);
          elements.media.addEventListener('canplay', initializeCrop);
          elements.media.addEventListener('load', initializeCrop);
          elements.media.addEventListener('error', () => {{
            console.error("Media failed to load.");
            hideLoading();
          }});
        }}
      }} else {{
        setTimeout(() => {{
          initializeCrop();
        }}, 100);
      }}
    }});
    """
    return js_code