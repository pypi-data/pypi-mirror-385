# The Composable Transcription API

## Inspiration: dplyr + ggplot

**dplyr's genius:** Verbs + pipe = infinite compositions
**ggplot's genius:** Layers + grammar = infinite visualizations
**Our goal:** Components + composition = infinite transcription flows

---

## The Core Abstraction

```python
from parakeet_stream import stream

# The 80/20 pattern - everything builds from this:
stream.from_mic() | process() | to_text()
```

Three parts, infinitely composable.

---

## Part 1: Sources (where audio comes from)

```python
from parakeet_stream import stream

# Microphone
stream.from_mic()
stream.from_mic(device=1)
stream.from_mic(duration=60)

# Files
stream.from_file("audio.mp3")
stream.from_files(["f1.mp3", "f2.mp3"])
stream.from_folder("recordings/*.wav")

# URLs
stream.from_url("https://example.com/podcast.mp3")
stream.from_youtube("https://youtube.com/watch?v=...")

# System audio (capture what's playing)
stream.from_system_audio()

# Live input
stream.from_websocket("ws://...")
stream.from_rtmp("rtmp://...")
```

---

## Part 2: Processing (how to transcribe)

```python
# Default - auto-optimized
stream.from_mic() | process()

# Quality presets
stream.from_mic() | process(quality='maximum')
stream.from_mic() | process(quality='balanced')
stream.from_mic() | process(quality='realtime')

# Explicit control
stream.from_mic() | process(
    chunk_secs=10.0,
    left_context=5.0,
    right_context=0.5,
)

# Strategies
stream.from_mic() | process(strategy='overlapping', update_every=0.5)

# Hardware
stream.from_mic() | process(device='cpu')
stream.from_mic() | process(device='cuda')
stream.from_mic() | process(remote='ws://gpu-server:8765')

# Language
stream.from_mic() | process(language='fr')
stream.from_mic() | process(language='auto')
```

---

## Part 3: Outputs (what to do with results)

```python
# Print
stream.from_mic() | process() | to_text()
stream.from_mic() | process() | to_text(style='minimal')

# Save
stream.from_file("audio.mp3") | process() | to_file("transcript.txt")
stream.from_file("audio.mp3") | process() | to_json("transcript.json")
stream.from_file("audio.mp3") | process() | to_srt("subtitles.srt")

# Callback
def handle(segment):
    print(segment.text)
    if "stop" in segment.text:
        return False  # Stop

stream.from_mic() | process() | to_callback(handle)

# Multiple outputs
stream.from_mic() | process() | [
    to_text(style='minimal'),
    to_file("log.txt"),
    to_callback(my_handler)
]

# Custom display
stream.from_mic() | process() | to_display(
    show_confidence=True,
    show_timing=True,
    lines=5
)

# Data structures
segments = stream.from_file("audio.mp3") | process() | to_list()
df = stream.from_files(["*.mp3"]) | process() | to_dataframe()

# Web/Network
stream.from_mic() | process() | to_websocket("ws://...")
stream.from_mic() | process() | to_http("http://api/transcribe")
```

---

## Composition Examples

### Voice Commands (Simple)
```python
from parakeet_stream import stream

def on_command(segment):
    text = segment.text.lower()
    if "lights on" in text:
        smart_home.lights_on()
    elif "lights off" in text:
        smart_home.lights_off()

# That's it
stream.from_mic() | process(quality='realtime') | to_callback(on_command)
```

### Live Captions
```python
# Auto-updating display
stream.from_mic() | process() | to_display(
    style='captions',
    font_size=32,
    lines=3
)
```

### Transcribe Files
```python
# Batch transcribe with progress
stream.from_files("recordings/*.mp3") | process(quality='maximum') | to_folder("transcripts/")
```

### Developer Integration
```python
# Event stream
for segment in stream.from_mic() | process():
    update_ui(segment.text)
    database.save(segment)

# Or async
async for segment in stream.from_mic() | process() | async_iter():
    await websocket.send(segment.json())
```

### Research Analysis
```python
# Get detailed data
results = (
    stream.from_files(["interview*.mp3"])
    | process(detail='full')
    | to_dataframe()
)

# Now analyze
print(results.groupby('file')['confidence'].mean())
results.to_csv('analysis.csv')
```

---

## The Magic: Chainable Transformations

Like dplyr's mutate/filter, add transformation steps:

```python
from parakeet_stream import stream

(stream.from_mic()
 | process()
 | filter(lambda s: s.confidence > 0.8)  # Only high confidence
 | map(lambda s: s.text.upper())         # Transform text
 | buffer(5)                              # Batch 5 at a time
 | to_callback(handle_batch))
```

---

## Smart Defaults + Easy Overrides

The key to 80/20:

