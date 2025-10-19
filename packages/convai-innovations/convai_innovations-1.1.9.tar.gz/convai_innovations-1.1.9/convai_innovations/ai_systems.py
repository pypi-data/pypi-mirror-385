"""
AI systems for ConvAI Innovations platform with Argostranslate (2025 Enhanced).
Offline neural translation with intelligent caching and optimized performance.
"""

import threading
import time
import concurrent.futures
import re
import os
from typing import Optional, Dict, List
from pathlib import Path
from functools import lru_cache
import json
import hashlib

from .models import Language, CodeGenRequest, CodeGenResponse

# Dependency checks
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from kokoro.pipeline import KPipeline
    import torch
    import sounddevice as sd
    KOKORO_TTS_AVAILABLE = True
except ImportError:
    KOKORO_TTS_AVAILABLE = False

# ARGOSTRANSLATE - 2025 Enhanced Version
try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_TRANSLATE_AVAILABLE = True
    print("[OK] Argostranslate available - Offline neural translation ready!")
except ImportError:
    ARGOS_TRANSLATE_AVAILABLE = False
    print("[!] Argostranslate not available. Install with: pip install argostranslate")

# Language code mappings for Argostranslate (ISO 639-1)
ARGOS_LANGUAGE_MAPPING = {
    Language.ENGLISH: "en",
    Language.SPANISH: "es", 
    Language.FRENCH: "fr",
    Language.HINDI: "hi",
    Language.ITALIAN: "it",
    Language.PORTUGUESE: "pt"
}

# Enhanced fallback translations (2025 optimized)
ENHANCED_FALLBACK_TRANSLATIONS = {
    Language.SPANISH: {
        "AI mentor is currently unavailable.": "El mentor de IA no está disponible actualmente.",
        "Could not generate AI feedback at this time.": "No se pudo generar retroalimentación de IA en este momento.",
        "Welcome! Start by typing the reference code on the left to practice. Sandra is here to help!": "¡Bienvenido! Comience escribiendo el código de referencia de la izquierda para practicar. ¡Sandra está aquí para ayudar!",
        "Excellent! Keep exploring!": "¡Excelente! ¡Sigue explorando!",
        "Check the error carefully and try again.": "Revisa el error cuidadosamente e inténtalo de nuevo.",
        "Great job! Keep up the great work!": "¡Excelente trabajo! ¡Sigue así!",
        "Welcome to the new session! Try typing the reference code to learn.": "¡Bienvenido a la nueva sesión! Intenta escribir el código de referencia para aprender.",
        "Hello! I'm Sandra, your AI mentor.": "¡Hola! Soy Sandra, tu mentora de IA."
    },
    Language.FRENCH: {
        "AI mentor is currently unavailable.": "Le mentor IA n'est actuellement pas disponible.",
        "Could not generate AI feedback at this time.": "Impossible de générer des commentaires IA pour le moment.",
        "Welcome! Start by typing the reference code on the left to practice. Sandra is here to help!": "Bienvenue ! Commencez par taper le code de référence à gauche pour vous entraîner. Sandra est là pour vous aider !",
        "Excellent! Keep exploring!": "Excellent ! Continuez à explorer !",
        "Check the error carefully and try again.": "Vérifiez l'erreur attentivement et réessayez.",
        "Great job! Keep up the great work!": "Excellent travail ! Continuez comme ça !",
        "Welcome to the new session! Try typing the reference code to learn.": "Bienvenue dans la nouvelle session ! Essayez de taper le code de référence pour apprendre.",
        "Hello! I'm Sandra, your AI mentor.": "Bonjour ! Je suis Sandra, votre mentor IA."
    },
    Language.HINDI: {
        "AI mentor is currently unavailable.": "AI मेंटर वर्तमान में उपलब्ध नहीं है।",
        "Could not generate AI feedback at this time.": "इस समय AI फीडबैक जेनरेट नहीं कर सका।",
        "Welcome! Start by typing the reference code on the left to practice. Sandra is here to help!": "स्वागत! अभ्यास के लिए बाईं ओर का संदर्भ कोड टाइप करना शुरू करें। सैंड्रा यहाँ मदद के लिए है!",
        "Excellent! Keep exploring!": "उत्कृष्ट! खोजते रहें!",
        "Check the error carefully and try again.": "त्रुटि को ध्यान से जांचें और फिर कोशिश करें।",
        "Great job! Keep up the great work!": "बहुत बढ़िया! ऐसे ही करते रहें!",
        "Welcome to the new session! Try typing the reference code to learn.": "नए सत्र में आपका स्वागत है! सीखने के लिए संदर्भ कोड टाइप करने का प्रयास करें।",
        "Hello! I'm Sandra, your AI mentor.": "नमस्ते! मैं सैंड्रा हूँ, आपकी AI मेंटर।"
    },
    Language.ITALIAN: {
        "AI mentor is currently unavailable.": "Il mentor AI non è attualmente disponibile.",
        "Could not generate AI feedback at this time.": "Non è stato possibile generare feedback AI in questo momento.",
        "Welcome! Start by typing the reference code on the left to practice. Sandra is here to help!": "Benvenuto! Inizia digitando il codice di riferimento a sinistra per esercitarti. Sandra è qui per aiutare!",
        "Excellent! Keep exploring!": "Eccellente! Continua ad esplorare!",
        "Check the error carefully and try again.": "Controlla attentamente l'errore e riprova.",
        "Great job! Keep up the great work!": "Ottimo lavoro! Continua così!",
        "Welcome to the new session! Try typing the reference code to learn.": "Benvenuto nella nuova sessione! Prova a digitare il codice di riferimento per imparare.",
        "Hello! I'm Sandra, your AI mentor.": "Ciao! Sono Sandra, la tua mentor AI."
    },
    Language.PORTUGUESE: {
        "AI mentor is currently unavailable.": "O mentor de IA não está disponível no momento.",
        "Could not generate AI feedback at this time.": "Não foi possível gerar feedback de IA neste momento.",
        "Welcome! Start by typing the reference code on the left to practice. Sandra is here to help!": "Bem-vindo! Comece digitando o código de referência à esquerda para praticar. Sandra está aqui para ajudar!",
        "Excellent! Keep exploring!": "Excelente! Continue explorando!",
        "Check the error carefully and try again.": "Verifique o erro cuidadosamente e tente novamente.",
        "Great job! Keep up the great work!": "Ótimo trabalho! Continue assim!",
        "Welcome to the new session! Try typing the reference code to learn.": "Bem-vindo à nova sessão! Tente digitar o código de referência para aprender.",
        "Hello! I'm Sandra, your AI mentor.": "Olá! Eu sou Sandra, sua mentora de IA."
    }
}


