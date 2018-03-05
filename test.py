from api import YahooFantasyApi
from standings import Standings
from operator import itemgetter
import heapq
import sqlite3
credentials_file = 'credentials.json'
tokens_file = '.tokens.json'
league_id = 175

FANTASY_CONTENT = 'fantasy_content'
STAT_MAP = {1: 'goals', 2: 'assists', 4:'plus_minus',
            8: 'power_play_points', 11: 'short-handed-points',
            14: 'shots', 31: 'hits', 32: 'blocks',
            19: 'wins', 20: 'losses', 22: 'goals_against',
            25: 'saves', 27: 'shutouts'}

yfs = YahooFantasyApi(credentials_file, tokens_file, league_id=league_id)
def get_stats_map(stats):
    stat_map = {}
    for stat in stats:
        name = STAT_MAP[stat['stat']['stat_id']]
        value = stat['stat']['value']
        stat_map[name] = value
    return stat_map

def get_win_streak():
    team_map = {'1':{'current':0, 'longest':0}, '2':{'current':0, 'longest':0},
                '3':{'current':0, 'longest':0}, '4':{'current':0, 'longest':0},
                '5':{'current':0, 'longest':0}, '6':{'current':0, 'longest':0},
                '7':{'current':0, 'longest':0}, '8':{'current':0, 'longest':0},
                '9':{'current':0, 'longest':0}, '10':{'current':0, 'longest':0}}

    for wk in range(1, 16):
        scoreboard_data = yfs.get_scoreboard(wk)
        matchups = scoreboard_data[FANTASY_CONTENT]['leagues']['0']['league'][1]['scoreboard']['0']['matchups']
        for matchup in matchups:
            if matchup == 'count':
                continue

            winner = matchups[matchup]['matchup']['winner_team_key'][12:]

            teams = matchups[matchup]['matchup']['0']['teams']
            for team in teams:
                if team == 'count':
                    continue

                team_id = teams[team]['team'][0][1]['team_id']
                if team_id == winner:
                    #print('Team {} won'.format(team_id))
                    team_map[team_id]['current'] += 1
                if team_map[team_id]['current'] > team_map[team_id]['longest']:
                        team_map[team_id]['longest'] = team_map[team_id]['current']
                if team_id != winner:
                    #print('Team {} lost'.format(team_id))
                    team_map[team_id]['current'] = 0
    for team in sorted(team_map.items(), key=itemgetter(1), reverse=True):
        print(team)

def get_eligible_positions(player_data):
    for field in player_data:
        if 'eligible_positions' in field:
            return [pos['position'].encode("utf-8") for pos in field['eligible_positions']]

def get_max_goalies(goalie_dict):
    print(goalie_dict)
    print(dict(heapq.nlargest(2, goalie_dict.items(), key=itemgetter(1))))

def get_max_defense(defense_dict):
    print(defense_dict)
    print(dict(heapq.nlargest(5, defense_dict.items(), key=itemgetter(1))))


def get_missed():
    roster_data = yfs.get_stats(2, '2018-01-20')
    players = roster_data[FANTASY_CONTENT]['team'][1]['roster']['0']['players']
    goalies = {}
    defense = {}
    for player in players:
        if player == 'count':
            continue

        player_id = players[player]['player'][0][1]['player_id']
        eligible_positions = get_eligible_positions(players[player]['player'][0])
        selected_position = players[player]['player'][1]['selected_position'][1]['position']
        player_points = players[player]['player'][2]['player_points']['total']
        player_stats = players[player]['player'][2]['player_stats']['stats']


        if 'G' in eligible_positions:
            goalies[player_id] = player_points
        if 'D' in eligible_positions:
            defense[player_id] = player_points
    get_max_goalies(goalies)
    get_max_defense(defense)

