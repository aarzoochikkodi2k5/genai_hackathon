# 🏏 Sports Commentary AI

An AI-powered live sports commentary generator built in a **12-hour hackathon**. Feed it match data, and it generates natural-language commentary in real time — with support for both **cricket** and **football**, plus **Kannada translation** for regional accessibility.

---

## 🚀 Features

- **Multi-sport support** — switch between cricket and football commentary modes
- **AI-generated commentary** powered by Groq API running `llama-3.3-70b`
- **Regional language support** — auto-translation of commentary into Kannada
- **Interactive web UI** built with Streamlit
- **Real match data** sourced from Kaggle's ICC T20 World Cup 2026 dataset

---

## 🛠️ Tech Stack

| Component        | Tool/Library                     |
|-------------------|-----------------------------------|
| LLM Inference     | Groq API (`llama-3.3-70b`)         |
| Frontend/UI       | Streamlit                        |
| Data Source       | Kaggle ICC T20 World Cup 2026 CSVs |
| Language          | Python                           |
| Translation       | Kannada language support module   |

---

## 📂 Project Structure

```
sports-commentary-ai/
├── app.py                 # Streamlit app entry point
├── data/                  # ICC T20 WC 2026 CSV files
├── commentary/            # Commentary generation logic (cricket + football)
├── translation/           # Kannada translation module
├── requirements.txt
└── README.md
```

---

## ⚡ Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/sports-commentary-ai.git
cd sports-commentary-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your Groq API key
Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_api_key_here
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🏗️ How It Works

1. Match data (ball-by-ball / event-by-event) is loaded from the CSV dataset
2. Each event is passed as context to the LLM via the Groq API
3. `llama-3.3-70b` generates natural, broadcast-style commentary for the event
4. Commentary is optionally translated into Kannada
5. Output is streamed live to the Streamlit interface as the match "progresses"

---

## 🐛 Known Issues / Lessons Learned

Built under hackathon time pressure, so a few rough edges were debugged along the way:
- **JSON parsing errors** from occasionally malformed LLM output — added stricter response validation
- **Windows encoding issues** when handling Kannada Unicode text — fixed by explicitly setting UTF-8 encoding
- **PATH/environment issues** when running Streamlit from certain terminals — resolved via virtual environment setup

---

## 🎯 Future Improvements

- [ ] Add more regional languages beyond Kannada
- [ ] Support live data feeds instead of static CSVs
- [ ] Add voice/audio commentary output (text-to-speech)
- [ ] Extend to more sports (basketball, kabaddi, etc.)

---

## 📜 License

This project was built for hackathon purposes. Feel free to fork and extend it.

---

## 🙌 Acknowledgements

- [Groq](https://groq.com/) for blazing-fast LLM inference
- [Kaggle](https://www.kaggle.com/) for the ICC T20 World Cup 2026 dataset
- Built in 12 hours, fueled by caffeine and stubbornness ☕
