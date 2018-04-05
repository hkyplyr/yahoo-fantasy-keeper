from app import db, Team, Draft, Player, Ownership, Pick
from api import YahooFantasyApi
import sys

league_id = 175

yfs = YahooFantasyApi(league_id=league_id)

def get_teams():
    data = yfs.get_teams()
    teams = data['fantasy_content']['league'][1]['teams']
    for team in teams:
        if team == 'count':
            continue
        team_data = teams[team]['team'][0]
        
        team_id = team_data[1]['team_id']
        name = team_data[2]['name']
        manager = team_data[19]['managers'][0]['manager']['nickname']

        team_vo = Team(team_id=team_id, name=name, manager=manager)
        db.session.merge(team_vo)
        db.session.commit()
            
def get_draft():
    data = yfs.get_draft()
    draft_results = data['fantasy_content']['league'][1]['draft_results']
    for pick_number in draft_results:
        if pick_number == 'count':
            continue
        pick_data = draft_results[pick_number]['draft_result']

        player_id = pick_data['player_key'][6:]
        team_id = pick_data['team_key'][12:]
        pick = pick_data['pick']
        round = pick_data['round']
        
        draft_vo = Draft(player_id=player_id, team_id=team_id, pick=pick, round=round)
        owner_vo = Ownership(player_id=player_id, team_id=team_id)
        db.session.merge(draft_vo)
        db.session.merge(owner_vo)
        db.session.commit()

        check_if_player_exists(player_id)

def check_if_player_exists(player_id):
    player = Player.query.get(player_id)
    if player is None:
        get_player_info(player_id)

def get_player_info(player_id):
    data = yfs.get_player(player_id)
    player = data['fantasy_content']['player'][0]
    parse_player_info(player)    
    
def parse_player_info(player_data):
    mod = 1 if 'status' in player_data[3] else 0
    mod = mod + 1 if 'on_disabled_list' in player_data[4] else mod

    player_id = player_data[1]['player_id']
    first_name = player_data[2]['name']['ascii_first']
    last_name = player_data[2]['name']['ascii_last']
    status = player_data[3]['status'] if 'status' in player_data[3] else None
    nhl_team = player_data[6 + mod]['editorial_team_abbr'].upper()
    number = player_data[7 + mod]['uniform_number']
    number = int(number) if len(number) > 0 else None
    #number = int(number) if type(number) == int else None
    position = player_data[8 + mod]['display_position']

    print("Saving {} {} {}.".format(player_id, first_name, last_name))
    player_vo = Player(player_id=player_id,
                       first_name=first_name,
                       last_name=last_name,
                       status=status,
                       nhl_team=nhl_team,
                       number=number,
                       position=position)
    db.session.merge(player_vo)
    db.session.commit()

def get_transactions():
    data = yfs.get_transactions()
    transactions = data['fantasy_content']['league'][1]['transactions']
    for t in range(transactions['count']-1, -1, -1):
        transaction_info = transactions[str(t)]['transaction'][0]
        transaction_id = transaction_info['transaction_id']
        transaction_type = transaction_info['type']
        status = transaction_info['status']
        timestamp = transaction_info['timestamp']

        print(transaction_id)

        transaction = transactions[str(t)]['transaction'][1]
        if transaction_type == 'trade':
            players = transaction['players']
            for p in players:
                if p == 'count':
                    continue
                player_id = players[p]['player'][0][1]['player_id']
                check_if_player_exists(player_id)
                transaction_data = players[p]['player'][1]['transaction_data'][0]

                source_id = transaction_data['source_team_key'][12:]
                destination_id = transaction_data['destination_team_key'][12:]

                owner_vo = Ownership(player_id=player_id, team_id=destination_id)
                db.session.merge(owner_vo)
                db.session.commit()

            picks = transaction_info['picks']
            for pick in picks:
                source_id = pick['pick']['source_team_key'][12:]
                destination_id = pick['pick']['destination_team_key'][12:]
                original_id = pick['pick']['original_team_key'][12:]
                draft_round = pick['pick']['round']

                pick_vo = Pick(original_id=original_id, draft_round=draft_round, owner_id=destination_id)
                db.session.merge(pick_vo)
                db.session.commit()
        
        if transaction_type == 'add':
            player = transaction['players']['0']['player']
            player_id = player[0][1]['player_id']

            transaction_data = player[1]['transaction_data'][0]
            team_id = transaction_data['destination_team_key'][12:]

            if player_id == '3344' and team_id == '1':
                print(t)
                print('Vanek added')

            owner_vo = Ownership(player_id=player_id, team_id=team_id)
            db.session.merge(owner_vo)
            db.session.commit()
        
        if transaction_type == 'drop':
            player = transaction['players']['0']['player']
            player_id = player[0][1]['player_id']

            transaction_data = player[1]['transaction_data']
            team_id = transaction_data['source_team_key'][12:]

            if player_id == '3344' and team_id == '1':
                print(t)
                print('Vanek dropped')

            owner_vo = Ownership.query.get(player_id)
            if owner_vo is not None:
                db.session.delete(owner_vo)
            db.session.commit()

        if transaction_type == 'add/drop':
            added_player = transaction['players']['0']['player']
            added_id = added_player[0][1]['player_id']

            add_transaction = added_player[1]['transaction_data'][0]
            destination_id = add_transaction['destination_team_key'][12:]

            dropped_player = transaction['players']['1']['player']
            dropped_id = dropped_player[0][1]['player_id']

            drop_transaction = dropped_player[1]['transaction_data']
            source_id = drop_transaction['source_team_key'][12:]

            added_owner_vo = Ownership(player_id=added_id, team_id=destination_id)
            db.session.merge(added_owner_vo)
            
            dropped_owner_vo = Ownership.query.get(dropped_id)
            if dropped_owner_vo is not None:
                db.session.delete(dropped_owner_vo)
            
            db.session.commit()

def get_players():
    more_players = True
    start = 0
    while more_players:
        data = yfs.get_players(start)  
        players = data['fantasy_content']['league'][1]['players']
        
        if len(players) == 0:
            more_players = False
            continue
        
        for p in players:
            if p == 'count':
                continue

            player = players[p]['player'][0]  
            parse_player_info(player)


        start += 25       

def set_initial_picks():
    for draft_round in range(1,25):
        for team in range(1,11):
            pick_vo = Pick(original_id=team, draft_round=draft_round, owner_id=team)
            db.session.merge(pick_vo)
            db.session.commit()

get_teams()
get_players()
if len(sys.argv) > 1 and sys.argv[1] == 'setup':
    set_initial_picks()
    get_draft()
get_transactions()