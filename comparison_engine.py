import random
import os
from google import genai

api_key = os.environ.get('GEMINI_API_KEY')
client = genai.Client(api_key='AIzaSyCTOHSpQkj6PbEKTYnmvfCdT6FKBQibo_s')

athletes = {
    'Usain Bolt': {
        'Sprinting': 10, 'Strength': 3, 'Height': 7,
        'Endurance': 8, 'Agility': 9,
    },
    'Michael Phelps': {
        'Sprinting': 5, 'Strength': 5, 'Height': 8,
        'Endurance': 10, 'Agility': 6,
    }
}

activity =   {
    'name': 'Fastest time to down a pint',
    'attributes': { 'Height': 0.4, 'Weight': 0.3, 'Water': 0.6, 'Speed': 0.5}
  }

def generate_commentary(athlete1: str, athlete2: str, activity_name: str, winner: str, total: float):
    prompt = (
        f'Write a funny, dramatic commentary about a competition between '
        f'{athlete1} and {athlete2} in {activity_name}. '
        f'{winner} won. The larger the difference ({total:.2f}), the more dramatic and humorous it should be. '
        f'Keep it 2-3 sentences and make it funny.'
    )
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text


def calculate_weighted_score(athlete_stats: dict, activity_weights: dict) -> float:
    total = 0
    for attribute, weight in activity_weights.items():
        # multiply athlete attribute by weight if it exists
        athlete_value = athlete_stats.get(attribute, 0)
        total += athlete_value * weight

    # add randomness
    total += random.uniform(-2,2)
    return total

def compare_athletes(athlete1_name: str, athlete2_name: str, activity: dict):
    activity_name = activity['name']
    weights = activity['attributes']

    athlete1 = athletes.get(athlete1_name)
    athlete2 = athletes.get(athlete2_name)

    if not athlete1 or not athlete2:
        return 'One or both athletes not found'
    
    score1 = calculate_weighted_score(athlete1, weights)
    score2 = calculate_weighted_score(athlete2, weights)
    total = abs(score1 - score2)

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

if __name__ == '__main__':
    athlete1 = 'Usain Bolt'
    athlete2 = 'Michael Phelps'
    activity_selected = activity

    result = compare_athletes(athlete1, athlete2, activity_selected)
    winner_name = result['winner']
    total_diff = result['difference']
    commentary = generate_commentary(athlete1, athlete2, activity_selected['name'], winner_name, total_diff)

    print(result)
    print('\nFunny Commentary: ')
    print(commentary)