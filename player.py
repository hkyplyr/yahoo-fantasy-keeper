class Players:
    @staticmethod
    def convert_to_player(player_info):
        mod = 1 if 'status' in player_info[3] else 0
        if 'on_disabled_list' in player_info[4]:
            mod += 1
        
        player_id = player_info[1]['player_id']
        first_name = player_info[2]['name']['first']
        last_name = player_info[2]['name']['last']
        status = player_info[3]['status'] if 'status' in player_info[3] else 'H'
        on_disabled_list = player_info[4]['on_disabled_list'] if 'on_disabled_list' in player_info[4] else 0
        team_name = player_info[5 + mod]['editorial_team_full_name']
        team_abbr = player_info[6 + mod]['editorial_team_abbr']
        number = player_info[7 + mod]['uniform_number']
        position = player_info[8 + mod]['display_position']
        position_type = player_info[11 + mod]['position_type']
        positions = [str(pos['position']) for pos in player_info[12 + mod]['eligible_positions']]

        return Player(player_id, first_name, last_name, status, on_disabled_list, 
                     team_name, team_abbr, number, position, position_type, positions)

        


class Player:
    def __init__(self, player_id, first_name, last_name, status, on_disabled_list, 
                team_name, team_abbr, number, position, position_type, positions):
        self.player_id = player_id
        self.first_name = first_name
        self.last_name = last_name
        self.status = status
        self.on_disabled_list = on_disabled_list
        self.team_name = team_name
        self.team_abbr = team_abbr.upper()
        self.number = number
        self.position = position
        self.position_type = position_type
        self.positions = positions

    def __repr__(self):
        return "{} {}\n".format(self.first_name, self.last_name) + \
               "{} - {} - {}\n".format(self.team_abbr, self.number, self.position) + \
               "Status: {} | On IR: {}\n".format(self.status, self.on_disabled_list)
