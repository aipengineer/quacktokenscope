# 🧙‍♂️ QuackTokenScope

**Token wizards unite!**  
`QuackTokenScope` is a magical CLI tool that compares how different tokenizers "see" the same text.

Powered by 🧠 [OpenAI's `tiktoken`](https://github.com/openai/tiktoken), 📚 [HuggingFace's `transformers`](https://github.com/huggingface/transformers), and 🧬 [Google's SentencePiece](https://github.com/google/sentencepiece), this tool lets you:
- Compare token outputs across multiple libraries
- Analyze token frequencies
- Reverse map tokens into readable text
- Export results to Excel, JSON, or CSV
- Optionally upload results to Google Drive

> 🪄 Ideal for NLP learners, tokenizer researchers, and AI tool builders.

---

## ✨ Features

- 🔄 **Multi-tokenizer analysis**: `tiktoken`, `huggingface`, `sentencepiece`
- 📊 **Token frequency reports** (JSON/CSV/Excel)
- 🔁 **Reverse mapping** with fidelity scoring
- 🧙 **Playful CLI** with token cards and glyphs
- ☁️ **Google Drive upload** support via `quackcore`
- 📁 Structured outputs with summary reports

---

## 🚀 Installation

```bash
# Install from source
git clone https://github.com/<your-org>/quacktokenscope.git
cd quacktokenscope
pip install -e .

# Or with pip (once released on PyPI):
pip install quacktokenscope
```

Sentencepiece requires cmake:
```bash
brew install cmake  # macOS
# or
sudo apt-get install cmake  # Ubuntu/Debian
```

---

## 📖 Usage

### Basic Commands

```bash
# Tokenize a local file
quacktool tokenscope tokenize sample.txt

# Tokenize with specific tokenizers
quacktool tokenscope tokenize sample.txt --tokenizers tiktoken,huggingface

# Tokenize a file from Google Drive
quacktool tokenscope tokenize abcdef1234567890 --output ./my_results
```

### Advanced Options

| Option | Description |
|--------|-------------|
| `--output` | Path to output directory |
| `--output-format` | `excel` (default), `json`, `csv`, or `all` |
| `--tokenizers` | Choose subset: `tiktoken,huggingface,sentencepiece` |
| `--limit` | Limit number of characters to process |
| `--dry-run` | Prevent Drive upload |
| `--upload/--no-upload` | Control Drive upload behavior |
| `--verbose` | Show token cards and detailed analysis in terminal |

### Example Commands

```bash
# Export in different formats
quacktool tokenscope tokenize sample.txt --output-format json

# Limit the number of characters to process
quacktool tokenscope tokenize large_file.txt --limit 10000

# Dry run (don't upload to Google Drive)
quacktool tokenscope tokenize sample.txt --dry-run

# Verbose output
quacktool tokenscope tokenize sample.txt --verbose
```

---

## 🧠 Example Output

```
🔮 Summoning tokens from the three Great Tokenizer Guilds...
• 🧠 OpenAI's Neural Precision
• 📚 HuggingFace's Legacy Lexicon
• 🧬 SentencePiece of Statistical Fragmentation

🎴 Token #42
Segment: "learning"
🧠 ID: 1729 | 📚 ID: 1337 | 🧬 ID: 2201
📊 Frequency (HuggingFace): ██████ (6x)

🧪 Reverse mapping...
• tiktoken → 💯 Flawless
• HuggingFace → ⚠️ Imperfect (98.3%)
• SentencePiece → ❌ Botched (81.2%)

📦 QuackTokenScope Mission Report:
• Tokens compared: 3,210
• Most common string: "the" (233x)
• Rarest token: "phantasmagoria" 🟣 Legendary
• Best reconstruction: HuggingFace (99.2%)

📁 Results exported to: ./output/token_spellbook.xlsx
```

---

## 📊 Output Structure

The tool generates a variety of output files for analysis:

```
output/
└── <filename>/
    ├── token_table.xlsx / .json / .csv
    ├── tiktoken_frequency.json
    ├── huggingface_frequency.json
    ├── sentencepiece_frequency.json
    ├── reverse_mapping_scores.json
    └── summary.json
```

- **Excel Workbook**: Multiple sheets with token tables, frequencies, and statistics
- **JSON Files**: Structured data for programmatic analysis
- **CSV Files**: Simple tabular data for compatibility

---

## 📤 Google Drive Integration

If your input is from Google Drive (a file ID), QuackTokenScope will download it, and — unless `--dry-run` is set — upload your reports back to the same folder.

Requires:
- A valid `quack_config.yaml`
- Google credentials managed via `quackcore`

---

## 🛠️ Configuration

Configuration is handled through `quack_config.yaml` or environment variables.

Example configuration:

```yaml
custom:
  quacktokenscope:
    log_level: INFO
    output_dir: ./output
    temp_dir: ./temp
    default_tokenizers:
      - tiktoken
      - huggingface
      - sentencepiece
    output_format: excel
    max_tokens_to_display: 10
    use_mock_tokenizers: false  # Set to true for testing without dependencies
```

---

## 🛠 Development

To run locally for development:

```bash
# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run directly
python src/quacktokenscope/demo_cli.py tokenize ./sample.txt --verbose
```

To run tests:

```bash
pytest
```

---

## 🧑‍🎓 Who is this for?

- Curious developers wondering how GPT or BERT slice your text
- Educators teaching NLP or tokenization
- Debuggers working with LLM prompt limits
- Prompt engineers comparing tokenizer lengths
- Anyone interested in how different models process text

---

## 📚 Related Projects

- [QuackMetadata](https://github.com/aipengineer/quackmetadata): Extracts structured metadata from content
- [QuackCore](https://github.com/aipengineer/quackcore): Shared infrastructure for QuackTools

---

## 🦆 QuackVerse Ecosystem

QuackTokenScope is part of the QuackVerse, a growing ecosystem of magical CLI tools for developers, creators, and AI adventurers.

> Build. Learn. Quack.

---

## 📃 License

GNU GPL - See LICENSE file for details.

---

## 🛸 Contributing

Open an issue or submit a pull request if you'd like to improve the tokenizer adapters, add visualizations, or support more libraries.

# 🦆 QuackVerse Licensing Overview

QuackVerse is a modular ecosystem with mixed licensing to balance community contribution and project protection.

### 🔓 Open Source (with strong copyleft)
- **Repositories**: `quackcore`, `ducktyper`
- **License**: [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.en.html)
- **Why?** This license ensures that any public use of these tools — including SaaS or hosted services — must release the source code and improvements back to the community.

### 🔐 Source-Available (with delayed open-source)
- **Repositories**: All `quacktools/*`
- **License**: [Business Source License 1.1 (BUSL-1.1)](https://mariadb.com/bsl11/)
- **What does this mean?**
  - You can **view, fork, and modify** the code.
  - **Production or commercial use is not allowed** unless you obtain a commercial license from us.
  - The license **automatically converts to Apache 2.0 after 3 years**, ensuring long-term openness.
- A short human summary is provided in each tool's README.

### 🎨 Brand and Creative Assets
- **Assets**: Logos, Mascot (Quackster), design elements
- **License**: [Creative Commons Attribution-NonCommercial-NoDerivs 4.0 (CC BY-NC-ND 4.0)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
- **You may not** redistribute, remix, or use our branding for commercial purposes.

---

### 🧠 Why this setup?

We love open-source and education. However, to continue building high-quality learning tools, we need to protect our work from being commercialized or rebranded by others without contributing back. Our structure enables:
- A healthy developer community.
- Opportunities for contributors to shape the future.
- Commercial protection for sustainability.

We welcome pull requests, issues, and feedback. If you're interested in **commercial use**, please reach out via [rod@aip.engineer](mailto:rod@aip.engineer).


---

## 💬 Questions?

Tweet at [@aipengineer](https://twitter.com/aipengineer) or file an issue on GitHub!
