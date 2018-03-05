from team import Team

STAT_MAP = {'1': 'goals', '2': 'assists', '4': 'plus_minus',
            '8': 'power_play_points', '11': 'short-handed-points',
            '14': 'shots', '31': 'hits', '32': 'blocks',
            '19': 'wins', '20': 'losses', '22': 'goals_against',
            '25': 'saves', '27': 'shutouts'}




def map_stats(stats_json):
    stat_map = {}
    for stat in stats_json:
        name = STAT_MAP[stat['stat']['stat_id']]
        value = stat['stat']['value']
        # Add key-value pair of stat:value to map
        stat_map[name] = value
    return stat_map


class Standings:
    def __init__(self, teams, teams_stats, teams_standings):
        self.teams = teams
        self.teams_stats = teams_stats
        self.teams_standings = teams_standings

    @staticmethod
    def parse_standings(standings_json):
        __teams = {}
        __teams_stats = {}
        __teams_standings = {}

        standings = standings_json['fantasy_content']
        teams = standings['league'][1]['standings'][0]['teams']
        for t in teams:
            if t == 'count':
                continue
            team_base = teams[t]['team']
            __teams[t] = Team.parse_sub_resource(team_base[0])
            __teams_stats[t] = TeamStats.parse_sub_resource(team_base[1])
            __teams_standings[t] = TeamStandings.parse_sub_resource(team_base[2])

        return Standings(__teams, __teams_stats, __teams_standings)


class TeamStats:
    def __init__(self, coverage_type, season, stats, points):
        self.coverage_type = coverage_type
        self.season = season
        self.stats = stats
        self.points = points

    @staticmethod
    def parse_sub_resource(team_stats_json):
        team_stats = team_stats_json['team_stats']
        __coverage_type = team_stats['coverage_type']
        __season = team_stats['season']
        __stats = map_stats(team_stats['stats'])
        __points = team_stats_json['team_points']['total']

        return TeamStats(__coverage_type, __season, __stats, __points)


class TeamStandings:
    def __init__(self, rank, points_for, points_against, playoff_seed,
                 wins, losses, ties, percentage):
        self.rank = rank
        self.points_for = points_for
        self.points_against = points_against
        self.playoff_seed = playoff_seed
        self.wins = wins
        self.losses = losses
        self.ties = ties
        self.percentage = percentage

    @staticmethod
    def parse_sub_resource(team_standings_json):
        team_standings = team_standings_json['team_standings']
        __rank = team_standings['rank']
        __points_for = team_standings['points_for']
        __points_against = team_standings['points_against']
        __playoff_seed = team_standings['playoff_seed'] if 'playoff_seed' in team_standings else None

        outcome_totals = team_standings['outcome_totals']
        __wins = outcome_totals['wins']
        __losses = outcome_totals['losses']
        __ties = outcome_totals['ties']
        __percentage = outcome_totals['percentage']

        return TeamStandings(__rank, __points_for, __points_against, __playoff_seed,
                             __wins, __losses, __ties, __percentage)
