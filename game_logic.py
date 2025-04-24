import random

class Fighter:
    def __init__(self, name, stats):
        self.name = name
        self.stats = stats
        self.health = 100
        self.fatigue = 0
        self.score = 0
        self.position = 'neutral'

    def apply_fatigue(self, amount):
        self.fatigue = min(100, self.fatigue + amount)

    def recover(self, amount):
        self.fatigue = max(0, self.fatigue - amount)

    def is_tired(self):
        return self.fatigue > 60

    def add_score(self, points):
        self.score += points


class BJJGame:
    def __init__(self, fighter1, fighter2):
        self.fighter1 = fighter1
        self.fighter2 = fighter2
        self.turn = 0
        self.round = 1
        self.turns_per_round = 10
        self.in_rest_phase = False
        self.log = []

    def simulate_turn(self, action_p1, action_p2):
        if self.turn >= 20:
            self.log.append((self.turn, "Match", "ended", self.judge_decision()))
            return

        self.turn += 1
        outcome_p1 = self.evaluate_action(self.fighter1, self.fighter2, action_p1)
        outcome_p2 = self.evaluate_action(self.fighter2, self.fighter1, action_p2)

        self.resolve_outcomes(self.fighter1, self.fighter2, outcome_p1, outcome_p2)

        if self.fighter1.position == "submitted":
            self.log.append((self.turn, "Match", "ended", f"{self.fighter2.name} wins by submission!"))
            return
        elif self.fighter2.position == "submitted":
            self.log.append((self.turn, "Match", "ended", f"{self.fighter1.name} wins by submission!"))
            return

        self.log.append((self.turn, self.fighter1.name, action_p1, outcome_p1["result"]))
        self.log.append((self.turn, self.fighter2.name, action_p2, outcome_p2["result"]))

        print(f"Turn {self.turn}: Player - {self.fighter1.position}, AI - {self.fighter2.position}")

        if self.turn % self.turns_per_round == 0:
            self.rest_phase()
            self.round += 1
            self.log.append((self.turn, "Rest", "Round Break", f"Entering round {self.round}"))

    def rest_phase(self):
        self.fighter1.recover(15)
        self.fighter2.recover(15)
        self.in_rest_phase = False

    def judge_decision(self):
        if self.fighter1.score > self.fighter2.score:
            return f"{self.fighter1.name} wins by decision!"
        elif self.fighter2.score > self.fighter1.score:
            return f"{self.fighter2.name} wins by decision!"
        else:
            return "Draw!"

    def compute_position_bonus(self, actor, opponent, action):
        bonus = 0
        if action == "submit":
            if actor.position == "dominant":
                bonus += 10
            elif actor.position in ["guard", "bottom"]:
                bonus -= 10
        elif action == "pressure_pass":
            if actor.position == "dominant":
                bonus += 5
        elif action == "sweep":
            if actor.position == "guard":
                bonus += 5
            if opponent.position == "dominant":
                bonus -= 5
        elif action == "escape":
            if actor.position == "bottom" and opponent.position == "dominant":
                bonus -= 10
        return bonus

    def evaluate_action(self, actor, opponent, action):
        iq = actor.stats['grappling_iq']
        agi = actor.stats['agility']
        str_ = actor.stats['strength']
        fatigue_penalty = actor.fatigue // 3
        position_bonus = self.compute_position_bonus(actor, opponent, action)

        base_success = iq + position_bonus + random.randint(-10, 10) - fatigue_penalty
        fatigue_cost = 0
        result = ""
        position_change = None

        # Safeguards
        if action == "takedown" and actor.position != "neutral":
            return {"success": False, "result": "Takedown not allowed unless standing.", "fatigue": 0, "position": actor.position}
        if action == "sweep" and actor.position not in ["bottom", "guard"]:
            return {"success": False, "result": "Sweep only allowed from bottom or guard.", "fatigue": 0, "position": actor.position}
        if action == "escape" and actor.position not in ["bottom", "guard"]:
            return {"success": False, "result": "Escape only allowed from bottom or guard.", "fatigue": 0, "position": actor.position}
        if action == "pull_guard" and actor.position != "neutral":
            return {"success": False, "result": "Can only pull guard while standing.", "fatigue": 0, "position": actor.position}
        if action == "stand_up" and actor.position not in ["bottom", "guard"]:
            return {"success": False, "result": "Stand up only possible from bottom or guard.", "fatigue": 0, "position": actor.position}
        if action == "maintain_position" and actor.position not in ["top", "dominant"]:
            return {"success": False, "result": "Can only maintain position if in control.", "fatigue": 0, "position": actor.position}

        # Action logic
        if action == "submit":
            fatigue_cost = 15
            if base_success > 65 and opponent.is_tired():
                opponent.health -= 40
                result = "Submission successful!"
                position_change = "submitted"
                return {"success": True, "result": result, "fatigue": fatigue_cost, "score": 4, "position": position_change}
            else:
                result = "Submission failed."

        elif action == "sweep":
            fatigue_cost = 8
            if base_success > 55:
                result = "Sweep successful!"
                position_change = "top"
                return {"success": True, "result": result, "fatigue": fatigue_cost, "score": 2, "position": position_change}
            else:
                result = "Sweep failed."

        elif action == "takedown":
            fatigue_cost = 10
            if base_success > 60:
                result = "Takedown successful!"
                position_change = "top"
                return {"success": True, "result": result, "fatigue": fatigue_cost, "score": 2, "position": position_change}
            else:
                result = "Takedown failed."

        elif action == "pass_guard":
            fatigue_cost = 8
            if opponent.position == "guard" and base_success > 60:
                result = "Guard passed!"
                position_change = "top"
                return {"success": True, "result": result, "fatigue": fatigue_cost, "score": 3, "position": position_change}
            else:
                result = "Pass failed."

        elif action == "pressure_pass":
            fatigue_cost = 12
            if opponent.position == "guard" and base_success > 70 and str_ > 65:
                result = "Powerful pressure pass!"
                position_change = "dominant"
                return {"success": True, "result": result, "fatigue": fatigue_cost, "score": 3, "position": position_change}
            else:
                result = "Failed pressure pass."

        elif action == "stand_up":
            fatigue_cost = 4
            result = "Returned to standing."
            position_change = "neutral"

        elif action == "pull_guard":
            fatigue_cost = 5
            result = "Pulled guard."
            position_change = "guard"

        elif action == "escape":
            fatigue_cost = 6
            if base_success > 60:
                result = "Escaped to standing!"
                position_change = "neutral"
            else:
                result = "Escape failed."

        elif action == "maintain_position":
            fatigue_cost = -7
            result = "Rested and held position."

        else:
            result = "Unknown action."

        # Ensure position continuity
        if position_change is None:
            position_change = actor.position

        return {
            "success": False,
            "result": result,
            "fatigue": fatigue_cost,
            "position": position_change
        }

    def resolve_outcomes(self, p1, p2, o1, o2):
        if o1["fatigue"] > 0:
            p1.apply_fatigue(o1["fatigue"])
        elif o1["fatigue"] < 0:
            p1.recover(abs(o1["fatigue"]))

        if o2["fatigue"] > 0:
            p2.apply_fatigue(o2["fatigue"])
        elif o2["fatigue"] < 0:
            p2.recover(abs(o2["fatigue"]))

        if o1.get("score"):
            p1.add_score(o1["score"])
        if o2.get("score"):
            p2.add_score(o2["score"])

        if o1.get("position") == "submitted":
            p2.position = "submitted"
        elif o2.get("position") == "submitted":
            p1.position = "submitted"
        else:
            p1.position = o1.get("position", p1.position)
            p2.position = o2.get("position", p2.position)
