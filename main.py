from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import anthropic
import json
import math

app = FastAPI(title="MoneyMentor AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic()

# ── MODELS ──────────────────────────────────────────────────────────────────

class UserProfile(BaseModel):
    name: str = "Friend"
    age: int = 28
    city: str = ""
    employment: str = "Salaried (private)"
    income: float = 0
    expenses: float = 0
    emi: float = 0
    savings: float = 0
    investments: float = 0
    life_ins: str = "no"        # yes / no / endowment
    health_cover: int = 0       # lakh
    goals: List[str] = []       # emergency, home, retirement, education, travel
    tax_regime: str = "new"
    sec80c: int = 0
    nps: str = "no"

# ── PROMPTS ─────────────────────────────────────────────────────────────────

SCORE_PROMPT = """You are an expert Indian personal finance advisor (SEBI-RIA level knowledge).

Given this user's financial profile, score them across 6 dimensions (0-100 each) and provide actionable Indian-context advice.

User profile (JSON):
{profile}

Return ONLY valid JSON matching this exact schema (no markdown, no explanation):
{{
  "overall": <integer 0-100>,
  "scores": {{
    "emergency": <integer 0-100>,
    "insurance": <integer 0-100>,
    "diversification": <integer 0-100>,
    "debt": <integer 0-100>,
    "tax": <integer 0-100>,
    "retirement": <integer 0-100>
  }},
  "insights": [
    {{
      "type": "critical|warning|good",
      "title": "<short title>",
      "body": "<2-3 sentence actionable advice with specific Indian financial products/deductions>"
    }}
  ],
  "one_liner": "<one punchy sentence summarising their financial health>"
}}

Scoring guide:
- emergency: 100 = 6+ months expenses in liquid savings; 0 = no liquid buffer
- insurance: 100 = 10x income term cover + adequate health floater; 0 = uninsured  
- diversification: 100 = balanced equity/debt/gold allocation + 20%+ savings rate; 0 = no investments
- debt: 100 = no EMIs; 0 = EMI > 50% income
- tax: 100 = fully utilised 80C (1.5L), 80D, NPS 80CCD(1B), HRA; 0 = no deductions
- retirement: 100 = on track for 25x annual expenses by age 60; 0 = no retirement savings

Generate 3-4 insights that are specific to this user's numbers. Be concrete — mention actual amounts in INR."""

FIRE_PROMPT = """You are an expert Indian personal finance planner.

Given this user profile, generate a FIRE (Financial Independence, Retire Early) roadmap.

User profile (JSON):
{profile}

Return ONLY valid JSON (no markdown):
{{
  "fire_target": <integer - corpus needed for financial independence in INR>,
  "years_to_fire": <integer>,
  "milestones": [
    {{
      "icon": "<single emoji>",
      "type": "reached|target|milestone",
      "timeline": "<e.g. Month 8, Year 3, Year 12>",
      "title": "<milestone name>",
      "body": "<specific detail with INR amounts>",
      "monthly_sip": <integer - INR amount>
    }}
  ],
  "sip_plan": [
    {{
      "goal": "<goal name>",
      "fund_type": "<Indian fund category>",
      "badge_type": "equity|debt|tax",
      "monthly_sip": <integer>,
      "horizon": "<time horizon>"
    }}
  ],
  "tax_savings": {{
    "80c_gap": <integer - unused 80C allowance>,
    "potential_saving": <integer - tax rupees saveable>,
    "recommendation": "<specific action>"
  }}
}}

Rules:
- FIRE target = 25x annual expenses (inflation-adjusted at 6% pa)
- Equity return assumption: 12% pa; Debt: 7% pa
- Mention specific Indian instruments: ELSS, NPS, PPF, liquid funds, index funds
- All SIP amounts must sum to less than the user's monthly surplus (income - expenses - EMI)
- Generate 4-5 realistic milestones starting from now"""

# ── ENDPOINTS ────────────────────────────────────────────────────────────────

@app.post("/api/score")
async def get_score(profile: UserProfile):
    """Generate Money Health Score using Claude."""
    profile_dict = profile.model_dump()
    
    prompt = SCORE_PROMPT.format(profile=json.dumps(profile_dict, indent=2))
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw = message.content[0].text.strip()
    # Strip any accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    result = json.loads(raw)
    return {"status": "ok", "data": result}


@app.post("/api/roadmap")
async def get_roadmap(profile: UserProfile):
    """Generate FIRE roadmap using Claude."""
    profile_dict = profile.model_dump()
    
    prompt = FIRE_PROMPT.format(profile=json.dumps(profile_dict, indent=2))
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    result = json.loads(raw)
    return {"status": "ok", "data": result}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "MoneyMentor AI"}


# Serve frontend at root
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