def standings():
    standings_data = yfs.get_standings()
    teams = standings_data[FANTASY_CONTENT]['league'][1]['standings'][0]['teams']
    for team in teams:
        if team == 'count':
            continue

        team_info = teams[team]['team'][0]
        team_id = team_info[1]['team_id']
        team_stats = teams[team]['team'][1]['team_stats']
        team_standings = teams[team]['team'][2]['team_standings']
        rank = team_standings['rank']
        points_for = team_standings['points_for']
        points_agains = team_standings['points_against']

        wins = team_standings['outcome_totals']['wins']
        losses = team_standings['outcome_totals']['losses']
        ties = team_standings['outcome_totals']['ties']

        print('{}: {}-{}-{}'.format(team_id, wins, losses, ties))

def matchups():
    for t in range(1, 11):
        for wk in range(1, 5):
            print('Getting matchup for team:{} week:{}'.format(t, wk))
            matchup_data = yfs.get_matchups(t, [wk])
            matchups = matchup_data[FANTASY_CONTENT]['team'][1]['matchups']
            for matchup in matchups:
                if matchup == 'count':
                    continue

                teams = matchups[matchup]['matchup']['0']['teams']
                for team in teams:
                    if team == 'count':
                        continue

                    team_key = teams[team]['team'][0][1]['team_id']
                    if team_key != str(t):
                        continue

                    team_data = teams[team]['team'][1]
                    # Total points scored by a team in a given week
                    team_points = team_data['team_points']['total']
                    print('Team {} scored {} points'.format(t, team_points))
                    # Totals of all stats for a team in a given week
                    team_stats = get_stats_map(team_data['team_stats']['stats'])


def get_draft_map():
    draft_map = {}
    data = yfs.get_draft_results()
    draft_results = data['fantasy_content']['league'][1]['draft_results']
    for pk in draft_results:
        if pk == 'count':
            continue

        draft_result = draft_results[pk]['draft_result']
        player_id = draft_result['player_key'][6:]
        team_id = draft_result['team_key'][12:]
        pick = draft_result['pick']
        rd = draft_result['round']

        draft_map[player_id] = rd
    return draft_map

def __getOrRaiseError(data, key):
    value = data.get(key)
    if value is not None:
        return value
    raise KeyError("{} is not present.".format(key))

def save_team(team_map):
    for key in team_map:
        print(key, team_map.get(key))
    print('')

    team_id = __getOrRaiseError(team_map, 'team_id')
    name = __getOrRaiseError(team_map, 'name')
    url = __getOrRaiseError(team_map, 'url')
    logo = __getOrRaiseError(team_map, 'team_logos')[0]['team_logo']['url']
    waiver = __getOrRaiseError(team_map, 'waiver_priority')
    faab = __getOrRaiseError(team_map, 'faab_balance')
    moves = __getOrRaiseError(team_map, 'number_of_moves')
    trades = __getOrRaiseError(team_map, 'number_of_trades')
    manager = __getOrRaiseError(team_map, 'managers')[0].get('manager')
    manager_name = manager.get('nickname')
    manager_email = manager.get('email')
    manager_logo = manager.get('image_url')
    print(team_id, name, url, logo, waiver,faab, moves, trades, manager_name, manager_email, manager_logo)

    rv = sqlite3.connect('keeper/keeper/keeper.db')
    rv.row_factory = sqlite3.Row

    rv.execute('insert into teams (id, name, url, logo_url, waiver, faab, moves, trades, mgr_name, mgr_email, mgr_logo)' +
               ' values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [team_id, name, url, logo, waiver, faab, moves, trades,
               manager_name, manager_email, manager_logo])
    rv.commit()

def main():
    data = yfs.get_teams()
    teams = data['fantasy_content']['league'][1]['teams']

    for team in teams:
        team_map = {}
        if team == 'count':
            continue

        team_info = teams[team]['team'][0]
        for info_item in team_info:
            if type(info_item) is list:
                continue

            for key, value in info_item.items():
                team_map[key] = value
        save_team(team_map)



    """
    d_m = get_draft_map()

    for tm in range(1, 11):
        data = yfs.get_roster(tm)
        team_name = data['fantasy_content']['team'][0][2]['name']
        print("\n;;;Keeper values for {}".format(team_name))
        players = data['fantasy_content']['team'][1]['roster']['0']['players']

        for player in players:
            if player == 'count':
                continue

            player_info = players[player]['player'][0]

            for item in player_info:
                if 'player_id' in item:
                    pid = item['player_id']
                if 'name' in item:
                    name = item['name']['full']
                if 'display_position' in item:
                    pos = item['display_position']
                if 'editorial_team_abbr' in item:
                    nhl_tm = item['editorial_team_abbr'].upper()

            if pid in d_m:
                keeper_round = d_m[pid]
            else:
                keeper_round = 19
            print("{};{};{};{}".format(keeper_round-1, pos, nhl_tm, name))




            #print("{} - {} - {} - {}".format(keeper_round, pos, nhl_tm, keeper_round))
"""



