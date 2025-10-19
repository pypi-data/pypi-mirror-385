"""
AI Tutor Narrator for ConvAI Innovations
Human-like voice tutor that guides users through typing code line by line
"""

import time
import threading
import random
import re
from typing import Optional, List
from dataclasses import dataclass

from .models import Language


@dataclass
class NarrationSegment:
    """Represents a segment of the narration"""
    segment_type: str  # 'introduction', 'line_instruction', 'encouragement', 'completion'
    content: str
    line_number: Optional[int] = None
    timestamp: Optional[float] = None


class AITutorNarrator:
    """
    Human-like AI tutor that:
    1. Introduces the lesson
    2. Instructs user to type each line
    3. Provides encouragement after each line
    4. Celebrates completion
    """

    def __init__(self, code_editor, ai_system, tts_system, language_selector):
        self.code_editor = code_editor
        self.ai_system = ai_system
        self.tts_system = tts_system
        self.language_selector = language_selector

        # State
        self.enabled = False
        self.is_narrating = False
        self.current_line_index = 0
        self.reference_code = ""
        self.reference_lines: List[str] = []
        self.session_title = ""
        self.session_description = ""

        # User progress tracking
        self.user_current_line = 0
        self.last_user_content = ""

        # Inactivity tracking
        self.last_activity_time = time.time()
        self.inactivity_timeout = 20  # seconds (configurable)
        self.inactivity_thread = None
        self.last_joke_time = 0

        # Threading
        self.lock = threading.Lock()
        self.narration_thread = None

        # Event binding
        self.bound_events = []

    def start_narration(self, session_title: str, session_description: str, reference_code: str):
        """Start the AI tutor narration for a session"""
        with self.lock:
            if self.is_narrating:
                print("⚠️ Narration already in progress")
                return

            self.enabled = True
            self.is_narrating = True
            self.current_line_index = 0
            self.user_current_line = 0
            self.session_title = session_title
            self.session_description = session_description
            self.reference_code = reference_code
            self.last_user_content = ""

            # Parse reference code into lines (skip empty lines and full-line comments)
            self.reference_lines = []
            for line in reference_code.split('\n'):
                stripped = line.strip()
                # Skip empty lines
                if not stripped:
                    continue
                # Skip full comment lines (lines that ONLY have comments)
                if stripped.startswith('#'):
                    continue
                # Keep lines with code (even if they have inline comments)
                self.reference_lines.append(line)

            print(f"🎙️ Starting AI tutor narration for: {session_title}")
            print(f"📝 {len(self.reference_lines)} lines to teach")

        # Bind to editor events to detect line completion
        self._bind_events()

        # Start narration in background thread
        self.narration_thread = threading.Thread(
            target=self._run_narration_sequence,
            daemon=True
        )
        self.narration_thread.start()

        # Start inactivity monitoring thread
        self.last_activity_time = time.time()
        self.inactivity_thread = threading.Thread(
            target=self._monitor_inactivity,
            daemon=True
        )
        self.inactivity_thread.start()
        print("✅ Started inactivity monitoring thread")

    def stop_narration(self):
        """Stop the narration"""
        with self.lock:
            if self.enabled:
                self.enabled = False
                self.is_narrating = False
                self._unbind_events()
                self.tts_system.stop_speech()
                print("🔇 AI tutor narration stopped")

    def _bind_events(self):
        """Bind to editor events to detect user typing"""
        try:
            # Bind to multiple events to catch line completion
            # Enter key release
            binding_id1 = self.code_editor.text_widget.bind(
                '<KeyRelease-Return>',
                self._on_line_completed,
                add='+'
            )
            self.bound_events.append(('<KeyRelease-Return>', binding_id1))

            # Also bind to Return key press as backup
            binding_id2 = self.code_editor.text_widget.bind(
                '<Return>',
                self._on_line_completed,
                add='+'
            )
            self.bound_events.append(('<Return>', binding_id2))

            print(f"✅ Event bindings created for line completion detection")
        except Exception as e:
            print(f"⚠️ Error binding events: {e}")

    def _unbind_events(self):
        """Unbind editor events"""
        try:
            for event_type, binding_id in self.bound_events:
                self.code_editor.text_widget.unbind(event_type, binding_id)
            self.bound_events.clear()
        except Exception as e:
            print(f"⚠️ Error unbinding events: {e}")

    def _on_line_completed(self, event):
        """Handle when user completes a line (presses Enter)"""
        print(f"🔑 Enter key detected! Checking line completion...")

        # Reset inactivity timer
        self.last_activity_time = time.time()

        if not self.enabled or not self.is_narrating:
            print(f"⚠️ Narration not active (enabled={self.enabled}, narrating={self.is_narrating})")
            return

        current_content = self.code_editor.get_text()
        print(f"📝 Current editor content: {repr(current_content[:100])}")

        with self.lock:
            # Get all non-empty lines (lines with actual code)
            user_lines = [l for l in current_content.split('\n') if l.strip()]
            new_line_count = len(user_lines)

            print(f"📊 Line count: {new_line_count} (previous: {self.user_current_line})")

            # User completed a new line
            if new_line_count > self.user_current_line:
                # Get the line that was just typed
                typed_line = user_lines[self.user_current_line] if self.user_current_line < len(user_lines) else ""
                expected_line = self.reference_lines[self.user_current_line] if self.user_current_line < len(self.reference_lines) else ""

                print(f"📝 Typed: '{typed_line}'")
                print(f"📋 Expected: '{expected_line}'")

                # Check if the line is correct
                if self._check_line_match(typed_line, expected_line):
                    # Correct! Move to next line
                    self.user_current_line = new_line_count
                    print(f"✅ User completed line {self.user_current_line} correctly! Providing encouragement...")

                    # Trigger next instruction in background
                    threading.Thread(
                        target=self._provide_encouragement_and_next_instruction,
                        daemon=True
                    ).start()
                else:
                    # Mistake detected - provide correction
                    print(f"❌ Mistake detected in line {self.user_current_line + 1}")
                    threading.Thread(
                        target=lambda: self._narrate_correction(typed_line, expected_line),
                        daemon=True
                    ).start()
            else:
                print(f"⏸️ No new line detected (user may have pressed Enter on empty line)")

    def _check_line_match(self, typed_line: str, expected_line: str) -> bool:
        """Check if typed line matches expected line (with some flexibility)"""
        # Remove inline comments from both for comparison
        typed_clean = typed_line.split('#')[0].rstrip()  # Keep leading whitespace (indentation)
        expected_clean = expected_line.split('#')[0].rstrip()  # Keep leading whitespace (indentation)

        # Get indentation (leading whitespace)
        typed_indent = len(typed_clean) - len(typed_clean.lstrip())
        expected_indent = len(expected_clean) - len(expected_clean.lstrip())

        # Check if indentation matches (CRITICAL for Python!)
        if typed_indent != expected_indent:
            print(f"❌ Indentation mismatch: typed has {typed_indent} spaces, expected {expected_indent} spaces")
            return False

        # Remove leading whitespace for content comparison
        typed_content = typed_clean.lstrip()
        expected_content = expected_clean.lstrip()

        # Normalize internal whitespace (allow flexible spacing: x=5 vs x = 5)
        # First collapse multiple spaces
        typed_normalized = re.sub(r'\s+', ' ', typed_content)
        expected_normalized = re.sub(r'\s+', ' ', expected_content)

        # Remove all spaces to compare just the code structure
        typed_no_spaces = typed_normalized.replace(' ', '')
        expected_no_spaces = expected_normalized.replace(' ', '')

        # Debug output
        print(f"🔍 Comparison:")
        print(f"   Indentation: {typed_indent} spaces (expected: {expected_indent})")
        print(f"   Typed (no spaces):    '{typed_no_spaces}'")
        print(f"   Expected (no spaces): '{expected_no_spaces}'")
        print(f"   Match: {typed_no_spaces == expected_no_spaces}")

        # Check if they match (ignoring all internal whitespace)
        return typed_no_spaces == expected_no_spaces

    def _narrate_correction(self, typed_line: str, expected_line: str):
        """Narrate correction for incorrect line"""
        if not self.enabled or not self.is_narrating:
            return

        print(f"🔊 Narrating correction...")

        # Detect silly/irrelevant inputs
        silly_words = ['boring', 'help', 'what', 'huh', 'idk', 'dunno', 'skip',
                       'next', 'stupid', 'hard', 'difficult', 'tired', 'sleepy',
                       'lol', 'lmao', 'haha', 'wtf', 'omg', 'bruh']

        typed_lower = typed_line.lower().strip()
        is_silly = any(word in typed_lower for word in silly_words)

        if is_silly or len(typed_lower) < 3:
            # User typed something silly or very short - respond with humor
            correction = self._get_silly_response()
        else:
            # Regular correction
            correction = f"That's not quite right. The correct line is: {self._code_to_speech(expected_line)}. Please fix it and try again."

        # Speak the correction
        current_language = self.language_selector.get_current_language()
        self.tts_system.speak(correction, current_language)

        print(f"📢 Correction: {correction}")

        # Wait for TTS to finish
        self._wait_for_tts()

    def _get_silly_response(self) -> str:
        """Get a funny response for silly inputs"""
        responses = [
            "Nice try, but that's not Python! Let's focus and type the actual code!",
            "Haha, that's creative! But I need real code here. Come on, you got this!",
            "I appreciate the humor, but the computer won't understand that. Let's code!",
            "That's not in the Python manual! Type the actual line and let's keep going!",
            "LOL! But seriously, let's get back to coding. You can do it!",
            "I see what you did there, but Python expects actual code. Let's try again!",
            "Ha! Good one! Now let's type the real code, shall we?",
            "That's funny, but the interpreter won't laugh. Let's code for real!",
            "Nice creativity! But I need you to type the actual code. Focus!",
            "I like your spirit, but let's channel that energy into real coding!"
        ]
        return random.choice(responses)

    def _get_inactivity_joke(self) -> str:
        """Get an encouraging joke for inactivity"""
        jokes = [
            "Still there? Don't worry, take your time! But maybe wake up your keyboard?",
            "Did you fall asleep? Come on, let's keep coding! You're doing great!",
            "Hey! The code won't write itself! Let's get back to it!",
            "Taking a coffee break? That's fine, but let's finish this line first!",
            "I'm still here waiting! Let's continue - you're so close!",
            "No rush, but your code is getting lonely! Let's type that line!",
            "Are you thinking really hard, or just staring at the screen? Either way, let's code!",
            "Hello? Is anyone there? Come on, we can do this together!",
            "The computer is waiting patiently, but I'm getting impatient! Let's go!",
            "Don't give up now! You've got this - just type the next line!"
        ]
        return random.choice(jokes)

    def _monitor_inactivity(self):
        """Monitor for user inactivity and provide encouragement"""
        print("👀 Inactivity monitoring started")

        while True:
            time.sleep(2)  # Check every 2 seconds

            if not self.enabled or not self.is_narrating:
                print("🛑 Inactivity monitoring stopped")
                break

            # Check if user has been inactive
            inactive_time = time.time() - self.last_activity_time

            # Only trigger if enough time passed since last joke
            time_since_last_joke = time.time() - self.last_joke_time

            if inactive_time >= self.inactivity_timeout and time_since_last_joke >= self.inactivity_timeout:
                print(f"😴 User inactive for {inactive_time:.1f} seconds - sending encouragement")

                # Get a joke/encouragement
                joke = self._get_inactivity_joke()

                # Speak it
                current_language = self.language_selector.get_current_language()
                self.tts_system.speak(joke, current_language)

                print(f"📢 Inactivity joke: {joke}")

                # Update last joke time
                self.last_joke_time = time.time()

                # Wait for TTS
                self._wait_for_tts()

    def _run_narration_sequence(self):
        """Run the complete narration sequence"""
        try:
            # Step 1: Introduction (speaks and waits to finish)
            self._narrate_introduction()

            # Step 2: First line instruction (speaks after intro completes)
            if self.reference_lines:
                self._narrate_line_instruction(0)

        except Exception as e:
            print(f"❌ Narration sequence error: {e}")
            self.is_narrating = False

    def _provide_encouragement_and_next_instruction(self):
        """Provide encouragement and next line instruction"""
        if not self.enabled or not self.is_narrating:
            return

        with self.lock:
            current_line = self.user_current_line

            # Check if there are more lines to teach
            if current_line >= len(self.reference_lines):
                # All lines completed!
                threading.Thread(
                    target=self._narrate_completion,
                    daemon=True
                ).start()
                return

        # Generate encouragement (waits to finish)
        self._narrate_encouragement(current_line - 1)

        # Narrate next line instruction (speaks after encouragement completes)
        self._narrate_line_instruction(current_line)

    def _narrate_introduction(self):
        """Narrate the lesson introduction"""
        print(f"🎙️ Narrating introduction for {self.session_title}")

        # Use instant template (no AI generation - zero delay!)
        introduction = f"Welcome to {self.session_title}! I'll guide you line by line. Let's start coding together!"

        # Speak the introduction
        current_language = self.language_selector.get_current_language()
        self.tts_system.speak(introduction, current_language)

        print(f"📢 Introduction: {introduction}")

        # Wait for TTS to finish speaking
        self._wait_for_tts()

    def _narrate_line_instruction(self, line_index: int):
        """Narrate instruction for typing a specific line"""
        if line_index >= len(self.reference_lines):
            return

        line_content = self.reference_lines[line_index]
        line_number = line_index + 1

        print(f"🎙️ Narrating instruction for line {line_number}")

        # Use instant template (no AI - just speak the code!)
        # Convert code to speakable format
        speakable_code = self._code_to_speech(line_content)

        if line_number == 1:
            instruction = f"Now type: {speakable_code}"
        elif line_number == len(self.reference_lines):
            instruction = f"Last line! Type: {speakable_code}"
        else:
            instruction = f"Next, type: {speakable_code}"

        # Speak the instruction
        current_language = self.language_selector.get_current_language()
        self.tts_system.speak(instruction, current_language)

        print(f"📢 Instruction: {instruction}")

        # Wait for TTS to finish
        self._wait_for_tts()

    def _code_to_speech(self, code: str) -> str:
        """Convert code to speakable format"""
        # Remove inline comments first (anything after #)
        if '#' in code:
            code = code.split('#')[0]

        # Remove extra whitespace
        code = code.strip()

        # Simple replacements for common symbols
        speech = code.replace('=', ' equals ')
        speech = speech.replace('+', ' plus ')
        speech = speech.replace('-', ' minus ')
        speech = speech.replace('*', ' times ')
        speech = speech.replace('/', ' divided by ')
        speech = speech.replace('(', ' open parenthesis ')
        speech = speech.replace(')', ' close parenthesis ')
        speech = speech.replace('[', ' open bracket ')
        speech = speech.replace(']', ' close bracket ')
        speech = speech.replace('{', ' open brace ')
        speech = speech.replace('}', ' close brace ')
        speech = speech.replace(':', ' colon ')
        speech = speech.replace(',', ' comma ')
        speech = speech.replace('"', ' quote ')
        speech = speech.replace("'", ' quote ')
        return speech.strip()

    def _narrate_encouragement(self, completed_line_index: int):
        """Narrate encouragement after completing a line"""
        if completed_line_index < 0 or completed_line_index >= len(self.reference_lines):
            return

        completed_line = self.reference_lines[completed_line_index]
        progress_pct = ((completed_line_index + 1) / len(self.reference_lines)) * 100

        print(f"🎙️ Narrating encouragement after line {completed_line_index + 1}")

        # Use instant templates (no AI - instant response!)
        encouragements = [
            "Great job!",
            "Excellent!",
            "Perfect!",
            "Nice work!",
            "Well done!",
            "Awesome!",
            "You got it!",
            "Keep going!",
            "Fantastic!",
            "Good!",
        ]

        encouragement = random.choice(encouragements)

        # Speak the encouragement
        current_language = self.language_selector.get_current_language()
        self.tts_system.speak(encouragement, current_language)

        print(f"📢 Encouragement: {encouragement}")

        # Wait for TTS to finish
        self._wait_for_tts()

    def _narrate_completion(self):
        """Narrate completion message when all lines are done"""
        print(f"🎙️ Narrating completion message")

        # Use instant template (no AI - instant!)
        completion = f"Amazing work! You've completed all {len(self.reference_lines)} lines! Now click Run Code to see your program in action!"

        # Speak the completion
        current_language = self.language_selector.get_current_language()
        self.tts_system.speak(completion, current_language)

        print(f"📢 Completion: {completion}")
        print(f"🎉 Lesson complete! User finished all {len(self.reference_lines)} lines!")

        # Wait for TTS to finish
        self._wait_for_tts()

        # Mark narration as complete
        with self.lock:
            self.is_narrating = False

    def _wait_for_tts(self, timeout: int = 30):
        """Wait for TTS to finish speaking"""
        start_time = time.time()
        while self.tts_system.is_speaking:
            if time.time() - start_time > timeout:
                print("⚠️ TTS wait timeout")
                break
            time.sleep(0.1)  # Check every 100ms

    def _generate_ai_text(self, prompt: str, max_length: int = 100) -> str:
        """Generate text using Qwen AI model"""
        try:
            if not self.ai_system.is_available:
                return "Great! Keep going!"  # Fallback

            # Generate with Qwen (fast settings)
            response = self.ai_system.generate_text(
                prompt=prompt,
                max_length=max_length,
                temperature=0.5,  # Lower for faster, more direct generation
                system_prompt="You are Sandra, a coding tutor. Be brief and clear."
            )

            # Clean up the response
            response = response.strip()

            # Remove quotes if AI wrapped the response
            if response.startswith('"') and response.endswith('"'):
                response = response[1:-1]
            if response.startswith("'") and response.endswith("'"):
                response = response[1:-1]

            return response

        except Exception as e:
            print(f"❌ AI generation error: {e}")
            return "Great job! Keep typing!"  # Fallback

    def repeat_current_line(self):
        """Repeat the current line instruction"""
        if not self.enabled or not self.is_narrating:
            print("⚠️ Narration not active - cannot repeat")
            return

        with self.lock:
            # Get the line we're currently waiting for user to type
            line_to_repeat = self.user_current_line

        if line_to_repeat < len(self.reference_lines):
            print(f"🔄 Repeating line {line_to_repeat + 1}")

            line_content = self.reference_lines[line_to_repeat]
            speakable_code = self._code_to_speech(line_content)

            repeat_instruction = f"Let me repeat: {speakable_code}"

            current_language = self.language_selector.get_current_language()
            self.tts_system.speak(repeat_instruction, current_language)

            print(f"📢 Repeated: {repeat_instruction}")
        else:
            print("⚠️ No current line to repeat")

    def get_status(self) -> dict:
        """Get current narration status"""
        with self.lock:
            return {
                'enabled': self.enabled,
                'is_narrating': self.is_narrating,
                'current_line': self.current_line_index + 1 if self.current_line_index < len(self.reference_lines) else len(self.reference_lines),
                'total_lines': len(self.reference_lines),
                'user_completed_lines': self.user_current_line,
                'progress_percentage': (self.user_current_line / len(self.reference_lines) * 100) if self.reference_lines else 0,
                'session_title': self.session_title
            }

    def set_inactivity_timeout(self, timeout: int):
        """Set the inactivity timeout in seconds"""
        with self.lock:
            self.inactivity_timeout = max(5, min(60, timeout))  # Clamp between 5-60 seconds
            print(f"⏱️ Inactivity timeout set to {self.inactivity_timeout} seconds")
