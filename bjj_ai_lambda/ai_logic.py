def ai_choose_action(self_fighter, opponent):
    pos = self_fighter["position"]
    tired = self_fighter["fatigue"] > 60
    iq = self_fighter["stats"]["grappling_iq"]
    str_ = self_fighter["stats"]["strength"]
    agi = self_fighter["stats"]["agility"]

    if pos in ["top", "dominant"] and opponent["fatigue"] > 60 and iq > 60:
        return "submit"
    if pos in ["guard", "bottom"] and agi > 55:
        return "sweep"
    if pos == "neutral" and str_ > 50:
        return "takedown"
    if pos == "top" and str_ > 60:
        return "pressure_pass"
    if tired:
        return "maintain_position"
    if pos == "top":
        return "pass_guard"
    elif pos == "neutral":
        return "pull_guard"
    elif pos in ["bottom", "guard"]:
        return "escape"
    return "maintain_position"
