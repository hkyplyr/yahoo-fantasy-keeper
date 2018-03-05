
class Roster:
    def __init__(self, roster_json):
        roster = roster_json['fantasy_content']['team'][1]['roster']

        coverage_type = roster['coverage_type']
        date = roster['date']
        is_editable = roster['is_editable']

        players = roster['0']['players']
        for p in players:
            if p == 'count':
                continue
            for key in players[p]['player']:
                print(key)
