# Live Transcription Architecture Design

## Philosophy

Live transcription should be:
- **Silent by default** - No output spam
- **Easy to program** - Simple callbacks and events
- **Auto-tuning** - Discover optimal settings for your hardware
- **Progressive** - CPU → GPU → Remote GPU
- **Observable** - Rich display when you want it

## Core API Design

### 1. Clean Callback Interface

```python
from parakeet_stream import LiveTranscriber

def on_update(segment):
    """Called every time transcription updates"""
    print(f"Latest: {segment.text[-50:]}")  # Last 50 chars

    # Your logic here
    if "stop recording" in segment.text.lower():
        return False  # Signal to stop
    return True

# Simple, clean usage
transcriber = LiveTranscriber(
    on_update=on_update,
    mode='auto',  # Auto-detect best mode (cpu/gpu/remote)
)

transcriber.start()  # Blocking
```

### 2. Generator Interface (for loops)

```python
from parakeet_stream import LiveTranscriber

transcriber = LiveTranscriber(mode='auto', verbose=False)

# Get updates as they come
for segment in transcriber.stream():
    # segment.text - full transcription so far
    # segment.new_text - just the new part
    # segment.confidence - quality score
    # segment.is_final - is this a final version?

    print(segment.new_text, end='', flush=True)

    if "stop" in segment.text.lower():
        break
```

### 3. Event-Driven Interface

```python
from parakeet_stream import LiveTranscriber

transcriber = LiveTranscriber(mode='auto')

@transcriber.on_segment
def handle_segment(text, is_final):
    """Handle each segment as it arrives"""
    if is_final:
        print(f"\n✓ {text}")
    else:
        print(f"\r{text[-100:]}", end='', flush=True)

@transcriber.on_word
def handle_word(word, confidence):
    """Handle individual words (for fine-grained control)"""
    if confidence > 0.9:
        trigger_action(word)

transcriber.start(duration=60)
```

### 4. Display Modes

```python
from parakeet_stream import LiveTranscriber, DisplayMode

# Minimal - just show latest
transcriber = LiveTranscriber(display=DisplayMode.MINIMAL)
# Output: "And if I speak English does it go well?"

# Progress - show updates in place
transcriber = LiveTranscriber(display=DisplayMode.PROGRESS)
# Output: "⏺ Recording... | Latest: does it go well?"

# Rich - full status panel
transcriber = LiveTranscriber(display=DisplayMode.RICH)
# Output:
# ┌─ Live Transcription ────────────────────┐
# │ Status: Recording (15.2s)               │
# │ Quality: ●●●●○ (0.87 avg confidence)    │
# │ Latency: ~2.3s                          │
# ├─────────────────────────────────────────┤
# │ And if I speak English does it go well? │
# └─────────────────────────────────────────┘

# Silent - no output at all (for pure programming)
transcriber = LiveTranscriber(display=DisplayMode.SILENT)
```

## Hardware Auto-Tuning

### Auto-Discovery

```python
from parakeet_stream import benchmark_hardware

# Run once to discover optimal settings
results = benchmark_hardware(duration=10)

print(results)
# Hardware Profile:
#   Device: CPU (Intel i7-1185G7)
#   Transcription speed: 0.23x realtime
#   Recommended mode: 'cpu_optimized'
#   Max window: 5.0s (for live-ish feel)
#   Suggested params:
#     chunk_secs: 2.0
#     left_context_secs: 3.0
#     right_context_secs: 0.5

# Use recommended settings
transcriber = LiveTranscriber(profile=results.profile)
```

### Mode Presets

```python
# CPU-optimized (works everywhere)
transcriber = LiveTranscriber(mode='cpu')
# - Smaller chunks
# - Less context
# - Lower quality but fast

# GPU-optimized (local GPU)
transcriber = LiveTranscriber(mode='gpu')
# - Larger chunks
# - More context
# - Higher quality

# Remote GPU (client-server)
transcriber = LiveTranscriber(mode='remote', server='ws://gpu-server:8765')
# - Maximum quality
# - Network latency
# - Best results

# Auto (detect and choose best)
transcriber = LiveTranscriber(mode='auto')
# Tries: GPU → CPU → Remote (if configured)
```

## Overlapping Window Strategy

### Built-in Strategy

```python
from parakeet_stream import LiveTranscriber, Strategy

transcriber = LiveTranscriber(
    strategy=Strategy.OVERLAPPING,
    window_size=10.0,      # Large windows for quality
    update_interval=0.5,   # Fast updates
    mode='gpu',            # Need GPU for this to be realtime
)

# Updates every 0.5s with full 10s context
for segment in transcriber.stream():
    # Gets progressively better as more context arrives
    print(segment.text)
```

