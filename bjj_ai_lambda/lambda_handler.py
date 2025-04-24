import json
from ai_logic import ai_choose_action

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        fighter = body.get('self_fighter')
        opponent = body.get('opponent')

        if not fighter or not opponent:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing fighter or opponent data"})
            }

        action = ai_choose_action(fighter, opponent)

        return {
            "statusCode": 200,
            "body": json.dumps({"chosen_action": action})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