class ArgosTranslateEngine:
    """
    Enhanced Argostranslate engine with 2025 optimizations:
    - Intelligent caching
    - Background package management
    - Performance monitoring
    - Error resilience
    """
    
    def __init__(self, progress_callback=None):
        self.available = ARGOS_TRANSLATE_AVAILABLE
        self.installed_packages = set()
        self.translation_cache = {}  # In-memory cache for translations
        self.cache_file = Path.home() / ".convai_translations_cache.json"
        self.package_install_lock = threading.Lock()
        self.translation_models = {}  # Cache loaded models
        self.progress_callback = progress_callback
        
        if self.progress_callback:
            self.progress_callback("Initializing translation system...")
        
        print(f"🌍 ArgosTranslate Engine initialized: {'✅' if self.available else '❌'}")
        
        if self.available:
            self._load_cache()
            # Don't initialize packages in __init__ - will be done in background
        else:
            print("💡 Install with: pip install argostranslate")
    
    def _load_cache(self):
        """Load persistent translation cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.translation_cache = json.load(f)
                print(f"✅ Loaded {len(self.translation_cache)} cached translations")
        except Exception as e:
            print(f"⚠️ Could not load translation cache: {e}")
            self.translation_cache = {}
    
    def _save_cache(self):
        """Save translation cache to disk (2025 performance optimization)"""
        try:
            # Limit cache size to prevent unlimited growth
            if len(self.translation_cache) > 1000:
                # Keep only the most recent 800 entries
                items = list(self.translation_cache.items())
                self.translation_cache = dict(items[-800:])
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.translation_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save translation cache: {e}")
    
    def _cache_key(self, text: str, target_language: Language) -> str:
        """Generate cache key for translation"""
        content = f"{text}:{target_language.code}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _initialize_packages(self):
        """Initialize and check installed packages"""
        try:
            self.installed_packages = set()
            installed = argostranslate.translate.get_installed_languages()
            
            for lang in installed:
                self.installed_packages.add(lang.code)
            
            print(f"📦 Found {len(self.installed_packages)} installed language packages")
            
            # Pre-install common language pairs in background
            threading.Thread(
                target=self._preinstall_common_packages, 
                daemon=True
            ).start()
            
        except Exception as e:
            print(f"❌ Package initialization failed: {e}")
    
    def initialize_packages_async(self):
        """Initialize packages in background thread"""
        try:
            if self.progress_callback:
                self.progress_callback("Checking installed language packages...")
            
            self.installed_packages = set()
            installed = argostranslate.translate.get_installed_languages()
            
            for lang in installed:
                self.installed_packages.add(lang.code)
            
            if self.progress_callback:
                self.progress_callback(f"Found {len(self.installed_packages)} installed packages")
            print(f"📦 Found {len(self.installed_packages)} installed language packages")
            
            # Install common packages
            self._preinstall_common_packages()
            
        except Exception as e:
            error_msg = f"Package initialization failed: {e}"
            if self.progress_callback:
                self.progress_callback(error_msg)
            print(f"❌ {error_msg}")
    
    def _preinstall_common_packages(self):
        """Background installation of common language packages"""
        common_pairs = [
            ("en", "es"), ("en", "fr"), ("en", "it"), 
            ("en", "pt"), ("en", "hi")
        ]
        
        for i, (from_code, to_code) in enumerate(common_pairs, 1):
            try:
                if self.progress_callback:
                    self.progress_callback(f"Installing translation package {i}/{len(common_pairs)}: {from_code} → {to_code}")
                
                self._ensure_package_installed(from_code, to_code)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"⚠️ Background package install failed for {from_code}->{to_code}: {e}")
    
    def _ensure_package_installed(self, from_code: str, to_code: str) -> bool:
        """Ensure translation package is installed with thread safety"""
        package_key = f"{from_code}-{to_code}"
        
        if package_key in self.installed_packages:
            return True
        
        with self.package_install_lock:
            # Double-check after acquiring lock
            if package_key in self.installed_packages:
                return True
            
            try:
                print(f"📥 Installing translation package: {from_code} -> {to_code}")
                
                # Update package index
                argostranslate.package.update_package_index()
                
                # Find and install package
                available_packages = argostranslate.package.get_available_packages()
                package_to_install = next(
                    (pkg for pkg in available_packages 
                     if pkg.from_code == from_code and pkg.to_code == to_code),
                    None
                )
                
                if package_to_install:
                    argostranslate.package.install_from_path(
                        package_to_install.download()
                    )
                    self.installed_packages.add(package_key)
                    print(f"✅ Package installed: {from_code} -> {to_code}")
                    return True
                else:
                    print(f"❌ Package not found: {from_code} -> {to_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Package installation failed: {e}")
                return False
    
    @lru_cache(maxsize=32)
    def _get_translation_model(self, from_code: str, to_code: str):
        """Get cached translation model (2025 performance optimization)"""
        try:
            installed_languages = argostranslate.translate.get_installed_languages()
            
            from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
            to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)
            
            if from_lang and to_lang:
                return from_lang.get_translation(to_lang)
            return None
            
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            return None
    
    def translate(self, text: str, target_language: Language) -> str:
        """
        Translate text using Argostranslate with advanced caching (2025 optimized)
        """
        if not text or not text.strip():
            return text
            
        if not self.available or target_language == Language.ENGLISH:
            return text
        
        # Check cache first (fastest path)
        cache_key = self._cache_key(text, target_language)
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        target_code = ARGOS_LANGUAGE_MAPPING.get(target_language, target_language.code) 
        from_code = "en"
        
        print(f"🔄 Translating: '{text[:50]}...' -> {target_language.display_name}")
        
        try:
            # Ensure package is installed
            if not self._ensure_package_installed(from_code, target_code):
                return self._get_fallback_translation(text, target_language)
            
            # Get translation model
            translation_model = self._get_translation_model(from_code, target_code)
            if not translation_model:
                print(f"❌ No translation model available for {from_code} -> {target_code}")
                return self._get_fallback_translation(text, target_language)
            
            # Perform translation
            result = translation_model.translate(text)
            
            if result and result.strip() and result != text:
                # Cache successful translation
                self.translation_cache[cache_key] = result
                
                # Periodically save cache (every 10 translations)
                if len(self.translation_cache) % 10 == 0:
                    threading.Thread(target=self._save_cache, daemon=True).start()
                
                print(f"✅ Translation successful: '{result[:50]}...'")
                return result
            else:
                print(f"⚠️ Translation returned empty or same result")
                return self._get_fallback_translation(text, target_language)
                
        except Exception as e:
            print(f"❌ Argostranslate error: {e}")
            return self._get_fallback_translation(text, target_language)
    
    def _get_fallback_translation(self, text: str, target_language: Language) -> str:
        """Get fallback translation from hardcoded dictionary"""
        fallback_dict = ENHANCED_FALLBACK_TRANSLATIONS.get(target_language, {})
        result = fallback_dict.get(text, text)
        
        if result != text:
            print(f"🔄 Using fallback translation: '{result[:50]}...'")
        else:
            print(f"⚠️ No fallback available for: '{text[:30]}...'")
        
        return result
    
    def get_available_languages(self) -> List[str]:
        """Get list of available language codes"""
        if not self.available:
            return []
        
        try:
            available_packages = argostranslate.package.get_available_packages()
            return list(set(pkg.to_code for pkg in available_packages))
        except Exception:
            return ["es", "fr", "it", "pt", "hi"]  # Common languages
    
    def get_cache_stats(self) -> Dict:
        """Get translation cache statistics"""
        return {
            "cache_size": len(self.translation_cache),
            "installed_packages": len(self.installed_packages),
            "cache_file_exists": self.cache_file.exists(),
            "available": self.available
        }
    
    def clear_cache(self):
        """Clear translation cache"""
        self.translation_cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        print("🗑️ Translation cache cleared")


class LLMAIFeedbackSystem:
    """Enhanced LLM system with Transformers (2025 optimized)"""
    
    def __init__(self, model_path: Optional[str] = None, progress_callback=None):
        self.model = None
        self.tokenizer = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.translator = ArgosTranslateEngine(progress_callback)
        self.progress_callback = progress_callback
        self.model_name = "convaiinnovations/fine_tuned_coder"
        
        # Don't load model in __init__ - will be loaded later in background
    
    def load_model_async(self):
        """Load model in background thread"""
        if not TRANSFORMERS_AVAILABLE:
            if self.progress_callback:
                self.progress_callback("Transformers library not found. AI features will be disabled.")
            print("❌ Transformers library not found. AI features will be disabled.")
            return
            
        try:
            if self.progress_callback:
                self.progress_callback(f"Loading AI mentor model: {self.model_name}")
            print(f"🤖 Loading LLM Training Mentor AI: {self.model_name}")
            
            # Load tokenizer first
            if self.progress_callback:
                self.progress_callback("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load model
            if self.progress_callback:
                self.progress_callback("Loading AI model (this may take a moment)...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype="auto",
                device_map="auto"
            )
            
            if self.progress_callback:
                self.progress_callback("AI mentor loaded successfully!")
            print("✅ LLM Training Mentor AI Initialized.")
            
        except Exception as e:
            error_msg = f"Failed to load AI model: {e}"
            if self.progress_callback:
                self.progress_callback(error_msg)
            print(f"❌ {error_msg}")
    
    @property
    def is_available(self) -> bool: 
        return self.model is not None and self.tokenizer is not None

    def generate_feedback(self, code: str, error: str, session_id: str, target_language: Language = Language.ENGLISH) -> str:
        """Generate feedback with Argostranslate translation"""
        if not self.is_available: 
            base_msg = "AI mentor is currently unavailable."
            return self.translator.translate(base_msg, target_language)
        
        system_prompt = """You are Sandra, an expert LLM training mentor. You guide students through learning to build language models from scratch. 

