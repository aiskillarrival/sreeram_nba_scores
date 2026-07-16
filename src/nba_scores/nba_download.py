import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder


def download_nba_scores(season="2025-26"):
    print(
        f"Connecting to NBA.com and downloading games for the {season} season...")

    try:
        # Initialize LeagueGameFinder for NBA games (League ID '00' is NBA)
        game_finder = leaguegamefinder.LeagueGameFinder(
            season_nullable=season,
            league_id_nullable="00"
        )

        # Get the raw dataframe
        raw_games = game_finder.get_data_frames()[0]

        # Ensure SEASON_ID is treated as a string
        raw_games['SEASON_ID'] = raw_games['SEASON_ID'].astype(str)

        # Filter for regular season ('2' prefix) and playoff games ('4' prefix)
        games = raw_games[
            raw_games['SEASON_ID'].str.startswith(('2', '4'))].copy()

        # NBA.com returns two rows per game (one for home, one for away).
        # Split these and merge them so each game occupies a single row.
        # Home matchups contain 'vs.', away matchups contain '@'
        home_games = games[~games['MATCHUP'].str.contains('@')]
        away_games = games[games['MATCHUP'].str.contains('@')]

        # Merge home and away dataframes on GAME_ID
        merged = pd.merge(
            home_games[['GAME_ID', 'GAME_DATE', 'TEAM_NAME', 'PTS', 'WL']],
            away_games[['GAME_ID', 'TEAM_NAME', 'PTS', 'WL']],
            on='GAME_ID',
            suffixes=('_HOME', '_AWAY')
        )

        # Format and rename columns
        merged = merged.rename(columns={
            'GAME_DATE': 'Date',
            'TEAM_NAME_HOME': 'Home Team',
            'PTS_HOME': 'Home Score',
            'TEAM_NAME_AWAY': 'Away Team',
            'PTS_AWAY': 'Away Score',
            'WL_HOME': 'Home Team Result'
        })

        # Sort chronologically by game date
        merged = merged.sort_values(by='Date', ascending=True)

        # Reorder columns
        output_df = merged[
            ['Date', 'Home Team', 'Home Score', 'Away Team', 'Away Score',
             'Home Team Result']]

        # Save to CSV
        file_name = f"nba_scores_{season.replace('-', '_')}.csv"
        output_df.to_csv(file_name, index=False)

        print(f"Success! {len(output_df)} game scores saved to '{file_name}'")
        print("\nPreview of downloaded scores:")
        print(output_df.head(10).to_string(index=False))

    except Exception as e:
        print(f"An error occurred: {e}")
        print(
            "Tip: If you're blocked, NBA.com might be rate-limiting your IP. Try running again in a few minutes.")


if __name__ == "__main__":
    # Downloads the completed 2025-26 season games played in 2026
    download_nba_scores("2025-26")