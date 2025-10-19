"""
Line-by-Line Code Narrator for ConvAI Innovations
Reads reference code line by line as the user types, providing audio guidance
"""

import time
import threading
from typing import Optional, List, Callable
from dataclasses import dataclass

from .models import Language


@dataclass
class CodeLine:
    """Represents a line of code to narrate"""
    line_number: int
    content: str
    is_narrated: bool = False
    timestamp: Optional[float] = None


class CodeNarratorSystem:
    """
    Line-by-line code narrator that:
    1. Reads reference code line by line
    2. Speaks each line when user completes the previous line
    3. Adapts to user's typing speed
    4. Provides encouragement between lines
    """

    def __init__(self, code_editor, tts_system, language_selector):
        self.code_editor = code_editor
        self.tts_system = tts_system
        self.language_selector = language_selector

        # State
        self.enabled = False
        self.reference_lines: List[CodeLine] = []
        self.current_line_index = 0
        self.user_current_line = 0
        self.is_speaking = False

        # Configuration
        self.auto_start = True  # Automatically speak first line when enabled
        self.encouragement_enabled = True  # Add encouragement between lines
        self.speak_line_numbers = False  # Whether to say "Line 1, ..."

        # Tracking
        self.lines_completed = 0
        self.session_start_time = None
        self.last_line_time = None

        # Lock for thread safety
        self.lock = threading.Lock()

        # Encouragement phrases
        self.encouragement_phrases = [
            "Good job!",
            "Keep going!",
            "Great work!",
            "You're doing well!",
            "Nice progress!",
            "Excellent!",
            "Well done!"
        ]
        self.encouragement_index = 0

    def load_reference_code(self, reference_code: str):
        """Load reference code and prepare for narration"""
        with self.lock:
            self.reference_lines = []
            self.current_line_index = 0
            self.user_current_line = 0
            self.lines_completed = 0

            # Split into lines and create CodeLine objects
            lines = reference_code.split('\n')
            for i, line in enumerate(lines):
                # Skip empty lines or comment-only lines for narration
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    self.reference_lines.append(
                        CodeLine(
                            line_number=i,
                            content=line,
                            is_narrated=False
                        )
                    )

            print(f"📖 Code narrator loaded {len(self.reference_lines)} lines to narrate")

    def enable(self, reference_code: str):
        """Enable the narrator with reference code"""
        with self.lock:
            if not self.reference_lines or reference_code:
                self.load_reference_code(reference_code)

            self.enabled = True
            self.session_start_time = time.time()
            self.last_line_time = time.time()

            # Bind to editor events
            self._bind_events()

            print("✅ Code narrator enabled")

            # Speak first line automatically
            if self.auto_start and self.reference_lines:
                threading.Thread(
                    target=self._speak_next_line,
                    daemon=True
                ).start()

    def disable(self):
        """Disable the narrator"""
        with self.lock:
            if self.enabled:
                self.enabled = False
                self._unbind_events()
                self.tts_system.stop_speech()
                print("🔇 Code narrator disabled")

    def configure(self, **kwargs):
        """Configure narrator settings"""
        with self.lock:
            if 'auto_start' in kwargs:
                self.auto_start = kwargs['auto_start']
            if 'encouragement_enabled' in kwargs:
                self.encouragement_enabled = kwargs['encouragement_enabled']
            if 'speak_line_numbers' in kwargs:
                self.speak_line_numbers = kwargs['speak_line_numbers']

    def _bind_events(self):
        """Bind to editor events"""
        self.code_editor.text_widget.bind('<KeyRelease>', self._on_key_release, add='+')
        self.code_editor.text_widget.bind('<<Modified>>', self._on_content_modified, add='+')

    def _unbind_events(self):
        """Unbind editor events"""
        try:
            self.code_editor.text_widget.unbind('<KeyRelease>')
            self.code_editor.text_widget.unbind('<<Modified>>')
        except:
            pass

    def _on_key_release(self, event):
        """Handle key release - detect Enter key"""
        if not self.enabled:
            return

        # Check for Enter key (line completion)
        if event.keysym == 'Return':
            self._on_user_line_completed()

    def _on_content_modified(self, event):
        """Handle content modification - detect paste operations"""
        if not self.enabled:
            return

        # Reset modified flag
        self.code_editor.text_widget.edit_modified(False)

        # Check if user added new lines (paste)
        current_content = self.code_editor.get_text()
        current_line_count = len(current_content.split('\n'))

        with self.lock:
            if current_line_count > self.user_current_line:
                # User added lines (possibly by pasting)
                lines_added = current_line_count - self.user_current_line
                self.user_current_line = current_line_count

                # Speak next line for each completed line
                for _ in range(lines_added):
                    if not self.is_speaking:
                        threading.Thread(
                            target=self._speak_next_line,
                            daemon=True
                        ).start()
                        time.sleep(0.5)  # Small delay between lines

    def _on_user_line_completed(self):
        """Handle user completing a line"""
        if not self.enabled:
            return

        current_time = time.time()

        with self.lock:
            self.user_current_line += 1
            self.lines_completed += 1
            self.last_line_time = current_time

            print(f"📝 User completed line {self.user_current_line}")

        # Speak next line
        if not self.is_speaking:
            threading.Thread(
                target=self._speak_next_line,
                daemon=True
            ).start()

    def _speak_next_line(self):
        """Speak the next line of reference code"""
        if not self.enabled or self.is_speaking:
            return

        with self.lock:
            # Check if there are more lines to narrate
            if self.current_line_index >= len(self.reference_lines):
                # All lines completed!
                self._speak_completion_message()
                return

            # Get next line to narrate
            code_line = self.reference_lines[self.current_line_index]
            self.is_speaking = True

        try:
            # Prepare the narration text
            narration = self._prepare_narration(code_line)

            # Get current language
            current_language = self.language_selector.get_current_language()

            # Speak the line
            if self.tts_system.is_available:
                print(f"🔊 Narrating line {code_line.line_number + 1}: {code_line.content[:50]}...")
                self.tts_system.speak(narration, current_language)

                # Mark as narrated
                with self.lock:
                    code_line.is_narrated = True
                    code_line.timestamp = time.time()
                    self.current_line_index += 1

                # Add small delay before allowing next narration
                time.sleep(1)

        except Exception as e:
            print(f"❌ Narration error: {e}")
        finally:
            self.is_speaking = False

    def _prepare_narration(self, code_line: CodeLine) -> str:
        """Prepare narration text for a code line"""
        content = code_line.content.strip()

        # Add line number if enabled
        if self.speak_line_numbers:
            narration = f"Line {code_line.line_number + 1}. "
        else:
            narration = ""

        # Add encouragement every few lines
        if self.encouragement_enabled and self.lines_completed > 0 and self.lines_completed % 5 == 0:
            encouragement = self.encouragement_phrases[self.encouragement_index]
            self.encouragement_index = (self.encouragement_index + 1) % len(self.encouragement_phrases)
            narration = f"{encouragement} " + narration

        # Process the code line for better speech
        processed_content = self._process_code_for_speech(content)
        narration += processed_content

        return narration

    def _process_code_for_speech(self, code: str) -> str:
        """Process code to make it more natural for speech"""
        # Replace common symbols with words
        replacements = {
            '=': ' equals ',
            '==': ' double equals ',
            '!=': ' not equals ',
            '<=': ' less than or equal to ',
            '>=': ' greater than or equal to ',
            '<': ' less than ',
            '>': ' greater than ',
            '+': ' plus ',
            '-': ' minus ',
            '*': ' times ',
            '/': ' divided by ',
            '//': ' integer divided by ',
            '%': ' modulo ',
            '**': ' to the power of ',
            '+=': ' plus equals ',
            '-=': ' minus equals ',
            '(': ' open parenthesis ',
            ')': ' close parenthesis ',
            '[': ' open bracket ',
            ']': ' close bracket ',
            '{': ' open brace ',
            '}': ' close brace ',
            ':': ' colon ',
            ',': ' comma ',
            '.': ' dot ',
            '#': ' comment ',
            '->': ' arrow ',
            '=>': ' arrow ',
        }

        # Special handling for common patterns
        if code.strip().startswith('def '):
            code = code.replace('def ', 'define function ', 1)
        elif code.strip().startswith('class '):
            code = code.replace('class ', 'define class ', 1)
        elif code.strip().startswith('import '):
            code = code.replace('import ', 'import module ', 1)
        elif code.strip().startswith('from '):
            code = code.replace('from ', 'from module ', 1)
        elif code.strip().startswith('return '):
            code = code.replace('return ', 'return value ', 1)
        elif code.strip().startswith('if '):
            code = code.replace('if ', 'if condition ', 1)
        elif code.strip().startswith('elif '):
            code = code.replace('elif ', 'else if condition ', 1)
        elif code.strip().startswith('else:'):
            code = code.replace('else:', 'else', 1)
        elif code.strip().startswith('for '):
            code = code.replace('for ', 'for loop ', 1)
        elif code.strip().startswith('while '):
            code = code.replace('while ', 'while loop ', 1)

        # Apply symbol replacements (order matters for multi-char symbols)
        for symbol, word in sorted(replacements.items(), key=lambda x: -len(x[0])):
            code = code.replace(symbol, word)

        return code

    def _speak_completion_message(self):
        """Speak completion message when all lines are done"""
        if not self.tts_system.is_available:
            return

        self.is_speaking = True
        try:
            current_language = self.language_selector.get_current_language()

            completion_messages = {
                Language.ENGLISH: "Excellent work! You've completed all the lines. Now try running your code!",
                Language.SPANISH: "¡Excelente trabajo! Has completado todas las líneas. ¡Ahora intenta ejecutar tu código!",
                Language.FRENCH: "Excellent travail! Vous avez terminé toutes les lignes. Essayez maintenant d'exécuter votre code!",
                Language.HINDI: "उत्कृष्ट काम! आपने सभी पंक्तियाँ पूरी कर ली हैं। अब अपना कोड चलाने का प्रयास करें!",
                Language.ITALIAN: "Ottimo lavoro! Hai completato tutte le righe. Ora prova a eseguire il tuo codice!",
                Language.PORTUGUESE: "Excelente trabalho! Você completou todas as linhas. Agora tente executar seu código!"
            }

            message = completion_messages.get(current_language, completion_messages[Language.ENGLISH])
            self.tts_system.speak(message, current_language)

            print("🎉 All lines completed!")

        except Exception as e:
            print(f"❌ Completion message error: {e}")
        finally:
            self.is_speaking = False

    def speak_current_line(self):
        """Manually speak the current line (repeat)"""
        if not self.enabled:
            return

        with self.lock:
            if self.current_line_index > 0:
                # Speak the last narrated line again
                line_index = self.current_line_index - 1
                if 0 <= line_index < len(self.reference_lines):
                    code_line = self.reference_lines[line_index]

                    threading.Thread(
                        target=self._speak_line_directly,
                        args=(code_line,),
                        daemon=True
                    ).start()

    def _speak_line_directly(self, code_line: CodeLine):
        """Directly speak a specific line (for repeat functionality)"""
        if self.is_speaking:
            return

        self.is_speaking = True
        try:
            narration = f"Repeating: {self._process_code_for_speech(code_line.content.strip())}"
            current_language = self.language_selector.get_current_language()

            if self.tts_system.is_available:
                self.tts_system.speak(narration, current_language)

        except Exception as e:
            print(f"❌ Repeat narration error: {e}")
        finally:
            self.is_speaking = False

    def skip_to_line(self, line_number: int):
        """Skip to a specific line number"""
        with self.lock:
            if 0 <= line_number < len(self.reference_lines):
                self.current_line_index = line_number
                print(f"⏭️ Skipped to line {line_number + 1}")

                # Speak the new current line
                threading.Thread(
                    target=self._speak_next_line,
                    daemon=True
                ).start()

    def reset(self):
        """Reset narrator to beginning"""
        with self.lock:
            self.current_line_index = 0
            self.user_current_line = 0
            self.lines_completed = 0
            self.session_start_time = time.time()
            self.last_line_time = time.time()

            # Reset narrated flags
            for line in self.reference_lines:
                line.is_narrated = False
                line.timestamp = None

            print("🔄 Narrator reset to beginning")

    def get_progress(self) -> dict:
        """Get current progress statistics"""
        with self.lock:
            total_lines = len(self.reference_lines)
            completed_lines = self.current_line_index
            progress_pct = (completed_lines / total_lines * 100) if total_lines > 0 else 0

            return {
                'enabled': self.enabled,
                'total_lines': total_lines,
                'completed_lines': completed_lines,
                'current_line': self.current_line_index + 1 if self.current_line_index < total_lines else total_lines,
                'progress_percentage': progress_pct,
                'is_speaking': self.is_speaking,
                'lines_completed_by_user': self.lines_completed
            }
