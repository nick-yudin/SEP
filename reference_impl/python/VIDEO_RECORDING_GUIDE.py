# 🎥 Video Recording Guide for Resonance Protocol Demos

## Goal
Create a 30-60 second screencast showing the protocol in action.

---

## Option 1: Quick Terminal Recording (Recommended)

### Using `asciinema` (Best for GitHub)

```bash
# Install
brew install asciinema  # macOS
# or: pip install asciinema

# Record
asciinema rec demo.cast

# Run your demo
python quick_demo.py

# Stop recording (Ctrl+D)

# Upload to asciinema.org (optional)
asciinema upload demo.cast

# Convert to GIF for README
docker run --rm -v $PWD:/data asciinema/asciicast2gif demo.cast demo.gif
```

**Put the file here:** `/reference_impl/python/assets/demo.gif`

---

## Option 2: Full Screen Recording

### Using QuickTime (macOS)

1. Open QuickTime Player
2. File → New Screen Recording
3. Select area (just terminal window)
4. Record `python quick_demo.py`
5. Stop when done
6. Export as `demo.mp4`

**Put the file here:** `/reference_impl/python/assets/demo.mp4`

---

## Option 3: GIF from Terminal (Simple)

### Using `terminalizer`

```bash
# Install
npm install -g terminalizer

# Record
terminalizer record demo

# Run your commands
python quick_demo.py

# Render to GIF
terminalizer render demo
```

**Output:** `demo.gif`

---

## What to Show in the Video

### Script (30 seconds):

```bash
# 1. Show quick start (5 sec)
cd reference_impl/python
ls -la

# 2. Run demo (20 sec)
python quick_demo.py
# Let it run through Demo 1 (semantic filtering)
# Show the TRANSMIT vs SILENCE output

# 3. Show result (5 sec)
# Highlight "67% bandwidth reduction"
```

### Key moments to capture:
- ⚡ "TRANSMIT" events (green/yellow)
- 🔇 "SILENCE" suppressions (gray)
- ✅ Final statistics ("67% bandwidth reduction")

---

## Video Specs

| Setting | Value |
|---------|-------|
| **Resolution** | 1920x1080 or 1280x720 |
| **FPS** | 30 (or 60 for smooth) |
| **Duration** | 30-60 seconds |
| **Format** | MP4 (video) or GIF (animation) |
| **Size** | <5MB for GIF, <20MB for MP4 |

---

## Where to Put Videos

```
/reference_impl/python/
├── assets/
│   ├── demo.gif              ← Quick demo animation
│   ├── alignment_demo.gif    ← Procrustes visualization
│   ├── gossip_demo.gif       ← Mesh propagation
│   └── full_demo.mp4         ← Complete walkthrough (optional)
└── README.md                  ← Embed with ![Demo](assets/demo.gif)
```

---

## Embedding in README

```markdown
## 🎬 See It In Action

![Resonance Protocol Demo](assets/demo.gif)

*30-second demo showing semantic filtering in real-time*
```

---

## Tips for Great Demos

1. **Clean terminal:** `clear` before starting
2. **Large font:** Increase terminal font size (16-18pt)
3. **Dark theme:** Better contrast for recording
4. **Slow down:** Add `time.sleep(0.5)` between outputs
5. **Highlight key moments:** Use colored output (✅ 🔇 ⚡)

---

## Optional: Multi-Window Demo

For advanced users, show two terminals side-by-side:

**Terminal 1:** `python receiver.py`  
**Terminal 2:** `python sender.py`

Record both with:
```bash
# Split screen in iTerm2 or tmux
# Record with QuickTime selecting both panes
```

---

## Example Recording Session

```bash
# 1. Prepare
cd resonance-protocol/reference_impl/python
clear

# 2. Start recording
asciinema rec quick_demo.cast

# 3. Run demo
python quick_demo.py
# Press ENTER to go through each demo

# 4. Stop (Ctrl+D)

# 5. Convert to GIF
# (see Option 1 above)

# 6. Commit
git add assets/demo.gif
git commit -m "Add quick demo screencast"
git push
```

---

## Questions?

Need help with recording? → 1@resonanceprotocol.org