```python
# Minimal - does the right thing
stream.from_mic() | process() | to_text()

# But every part can be customized
(stream.from_mic(device=2, sample_rate=16000)
 | process(
     quality='maximum',
     device='cuda',
     strategy='overlapping',
     update_every=0.5
   )
 | to_display(
     style='rich',
     show_confidence=True,
     update_rate=0.1
   ))
```

---

## Implementation: The Pipe

```python
class Stream:
    """Composable stream that supports | operator"""

    def __init__(self, source):
        self.source = source
        self.processors = []
        self.outputs = []

    def __or__(self, other):
        """Enable | operator for chaining"""
        if isinstance(other, Processor):
            self.processors.append(other)
            return self
        elif isinstance(other, Output):
            self.outputs.append(other)
            return self
        elif callable(other):
            return other(self)
        elif isinstance(other, list):
            self.outputs.extend(other)
            return self

    def __iter__(self):
        """Enable: for segment in stream..."""
        # Execute the pipeline
        audio_stream = self.source.stream()

        for processor in self.processors:
            audio_stream = processor.process(audio_stream)

        for segment in audio_stream:
            for output in self.outputs:
                output.handle(segment)
            yield segment
```

---

## Comparison to Current API

### Current (Scattered)
```python
# Different interfaces for each use case
parakeet = Parakeet(config='balanced')
result = parakeet.transcribe('audio.wav')

live = parakeet.listen()
live.stop()

client = ParakeetClient('ws://...')
for segment in client.stream_microphone():
    ...
```

### New (Unified)
```python
# Same pattern everywhere
stream.from_file('audio.wav') | process() | to_text()

stream.from_mic() | process() | to_text()

stream.from_mic() | process(remote='ws://...') | to_text()
```

---

## Power Features (Advanced Users)

### Custom Sources
```python
from parakeet_stream import AudioSource

class MySource(AudioSource):
    def stream(self):
        while True:
            audio = get_audio_somehow()
            yield audio

stream.from_source(MySource()) | process() | to_text()
```

### Custom Processors
```python
from parakeet_stream import Processor

class MyProcessor(Processor):
    def process(self, segment):
        # Custom logic
        segment.text = clean_up(segment.text)
        return segment

stream.from_mic() | process() | MyProcessor() | to_text()
```

### Custom Outputs
```python
class DatabaseOutput:
    def handle(self, segment):
        db.save(segment)

stream.from_mic() | process() | DatabaseOutput()
```

---

## Why This Is The 80/20

1. **One pattern for everything** - learn once, use everywhere
2. **Composable** - mix and match sources, processors, outputs
3. **Progressive disclosure** - simple by default, powerful when needed
4. **Readable** - pipeline reads like English
5. **Extensible** - custom components fit naturally

### The 80%
```python
# Most users just need this
stream.from_mic() | process() | to_text()
stream.from_file('audio.mp3') | process() | to_file('transcript.txt')
```

### The 20%
```python
# Power users can go deep
(stream.from_folder("recordings/*.mp3")
 | process(
     quality='maximum',
     device='cuda',
     strategy='consensus',
     languages=['en', 'fr']
   )
 | filter(lambda s: s.confidence > 0.9)
 | transform(remove_filler_words)
 | [
     to_json('results.json'),
     to_dataframe() | analyze() | plot(),
     to_webhook('http://api.example.com/transcripts')
   ])
```

---

## Migration Path

Keep old API for backwards compatibility:
```python
# Old way still works
parakeet = Parakeet()
result = parakeet.transcribe('audio.wav')

# New way preferred
result = stream.from_file('audio.wav') | process() | to_result()
```

---

## Questions

1. Should `process()` be explicit or implied?
   ```python
   # Explicit (more control)
   stream.from_mic() | process() | to_text()

   # Implicit (more concise)
   stream.from_mic() | to_text()  # process() is automatic
   ```

2. Should outputs execute immediately or lazily?
   ```python
   # Immediate
   stream.from_mic() | process() | to_text()  # Starts now

   # Lazy
   pipeline = stream.from_mic() | process() | to_text()
   pipeline.start()  # Start explicitly
   ```

3. How to handle async?
   ```python
   # Option 1: Separate async methods
   async for segment in stream.from_mic() | process() | async_iter():
       ...

   # Option 2: Auto-detect context
   for segment in stream.from_mic() | process():  # sync
       ...
   async for segment in stream.from_mic() | process():  # async
       ...
   ```

## This IS the 80/20

Like dplyr's verbs and ggplot's layers, this gives you:
- **One mental model** for all transcription tasks
- **Composable primitives** that combine naturally
- **Sensible defaults** with easy customization
- **Discoverable API** (tab completion shows options)
- **Readable code** that documents itself
