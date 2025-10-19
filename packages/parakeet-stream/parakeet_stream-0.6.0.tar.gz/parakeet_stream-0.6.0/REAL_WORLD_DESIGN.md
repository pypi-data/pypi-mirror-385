# Parakeet Stream: Real-World Design

## Philosophy: One Tool, Many Faces

Instead of one API that tries to do everything, provide **focused interfaces for specific use cases**.

---

## Use Case 1: Voice Commands (Dead Simple)

**User Story:** "I want my computer to do things when I speak"

### What They Actually Need
- Ultra-low latency (< 1s)
- Pattern matching on keywords
- NO visual clutter
- Works on any machine
- Auto-starts on boot

### Perfect API

```python
from parakeet_stream import VoiceCommands

# Dead simple - just map phrases to functions
commands = VoiceCommands({
    "lights on": lambda: smart_home.lights(True),
    "lights off": lambda: smart_home.lights(False),
    "play music": lambda: spotify.play(),
    "stop": lambda: exit(),
})

commands.listen()  # That's it. Runs forever, no output.
```

### Advanced Version

```python
import re
from parakeet_stream import VoiceCommands

def handle_volume(match):
    level = match.group(1)  # Extract number
    speaker.volume(int(level))

commands = VoiceCommands({
    r"volume (\d+)": handle_volume,  # Regex patterns
    r"(play|pause)": lambda m: player.toggle(),
    "what time": lambda: speaker.say(datetime.now()),
})

# Options for this use case
commands.listen(
    latency='ultra',     # Optimize for speed
    language='en',       # Or 'fr', 'auto'
    wake_word='computer' # Only listen after "computer"
)
```

**Key Features:**
- ✅ No clutter (silent by default)
- ✅ Fast (CPU-optimized internally)
- ✅ Simple (just a dict)
- ✅ Powerful (regex, callbacks)

---

## Use Case 2: Live Captions (Visual Focus)

**User Story:** "I need to see what's being said in real-time"

### What They Actually Need
- Large, readable text
- Updates smoothly
- High accuracy (not speed)
- Full-screen or window mode
- Works with any audio source

### Perfect API

```python
from parakeet_stream import LiveCaptions

# One line - opens a window with live captions
LiveCaptions().show()
```

### Customized

```python
from parakeet_stream import LiveCaptions

captions = LiveCaptions(
    font_size=32,           # Big text
    window_mode='overlay',  # Floats over everything
    quality='maximum',      # Accuracy over speed
    language='auto',        # Detect language
    history=5,              # Show last 5 lines
)

captions.show()

# Or embed in your app
window = captions.get_widget()  # Returns QWidget/tkinter/etc
```

**Key Features:**
- ✅ Visual-first (designed for reading)
- ✅ Smooth updates (no flicker)
- ✅ Accessible (big fonts, high contrast)
- ✅ Non-intrusive (overlay mode)

---

## Use Case 3: Save Transcript (Fire & Forget)

**User Story:** "Just transcribe this file and save it"

### What They Actually Need
- Best quality
- Progress bar
- Output file
- Batch processing
- CLI tool

### Perfect API

```python
from parakeet_stream import transcribe

# One function call
transcribe('meeting.mp3', output='meeting.txt')

# Batch
transcribe(['file1.mp3', 'file2.mp3'], output_dir='transcripts/')

# With options
transcribe(
    'interview.wav',
    output='interview.txt',
    quality='maximum',
    format='json',  # or 'txt', 'srt', 'vtt'
    timestamps=True,
    speaker_labels=True,  # If available
)
```

### CLI Tool

```bash
# Simple
parakeet transcribe meeting.mp3

# Output to file
parakeet transcribe meeting.mp3 -o meeting.txt

# Batch
parakeet transcribe *.mp3 --output-dir transcripts/

# High quality
parakeet transcribe interview.wav --quality maximum --format json
```

**Key Features:**
- ✅ Simple function/command
- ✅ Progress bar
- ✅ Multiple formats
- ✅ Batch processing

---

## Use Case 4: Build Your Own App (Developer Power)

**User Story:** "I'm building a voice app and need full control"

### What They Actually Need
- Event-driven or streaming
- Low-level access
- Performance control
- No assumptions about UI

### Perfect API (Event-Driven)