Provide brief, encouraging feedback (1-2 sentences) focused on the current learning session. When code runs successfully, celebrate and suggest next steps. When code fails, give clear, specific hints to fix the error.

Don't tell about the next session or task, just focus on the current one."""

        if not error:
            user_prompt = f"Session: {session_id}. Student's code ran successfully! Give brief positive feedback and encourage them toward the next concept."
        else:
            user_prompt = f"Session: {session_id}. Student's code failed with: '{error}'. Give a concise hint to fix it, related to the session topic."
        
        try:
            # Prepare messages for chat template
            messages = [
                {"role": "user", "content": user_prompt}
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False  # Disable thinking mode as requested
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            # Generate response
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=512,
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode response
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            feedback = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()
            
            if not feedback:
                fallback = "Excellent! Keep exploring!" if not error else "Check the error carefully and try again."
                feedback = fallback
            
            # Translate using Argostranslate
            if target_language != Language.ENGLISH:
                feedback = self.translator.translate(feedback, target_language)
            
            return feedback
            
        except Exception as e:
            print(f"❌ AI feedback generation error: {e}")
            base_msg = "Could not generate AI feedback at this time."
            return self.translator.translate(base_msg, target_language)

    def generate_text(self, prompt: str, max_length: int = 100, temperature: float = 0.5, system_prompt: str = "") -> str:
        """Generic text generation for AI tutor narrator"""
        if not self.is_available:
            return "Great job! Keep going!"

        try:
            # Prepare messages
            messages = [
                {"role": "user", "content": prompt}
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            # Generate response (fast settings)
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            # Decode response
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            response = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()

            return response if response else "Great job!"

        except Exception as e:
            print(f"❌ AI text generation error: {e}")
            return "Keep going!"

    def generate_code(self, request: CodeGenRequest) -> CodeGenResponse:
        """Generate code based on user prompt"""
        if not self.is_available:
            return CodeGenResponse(
                generated_code="",
                explanation="AI code generation is currently unavailable.",
                success=False,
                error_message="LLM not available"
            )
        
        system_prompt = f"""You are Sandra, an expert programmer and ML educator. Generate clean, well-commented {request.language} code for the student's request. 

Session context: {request.session_id}

Provide:
1. Working code that follows best practices
2. Clear comments explaining key concepts
3. Code that's appropriate for the current learning level

Keep code concise but educational. Focus on the core concept being asked about."""

        user_prompt = f"Generate {request.language} code for: {request.prompt}"
        
        try:
            # Prepare messages for chat template
            messages = [
                {"role": "user", "content": user_prompt}
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False  # Disable thinking mode as requested
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            # Generate response
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode response
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            content = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()
            
            # Try to separate code from explanation
            parts = content.split("```")
            if len(parts) >= 3:
                # Code is between first pair of ```
                generated_code = parts[1]
                if generated_code.startswith(request.language):
                    generated_code = generated_code[len(request.language):].strip()
                
                explanation = parts[0] + (parts[2] if len(parts) > 2 else "")
            else:
                # No code blocks, treat entire content as code
                generated_code = content
                explanation = f"Generated {request.language} code for: {request.prompt}"
            
            return CodeGenResponse(
                generated_code=generated_code.strip(),
                explanation=explanation.strip(),
                success=True
            )
            
        except Exception as e:
            print(f"❌ Code generation error: {e}")
            return CodeGenResponse(
                generated_code="",
                explanation="Failed to generate code.",
                success=False,
                error_message=str(e)
            )

    def generate_code_streaming(self, request: CodeGenRequest, stream_callback=None, stop_event=None):
        """Generate code with streaming support"""
        if not self.is_available:
            return CodeGenResponse(
                generated_code="",
                explanation="AI code generation is currently unavailable.",
                success=False,
                error_message="LLM not available"
            )
        
        system_prompt = f"""You are Sandra, an expert programmer and ML educator. Generate clean, well-commented {request.language} code for the student's request. 

Session context: {request.session_id}

Provide:
1. Working code that follows best practices
2. Clear comments explaining key concepts
3. Code that's appropriate for the current learning level

Keep code concise but educational. Focus on the core concept being asked about."""

        user_prompt = f"Generate {request.language} code for: {request.prompt}"
        
        try:
            # Prepare messages for chat template
            messages = [
                {"role": "user", "content": user_prompt}
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            # Streaming generation setup
            generated_text = ""
            
            # Use transformers streaming
            from transformers import TextIteratorStreamer
            import torch
            
            streamer = TextIteratorStreamer(
                self.tokenizer,
                skip_prompt=True,
                skip_special_tokens=True
            )
            
            # Generate with streaming
            generation_kwargs = {
                **model_inputs,
                "max_new_tokens": request.max_tokens,
                "temperature": request.temperature,
                "do_sample": True,
                "pad_token_id": self.tokenizer.eos_token_id,
                "streamer": streamer
            }
            
            # Start generation in a separate thread
            import threading
            generation_thread = threading.Thread(
                target=lambda: self.model.generate(**generation_kwargs)
            )
            generation_thread.start()
            
            # Stream the output
            for new_text in streamer:
                if stop_event and stop_event.is_set():
                    break
                    
                generated_text += new_text
                
                if stream_callback:
                    if not stream_callback(generated_text):
                        break
            
            # Wait for generation to complete
            generation_thread.join()
            
            if stop_event and stop_event.is_set():
                return CodeGenResponse(
                    generated_code="",
                    explanation="Generation was stopped.",
                    success=False,
                    error_message="Stopped by user"
                )
            
            # Try to separate code from explanation
            content = generated_text.strip()
            parts = content.split("```")
            if len(parts) >= 3:
                # Code is between first pair of ```
                generated_code = parts[1]
                if generated_code.startswith(request.language):
                    generated_code = generated_code[len(request.language):].strip()
                
                explanation = parts[0] + (parts[2] if len(parts) > 2 else "")
            else:
                # No code blocks, treat entire content as code
                generated_code = content
                explanation = f"Generated {request.language} code for: {request.prompt}"
            
            return CodeGenResponse(
                generated_code=generated_code.strip(),
                explanation=explanation.strip(),
                success=True
            )
            
        except Exception as e:
            print(f"❌ Streaming code generation error: {e}")
            return CodeGenResponse(
                generated_code="",
                explanation="Failed to generate code with streaming.",
                success=False,
                error_message=str(e)
            )

    def initial_session_message(self, session_id: str, language: Language = Language.ENGLISH) -> str:
        """Generate initial message with Argostranslate"""
        if not self.is_available:
            return self.translator.translate("Welcome to the new session! Try typing the reference code to learn.", language)
        
        system_prompt = """You are Sandra, an LLM training mentor. Give a warm welcome and encourage manual typing practice. Be brief (1-2 sentences) and encouraging."""
        
        user_prompt = f"Student just started session: {session_id}. Welcome them and encourage manual typing practice."
        
        try:
            # Prepare messages for chat template
            messages = [
                {"role": "user", "content": user_prompt}
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False  # Disable thinking mode as requested
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            # Generate response
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode response
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            feedback = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()
            
            if not feedback:
                feedback = "Welcome! Start by typing the reference code on the left to practice. Sandra is here to help!"
            
            # Translate using Argostranslate
            if language != Language.ENGLISH:
                feedback = self.translator.translate(feedback, language)
            
            return feedback
            
        except Exception as e:
            return self.translator.translate("Welcome! Start by typing the reference code on the left to practice. Sandra is here to help!", language)

    def generate_followup_response(self, question: str, context: str, session_id: str, language: Language = Language.ENGLISH) -> str:
        """Generate followup response with context"""
        if not self.is_available:
            base_msg = "AI mentor is currently unavailable for followup questions."
            return self.translator.translate(base_msg, language)
        
        system_prompt = """You are Sandra, an expert LLM training mentor. Answer the student's followup question based on the conversation context. Be helpful, encouraging, and provide clear explanations. Keep responses concise but informative (2-3 sentences)."""
        
        user_prompt = f"Context: {context}\n\nStudent's followup question: {question}\n\nProvide a helpful response related to session: {session_id}"
        
        try:
            # Prepare messages for chat template
            messages = [
                {"role": "user", "content": user_prompt}
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            # Generate response
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode response
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            response = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()
            
            if not response:
                response = "I'm here to help! Could you ask your question in a different way?"
            
            # Translate using Argostranslate
            if language != Language.ENGLISH:
                response = self.translator.translate(response, language)
            
            return response
            
        except Exception as e:
            print(f"❌ Followup response generation error: {e}")
            base_msg = "I'd be happy to help, but I'm having trouble generating a response right now."
            return self.translator.translate(base_msg, language)

    def generate_code_followup(self, question: str, code_context: str, conversation_context: str = "") -> str:
        """Generate followup response for code questions"""
        if not self.is_available:
            return "AI code assistant is currently unavailable."
        
        system_prompt = """You are Sandra, an expert programming mentor and code assistant. Help students with their code questions, errors, and improvements. Provide clear, helpful explanations and solutions.

When helping with errors:
1. Identify the specific problem
2. Explain why it's happening
3. Provide the corrected solution
4. Suggest best practices to avoid similar issues

Keep responses concise but thorough (2-4 sentences)."""
        
        user_prompt = f"""Code Context:
{code_context}

Conversation History: {conversation_context}

Student Question: {question}

Please provide helpful guidance."""
        
        try:
            # Prepare messages for chat template
            messages = [
                {"role": "user", "content": user_prompt}
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            # Generate response
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode response
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            response = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()
            
            if not response:
                response = "I'm here to help! Could you provide more details about your specific issue?"
            
            return response
            
        except Exception as e:
            print(f"❌ Code followup generation error: {e}")
            return "I'd be happy to help with your code question, but I'm having trouble generating a response right now."


class EnhancedKokoroTTSSystem:
    """Enhanced multi-language TTS system using Kokoro"""
    
    def __init__(self):
        self.pipelines = {}  # Cache pipelines for different languages
        self.current_pipeline = None
        self.current_language = Language.ENGLISH
        self.stop_event = threading.Event()
        self.is_speaking = False

        if KOKORO_TTS_AVAILABLE:
            try:
                # Initialize default English pipeline
                self._load_pipeline(Language.ENGLISH)
                print("✅ Enhanced Multi-language Kokoro TTS System Initialized.")
            except Exception as e:
                print(f"❌ Failed to initialize Kokoro TTS: {e}")

    @property
    def is_available(self) -> bool: 
        return bool(self.pipelines)

    def _load_pipeline(self, language: Language):
        """Load TTS pipeline for a specific language"""
        if language not in self.pipelines:
            try:
                pipeline = KPipeline(
                    repo_id='hexgrad/Kokoro-82M', 
                    lang_code=language.tts_code
                )
                self.pipelines[language] = pipeline
                print(f"✅ Loaded TTS pipeline for {language.display_name} (code: {language.tts_code})")
            except Exception as e:
                print(f"❌ Failed to load TTS pipeline for {language.display_name}: {e}")

    def set_language(self, language: Language):
        """Set the current language for TTS"""
        if language != self.current_language:
            self.current_language = language
            self._load_pipeline(language)
            self.current_pipeline = self.pipelines.get(language)
            print(f"🔊 TTS language changed to {language.display_name}")

    def speak(self, text: str, language: Optional[Language] = None):
        """Speak text in the specified or current language"""
        if not text or self.is_speaking:
            return
            
        # Use specified language or current language
        target_language = language or self.current_language
        
        # Load pipeline if needed
        if target_language not in self.pipelines:
            self._load_pipeline(target_language)
        
        pipeline = self.pipelines.get(target_language)
        if not pipeline:
            print(f"❌ TTS pipeline not available for {target_language.display_name}")
            return
            
        self.stop_event.clear()
        self.is_speaking = True
        threading.Thread(
            target=self._audio_worker, 
            args=(text, pipeline, target_language), 
            daemon=True
        ).start()

    def stop_speech(self):
        """Stop current speech"""
        if self.is_speaking: 
            self.stop_event.set()

    def _audio_worker(self, text: str, pipeline: KPipeline, language: Language):
        """Audio worker thread"""
        try:
            processed_text = self._preprocess_text_for_tts(text, language)
            audio_chunks = []
            
            for _, _, audio in pipeline(processed_text, voice=language.voice):
                if self.stop_event.is_set():
                    print("🔊 Audio stopped by user.")
                    return
                audio_chunks.append(audio)
            
            if audio_chunks:
                full_audio = torch.cat(audio_chunks)
                sd.play(full_audio, samplerate=24000)
                while sd.get_stream().active:
                    if self.stop_event.is_set():
                        sd.stop()
                        print("🔊 Audio stream stopped.")
                        break
                    time.sleep(0.1)
        except Exception as e: 
            print(f"❌ Kokoro TTS error: {e}")
        finally:
            self.is_speaking = False
            self.stop_event.clear()

    def _preprocess_text_for_tts(self, text: str, language: Language) -> str:
        """Preprocess text to improve TTS quality and remove emojis"""
        
        # Step 1: Remove emoji symbols and other unwanted unicode characters
        processed = self._remove_emojis_and_symbols(text)
        
        # Step 2: Common technical term replacements
        common_replacements = {
            "PyTorch": "pie torch",
            "LLM": "large language model",
            "GPU": "graphics processing unit",
            "CPU": "central processing unit",
            "API": "A P I",
            "URL": "U R L",
            "JSON": "jay son",
            "HTML": "H T M L",
            "CSS": "C S S",
            "JavaScript": "java script"
        }
        
        # Step 3: Language-specific replacements
        if language == Language.ENGLISH:
            replacements = {
                **common_replacements,
                "RMSNorm": "R M S normalization",
                "RoPE": "rotary position encoding",
                "AdamW": "Adam W optimizer",
                "BPE": "byte pair encoding",
                "GELU": "G E L U activation",
                "SiLU": "S I L U activation"
            }
        else:
            replacements = common_replacements
        
        for term, replacement in replacements.items():
            processed = processed.replace(term, replacement)
        
        return processed
    
    def _remove_emojis_and_symbols(self, text: str) -> str:
        """Remove emoji symbols and other visual unicode characters that shouldn't be spoken"""
        import re
        
        # Step 1: Remove code blocks and their language indicators
        text = self._remove_code_blocks(text)
        
        # Step 2: Remove emojis and symbols using Unicode ranges
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002500-\U00002BEF"  # chinese char
            "\U00002702-\U000027B0"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"  # dingbats
            "\u3030"
            "]+", 
            flags=re.UNICODE
        )
        
        # Remove emojis
        text_no_emojis = emoji_pattern.sub(' ', text)
        
        # Step 3: Remove common symbols that are visual indicators
        symbol_replacements = {
            '✅': 'success',
            '❌': 'error',
            '🔍': '',
            '📋': '',
            '🤖': '',
            '💡': 'hint',
            '📚': '',
            '🔊': '',
            '🧠': '',
            '⚠️': 'warning',
            '📤': '',
            '💻': '',
            '▶': '',
            '🧹': '',
            '💾': '',
            '📁': '',
            '→': 'to',
            '←': 'from',
            '↶': '',
            '↷': '',
            '⏹️': '',
            '🎯': '',
            '🚀': '',
            '🌍': '',
            '🔒': '',
            '✏️': '',
            '🗑️': '',
            '🔄': '',
            '📊': ''
        }
        
        for symbol, replacement in symbol_replacements.items():
            text_no_emojis = text_no_emojis.replace(symbol, replacement)
        
        # Step 4: Clean up extra spaces
        text_no_emojis = re.sub(r'\s+', ' ', text_no_emojis).strip()
        
        return text_no_emojis

    def _remove_code_blocks(self, text: str) -> str:
        """Remove code blocks and their language indicators that shouldn't be spoken"""
        import re
        
        # Remove entire code blocks including language specifiers
        # Pattern for ```language\ncode\n```
        code_block_pattern = re.compile(
            r'```\s*\w*\s*\n.*?\n```',  # Match ```lang\ncode\n```
            re.DOTALL | re.MULTILINE
        )
        text = code_block_pattern.sub('', text)
        
        # Remove inline code blocks with single backticks
        inline_code_pattern = re.compile(r'`[^`]+`')
        text = inline_code_pattern.sub('', text)
        
        # Remove standalone language indicators that might be left
        language_indicators = [
            'bash', 'python', 'javascript', 'java', 'cpp', 'c++', 'html', 'css',
            'sql', 'json', 'yaml', 'xml', 'shell', 'powershell', 'cmd',
            'typescript', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift'
        ]
        
        for lang in language_indicators:
            # Remove language name when it appears standalone or at start of line
            text = re.sub(rf'\b{lang}\b\s*(?=\n|$)', '', text, flags=re.IGNORECASE)
            text = re.sub(rf'^{lang}\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove triple backticks that might be left over
        text = re.sub(r'```+', '', text)
        text = re.sub(r'`+', '', text)
        
        return text

    def get_available_languages(self) -> list[Language]:
        """Get list of available languages"""
        return list(Language)

    def get_language_status(self) -> dict:
        """Get status of all language pipelines"""
        status = {}
        for language in Language:
            status[language.display_name] = {
                'loaded': language in self.pipelines,
                'current': language == self.current_language,
                'iso_code': language.code,
                'tts_code': language.tts_code,
                'voice': language.voice
            }
        return status