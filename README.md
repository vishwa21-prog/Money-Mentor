# MoneyMentor AI 💰

### Economic Times AI Hackathon 2026 — PS9: AI Money Mentor

> Your personal CFO — powered by AI, built for every Indian.

---

## What it does

1. **Money Health Score** — 5-minute onboarding → scores across 6 financial dimensions (0–100) with a radar chart and personalised insights
2. **FIRE Path Planner** — month-by-month SIP roadmap, milestone timeline, and tax optimisation plan

## Stack

| Layer    | Tech                                              |
| -------- | ------------------------------------------------- |
| Frontend | HTML/CSS/JS — zero dependencies, works standalone |
| Backend  | FastAPI + Python                                  |
| AI       | Groq (Llama 3.3 70B)                              |

---

## Run locally

### Frontend only (no API key needed)

```bash
open index.html
```

### Full stack with AI

```bash
pip install -r requirements.txt
set GROQ_API_KEY=your_key_here
uvicorn main:app --reload --port 8000
# Visit http://localhost:8000
```

Get a free Groq key at console.groq.com

---

## Project structure

```
moneymentor/
├── index.html        # Full frontend — also works standalone
├── main.py           # FastAPI backend with Groq/Llama integration
├── requirements.txt
└── README.md
```

---

## Demo personas

| Persona | Age | Income       | Situation                                  |
| ------- | --- | ------------ | ------------------------------------------ |
| Arjun   | 25  | ₹60,000/mo   | Fresh grad, no savings, no insurance       |
| Priya   | 34  | ₹1,20,000/mo | High EMI, endowment policy, under-invested |
| Ramesh  | 45  | ₹2,00,000/mo | Near retirement, no NPS, tax inefficient   |

---
