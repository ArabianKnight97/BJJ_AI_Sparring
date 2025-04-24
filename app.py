from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from uuid import uuid4
from typing import List
from sqlalchemy.orm import Session
from db import SessionLocal, Match
from game_logic import Fighter, BJJGame
import requests
import json

app = FastAPI()

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

class TurnVsAI(BaseModel):
    match_id: str
    action_p1: str

def choose_ai_action(ai: Fighter, opponent: Fighter) -> str:
    url = "https://nzn6xl9x7e.execute-api.us-east-1.amazonaws.com/choose"  # Your deployed Lambda API URL

    payload = {
        "self_fighter": {
            "position": ai.position,
            "fatigue": ai.fatigue,
            "stats": ai.stats
        },
        "opponent": {
            "position": opponent.position,
            "fatigue": opponent.fatigue,
            "stats": opponent.stats
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)['chosen_action']
        else:
            print(f"Lambda error ({response.status_code}): {response.text}")
            return "maintain_position"
    except Exception as e:
        print("Lambda call failed:", e)
        return "maintain_position"

@app.get("/")
def root():
    return {"message": "BJJ Turn-Based Game API is running!"}

@app.post("/start_match")
def start_match(request: StartMatchRequest, db: Session = Depends(get_db)):
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
        round=game.round
    )
    db.add(db_match)
    db.commit()

    return {
        "match_id": match_id,
        "message": "Match started!",
        "fighters": [fighter1.name, fighter2.name]
    }

@app.post("/turn_vs_ai")
def run_turn_vs_ai(turn: TurnVsAI, db: Session = Depends(get_db)):
    db_match = db.query(Match).filter(Match.id == turn.match_id).first()
    if not db_match:
        raise HTTPException(status_code=404, detail="Match ID not found")

    fighter1 = Fighter(db_match.fighter1["name"], db_match.fighter1["stats"])
    fighter2 = Fighter(db_match.fighter2["name"], db_match.fighter2["stats"])
    game = BJJGame(fighter1, fighter2)
    game.log = db_match.log
    game.turn = db_match.turn
    game.round = db_match.round

    ai_action = choose_ai_action(game.fighter2, game.fighter1)
    game.simulate_turn(turn.action_p1, ai_action)

    # --- Log training data for SageMaker ---
    try:
        with open("ai_training_data.jsonl", "a") as f:
            json.dump({
                "self_fighter": {
                    "position": game.fighter2.position,
                    "fatigue": game.fighter2.fatigue,
                    "stats": game.fighter2.stats
                },
                "opponent": {
                    "position": game.fighter1.position,
                    "fatigue": game.fighter1.fatigue,
                    "stats": game.fighter1.stats
                },
                "action_taken": ai_action
            }, f)
            f.write("\n")
    except Exception as e:
        print("Logging failed:", e)

    # Save updated match state to DB
    db_match.fighter1 = vars(game.fighter1)
    db_match.fighter2 = vars(game.fighter2)
    db_match.log = game.log
    db_match.turn = game.turn
    db_match.round = game.round
    db.commit()

    return {
        "turn": game.turn,
        "player_action": turn.action_p1,
        "ai_action": ai_action,
        "log": game.log[-3:],
        "fighter1": vars(game.fighter1),
        "fighter2": vars(game.fighter2)
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
        "fighter2": db_match.fighter2
    }
