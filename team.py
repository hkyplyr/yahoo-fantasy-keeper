
class Team:
    def __init__(self, key, id, name, url, logos, waiver, faab,
                 moves, trades, adds, clinched, manager):
        self.key = key
        self.id = id
        self.name = name
        self.url = url
        self.logos = logos
        self.waiver = waiver
        self.faab = faab
        self.moves = moves
        self.trades = trades
        self.adds = adds
        self.clinched = clinched
        self.manager = manager

    @staticmethod
    def parse_sub_resource(team_json):
        team_key = team_json[0]
        team_id = team_json[1]
        name = team_json[2]['name']
        url = team_json[4]
        logos = team_json[5]
        waiver = team_json[7]
        faab = team_json[8]
        moves = team_json[9]
        trades = team_json[10]
        week_adds = team_json[11]
        clinched = team_json[12]
        manager = team_json[19]

        return Team(team_key, team_id, name, url, logos, waiver, faab,
                    moves, trades, week_adds, clinched, manager)
