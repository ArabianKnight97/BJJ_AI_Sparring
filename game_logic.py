import random

class Fighter:
    def __init__(self, name, stats):
        self.name = name
        self.stats = stats
        self.health = 100
        self.fatigue = 0
        self.score = 0
        self.position = "neutral"

    def apply_fatigue(self, amount):
        self.fatigue = min(100, self.fatigue + amount)

    def recover_fatigue(self, amount):
        self.fatigue = max(0, self.fatigue - amount)

    def apply_damage(self, amount):
        self.health = max(0, self.health - amount)

    def add_score(self, points):
        self.score += points

    def is_tired(self):
        return self.fatigue >= 60

    def is_submitted(self):
        return self.health <= 0

class ActionEngine:
    def __init__(self):
        self.legal_transitions = {
            "takedown": ["neutral"],
            "pull_guard": ["neutral"],
            "sweep": ["guard", "bottom"],
            "escape": ["guard", "bottom"],
            "submit": ["guard", "top", "dominant", "bottom"],
            "pressure_pass": ["top"],
            "maintain_position": ["top", "dominant"],
            "stand_up": ["guard", "bottom"],
            "hip_escape": ["bottom"],
            "face_crank": ["dominant"],
            "feint": ["neutral"],
            "snap_down": ["neutral"],
            "knee_slide_pass": ["top"],
            "shoulder_pressure": ["top", "dominant"],
            "armbar": ["guard"],
            "omoplata": ["guard"],
            "technical_standup": ["bottom"],
            "rear_naked_choke": ["dominant"],
            "mount_strikes": ["dominant"]
        }

    def evaluate(self, actor, opponent, action):
        if actor.position not in self.legal_transitions.get(action, []):
            return {
                "success": False,
                "result": f"Cannot perform {action} from {actor.position} position.",
                "fatigue": 0,
                "position": actor.position
            }

        iq = actor.stats["grappling_iq"]
        strength = actor.stats["strength"]
        fatigue_penalty = actor.fatigue // 3
        roll = random.randint(-10, 10)
        success_chance = iq + roll - fatigue_penalty + (opponent.fatigue // 5)

        result = {
            "success": False,
            "result": f"{action} failed.",
            "fatigue": 0,
            "position": actor.position,
            "score": 0,
            "damage": 0
        }

        if action == "feint":
            result.update({
                "success": True,
                "result": "Feint successful — you confused your opponent!",
                "fatigue": 3,
                "score": 0
            })

        elif action == "snap_down":
            if success_chance > 55:
                result.update({
                    "success": True,
                    "result": "Snap down successful — front headlock position gained!",
                    "fatigue": 5,
                    "score": 2,
                    "position": "top"
                })

        elif action == "knee_slide_pass":
            if success_chance + strength // 5 > 65:
                result.update({
                    "success": True,
                    "result": "Knee slide pass successful — advanced to mount!",
                    "fatigue": 10,
                    "score": 3,
                    "position": "dominant"
                })

        elif action == "shoulder_pressure":
            result.update({
                "success": True,
                "result": "Applied shoulder pressure — opponent is tiring.",
                "fatigue": 6,
                "score": 1
            })

        elif action == "armbar":
            if success_chance > 75:
                result.update({
                    "success": True,
                    "result": "Armbar locked in!",
                    "fatigue": 14,
                    "score": 4,
                    "damage": 100
                })

        elif action == "omoplata":
            if success_chance > 70:
                result.update({
                    "success": True,
                    "result": "Omoplata swept and pressured opponent!",
                    "fatigue": 12,
                    "score": 3,
                    "position": "top"
                })

        elif action == "technical_standup":
            result.update({
                "success": True,
                "result": "Technical stand-up successful — returned to neutral.",
                "fatigue": 8,
                "position": "neutral"
            })

        elif action == "rear_naked_choke":
            if success_chance > 75 and opponent.is_tired():
                result.update({
                    "success": True,
                    "result": "Rear naked choke — opponent tapped!",
                    "fatigue": 18,
                    "score": 5,
                    "damage": 100
                })

        elif action == "maintain_position":
            result.update({
                "success": True,
                "result": "Maintained position and rested.",
                "fatigue": -5,
                "score": 1
            })

        elif action == "mount_strikes":
            result.update({
                "success": True,
                "result": "Mounted strikes landed — damage and points scored.",
                "fatigue": 10,
                "score": 3,
                "damage": 20
            })

        elif action == "hip_escape":
            result["fatigue"] = 7
            if success_chance + actor.stats["agility"] // 4 > 60:
                result.update({
                    "success": True,
                    "result": "Hip escape successful — created space and recovered guard.",
                    "position": "guard"
                })

        elif action == "face_crank":
            result.update({
                "success": True,
                "result": "Face crank applied — opponent fatigued.",
                "fatigue": 6,
                "score": 1,
                "damage": 0
            })
            opponent.apply_fatigue(10)

        return result

class BJJGame:
    def __init__(self, fighter1, fighter2):
        self.f1 = fighter1
        self.f2 = fighter2
        self.turn = 0
        self.round = 1
        self.max_turns = 20
        self.log = []
        self.engine = ActionEngine()

    def play_turn(self, action_p1, action_p2):
        if self.f1.is_submitted():
            return f"{self.f2.name} wins by submission."
        if self.f2.is_submitted():
            return f"{self.f1.name} wins by submission."

        self.turn += 1

        prev_pos1 = self.f1.position
        prev_pos2 = self.f2.position

        result_p1 = self.engine.evaluate(self.f1, self.f2, action_p1)
        result_p2 = self.engine.evaluate(self.f2, self.f1, action_p2)

        if action_p1 == action_p2:
            if self.f1.fatigue < self.f2.fatigue:
                self.update_fighter_state(self.f1, self.f2, result_p1)
                self.log.append((self.turn, self.f1.name, action_p1, result_p1["result"]))
                self.log.append((self.turn, self.f2.name, action_p2, "Move lost due to fatigue tie-break."))
            elif self.f2.fatigue < self.f1.fatigue:
                self.update_fighter_state(self.f2, self.f1, result_p2)
                self.log.append((self.turn, self.f1.name, action_p1, "Move lost due to fatigue tie-break."))
                self.log.append((self.turn, self.f2.name, action_p2, result_p2["result"]))
            else:
                self.f1.position = prev_pos1
                self.f2.position = prev_pos2
                self.log.append((self.turn, self.f1.name, action_p1, "Tied move. Fighters break and reset."))
                self.log.append((self.turn, self.f2.name, action_p2, "Tied move. Fighters break and reset."))
        else:
            self.update_fighter_state(self.f1, self.f2, result_p1)
            self.log.append((self.turn, self.f1.name, action_p1, result_p1["result"]))

            self.update_fighter_state(self.f2, self.f1, result_p2)
            self.log.append((self.turn, self.f2.name, action_p2, result_p2["result"]))

        if self.f1.position in ["top", "dominant"]:
            self.f2.position = "bottom"
        elif self.f2.position in ["top", "dominant"]:
            self.f1.position = "bottom"
        elif self.f1.position == "bottom":
            self.f2.position = "top"
        elif self.f2.position == "bottom":
            self.f1.position = "top"

        if self.turn >= self.max_turns:
            return self.judge_decision()

    def update_fighter_state(self, actor, opponent, outcome):
        if outcome["fatigue"] > 0:
            actor.apply_fatigue(outcome["fatigue"])
        elif outcome["fatigue"] < 0:
            actor.recover_fatigue(abs(outcome["fatigue"]))

        if outcome.get("score"):
            actor.add_score(outcome["score"])

        if outcome.get("damage"):
            opponent.apply_damage(outcome["damage"])

        # Apply additional fatigue to opponent if move was successful and not passive
        if outcome.get("success") and outcome["result"] != "Tied move. Fighters break and reset.":
            opponent.apply_fatigue(5)

        actor.position = outcome.get("position", actor.position)

    def judge_decision(self):
        if self.f1.score > self.f2.score:
            return f"{self.f1.name} wins by decision."
        elif self.f2.score > self.f1.score:
            return f"{self.f2.name} wins by decision."
        return "Draw."