if __name__ == '__main__':
    main()

"""
scoreboard_data = yfs.get_scoreboard(1)
#print scoreboard_data

matchups =  scoreboard_data['fantasy_content']['leagues']['0']['league'][1]['scoreboard']['0']['matchups']
for week in matchups:
    if week == 'count':
        continue

    teams = matchups[week]['matchup']['0']['teams']
    for team in teams:
        if team == 'count':
            continue
        
        info = teams[team]['team'][0]
        data = teams[team]['team'][1]

        for key in info:
            print key

        #for stat in data['team_stats']['stats']:
        #    print STAT_MAP[stat['stat']['stat_id']]
    print ' '
    


    wk = matchups[week]['matchup']['week']
    status =  matchups[week]['matchup']['status']
    week_end =  matchups[week]['matchup']['week_end']
    winner =  matchups[week]['matchup']['winner_team_key']
    consol =  matchups[week]['matchup']['is_consolation']
    tied =  matchups[week]['matchup']['is_tied']
    week_start =  matchups[week]['matchup']['week_start']
    playoff =  matchups[week]['matchup']['is_playoffs']
    stat_winner =  matchups[week]['matchup']['stat_winners']

    # DEAL WITH STAT WINNER
    


"""
"""
for i in range(1,11):
    roster_data = yfs.get_roster(i)

    players = roster_data['fantasy_content']['team'][1]['roster']['0']['players']
    for player_key in players:
        if player_key == 'count':
            continue
        player_info = players[player_key]['player'][0]
        player_data = players[player_key]['player'][1]
        
        mod = 1 if 'status' in player_info[3] else 0
        if 'on_disabled_list' in player_info[4]:
            mod += 1

        player_key = player_info[0]['player_key']
        player_id = player_info[1]['player_id']
        full_name = player_info[2]['name']['full']
        last_name = player_info[2]['name']['last']
        ascii_first = player_info[2]['name']['ascii_first']
        ascii_last = player_info[2]['name']['ascii_last']
        first_name = player_info[2]['name']['first']
        status = player_info[3]['status'] if 'status' in player_info[3] else None
        on_disabled_list = player_info[4]['on_disabled_list'] if 'on_disabled_list' in player_info[4] else None
        editorial_player_key = player_info[3 + mod]['editorial_player_key']
        editorial_team_key = player_info[4 + mod]['editorial_team_key']
        editorial_team_full_name = player_info[5 + mod]['editorial_team_full_name']
        editorial_team_abbr = player_info[6 + mod]['editorial_team_abbr']
        uniform_number = player_info[7 + mod]['uniform_number']
        display_position = player_info[8 + mod]['display_position']
        image_url = player_info[9 + mod]['image_url']
        headshot_url = player_info[9 + mod]['headshot']['url']
        headshot_size = player_info[9 + mod]['headshot']['size']
        is_undroppable = player_info[10 + mod]['is_undroppable']
        position_type = player_info[11 + mod]['position_type']
        positions = [str(pos['position']) for pos in player_info[12 + mod]['eligible_positions']]
        has_player_notes = player_info[13 + mod]['has_player_notes'] if 'has_player_notes' in player_info[13 + mod] else None
        has_recent_player_notes = player_info[14 + mod]['has_recent_player_notes'] if 'has_recent_player_notes' in player_info[14 + mod] else None 

        coverage_type = player_data['selected_position'][0]['coverage_type']
        selected_position_date = player_data['selected_position'][0]['date']
        selected_position = player_data['selected_position'][1]['position']
        

        player = Players.convert_to_player(player_info)
        print str(player)
"""