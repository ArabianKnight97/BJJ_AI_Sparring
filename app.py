from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from uuid import uuid4
from typing import List
from sqlalchemy.orm import Session
from db import SessionLocal, Match
from game_logic import Fighter, BJJGame
import openai
import json

app = FastAPI()

client = openai.OpenAI(api_key="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")  # Replace with your actual key or use env var

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class FighterModel(BaseModel):
    name: str
    strength: int
    agility: int
    grappling_iq: int

class StartMatchRequest(BaseModel):
    f1: FighterModel
    f2: FighterModel
    belt_level: str

class TurnVsAI(BaseModel):
    match_id: str
    action_p1: str

def choose_ai_action(ai: Fighter, opponent: Fighter, belt_level: str, turn: int, log: list) -> str:
    legal_actions = [
    "takedown", "pull_guard", "pressure_pass", "sweep",
    "submit", "escape", "stand_up", "maintain_position",
    "feint", "snap_down", "knee_slide_pass", "shoulder_pressure",
    "armbar", "omoplata", "technical_standup", "rear_naked_choke",
    "mount_strikes", "hip_escape", "face_crank"
]


    last_ai_action = "None"
    for entry in reversed(log):
        if entry[1] == ai.name:
            last_ai_action = entry[2]
            break

    prompt = f"""
You are a Brazilian Jiu-Jitsu fighter in a turn-based game. You are a {belt_level} belt with the following style:

- White: cautious, defensive, sometimes makes bad decisions.
- Blue: balanced, reliable fundamentals, avoids big risks.
- Purple: mixes offense with strategy, good at timing.
- Brown: very strategic, smart positioning, calculated responses.
- Black: expert grappler, reads opponent, adapts, dominant.

Match State:
- Turn: {turn}
- Your Position: {ai.position}
- Your Fatigue: {ai.fatigue}
- Opponent Position: {opponent.position}
- Opponent Fatigue: {opponent.fatigue}
- Your Stats: {ai.stats}
- Opponent Stats: {opponent.stats}
- Your Previous Action: {last_ai_action}

Choose your next move from: {legal_actions}.
Do not repeat the same action unless it's the best strategic choice.
Respond with only your action (no extra words).
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )
    return response.choices[0].message.content.strip().lower()

@app.get("/")
def root():
    return {"message": "BJJ Turn-Based Game API is running!"}

@app.post("/start_match")
def start_match(request: StartMatchRequest, db: Session = Depends(get_db)):
    try:
        match_id = str(uuid4())
        fighter1 = Fighter(request.f1.name, request.f1.dict(exclude={"name"}))
        fighter2 = Fighter(request.f2.name, request.f2.dict(exclude={"name"}))
        game = BJJGame(fighter1, fighter2)

        db_match = Match(
            id=match_id,
            fighter1=vars(fighter1),
            fighter2=vars(fighter2),
            log=game.log,
            turn=game.turn,
            round=game.round,
            belt_level=request.belt_level
        )
        db.add(db_match)
        db.commit()

        return {
            "match_id": match_id,
            "message": "Match started!",
            "fighters": [fighter1.name, fighter2.name],
            "belt_level": request.belt_level
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/turn_vs_ai")
def run_turn_vs_ai(turn: TurnVsAI, db: Session = Depends(get_db)):
    db_match = db.query(Match).filter(Match.id == turn.match_id).first()
    if not db_match:
        raise HTTPException(status_code=404, detail="Match ID not found")

    fighter1 = Fighter(db_match.fighter1["name"], db_match.fighter1["stats"])
    fighter1.health = db_match.fighter1["health"]
    fighter1.fatigue = db_match.fighter1["fatigue"]
    fighter1.position = db_match.fighter1["position"]
    fighter1.score = db_match.fighter1["score"]

    fighter2 = Fighter(db_match.fighter2["name"], db_match.fighter2["stats"])
    fighter2.health = db_match.fighter2["health"]
    fighter2.fatigue = db_match.fighter2["fatigue"]
    fighter2.position = db_match.fighter2["position"]
    fighter2.score = db_match.fighter2["score"]

    game = BJJGame(fighter1, fighter2)
    game.log = db_match.log
    game.turn = db_match.turn
    game.round = db_match.round

    belt_level = db_match.belt_level
    ai_action = choose_ai_action(game.f2, game.f1, belt_level, game.turn, db_match.log)
    match_end = game.play_turn(turn.action_p1, ai_action)

    db_match.fighter1 = vars(game.f1)
    db_match.fighter2 = vars(game.f2)
    db_match.log = game.log
    db_match.turn = game.turn
    db_match.round = game.round
    db.commit()

    return {
        "turn": game.turn,
        "player_action": turn.action_p1,
        "ai_action": ai_action,
        "log": game.log[-3:],
        "match_end": match_end,
        "fighter1": vars(game.f1),
        "fighter2": vars(game.f2)
    }

@app.get("/state/{match_id}")
def get_game_state(match_id: str, db: Session = Depends(get_db)):
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if not db_match:
        raise HTTPException(status_code=404, detail="Match ID not found")

    return {
        "turn": db_match.turn,
        "round": db_match.round,
        "log": db_match.log,
        "fighter1": db_match.fighter1,
        "fighter2": db_match.fighter2,
        "belt_level": db_match.belt_level
    }
