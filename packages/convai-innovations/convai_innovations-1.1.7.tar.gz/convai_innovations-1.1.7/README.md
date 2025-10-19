# 🧠 ConvAI Innovations Dashboard - Interactive LLM Training Academy

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Hugging Face Model](https://img.shields.io/badge/🤗_Model-convaiinnovations/fine__tuned__coder-blue)](https://huggingface.co/convaiinnovations/fine_tuned_coder)
[![Hugging Face Dataset](https://img.shields.io/badge/🤗_Dataset-bilingual--coding--qa-green)](https://huggingface.co/datasets/convaiinnovations/bilingual-coding-qa-dataset)

**Learn to build Large Language Models from scratch through hands-on coding sessions with AI mentor Sandra!**

ConvAI Innovations dashboard is a comprehensive educational platform that takes you from Python fundamentals to training your own LLMs. Powered by our custom fine-tuned model trained on 25,151 bilingual Q&A pairs, experience interactive learning with real-time AI feedback, adaptive voice guidance, offline multi-language support, and a structured curriculum covering everything from neural networks to transformer architecture.

## ✨ Features

### 🎓 **Comprehensive Learning Path**
- **13 Interactive Sessions**: From Python basics to LLM inference
- **Hands-on Coding**: Type code manually to build muscle memory
- **Progressive Difficulty**: Each session builds on previous knowledge
- **Real-world Applications**: Learn concepts used in ChatGPT, GPT-4, and other LLMs

### 🤖 **AI-Powered Learning (2025 Enhanced)**
- **Sandra, Your AI Mentor**: Powered by our fine-tuned model [convaiinnovations/fine_tuned_coder](https://huggingface.co/convaiinnovations/fine_tuned_coder)
- **Adaptive Learning**: Real-time behavior monitoring, typing speed analysis, and personalized pacing
- **Voice-Guided Coding**: Line-by-line narration with automatic progress detection
- **Multi-language Support**: Learn in 6+ languages with offline neural translation
- **Smart Error Correction**: Immediate validation and correction guidance for each line
- **Interactive Encouragement**: Humor and motivation when inactive or making mistakes
- **Advanced TTS**: Kokoro-powered text-to-speech in multiple languages
- **Offline Translation**: Argostranslate ensures privacy and fast responses

### 💻 **Advanced IDE Features**
- **Syntax Highlighting**: Professional code editor with line numbers
- **Auto-indentation**: Smart code formatting
- **Real-time Execution**: Run Python code instantly with output
- **Save/Load Projects**: Manage your learning progress
- **AI Code Generation**: Built-in code generator with editable output
- **Modern UI**: Responsive interface with real-time progress tracking

### 📚 **Complete Curriculum**

| Session | Topic | What You'll Learn |
|---------|-------|------------------|
| 🐍 1 | Python Fundamentals | Variables, functions, classes for ML |
| 🔢 2 | PyTorch & NumPy | Tensor operations, mathematical foundations |
| 🧠 3 | Neural Networks | Perceptrons, multi-layer networks, forward propagation |
| ⬅️ 4 | Backpropagation | How neural networks learn, gradient computation |
| 📚 5 | Data Structures | Lists, tuples, sets, dictionaries, comprehensions |
| 🔢 6 | NumPy Fundamentals | Arrays, broadcasting, indexing, statistics |
| 🔄 7 | Data Preprocessing | Missing values, normalization, train-test split |
| 📈 8 | Linear Regression | Gradient descent, MSE loss, training loop |
| 🎯 9 | Logistic Regression | Binary classification, sigmoid, cross-entropy |
| 📊 10 | Model Evaluation | Confusion matrix, precision, recall, F1, cross-validation |
| 🛡️ 11 | Regularization | Preventing overfitting, dropout, batch norm |
| 📉 12 | Loss Functions & Optimizers | Cross-entropy, MSE, SGD, Adam, AdamW |
| 🏗️ 13 | LLM Architecture | Transformers, attention mechanisms, embeddings |
| 🔤 14 | Tokenization & BPE | Text preprocessing, byte pair encoding |
| 🎯 15 | RoPE & Self-Attention | Rotary position encoding, modern attention |
| ⚖️ 16 | RMS Normalization | Advanced normalization techniques |
| 🔄 17 | FFN & Activations | Feed-forward networks, GELU, SiLU |
| 🚂 18 | Training LLMs | Complete training pipeline, optimization |
| 🎯 19 | Inference & Generation | Text generation, sampling strategies |

## 🎯 What's New in 2025

### 🚀 **Custom Fine-Tuned Model**
- **Model**: [convaiinnovations/fine_tuned_coder](https://huggingface.co/convaiinnovations/fine_tuned_coder)
  - Base: Qwen3-0.6B (600M parameters)
  - Training: 25,151 Q&A pairs, 7M+ tokens
  - Performance: 85% accuracy, 82% precision, 0.83 F1-score
  - Languages: English and Hindi bilingual support
  - Deployment: 16-bit precision, runs on CPU with 4GB RAM

### 📚 **Training Dataset**
- **Dataset**: [convaiinnovations/bilingual-coding-qa-dataset](https://huggingface.co/datasets/convaiinnovations/bilingual-coding-qa-dataset)
  - Size: 25,151 high-quality Q&A pairs
  - Coverage: Python, ML/AI, Neural Networks, Transformers
  - Languages: English and Hindi examples
  - Topics: From basics to advanced LLM concepts

### 🎙️ **Adaptive Voice Learning**
- **Line-by-Line Narration**: Sandra reads each line of code to you
- **Real-Time Validation**: Checks your code as you type
- **Smart Encouragement**: Provides motivation and humor
- **Inactivity Detection**: Configurable timeout (5-60 seconds)
- **Repeat Function**: Re-hear instructions anytime
- **Error Correction**: Immediate feedback with correct syntax

### 🧠 **Intelligent Adaptation**
- **Typing Speed Monitoring**: Adjusts pace to your speed
- **Pattern Recognition**: Detects common mistakes
- **Personalized Hints**: Context-aware assistance
- **Progress Tracking**: Session completion analytics
- **Behavior Analysis**: Adapts to individual learning style

### 🌍 **Multi-Language Learning**
- **6 Supported Languages**: English, Spanish, French, Hindi, Italian, Portuguese
- **Offline Translation**: Argostranslate neural translation (no API keys needed)
- **Cultural Adaptation**: Learning content adapted for different regions
- **Voice Support**: Multi-language text-to-speech with Kokoro

### 🛡️ **Privacy & Performance**
- **Offline-First**: All AI processing happens on your machine
- **No Data Collection**: Your code and progress stay private
- **Fast Response**: Optimized caching for instant feedback
- **Lightweight**: Efficient resource usage with modern compression

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install convai-innovations

# With audio features (recommended)
pip install convai-innovations[audio]

# Full installation with development tools
pip install convai-innovations[all]
```

### Launch the Academy

```bash
# Start the interactive learning dashboard
convai

# Launch without banner
convai --no-banner

# Use our fine-tuned model (default)
convai --model-path "convaiinnovations/fine_tuned_coder"

# Check dependencies
convai --check-deps

# Enable debug mode for troubleshooting
convai --debug
```

### Python API

```python
from convai_innovations import convai

# Launch the application
convai.main()

# Or use the alternative entry point
convai.run_convai()
```

## 📋 System Requirements

### Required Dependencies
- **Python 3.10+**
- **tkinter** (usually included with Python)
- **transformers** (for AI mentor - Hugging Face models)
- **torch** (for neural network operations and model inference)
- **requests** (for downloading models and translation packages)
- **argostranslate** (for offline multi-language support)

### Optional Dependencies
- **kokoro-tts** (for advanced text-to-speech features)
- **sounddevice** (for audio output)
- **argostranslate** (for offline translation - enables multi-language support)

### Hardware Requirements
- **Memory**: 6GB RAM minimum, 12GB recommended
- **Storage**: 3GB free space (for AI model and translation packages)
- **GPU**: Optional, but recommended for faster AI responses (CUDA support via PyTorch)

## 🛠️ Advanced Usage

### Custom Model Configuration

```bash
# Use your own Hugging Face model
convai --model-path "your-username/your-model-name"

# Custom data directory
convai --data-dir /path/to/custom/data

# Debug mode
convai --debug
```

### Environment Variables

```bash
# Set custom Hugging Face model
export CONVAI_MODEL_PATH="microsoft/DialoGPT-medium"

# Custom data directory
export CONVAI_DATA_DIR="/path/to/data"

# Enable debug mode
export CONVAI_DEBUG="1"
```

## 🎓 Learning Tips

### For Beginners
1. **Start with Python Fundamentals** - Even if you know Python, review ML-specific concepts
2. **Type Code Manually** - Don't copy-paste; typing builds muscle memory
3. **Use Sandra's Hints** - The AI mentor provides context-aware help
4. **Practice Regularly** - Consistency is key to mastering LLM concepts

### For Advanced Users
1. **Experiment with Code** - Modify examples to deepen understanding
2. **Ask Questions** - Use the AI mentor to explore advanced topics
3. **Build Projects** - Apply learned concepts to your own projects
4. **Contribute** - Share improvements and new sessions

## 🔧 Development

### Build from Source

```bash
# Clone the repository
git clone https://github.com/ConvAI-Innovations/ailearning.git
cd convai-innovations

# Install in development mode
pip install -e .[dev]

# Run tests
python scripts/build.py

# Build package
python scripts/build.py --skip-tests

# Deploy to Test PyPI
python scripts/deploy.py --test
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Write tests
5. Submit a pull request

## 📖 Documentation

- **Full Documentation**: [convai-innovations.readthedocs.io](https://convai-innovations.readthedocs.io/)
- **API Reference**: [API Documentation](https://convai-innovations.readthedocs.io/en/latest/api/)
- **Tutorials**: [Learning Guides](https://convai-innovations.readthedocs.io/en/latest/tutorials/)
- **Examples**: [Code Examples](https://github.com/ConvAI-Innovations/ailearning/tree/main/examples)

## 🆘 Support

### Getting Help
- **GitHub Issues**: [Report bugs or request features](https://github.com/ConvAI-Innovations/ailearning/issues)
- **Email**: support@convai-innovations.com

### Common Issues

**Q: The AI mentor isn't working**
A: Make sure you have `transformers` and `torch` installed and a stable internet connection for Hugging Face model download.

**Q: No audio from Sandra**
A: Install audio dependencies: `pip install convai-innovations[audio]`

**Q: Application crashes on startup**
A: Check dependencies with `convai --check-deps` and ensure Python 3.10+.

**Q: Model download is slow or fails**
A: The first launch downloads ~1.5GB from Hugging Face. Ensure stable internet and sufficient storage.

**Q: Translation features not working**
A: Install Argostranslate: `pip install argostranslate`. First launch will download translation packages.

**Q: UI becomes unresponsive during startup**
A: This has been fixed in v1.1.7+ with background loading. Update to the latest version.

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

This is a copyleft license that requires derivative works to also be licensed under GPL-3.0.

## 🙏 Acknowledgments

- **Hugging Face** for model hosting and transformers library
- **Qwen Team** for the efficient Qwen3-0.6B base model
- **Unsloth** for 2x faster fine-tuning framework
- **PyTorch** team for the deep learning framework
- **Argostranslate** for offline neural translation
- **Kokoro TTS** for natural-sounding text-to-speech
- **The open-source AI community** for inspiration and support

## 📊 Model & Dataset Information

### Fine-Tuned Model
- **Model**: [convaiinnovations/fine_tuned_coder](https://huggingface.co/convaiinnovations/fine_tuned_coder)
- **Base**: Qwen3-0.6B
- **Method**: LoRA fine-tuning with Unsloth
- **Parameters**: 10M trainable (1.67% of total)
- **Training**: 48 hours, 15,720 steps, 5 epochs
- **Performance**: 85% accuracy on code generation tasks

### Training Dataset
- **Dataset**: [convaiinnovations/bilingual-coding-qa-dataset](https://huggingface.co/datasets/convaiinnovations/bilingual-coding-qa-dataset)
- **Size**: 25,151 Q&A pairs (7M+ tokens)
- **Languages**: English and Hindi
- **Topics**: Python, ML/AI, Neural Networks, Transformers
- **Format**: Question-Answer pairs with code examples

## 🌟 Star History

If you find ConvAI Innovations dashboard helpful, please consider giving it a star! ⭐

---

**Ready to become an LLM expert? Start your journey today!**

```bash
pip install convai-innovations[audio]
convai
```

*Happy Learning! 🚀*