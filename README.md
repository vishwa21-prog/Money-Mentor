# MoneyMentor AI 💰

### Economic Times AI Hackathon 2026 — PS9: AI Money Mentor

---

## What it does

1. **Money Health Score** — 5-minute onboarding → scores across 6 financial dimensions (0–100 each) with a radar chart
2. **FIRE Path Planner** — personalised month-by-month SIP roadmap with compound growth math

## Stack

| Layer    | Tech                                                          |
| -------- | ------------------------------------------------------------- |
| Frontend | Vanilla HTML/CSS/JS (zero dependencies, opens in any browser) |
| Backend  | FastAPI + Python                                              |
| AI       | Anthropic Claude claude-sonnet-4-20250514                     |

---

## Run locally

### Frontend only (no API key needed — uses built-in scoring engine)

```bash
open frontend/index.html
# or
python -m http.server 8080 --directory frontend
```

### Full stack (AI-powered responses)

```bash
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
uvicorn main:app --reload --port 8000
# Visit http://localhost:8000
```

---

## Project structure

```
moneymentor/
├── frontend/
│   └── index.html          # Full UI — works standalone
├── backend/
│   ├── main.py             # FastAPI app with Claude integration
│   └── requirements.txt
└── README.md
```

---

## Demo personas (for judges)

| Persona | Age | Income       | Situation                       |
| ------- | --- | ------------ | ------------------------------- |
| Arjun   | 25  | ₹60,000/mo   | Fresh grad, no savings          |
| Priya   | 34  | ₹1,20,000/mo | High EMI, no term insurance     |
| Ramesh  | 45  | ₹2,00,000/mo | Near retirement, under-invested |

---

Built by **Jala Vishwa Keerthi** · vishwakeerthi.j@gmail.com