```python
from parakeet_stream import LiveStream

stream = LiveStream()

@stream.on_speech_start
def started():
    print("🎤 Listening...")

@stream.on_speech_end
def ended():
    print("✓ Done")

@stream.on_partial(interval=0.5)  # Every 0.5s
def partial(text, confidence):
    """Called with partial results (may change)"""
    update_ui(text, is_final=False)

@stream.on_final
def final(text, confidence, metadata):
    """Called with final, stable result"""
    update_ui(text, is_final=True)
    save_to_db(text, metadata)

# Start streaming
stream.start(mode='auto')  # or 'cpu', 'gpu', 'remote'
```

### Perfect API (Generator/Async)

```python
from parakeet_stream import LiveStream

stream = LiveStream(mode='auto', verbose=False)

# Sync generator
for segment in stream:
    print(segment.text)
    if segment.is_final:
        database.save(segment)

# Async generator
async for segment in stream.async_stream():
    await websocket.send(segment.to_json())
```

### Low-Level Access

```python
from parakeet_stream import Parakeet, Microphone

# Direct access for advanced users
parakeet = Parakeet(config='balanced', device='cuda')
mic = Microphone()

while True:
    audio = mic.record(duration=1.0)
    result = parakeet.transcribe(audio.data)

    # You handle everything
    your_custom_logic(result)
```

**Key Features:**
- ✅ Event-driven patterns
- ✅ Sync and async
- ✅ Full control
- ✅ No forced UI

---

## Use Case 5: Research & Analysis (Data Focus)

**User Story:** "I need transcripts with metadata for analysis"

### What They Actually Need
- Word-level timestamps
- Confidence scores
- Multiple export formats
- Batch processing
- Statistical analysis

### Perfect API

```python
from parakeet_stream import analyze

# Get detailed results
results = analyze('lecture.mp3', detail='full')

# Results include:
results.text              # Full transcript
results.segments          # List of segments with timing
results.words             # Word-level detail
results.confidence_avg    # Average confidence
results.language          # Detected language
results.duration          # Audio duration
results.wer_estimate      # Estimated word error rate

# Export to different formats
results.to_json('lecture.json')
results.to_dataframe()    # Pandas DataFrame
results.to_srt('lecture.srt')  # Subtitles
results.to_textgrid()     # Praat TextGrid

# Batch analysis
from parakeet_stream import batch_analyze

df = batch_analyze(['file1.mp3', 'file2.mp3', 'file3.mp3'])
print(df.head())
#    file        duration  words  confidence  language
# 0  file1.mp3   120.5     856    0.89        en
# 1  file2.mp3   95.2      723    0.92        en
```

**Key Features:**
- ✅ Rich metadata
- ✅ Multiple formats
- ✅ Pandas integration
- ✅ Batch processing

---

## Cross-Cutting: Performance Tuning

All APIs should auto-detect and optimize, but allow override:

```python
# Auto mode (default) - detects GPU, optimizes
VoiceCommands(mode='auto')

# Explicit control
VoiceCommands(
    mode='cpu',          # Force CPU
    latency='ultra',     # Optimize for speed
    quality='medium',    # Trade quality for speed
)

# Remote GPU
VoiceCommands(
    mode='remote',
    server='ws://gpu-box:8765',
)

# Custom params (advanced)
VoiceCommands(
    chunk_secs=1.0,
    left_context_secs=5.0,
    right_context_secs=0.5,
)
```

## Implementation Strategy

### Phase 1: Focused APIs (Most Value Fast)
1. `VoiceCommands` - solves voice assistant use case
2. `transcribe()` function - solves file transcription
3. Clean up `Parakeet` class - for developers

### Phase 2: Visual & Data
4. `LiveCaptions` - solves accessibility
5. `analyze()` - solves research

### Phase 3: Polish
6. Auto-tuning and benchmarking
7. Remote GPU improvements
8. Documentation and examples

---

## Questions to Answer

1. **For VoiceCommands:** Do we need wake words? Voice activity detection?
2. **For LiveCaptions:** Should it be a separate app or a library?
3. **For transcribe():** What formats are essential? (txt, json, srt - what else?)
4. **For developers:** Event-driven vs generators - which is better?
5. **Performance:** Should auto-tuning run once and save, or every time?

## What Makes This Brilliant

Each API is designed for **one job** and does it **perfectly**:
- Voice commands: No UI, fast, simple
- Live captions: UI-first, smooth, accessible
- Transcribe: Best quality, progress, done
- Developer: Full control, no assumptions
- Research: Rich data, analysis-ready

No more "one size fits none" - each user gets exactly what they need.
