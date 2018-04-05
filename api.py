from auth import AuthenticationService
import requests
import time

BASE_URL = 'https://fantasysports.yahooapis.com/fantasy/v2'
TOKENS_FILE = '.tokens.json'


class YahooFantasyApi:
    def __init__(self, credentials_file, tokens_file, league_id):
        self.league_id = league_id
        self.auth_service = AuthenticationService(credentials_file, tokens_file)
        self.__set_tokens()

    def __set_tokens(self):
        self.access_token = self.auth_service.get_access_token()
        self.refresh_token = self.auth_service.get_refresh_token()
        self.expires_by = self.auth_service.get_expires_by()

    def __check_tokens(self):
        if time.time() > self.expires_by:
            self.auth_service.refresh_tokens()
            self.__set_tokens()

    #############################
    # Yahoo Fantasy Api methods
    #############################
    def __get(self, path):
        self.__check_tokens()
        params = {'format': 'json'}
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        url = '{}/{}'.format(BASE_URL, path)

        return requests.get(url, params=params, headers=headers).json()

    def __get_game_resource(self, sub_resource):
        path = 'game/nhl/{}'.format(sub_resource)
        return self.__get(path)

    def __get_league_resource(self, sub_resource):
        path = 'league/nhl.l.{}/{}'.format(self.league_id, sub_resource)
        return self.__get(path)

    def __get_player_resource(self, sub_resource, player_id):
        path = 'player/nhl.p.{}/{}'.format(player_id, sub_resource)
        return self.__get(path)

    def __get_team_resource(self, sub_resource, team_id):
        path = 'team/nhl.l.{}.t.{}/{}'.format(self.league_id, team_id, sub_resource)
        return self.__get(path)

    def __get_transaction_resource(self, sub_resource, transaction_id):
        path = 'team/nhl.l.{}.tr.{}/{}'.format(self.league_id, transaction_id, sub_resource)
        return self.__get(path)

    #############################
    # Public facing Api methods
    #############################
    def get_standings(self):
        return self.__get_league_resource('standings')

    def get_roster(self, team_id):
        return self.__get_team_resource('roster/players', team_id)

    def get_scoreboard(self, week):
        return self.__get_league_resource('scoreboard;week={}'.format(week))

    def get_matchups(self, team_id, weeks_arr):
        weeks = ','.join(str(c) for c in weeks_arr)
        return self.__get_team_resource('matchups;weeks{}'.format(weeks), team_id)

    def get_stats(self, team_id, date):
        return self.__get_team_resource('roster;type=date;date={}/players/stats'.format(date), team_id)
    
    def get_teams(self):
        return self.__get_league_resource('teams')
    
    def get_draft(self):
        return self.__get_league_resource('draftresults')
