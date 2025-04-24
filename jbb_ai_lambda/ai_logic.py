def ai_choose_action(self_fighter, opponent):
    pos = self_fighter.position
    tired = self_fighter.fatigue > 60
    iq = self_fighter.stats['grappling_iq']
    str_ = self_fighter.stats['strength']
    agi = self_fighter.stats['agility']

    # Prioritize submissions if opponent is tired and AI has dominant/top position
    if pos in ["top", "dominant"] and opponent.is_tired() and iq > 60:
        return "submit"

    # Try to sweep if on bottom and AI has decent agility
    if pos in ["guard", "bottom"] and agi > 55:
        return "sweep"

    # If standing, takedown is ideal
    if pos == "neutral" and str_ > 50:
        return "takedown"

    # If on top and strong, go for pressure pass
    if pos == "top" and str_ > 60:
        return "pressure_pass"

    # If fatigued, recover
    if tired:
        return "maintain_position"

    # Default: aggressive pass attempt or safe score action
    if pos == "top":
        return "pass_guard"
    elif pos == "neutral":
        return "pull_guard"
    elif pos in ["bottom", "guard"]:
        return "escape"
    
    return "maintain_position"
