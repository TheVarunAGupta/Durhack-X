from flask import Flask, render_template, request, jsonify
import random
import os
from dotenv import load_dotenv
from google import genai
import json
import math

load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    raise ValueError('Missing GEMINI_API_KEY in environment!')
client = genai.Client(api_key=api_key)

with open('static/athelete_attributes.json', 'r') as f:
    data = json.load(f)

athletes = {ath['name']: ath['attributes'] for ath in data['athletes']}

with open('static/activities.json', 'r') as f:
    data = json.load(f)

activities = {}
for act in data['activities']:
    attributes = {k.lower(): v for k, v in act['attributes'].items()}
    activities[act['activity']] = {
        'name': act['activity'],
        'attributes': attributes
    }

def generate_commentary(athlete1: str, athlete2: str, activity_name: str, winner: str, total: float):
    prompt = (
        f'Write a funny, dramatic commentary about a competition between '
        f'{athlete1} and {athlete2} in {activity_name}. '
        f'{winner} won. (For context: the difference between their scores was {total:.2f}, '
        f'but do not include this number in your commentary.) '
        f'Keep it 2-3 sentences and make it funny.'
    )
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text


# def calculate_weighted_score(athlete_stats: dict, activity_weights: dict) -> float:
#     total = 0
#     for attribute, weight in activity_weights.items():
#         # multiply athlete attribute by weight if it exists
#         athlete_value = athlete_stats.get(attribute, 0)
#         total += athlete_value * weight

#     # add randomness
#     total += random.uniform(-2,2)
#     return total

def calculate_weighted_score(athlete_stats: dict, activity_weights: dict) -> float:
    total = 0
    # calculate sum of absolute weights for normalisation, avoid division by zero
    weight_sum = sum(abs(w) for w in activity_weights.values()) or 1

    for attribute, weight in activity_weights.items():
        athlete_value = athlete_stats.get(attribute, 0)
        # non linear scaling to reward higher attribute values, still works with negative values
        scaled_value = math.copysign(abs(athlete_value) ** 1.2, athlete_value)
        # add variation per attribute to simulate a bad/good day
        variation = random.uniform(0.9, 1.1)
        total += (scaled_value * weight * variation)

        # normalise by weighted sum
        total = total / weight_sum
        # add some randomness
        total += random.gauss(0, 1.5) # gaussian noise with mean 0 and stddev 1.5
    return total

def compare_athletes(athlete1_name: str, athlete2_name: str, activity: dict):
    activity_name = activity['name']
    weights = activity['attributes']

    athlete1 = athletes.get(athlete1_name)
    athlete2 = athletes.get(athlete2_name)

    if not athlete1 or not athlete2:
        return 'One or both athletes not found'
    
    score1 = calculate_weighted_score(athlete1, weights)
    # print(f' score1: {score1}')
    score2 = calculate_weighted_score(athlete2, weights)
    # print(f' score2: {score2}')
    total = abs(score1 - score2)
    # print(f' total: {total}')

    if score1 > score2:
        winner = athlete1_name
    elif score2 > score1:
        winner = athlete2_name
    else:
        winner = 'Draw'

    results =  {
        'activity': activity_name,
        'athlete1': athlete1_name,
        'score1': score1,
        'athlete2': athlete2_name,
        'score2': score2,
        'difference': total,
        'winner': winner,
    }
    return results

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('crystalBall.html', athletes=list(athletes.keys()), activities=list(activities.keys()))

@app.route('/compare', methods=['POST'])
def compare():
    data = request.json
    athlete1 = data.get('athlete1')
    athlete2 = data.get('athlete2')
    activity_name = data.get('activity')

    if not athlete1 or not athlete2 or not activity_name:
        return jsonify({'error': 'Missing selection'}), 400
    
    activity_selected = activities.get(activity_name)
    result = compare_athletes(athlete1, athlete2, activity_selected)
    if 'error' in result:
        return jsonify(result), 400

    winner_name = result['winner']
    total_diff = result['difference']

    commentary = generate_commentary(athlete1, athlete2, activity_name, winner_name, total_diff)

    result['commentary'] = commentary
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5003)

# if __name__ == '__main__':
#     athlete1 = 'David Attenborough'
#     athlete2 = 'Scarlett Johansson'
#     activity_selected = activities['Egg and Spoon']

#     result = compare_athletes(athlete1, athlete2, activity_selected)
#     winner_name = result['winner']
#     total_diff = result['difference']
#     commentary = generate_commentary(athlete1, athlete2, activity_selected['name'], winner_name, total_diff)

#     print(result)
#     print('\nFunny Commentary: ')
#     print(commentary)