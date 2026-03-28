from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from groq import Groq
import json
import os

app = FastAPI(title="MoneyMentor AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY", "insert your groq api key here"))

class UserProfile(BaseModel):
    name: str = "Friend"
    age: int = 28
    city: str = ""
    employment: str = ""
    income: float = 0
    expenses: float = 0
    emi: float = 0
    savings: float = 0
    investments: float = 0
    life_ins: str = "no"
    health_cover: int = 0
    goals: List[str] = []
    tax_regime: str = "new"
    sec80c: int = 0
    nps: str = "no"

SCORE_PROMPT = """You are an expert Indian personal finance advisor with SEBI-RIA level knowledge.

Analyse this user's financial profile carefully and score them across exactly 6 dimensions.

User profile (JSON):
{profile}

SCORING RULES — compute each score precisely from the numbers above:
- emergency: (investments * 0.2) / (expenses * 6) * 100, capped at 100. If investments=0, score=0.
- insurance: 20 base. +40 if life_ins=yes, +10 if life_ins=endowment, 0 if no. +40 if health_cover>=10, +25 if >=5, +10 if >=3. Cap at 100.
- diversification: (savings / income) * 250, capped at 100. If income=0, score=0.
- debt: if emi=0, score=95. Else max(0, (1 - emi/(income*0.4)) * 100).
- tax: 50 base. +30 if sec80c>=150000, +15 if >=100000, +5 if >=50000. +20 if nps=yes. Cap at 100.
- retirement: min(100, (investments * 1.12^(60-age) + savings*12*((1.12^(60-age)-1)/0.12)) / (income*12*25) * 100)
- overall: average of all 6 scores, rounded to integer.

Return ONLY this JSON structure, no markdown, no explanation:
{{
  "overall": <integer>,
  "scores": {{
    "emergency": <integer>,
    "insurance": <integer>,
    "diversification": <integer>,
    "debt": <integer>,
    "tax": <integer>,
    "retirement": <integer>
  }},
  "insights": [
    {{"type": "critical", "title": "<title>", "body": "<2-3 sentences. Mention exact INR amounts from their profile. Recommend specific Indian products: ELSS, NPS, term insurance, liquid funds, PPF.>"}},
    {{"type": "warning", "title": "<title>", "body": "<2-3 sentences with specific INR amounts and actionable next step.>"}},
    {{"type": "good", "title": "<title>", "body": "<2-3 sentences acknowledging what they are doing well.>"}},
    {{"type": "warning", "title": "<title>", "body": "<2-3 sentences on tax optimisation with exact deduction amounts available to them.>"}}
  ],
  "one_liner": "<one punchy sentence about their overall financial health, mention their name>"
}}"""

FIRE_PROMPT = """You are an expert Indian personal finance planner.

Build a detailed FIRE roadmap for this user:
{profile}

CALCULATION RULES:
- Monthly surplus = income - expenses - emi
- FIRE target = expenses * 12 * 25 (25x annual expenses)
- Equity return = 12% pa, Debt = 7% pa, Inflation = 6% pa
- All monthly_sip values must be realistic — total SIPs must be under monthly surplus

Return ONLY this JSON, no markdown:
{{
  "fire_target": <integer INR — expenses*12*25>,
  "years_to_fire": <integer — realistic estimate>,
  "milestones": [
    {{"icon": "🛡️", "type": "milestone", "timeline": "Month <N>", "title": "Emergency fund complete", "body": "Save ₹<expenses*6> in a liquid mutual fund. Monthly contribution: ₹<amount>.", "monthly_sip": <integer>}},
    {{"icon": "🏥", "type": "milestone", "timeline": "Month <N>", "title": "Insurance gaps closed", "body": "Get ₹<10x income> term cover + ₹10L health floater. Estimated premium: ₹<amount>/month.", "monthly_sip": <integer>}},
    {{"icon": "📈", "type": "milestone", "timeline": "Year <N>", "title": "First ₹10L invested", "body": "Consistent SIPs in index funds and ELSS. Corpus projected: ₹<amount> at 12% returns.", "monthly_sip": <integer>}},
    {{"icon": "🔥", "type": "target", "timeline": "Year <N>", "title": "Financial independence", "body": "Target corpus of ₹<fire_target> — 25x annual expenses of ₹<expenses*12>. You can retire at age <age+years_to_fire>.", "monthly_sip": <integer>}}
  ],
  "sip_plan": [
    {{"goal": "Emergency fund", "fund_type": "Liquid Fund", "badge_type": "debt", "monthly_sip": <integer — 30% of surplus>, "horizon": "6-12 months"}},
    {{"goal": "Retirement / FIRE", "fund_type": "Nifty 50 Index Fund", "badge_type": "equity", "monthly_sip": <integer — 40% of surplus>, "horizon": "<years_to_fire> years"}},
    {{"goal": "Tax saving (80C)", "fund_type": "ELSS Fund", "badge_type": "tax", "monthly_sip": <integer — min(surplus*0.2, remaining_80c/12)>, "horizon": "3 year lock-in"}},
    {{"goal": "Wealth building", "fund_type": "Flexi Cap Fund", "badge_type": "equity", "monthly_sip": <integer — remaining surplus>, "horizon": "10+ years"}}
  ],
  "tax_savings": {{
    "80c_gap": <integer — 150000 minus sec80c>,
    "potential_saving": <integer — 80c_gap * 0.3>,
    "recommendation": "Invest ₹<80c_gap/12>/month in ELSS to fully utilise Section 80C and save ₹<potential_saving> in taxes this year."
  }}
}}"""

def ask(prompt):
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a financial advisor. Always respond with valid JSON only. Never use markdown fences. Compute all numbers precisely from the user data provided."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(r.choices[0].message.content)

@app.post("/api/score")
async def get_score(profile: UserProfile):
    return {"status": "ok", "data": ask(SCORE_PROMPT.format(profile=json.dumps(profile.model_dump(), indent=2)))}

@app.post("/api/roadmap")
async def get_roadmap(profile: UserProfile):
    return {"status": "ok", "data": ask(FIRE_PROMPT.format(profile=json.dumps(profile.model_dump(), indent=2)))}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))
