import requests
import argparse
from datetime import datetime

def get_rank_info(team_id):
    """
    Utility function to get team rank and adjusted points
    - Input params: Team ID (type:str)
    - Output params: Team rank and adjusted points

    ** Handles rounding to 2 decimal places
    """

    url = "https://delivery.chalk247.com/team_rankings/NFL.json?api_key=74db8efa2a6db279393b433d97c2bc843f8e32b0"
    result = requests.get(url).json()
    dataset = result.get('results').get('data')
    for data in dataset:
        if data.get('team_id') == team_id:
            return data.get('rank'), round(float(data.get('adjusted_points')), 2)
    return None


def build_queryset(start_date, end_date, league):
    """
    Main function to build the result queryset
    - Input params: start date (type: str)
                    end date (type: str)
                    league type (typr:str)
    - Output: List of fields specified in the problem set

    ** Errors, if any, are assumed to be caught by API. Hence, printed as is.
    ** Handles conversion of matchdate to DD-MM-YYYY format. Assumes that API always returns datetime
        in YYYY-MM-DD HH:MM format
    """

    final_queryset = []
    url = "https://delivery.chalk247.com/scoreboard/"+ str(league) + \
    "/"+ str(start_date) +"/"+ str(end_date) +".json?api_key=74db8efa2a6db279393b433d97c2bc843f8e32b0"

    r = requests.get(url)

    result = r.json().get('results')
    if result.get('error'):
        return result.get('error').split('\'')[1]

    for key, value in result.items():
        if value:
            for inner_key, inner_value in value.get('data').items():
                home_team_rank, home_team_score = get_rank_info(str(inner_value.get('home_team_id')))
                away_team_rank, away_team_score = get_rank_info(str(inner_value.get('away_team_id')))

                event_date = datetime.strptime(inner_value.get('event_date'), '%Y-%m-%d %H:%M')
                formated_date = event_date.strftime('%d-%m-%Y')
                formated_time = event_date.strftime('%H:%M')

                final_queryset.append({
                    "event_id": str(inner_value.get('event_id')),
                    "event_date": str(formated_date),
                    "event_time": str(formated_time),
                    "away_team_id": str(inner_value.get('away_team_id')),
                    "away_nick_name": str(inner_value.get('away_nick_name')),
                    "away_city": str(inner_value.get('away_city')),
                    "away_rank": str(away_team_rank),
                    "away_rank_points": str(away_team_score),
                    "home_team_id": str(inner_value.get('home_team_id')),
                    "home_nick_name": str(inner_value.get('home_nick_name')),
                    "home_city": str(inner_value.get('home_city')),
                    "home_rank": str(home_team_rank),
                    "home_rank_points": str(home_team_score),
                    })
    return final_queryset


# print(build_queryset('2020-01-12', '2020-01-19', 'NFL'))
parser = argparse.ArgumentParser()
parser.add_argument("--start_date")
parser.add_argument("--end_date")
parser.add_argument("--league")
args = parser.parse_args()

if args.start_date and args.end_date and args.league:
    print(build_queryset(args.start_date, args.end_date, args.league))