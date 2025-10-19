#!/usr/bin/env python3
"""
Real-time overlapping window transcription client.

Sends audio every 0.5s but with 10s windows for high quality.
The GPU reprocesses overlapping audio, and we keep updating the transcript.
"""

import asyncio
import json
import time
import sys
import io
from collections import deque
from typing import Optional

import numpy as np
from parakeet_stream import ParakeetClient, Microphone


class RealtimeOverlappingClient:
    """
    Client that sends overlapping audio windows for high-quality real-time transcription.

    Strategy:
    - Send 10s audio windows every 0.5s
    - GPU reprocesses with full context each time
    - Keep last 10s in buffer
    - Display most recent transcription
    """

    def __init__(
        self,
        server_url: str,
        window_size: float = 10.0,
        update_interval: float = 0.5,
        display_words: int = 20,  # Show last N words
        display: str = 'full',  # 'silent', 'minimal', 'full'
        on_update=None,  # Callback for each update
    ):
        self.server_url = server_url
        self.window_size = window_size
        self.update_interval = update_interval
        self.display_words = display_words
        self.display = display
        self.on_update = on_update

        # Audio buffer (ring buffer for last 10s)
        self.sample_rate = 16000
        self.buffer_size = int(window_size * self.sample_rate)
        self.audio_buffer = np.zeros(self.buffer_size, dtype=np.float32)

        # Latest transcription
        self.latest_text = ""
        self.latest_words = deque(maxlen=display_words)

        # For yielding updates
        self.updates = []

    async def connect_and_send_window(self, audio_window: np.ndarray) -> Optional[str]:
        """Send audio window and get transcription."""
        try:
            # Create temporary client for this request
            import websockets

            async with websockets.connect(self.server_url) as websocket:
                # Wait for handshake
                handshake = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                handshake_data = json.loads(handshake)

                if handshake_data.get("type") != "ready":
                    return None

                # Send audio
                audio_int16 = (audio_window * 32768.0).astype(np.int16)
                await websocket.send(audio_int16.tobytes())

                # Send flush
                await websocket.send(json.dumps({"type": "flush"}))

                # Collect segments
                text_parts = []
                async for message in websocket:
                    data = json.loads(message)
                    if data.get("type") == "segment":
                        text_parts.append(data.get("text", ""))
                    elif data.get("type") == "flushed":
                        break

                return " ".join(text_parts).strip()

        except Exception as e:
            print(f"Error: {e}")
            return None

    def update_buffer(self, new_audio: np.ndarray):
        """Add new audio to ring buffer."""
        # Shift buffer left and add new audio
        shift_amount = len(new_audio)
        self.audio_buffer = np.roll(self.audio_buffer, -shift_amount)
        self.audio_buffer[-shift_amount:] = new_audio

    def update_display(self):
        """Update terminal display with latest words."""
        if self.display == 'silent':
            return

        if not self.latest_words:
            return

        if self.display == 'minimal':
            # Just show the text, updating in place
            words_text = " ".join(self.latest_words)
            print(f"\r{words_text:<100}", end="", flush=True)
        elif self.display == 'full':
            # Show with emoji
            words_text = " ".join(self.latest_words)
            print(f"\r🎤 {words_text:<100}", end="", flush=True)

    async def stream_with_overlap(self, duration: Optional[float] = None):
        """
        Stream audio with overlapping windows.

        Args:
            duration: Total duration to record (None = infinite)

        Yields:
            dict: Update with 'text', 'elapsed', 'is_final'
        """
        microphone = Microphone()  # Create microphone

        if self.display != 'silent':
            print(f"🎤 Real-time Overlapping Transcription")
            print(f"   Window: {self.window_size}s | Update: {self.update_interval}s")
            print(f"   Server: {self.server_url}")
            print(f"   Press Ctrl+C to stop\n")

        start_time = time.time()
        last_update = 0.0

        try:
            while duration is None or (time.time() - start_time) < duration:
                elapsed = time.time() - start_time

                # Record new chunk (suppress output if silent/minimal)
                if self.display == 'silent':
                    # Completely suppress microphone output
                    old_stdout = sys.stdout
                    sys.stdout = io.StringIO()
                    try:
                        chunk = microphone.record(duration=self.update_interval)
                    finally:
                        sys.stdout = old_stdout
                else:
                    chunk = microphone.record(duration=self.update_interval)

                self.update_buffer(chunk.data)

                # Send full window every update_interval
                if elapsed - last_update >= self.update_interval:
                    last_update = elapsed

                    # Send current window for transcription
                    text = await self.connect_and_send_window(self.audio_buffer.copy())

                    if text:
                        self.latest_text = text
                        # Split into words and keep last N
                        words = text.split()
                        self.latest_words.clear()
                        self.latest_words.extend(words[-self.display_words:])

                        # Create update dict
                        update = {
                            'text': text,
                            'latest_words': " ".join(self.latest_words),
                            'elapsed': elapsed,
                            'is_final': False
                        }

                        # Call callback if provided
                        if self.on_update:
                            should_continue = self.on_update(update)
                            if should_continue is False:
                                break

                        # Yield for generator usage
                        yield update

                        # Update display
                        self.update_display()

        except KeyboardInterrupt:
            if self.display != 'silent':
                print("\n\n✓ Stopped")

        finally:
            if self.display != 'silent':
                print("\n")
                if self.latest_text:
                    print("📝 Final transcript:")
                    print(self.latest_text)

            # Yield final result
            if self.latest_text:
                yield {
                    'text': self.latest_text,
                    'latest_words': self.latest_text,
                    'elapsed': time.time() - start_time,
                    'is_final': True
                }

    def run(self, duration: Optional[float] = None):
        """
        Run the streaming client (blocking).

        Returns the final transcript.
        """
        async def _run():
            final_text = None
            async for update in self.stream_with_overlap(duration):
                if update['is_final']:
                    final_text = update['text']
            return final_text

        return asyncio.run(_run())

    def stream(self, duration: Optional[float] = None):
        """
        Stream updates as a generator (for programming).

        Yields:
            dict: Updates with 'text', 'latest_words', 'elapsed', 'is_final'

        Example:
            for update in client.stream(duration=30):
                print(update['latest_words'])
                if "stop" in update['text']:
                    break
        """
        async def _stream():
            async for update in self.stream_with_overlap(duration):
                yield update

        # Run async generator in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            gen = _stream()
            while True:
                try:
                    yield loop.run_until_complete(gen.__anext__())
                except StopAsyncIteration:
                    break
        finally:
            loop.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Real-time overlapping transcription client")
    parser.add_argument(
        "--server",
        type=str,
        default="ws://192.168.2.24:8765",
        help="Server URL"
    )
    parser.add_argument(
        "--window",
        type=float,
        default=10.0,
        help="Window size in seconds (default: 10.0)"
    )
    parser.add_argument(
        "--update",
        type=float,
        default=0.5,
        help="Update interval in seconds (default: 0.5)"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Recording duration (default: infinite)"
    )
    parser.add_argument(
        "--words",
        type=int,
        default=20,
        help="Number of words to display (default: 20)"
    )

    args = parser.parse_args()

    client = RealtimeOverlappingClient(
        server_url=args.server,
        window_size=args.window,
        update_interval=args.update,
        display_words=args.words,
    )

    client.run(duration=args.duration)


if __name__ == "__main__":
    main()