### Strategy Comparison

```python
from parakeet_stream import compare_strategies

# Test different strategies on same audio
results = compare_strategies(
    audio_file='test.wav',
    strategies=['default', 'overlapping', 'consensus'],
)

# Output:
# Strategy Comparison:
#   default:      Quality: ●●●○○  Speed: 1.2x  Latency: 2.0s
#   overlapping:  Quality: ●●●●○  Speed: 0.8x  Latency: 10.5s
#   consensus:    Quality: ●●●●●  Speed: 0.3x  Latency: 15.0s
```

## Configuration Profiles

### Save/Load Profiles

```python
from parakeet_stream import LiveTranscriber

# Create with custom settings
transcriber = LiveTranscriber(
    chunk_secs=10.0,
    left_context_secs=5.0,
    right_context_secs=0.5,
)

# Save profile
transcriber.save_profile('my_profile.json')

# Load later
transcriber = LiveTranscriber.from_profile('my_profile.json')
```

### Built-in Profiles

```python
# High quality (for demos, recordings)
LiveTranscriber(profile='high_quality')

# Low latency (for live interactions)
LiveTranscriber(profile='low_latency')

# Balanced (good default)
LiveTranscriber(profile='balanced')

# Custom for specific hardware
LiveTranscriber(profile='macbook_m1')
LiveTranscriber(profile='rtx_4090')
```

## Example Use Cases

### 1. Voice Commands (Silent, Fast)

```python
from parakeet_stream import LiveTranscriber

def handle_command(text):
    if "lights on" in text.lower():
        smart_home.lights_on()
    elif "play music" in text.lower():
        music_player.play()

transcriber = LiveTranscriber(
    display=DisplayMode.SILENT,  # No output
    mode='cpu',                  # Fast, works everywhere
    on_update=handle_command,
)

transcriber.start()  # Run forever
```

### 2. Live Captions (Visible, Updating)

```python
from parakeet_stream import LiveTranscriber, DisplayMode

transcriber = LiveTranscriber(
    display=DisplayMode.PROGRESS,
    mode='gpu',
    strategy=Strategy.OVERLAPPING,
)

for segment in transcriber.stream():
    # Display updates in real-time
    # Built-in display handles it
    pass
```

### 3. Meeting Transcription (Rich Display + Save)

```python
from parakeet_stream import LiveTranscriber, DisplayMode

with open('meeting.txt', 'w') as f:
    transcriber = LiveTranscriber(
        display=DisplayMode.RICH,
        mode='remote',
        server='ws://gpu-server:8765',
    )

    for segment in transcriber.stream():
        if segment.is_final:
            f.write(segment.new_text + '\n')
            f.flush()
```

### 4. Research/Analysis (Get Everything)

```python
from parakeet_stream import LiveTranscriber

transcriber = LiveTranscriber(display=DisplayMode.SILENT)

segments = []
for segment in transcriber.stream(duration=60):
    segments.append({
        'text': segment.text,
        'confidence': segment.confidence,
        'timestamp': segment.timestamp,
        'words': segment.words,  # Word-level detail
    })

# Analyze after
import pandas as pd
df = pd.DataFrame(segments)
df.to_csv('analysis.csv')
```

## Implementation Priority

1. **Phase 1: Clean API** ✅ (partially done)
   - Silent by default
   - Clean callbacks
   - DisplayMode enum

2. **Phase 2: Auto-tuning**
   - Hardware benchmark
   - Profile system
   - Mode auto-detection

3. **Phase 3: Display System**
   - MINIMAL, PROGRESS, RICH, SILENT modes
   - Clean terminal output
   - Rich progress bars

4. **Phase 4: Strategies**
   - Clean overlapping implementation
   - Strategy comparison
   - Easy switching

## Output Examples

### MINIMAL Mode
```
And if I speak English does it go well?
```

### PROGRESS Mode
```
⏺ 15.2s | And if I speak English does it go well?
```

### RICH Mode
```
┌─ Live Transcription ────────────────────┐
│ ⏺ Recording: 15.2s                      │
│ Quality: ●●●●○ (0.87)                   │
│ Mode: GPU                               │
└─────────────────────────────────────────┘
And if I speak English does it go well?
Yeah, English is probably even better.
```

### SILENT Mode
```
(no output - just callbacks)
```

## Questions for Design

1. Do we want word-level callbacks or just segment-level?
2. Should `is_final` mean "no more updates to this text" or "high confidence"?
3. Should we support async/await or just sync API?
4. Do we need a "pause/resume" feature?
