"""
Real-time Voice Tutor System for ConvAI Innovations
Tracks typing, detects patterns, provides intelligent voice feedback using Qwen + Kokoro TTS
"""

import tkinter as tk
import time
import threading
import re
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import deque

from .models import Language


@dataclass
class TypingStats:
    """Track typing statistics"""
    total_chars: int = 0
    total_time: float = 0.0
    chars_per_minute: float = 0.0
    last_activity: float = 0.0
    typing_speed_history: deque = field(default_factory=lambda: deque(maxlen=10))

    def update_speed(self, chars: int, time_delta: float):
        """Update typing speed"""
        if time_delta > 0:
            cpm = (chars / time_delta) * 60
            self.chars_per_minute = cpm
            self.typing_speed_history.append(cpm)

    def get_average_speed(self) -> float:
        """Get average typing speed"""
        if self.typing_speed_history:
            return sum(self.typing_speed_history) / len(self.typing_speed_history)
        return 0.0


@dataclass
class LineEvent:
    """Represents a line completion event"""
    line_number: int
    line_content: str
    timestamp: float
    was_typed: bool  # Always True (removed paste detection)
    typing_time: float  # Time since last line


class RealTimeTutorSystem:
    """
    Real-time voice tutoring system that:
    1. Tracks typing (not copy-paste)
    2. Detects line completions
    3. Provides intelligent feedback based on context
    4. Adapts to typing speed
    5. Predicts errors and suggests help when stuck
    """

    def __init__(self, code_editor, ai_system, tts_system, language_selector):
        self.code_editor = code_editor
        self.ai_system = ai_system
        self.tts_system = tts_system
        self.language_selector = language_selector

        # State tracking
        self.enabled = False
        self.stats = TypingStats()
        self.previous_content = ""
        self.previous_line_count = 0
        self.current_line = 0
        self.line_start_time = time.time()
        self.last_key_time = time.time()
        self.line_history: List[LineEvent] = []

        # Configuration
        self.feedback_interval = 3  # Lines between feedback (adaptive)
        self.stuck_threshold = 15.0  # Seconds of inactivity = stuck
        self.slow_typing_threshold = 20.0  # CPM below this = slow
        self.fast_typing_threshold = 100.0  # CPM above this = fast

        # Feedback state
        self.lines_since_feedback = 0
        self.feedback_queue = deque(maxlen=5)
        self.is_speaking = False
        self.last_feedback_time = time.time()
        self.stuck_check_active = False

        # Context tracking for intelligent feedback
        self.current_context = {
            'session_id': 'unknown',
            'recent_errors': [],
            'difficulty_level': 'beginner',
            'code_type': 'general'  # function, class, loop, etc.
        }

        # Lock for thread safety
        self.lock = threading.Lock()

    def enable(self, session_id: str = 'unknown'):
        """Enable real-time tutoring"""
        with self.lock:
            if not self.enabled:
                self.enabled = True
                self.current_context['session_id'] = session_id
                self.stats = TypingStats()
                self.previous_content = self.code_editor.get_text()
                self.previous_line_count = len(self.previous_content.split('\n'))
                self.last_key_time = time.time()
                self.line_start_time = time.time()

                # Bind to editor events
                self._bind_events()

                # Start monitoring thread
                self._start_monitoring()

                print("✅ Real-time voice tutor enabled")

    def disable(self):
        """Disable real-time tutoring"""
        with self.lock:
            if self.enabled:
                self.enabled = False
                self.stuck_check_active = False
                self._unbind_events()
                self.tts_system.stop_speech()
                print("🔇 Real-time voice tutor disabled")

    def configure(self, **kwargs):
        """Configure tutor parameters"""
        with self.lock:
            if 'feedback_interval' in kwargs:
                self.feedback_interval = kwargs['feedback_interval']
            if 'stuck_threshold' in kwargs:
                self.stuck_threshold = kwargs['stuck_threshold']
            if 'slow_typing_threshold' in kwargs:
                self.slow_typing_threshold = kwargs['slow_typing_threshold']

    def _bind_events(self):
        """Bind to editor events"""
        # Monitor KeyPress and KeyRelease for typing detection
        self.code_editor.text_widget.bind('<KeyPress>', self._on_key_press, add='+')
        self.code_editor.text_widget.bind('<KeyRelease>', self._on_key_release, add='+')

        # Monitor content changes (including paste)
        self.code_editor.text_widget.bind('<<Modified>>', self._on_content_modified, add='+')

    def _unbind_events(self):
        """Unbind editor events"""
        try:
            self.code_editor.text_widget.unbind('<KeyPress>')
            self.code_editor.text_widget.unbind('<KeyRelease>')
            self.code_editor.text_widget.unbind('<<Modified>>')
        except:
            pass

    def _on_key_press(self, event):
        """Handle key press event"""
        if not self.enabled:
            return

        current_time = time.time()

        with self.lock:
            # Update last activity time
            self.last_key_time = current_time
            self.stats.last_activity = current_time

            # Track typing statistics
            if event.char and len(event.char) == 1:
                self.stats.total_chars += 1

                # Calculate typing speed
                time_delta = current_time - (self.line_start_time if self.line_start_time else current_time - 1)
                if time_delta > 0:
                    self.stats.update_speed(self.stats.total_chars, time_delta)

    def _on_key_release(self, event):
        """Handle key release event"""
        if not self.enabled:
            return

        # Check for Enter key (line completion)
        if event.keysym == 'Return':
            self._on_line_completed()

    def _on_content_modified(self, event):
        """Handle content modification (including paste operations)"""
        if not self.enabled:
            return

        # Reset the modified flag
        self.code_editor.text_widget.edit_modified(False)

        current_content = self.code_editor.get_text()
        current_time = time.time()

        with self.lock:
            # Check if new lines were added (either by typing or pasting)
            current_line_count = len(current_content.split('\n'))

            # If line count increased, treat as line completions
            if current_line_count > self.previous_line_count:
                lines_added = current_line_count - self.previous_line_count

                # Process each new line
                lines = current_content.split('\n')
                for i in range(lines_added):
                    line_index = self.previous_line_count + i - 1
                    if 0 <= line_index < len(lines):
                        line_content = lines[line_index].strip()

                        if line_content:  # Only process non-empty lines
                            # Create line event
                            line_event = LineEvent(
                                line_number=line_index,
                                line_content=line_content,
                                timestamp=current_time,
                                was_typed=True,  # Treat all input as typed
                                typing_time=current_time - self.line_start_time
                            )

                            self.line_history.append(line_event)
                            self.lines_since_feedback += 1

                            # Analyze and provide feedback
                            self._analyze_line_and_give_feedback(line_event)

                self.previous_line_count = current_line_count
                self.line_start_time = current_time

            self.previous_content = current_content

    def _on_line_completed(self):
        """Handle line completion event"""
        if not self.enabled:
            return

        current_time = time.time()

        with self.lock:
            current_content = self.code_editor.get_text()
            lines = current_content.split('\n')
            current_line_count = len(lines)

            # New line was added
            if current_line_count > self.previous_line_count:
                line_number = self.previous_line_count  # 0-indexed

                if line_number < len(lines):
                    line_content = lines[line_number].strip()

                    # Calculate typing time for this line
                    typing_time = current_time - self.line_start_time

                    # Create line event (was typed, not pasted)
                    line_event = LineEvent(
                        line_number=line_number,
                        line_content=line_content,
                        timestamp=current_time,
                        was_typed=True,
                        typing_time=typing_time
                    )

                    self.line_history.append(line_event)
                    self.lines_since_feedback += 1

                    # Analyze and provide feedback
                    self._analyze_line_and_give_feedback(line_event)

                    # Reset line timer
                    self.line_start_time = current_time

            self.previous_line_count = current_line_count


    def _analyze_line_and_give_feedback(self, line_event: LineEvent):
        """Analyze completed line and decide if feedback is needed"""
        if not self.enabled:
            return

        # Skip empty lines
        if not line_event.line_content:
            return

        # Detect code patterns
        self._update_code_context(line_event.line_content)

        # Adaptive feedback interval based on typing speed
        avg_speed = self.stats.get_average_speed()
        if avg_speed < self.slow_typing_threshold:
            # Slow typer = more frequent feedback
            adaptive_interval = 2
        elif avg_speed > self.fast_typing_threshold:
            # Fast typer = less frequent feedback
            adaptive_interval = 5
        else:
            adaptive_interval = self.feedback_interval

        # Check if it's time for feedback
        should_give_feedback = (
            self.lines_since_feedback >= adaptive_interval and
            (time.time() - self.last_feedback_time) > 5.0  # At least 5 sec between feedback
        )

        if should_give_feedback:
            self._generate_and_speak_feedback(line_event)
            self.lines_since_feedback = 0
            self.last_feedback_time = time.time()

    def _update_code_context(self, line_content: str):
        """Update context based on line content"""
        with self.lock:
            # Detect code patterns
            if re.match(r'^\s*def\s+\w+', line_content):
                self.current_context['code_type'] = 'function'
            elif re.match(r'^\s*class\s+\w+', line_content):
                self.current_context['code_type'] = 'class'
            elif re.match(r'^\s*for\s+', line_content) or re.match(r'^\s*while\s+', line_content):
                self.current_context['code_type'] = 'loop'
            elif re.match(r'^\s*if\s+', line_content):
                self.current_context['code_type'] = 'conditional'
            elif 'import' in line_content:
                self.current_context['code_type'] = 'import'

    def _generate_and_speak_feedback(self, line_event: LineEvent):
        """Generate intelligent feedback and speak it"""
        if not self.enabled or not self.ai_system.is_available:
            return

        # Don't interrupt if already speaking
        if self.is_speaking:
            return

        # Generate feedback in background
        threading.Thread(
            target=self._feedback_worker,
            args=(line_event,),
            daemon=True
        ).start()

    def _feedback_worker(self, line_event: LineEvent):
        """Background worker for generating feedback"""
        try:
            self.is_speaking = True

            # Get recent code context (last 3 lines)
            recent_lines = [event.line_content for event in self.line_history[-3:]]
            code_context = '\n'.join(recent_lines)

            # Get current language
            current_language = self.language_selector.get_current_language()

            # Create intelligent prompt for Qwen
            feedback_prompt = self._create_feedback_prompt(line_event, code_context)

            # Generate concise feedback using Qwen
            feedback = self._generate_concise_feedback(feedback_prompt, current_language)

            # Speak the feedback using Kokoro TTS
            if feedback and self.tts_system.is_available:
                self.tts_system.speak(feedback, current_language)
                print(f"🔊 Real-time feedback: {feedback}")

        except Exception as e:
            print(f"❌ Feedback generation error: {e}")
        finally:
            self.is_speaking = False

    def _create_feedback_prompt(self, line_event: LineEvent, code_context: str) -> str:
        """Create intelligent prompt for feedback generation"""
        avg_speed = self.stats.get_average_speed()
        typing_speed_feedback = ""

        if avg_speed < self.slow_typing_threshold:
            typing_speed_feedback = "The student is typing slowly, be encouraging."
        elif avg_speed > self.fast_typing_threshold:
            typing_speed_feedback = "The student is typing fast, acknowledge their pace."

        prompt = f"""You are Sandra, a supportive AI coding tutor providing VERY SHORT real-time voice feedback.

Session: {self.current_context['session_id']}
Code type: {self.current_context['code_type']}
{typing_speed_feedback}

Recent code:
{code_context}

Latest line: {line_event.line_content}

Provide ONE SHORT sentence (5-8 words max) of encouraging feedback. Focus on:
- Acknowledging progress ("Good!", "Nice work!", "Keep going!")
- Mentioning what they just did if significant (e.g., "Good function definition!")
- Brief tips only if there's an obvious issue

Be warm, encouraging, and VERY concise. Voice will speak this."""

        return prompt

    def _generate_concise_feedback(self, prompt: str, language: Language) -> str:
        """Generate concise feedback using Qwen model"""
        try:
            # Prepare messages for chat template
            messages = [{"role": "user", "content": prompt}]

            text = self.ai_system.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False
            )

            model_inputs = self.ai_system.tokenizer([text], return_tensors="pt").to(self.ai_system.model.device)

            # Generate with low temperature for concise, consistent feedback
            generated_ids = self.ai_system.model.generate(
                **model_inputs,
                max_new_tokens=50,  # Very short responses
                temperature=0.3,  # Low temperature for consistency
                do_sample=True,
                pad_token_id=self.ai_system.tokenizer.eos_token_id
            )

            # Decode response
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            feedback = self.ai_system.tokenizer.decode(output_ids, skip_special_tokens=True).strip()

            # Fallback if empty
            if not feedback:
                fallback_messages = [
                    "Great work!",
                    "Keep it up!",
                    "Nice progress!",
                    "You're doing well!",
                    "Good job!"
                ]
                import random
                feedback = random.choice(fallback_messages)

            # Translate if needed
            if language != Language.ENGLISH:
                feedback = self.ai_system.translator.translate(feedback, language)

            return feedback

        except Exception as e:
            print(f"❌ Feedback generation error: {e}")
            return "Keep going!"

    def _start_monitoring(self):
        """Start monitoring thread for stuck detection"""
        self.stuck_check_active = True
        threading.Thread(target=self._stuck_detection_worker, daemon=True).start()

    def _stuck_detection_worker(self):
        """Background worker to detect when user is stuck"""
        while self.stuck_check_active and self.enabled:
            time.sleep(3)  # Check every 3 seconds

            if not self.enabled:
                break

            current_time = time.time()
            time_since_last_activity = current_time - self.last_key_time

            # User seems stuck
            if time_since_last_activity > self.stuck_threshold and not self.is_speaking:
                # Check if there's incomplete code on current line
                current_content = self.code_editor.get_text()
                lines = current_content.split('\n')

                if lines:
                    last_line = lines[-1].strip()

                    # If there's content on the last line and user is stuck
                    if last_line and len(self.line_history) > 0:
                        self._provide_stuck_help(last_line)
                        # Reset timer to avoid repeated prompts
                        self.last_key_time = current_time

    def _provide_stuck_help(self, incomplete_line: str):
        """Provide help when user seems stuck"""
        if not self.ai_system.is_available or self.is_speaking:
            return

        print(f"🤔 User seems stuck on: {incomplete_line}")

        # Generate helpful hint
        threading.Thread(
            target=self._stuck_help_worker,
            args=(incomplete_line,),
            daemon=True
        ).start()

    def _stuck_help_worker(self, incomplete_line: str):
        """Background worker for stuck help"""
        try:
            self.is_speaking = True

            current_language = self.language_selector.get_current_language()

            # Get recent code context
            recent_lines = [event.line_content for event in self.line_history[-3:]]
            code_context = '\n'.join(recent_lines)

            help_prompt = f"""You are Sandra, a supportive coding tutor. The student has been stuck for a while.

Session: {self.current_context['session_id']}

Recent code:
{code_context}

They're stuck on: {incomplete_line}

Provide ONE SHORT helpful hint (8-10 words max) to get them unstuck. Be gentle and encouraging.
Example: "Try adding a colon at the end."
Voice will speak this."""

            # Generate help message
            messages = [{"role": "user", "content": help_prompt}]

            text = self.ai_system.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False
            )

            model_inputs = self.ai_system.tokenizer([text], return_tensors="pt").to(self.ai_system.model.device)

            generated_ids = self.ai_system.model.generate(
                **model_inputs,
                max_new_tokens=60,
                temperature=0.4,
                do_sample=True,
                pad_token_id=self.ai_system.tokenizer.eos_token_id
            )

            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            help_message = self.ai_system.tokenizer.decode(output_ids, skip_special_tokens=True).strip()

            if not help_message:
                help_message = "Need help? Check the reference code or ask a question."

            # Translate if needed
            if current_language != Language.ENGLISH:
                help_message = self.ai_system.translator.translate(help_message, current_language)

            # Speak the help
            if self.tts_system.is_available:
                self.tts_system.speak(help_message, current_language)
                print(f"💡 Stuck help: {help_message}")

        except Exception as e:
            print(f"❌ Stuck help error: {e}")
        finally:
            self.is_speaking = False

    def get_stats(self) -> Dict:
        """Get current statistics"""
        with self.lock:
            return {
                'enabled': self.enabled,
                'total_chars': self.stats.total_chars,
                'typing_speed': self.stats.chars_per_minute,
                'average_speed': self.stats.get_average_speed(),
                'lines_completed': len(self.line_history),
                'lines_since_feedback': self.lines_since_feedback,
                'is_speaking': self.is_speaking,
                'session_id': self.current_context['session_id']
            }
