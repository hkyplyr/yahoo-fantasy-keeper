import json
import os
import requests
import webbrowser

class YahooFantasyApi:
    def __init__(self, credentials_file, league_id=None):
        self.credentials_file = open(credentials_file)
        self.credentials = json.load(self.credentials_file)
        self.credentials_file.close()

        self.authorize_url = 'https://api.login.yahoo.com/oauth2/request_auth'
        self.access_token_url = 'https://api.login.yahoo.com/oauth2/get_token'

        self.client_id = self.credentials['client_id']
        self.client_secret = self.credentials['client_secret']

        self.redirect_uri = 'oob'

        self.league_id = league_id
        self.base_url = 'https://fantasysports.yahooapis.com/fantasy/v2'

        tokens = self.retrieve_tokens()

        if tokens:
            self.set_tokens(tokens)
        else:
            self.get_initial_tokens()

    def get_initial_tokens(self):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': 'oob',

            'response_type': 'code',
            'language': 'en-us',
        }

        res = requests.post(self.authorize_url, params=data, headers={'Content-Type': 'application/json'})
        webbrowser.open(res.url)

        code = raw_input('Enter code: ')

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': 'oob',
            'code': code,
            'grant_type': 'authorization_code',
        }

        response = requests.post(self.access_token_url, data=data)

        self.set_tokens(response.json())
        self.cache_tokens()
    
    def set_tokens(self, data):
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']

    def cache_tokens(self):
        tokens = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
        }

        with open('.tokens.json', 'w') as f:
            f.write(json.dumps(tokens))
    
    def retrieve_tokens(self):
        if not os.path.exists('.tokens.json'):
            return None
        
        with open('.tokens.json', 'r') as f:
            tokens = json.loads(f.read())
        return tokens

    def refresh_tokens(self):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': 'oob',
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
        }

        response = request.post(self.access_token_url, data=data)

        self.set_tokens(response.json())
        self.cache_tokens()

    def get(self, path):
        url = '{}/{}'.format(self.base_url, path)
        response = requests.get(url, params={'format':'json'}, headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        return response.json()
    
    def get_standings(self):
        path = 'leagues;league_keys=nhl.l.{}/standings'.format(self.league_id)
        return self.get(path)

    def get_roster(self, team_id):
        path = 'team/nhl.l.{}.t.{}/roster/players'.format(self.league_id, team_id)
        return self.get(path)

    def get_scoreboard(self, week):
        path = 'leagues;league_keys=nhl.l.{}/scoreboard;week={}'.format(self.league_id, week)
        return self.get(path)
    
    def get_matchups(self, team_id, weeks_arr):
        weeks = ','.join(str(c) for c in weeks_arr)
        path = 'team/nhl.l.{}.t.{}/matchups;weeks={}'.format(self.league_id, team_id, weeks)
        return self.get(path)

    def get_stats(self, team_id, date):
        path = 'team/nhl.l.{}.t.{}/roster;type=date;date={}/players/stats'.format(self.league_id, team_id, date)
        return self.get(path)
