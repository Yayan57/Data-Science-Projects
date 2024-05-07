import pandas as pd
import re
from bs4 import BeautifulSoup
import glob

# Teams to track and the required order
teams_to_track = ['Houston Astros', 'Oakland Athletics', 'Texas Rangers', 'Seattle Mariners', 'Los Angeles Angels']
required_order = ['Seattle Mariners', 'Houston Astros', 'Oakland Athletics', 'Texas Rangers', 'Los Angeles Angels']

# Regular expression to extract numbers
score_regex = re.compile(r'\((\d+)\)')

# Data collection for DataFrame and tracking dates
data = []
special_dates = []
season_records = {}

# Function to normalize team names based on year
def normalize_team_name(team, year):
    if year in ['2013', '2014', '2015'] and team == 'LA Angels of Anaheim':
        return 'Los Angeles Angels'
    return team

# Loop through all HTML files using glob
for file_path in glob.glob('*.html'):
    # Extract the season (year) from the file name
    season = file_path.split('_')[0]

    # Initialize records dictionary for each team
    records = {team: {'Wins': 0, 'Losses': 0} for team in teams_to_track}

    # Load HTML from each file
    with open(file_path, 'r') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Process each date block
    for date_block in soup.find_all('h3'):
        date = date_block.get_text()

        games = date_block.find_next_siblings('p', class_='game', limit=len(date_block.find_next_siblings('h3')))

        for game in games:
            parts = game.find_all('a')
            if len(parts) < 2:
                continue

            team1 = normalize_team_name(parts[0].get_text(), season)
            team2 = normalize_team_name(parts[1].get_text(), season)

            score1 = int(score_regex.search(parts[0].next_sibling).group(1))
            score2 = int(score_regex.search(parts[1].next_sibling).group(1))

            # Update records for each team if they are being tracked
            for team, score, opponent_score in [(team1, score1, score2), (team2, score2, score1)]:
                if team in teams_to_track:
                    if score > opponent_score:
                        records[team]['Wins'] += 1
                    else:
                        records[team]['Losses'] += 1

                    # Append each update to the data list
                    data.append({'Season': season, 'Date': date, 'Team': team, 'Wins': records[team]['Wins'], 'Losses': records[team]['Losses']})

        # Check if all teams have played at least one game
        if all(records[team]['Wins'] + records[team]['Losses'] > 0 for team in teams_to_track):
            # Check ranking order
            sorted_teams = sorted(records.items(), key=lambda x: x[1]['Wins'] / (x[1]['Wins'] + x[1]['Losses']), reverse=True)
            sorted_team_names = [team[0] for team in sorted_teams]
            if sorted_team_names == required_order:
                special_dates.append(f"{season}: {date}")

    # Save each season's final records
    season_records[season] = records

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(data)

# Pivot the DataFrame to have seasons and dates as rows and teams as columns with sub-columns for Wins and Losses
df = df.pivot_table(index=['Season', 'Date'], columns='Team', values=['Wins', 'Losses'], aggfunc='last')


# Print each team's final record per season, sorted by winning percentage
print("\nFinal Records per Team per Season (sorted by Winning Percentage):")
for season, records in season_records.items():
    print(f"\nSeason: {season}")
    sorted_records = sorted(records.items(), key=lambda x: x[1]['Wins'] / (x[1]['Wins'] + x[1]['Losses']) if (x[1]['Wins'] + x[1]['Losses']) > 0 else 0, reverse=True)
    for team, record in sorted_records:
        win_percentage = record['Wins'] / (record['Wins'] + record['Losses']) if (record['Wins'] + record['Losses']) > 0 else 0
        print(f"{team}: Wins - {record['Wins']}, Losses - {record['Losses']}, Win Percentage - {win_percentage:.3f}")

# Print special dates
print("\nDays when the AL West spelt Shasta:")
for date in special_dates:
    print(date)
