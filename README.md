# 🧙‍♂️ QuackTokenScope

**Token wizards unite!**  
`QuackTokenScope` is a magical CLI tool for exploring how different tokenizers break down and rebuild text.

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
git clone https://github.com/<your-org>/quacktokenscope.git
cd quacktokenscope
poetry install
```

FUTURE: Or with pip (once released on PyPI):

```bash
pip install quacktokenscope
```

Sentencepiece requires cmake
```bash
brew install cmake
```

---

## 🧪 Usage

### Basic Command

```bash
quacktokenscope tokenscope tokenize myfile.txt
```

### Options

| Option | Description |
|--------|-------------|
| `--output` | Path to output file (Excel, JSON, or CSV) |
| `--output-format` | `excel` (default), `json`, or `csv` |
| `--tokenizers` | Choose subset: `tiktoken,huggingface,sentencepiece` |
| `--limit` | Limit number of characters to process |
| `--dry-run` | Prevent Drive upload |
| `--upload` | Upload results to Drive if input is a Google Drive file ID |
| `--verbose` | Show token cards and summary in terminal |

---

## 🧠 Example Output

```bash
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

## 📤 Google Drive Integration

If your input is from Google Drive (a file ID), QuackTokenScope will download it, and — unless `--dry-run` is set — upload your reports back to the same folder.

Requires:
- A valid `quack_config.yaml`
- Google credentials managed via `quackcore`

---

## 🧩 Output Structure

```
output/
└── myfile.txt/
    ├── token_table.xlsx
    ├── tiktoken_frequency.json
    ├── huggingface_frequency.json
    ├── sentencepiece_frequency.json
    ├── reverse_mapping_scores.json
    └── summary.json
```

---

## 🛠 Development

To run locally for dev:

```bash
poetry shell
python src/quacktokenscope/demo_cli.py tokenize ./sample.txt --verbose
```

To run tests:

```bash
pytest
```

---

## 🧑‍🎓 Who is this for?

- Curious devs wondering how GPT or BERT slice your text
- Educators teaching NLP or tokenization
- Debuggers working with LLM prompt limits
- Prompt engineers comparing tokenizer lengths
- Anyone who thinks "phantasmagoria" is a legendary token 🟣

---

## 📚 Related Projects

- [QuackMetadata](https://github.com/aipengineer/quackmetadata): Extracts structured metadata from content
- [QuackCore](https://github.com/aipengineer/quackcore): Shared infrastructure for QuackTools
- [tiktoken](https://github.com/openai/tiktoken)
- [transformers](https://github.com/huggingface/transformers)
- [sentencepiece](https://github.com/google/sentencepiece)

---

## 🦆 QuackVerse Ecosystem

QuackTokenScope is part of the [QuackVerse](https://github.com/aipengineer), a growing ecosystem of magical CLI tools for developers, creators, and AI adventurers.

> Build. Learn. Quack.

---

## 🪄 License

MIT License

---

## 🛸 Contributing

Open an issue or submit a pull request if you'd like to improve the tokenizer adapters, add visualizations, or support more libraries like `open-tokenizer`.

---

## 💬 Questions?

Tweet at [@aipengineer](https://twitter.com/aipengineer) or file an issue on GitHub!