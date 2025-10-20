# ✂️ MediaCrop - The Visual FFmpeg Crop Tool

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/mediacrop.svg)](https://pypi.org/project/mediacrop/)
[![Downloads](https://static.pepy.tech/badge/mediacrop)](https://pepy.tech/project/mediacrop)
[![Last Commit](https://img.shields.io/github/last-commit/mallikmusaddiq1/mediacrop.svg)](https://github.com/mallikmusaddiq1/mediacrop/commits/main)
[![Stars](https://img.shields.io/github/stars/mallikmusaddiq1/mediacrop.svg)](https://github.com/mallikmusaddiq1/mediacrop/stargazers)
[![Instagram](https://img.shields.io/badge/Instagram-%40musaddiq.x7-E4405F?logo=instagram\&logoColor=white)](https://instagram.com/musaddiq.x7)

---

## 🧩 Overview

**MediaCrop** is a modern, lightweight, web-based utility that removes the guesswork from cropping media using **FFmpeg**. It provides a clean, visual interface to obtain precise crop coordinates for any video, image, or audio file. Simply drag, resize, and instantly get your perfect FFmpeg crop string.

The tool launches a local web server, opening a sleek, responsive browser interface complete with **Light & Dark themes** for a fast, enjoyable, and efficient experience.

---

## 📖 The Story Behind MediaCrop

Working with **FFmpeg** offers immense power, but it's rarely intuitive—especially when it comes to identifying accurate **crop coordinates**. Traditionally, this involved a tedious cycle of:

1. Opening the file in a media player.
2. Estimating coordinates by sight.
3. Running the FFmpeg command.
4. Checking the result and repeating the process.

This endless loop wasted valuable time and energy. **MediaCrop** was conceived to end this frustration—a **visual, drag-and-drop solution** that instantly provides command-line-ready FFmpeg filter strings. No trial and error. No stress. Just **precision made effortless**.

---

## ✨ Key Features

| Category            | Feature                           | Description                                                                                                                      |
| :------------------ | :-------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| **Interface & UX**  | 🌌 **Light & Dark Themes**        | Switch effortlessly between themes, automatically saved in your browser.                                                         |
|                     | 🖼️ **Floating Live Preview**     | Real-time preview of the cropped area in a movable, resizable window with 8 handles. Supports pinch-to-zoom and fullscreen mode. |
|                     | 📱 **Responsive Design**          | Automatically adapts to all screens—desktop, tablet, and mobile.                                                                 |
|                     | 🔎 **Media Zoom**                 | Zoom in/out precisely using mouse wheel or pinch gestures.                                                                       |
|                     | 🖐️ **Advanced Touch Support**    | Seamless touch gestures for resizing, dragging, and zooming.                                                                     |
|                     | 🕹️ **Interactive Crop Box**      | Move and resize with 8 directional handles (N, S, E, W, NW, NE, SW, SE).                                                         |
| **Media Handling**  | ⏯️ **Full Video Controls**        | Includes play/pause, seek bar, playback speed, time display, and volume/mute controls.                                           |
|                     | 🎵 **Broad Format Support**       | Preview a wide range of image, video, and audio formats, with fallbacks for unsupported files.                                   |
| **Precision Tools** | 📊 **Aspect Ratio Presets**       | Choose standard ratios like *16:9, 4:3, 9:16, 1:1, 21:9* or enter a custom ratio.                                                |
|                     | 📊 **Real-Time Info Panel**       | Displays live resolution, crop size, coordinates, aspect ratio, and zoom level.                                                  |
|                     | ⌨️ **Keyboard Controls**          | Nudge with Arrow Keys (10px) or fine-tune with Shift + Arrow Keys (1px).                                                         |
| **Usability**       | 🔧 **Quick Tools & Context Menu** | Instantly center, toggle grid, or reset via sidebar or right-click menu.                                                         |
| **System**          | ⚙️ **Zero Dependencies**          | Runs entirely on Python’s standard library—no installs, no pain.                                                                 |
|                     | 🔌 **Smart Port Detection**       | Auto-selects a new port if the default (8000) is busy.                                                                           |
|                     | 💻 **Cross-Platform**             | Fully compatible with Windows, macOS, and Linux.                                                                                 |

---

## 🖼️ Screenshots

A modern interface available in both light and dark themes, optimized for every device.

![MediaCrop Desktop Screenshot](Screenshots/Screenshot-1080x1836.png)
![MediaCrop Desktop Screenshot](Screenshots/Screenshot-1080x1837.png)

---

### 🧠 Supported Preview Formats

**MediaCrop** computes coordinates for **any file readable by FFmpeg**, with native in-browser previews for:

* **Images:** JPG, PNG, WEBP, AVIF, GIF, BMP, SVG, ICO, HEIC, TIFF
* **Videos:** MP4, WEBM, MOV, OGV
* **Audio:** MP3, WAV, FLAC, OGG, M4A, AAC, OPUS

---

## ⚙️ Installation

Requires **Python 3.7+**.

### Option 1: Install from PyPI (Recommended)

```bash
pip install mediacrop
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/mallikmusaddiq1/mediacrop.git

# Navigate into the project directory
cd mediacrop

# Install the package locally
pip install .
```

---

## 🚀 Usage

Run the command below in your terminal:

```bash
mediacrop "/path/to/your/mediafile.mp4"
```

> **Note:** Always enclose file paths with spaces in quotes.

* The tool automatically launches in your default browser at [http://127.0.0.1:8000](http://127.0.0.1:8000).
* Adjust the crop box visually, apply aspect ratios, or toggle the grid overlay.
* Click **💾 Save Coordinates** to confirm.

  * The FFmpeg crop string appears in your terminal.
  * Press **Ctrl + C** in the terminal to stop the server.

---

### 🕹️ Command-Line Options

| Option                        | Description                                   |
| :---------------------------- | :-------------------------------------------- |
| `-p <port>` / `--port <port>` | Specify a custom server port (default: 8000). |
| `-v` / `--verbose`            | Enable detailed logs for debugging.           |
| `-h` / `--help`               | Display help message and exit.                |

---

## 🎬 Using the Output with FFmpeg

MediaCrop produces a command-line-ready crop filter string:

```
crop=1280:720:320:180
```

Apply it directly in your FFmpeg command:

```bash
ffmpeg -i input.mp4 -vf "crop=1280:720:320:180" output_cropped.mp4
```

---

## ⌨️ Controls & Shortcuts

| Action             | Control                            |
| :----------------- | :--------------------------------- |
| Move Crop Box      | Click + Drag / Arrow Keys          |
| Fine Move (1px)    | Shift + Arrow Keys                 |
| Resize Crop Box    | Drag Edges/Corners / Pinch (Touch) |
| Zoom Media View    | Mouse Wheel / Pinch (Touch)        |
| Toggle Grid        | G Key                              |
| Center Crop Box    | C Key                              |
| Save Coordinates   | Enter Key                          |
| Toggle Help Panel  | ? Key / Esc to Close               |
| Access Quick Tools | Right-Click on Crop Box            |
| Fullscreen Preview | Long-Press on Live Preview Window  |

---

## 🤝 Contributing

Contributions are warmly welcomed! Whether you fix bugs, add features, or improve documentation—your input helps make MediaCrop even better.

### How to Contribute

1. Fork this repository.
2. Create a new branch for your update:

   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit with a clear, descriptive message.
4. Open a Pull Request.

If you find this project valuable, please **star ⭐ it on GitHub** to support future development!

---

## 👨‍💻 Author

**Name:** Mallik Mohammad Musaddiq
**Email:** [mallikmusaddiq1@gmail.com](mailto:mallikmusaddiq1@gmail.com)
**GitHub:** [mallikmusaddiq1](https://github.com/mallikmusaddiq1)
**Project Repo:** [MediaCrop](https://github.com/mallikmusaddiq1/mediacrop)

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full details.