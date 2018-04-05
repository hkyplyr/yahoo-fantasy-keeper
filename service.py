from website.app import db, Team, Draft
from api import YahooFantasyApi

credentials_file = 'credentials.json'
tokens_file = '.tokens.json'
league_id = 175

yfs = YahooFantasyApi(credentials_file, tokens_file, league_id=league_id)

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
        db.session.merge(draft_vo)
        db.session.commit()


#get_teams()
get_draft()