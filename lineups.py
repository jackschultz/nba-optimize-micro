from calculate import solve
from finders import get_stat_lines_for_date, get_actual_points_sal_for_ids

from db import actor

import numpy as np

class LineupError(Exception):
    def __init__(self, errvals):
        self.errvals = errvals

class Lineup:
    pass


class FanDuelLineup(Lineup):

    max_salary = 60000

    def __init__(self, date, excludes=[0], includes=[]):
        self.date = date
        self.excludes = excludes
        self.includes = includes
        self.combo_positions_dict = {'PG': 2, 'SG': 2, 'SF': 2, 'PF': 2, 'C': 1}
        self.combo_salary = 0
        self.players = []
        self.includes_stat_line_points = {}
        # probably a better way to do this validation...
        self.validate_and_load_input()

    def validate_and_load_input(self):

        errors = []

        matches = set(self.includes) & set(self.excludes)
        if len(matches) > 0:
            message = 'Same players id(s) in both include and exclude'
            ids = list(matches)
            errors.append({'message': message, 'vals': ids, 'code': 400})

        message = 'Some included players do not play on this date.'
        vals = []
        for pid in self.includes:
            #find the player and make sure he has a stat line for that date
            slpi = actor.find_stat_line_by_player_and_date(pid, self.date)
            if not slpi:
                vals.append(pid)
            else:
                # Now we can add the players as well
                self.includes_stat_line_points[pid] = slpi
                self.combo_salary += slpi['fd_salary']
                self.combo_positions_dict[slpi['fd_positions']] -= 1
        
        if self.invalid_combo_positions():
            message = f'Too many players of the same position included.'
            errors.append({'message': message, 'code': 400})

        if vals:
            errors.append({'message': message, 'vals': vals, 'code': 400})
 
        if len(errors) > 0:
            raise LineupError(errors)

        return None

        
    def remaining_position_dict(self):
        return self.combo_positions_dict
    
    def remaining_salary(self):
        return FanDuelLineup.max_salary - self.combo_salary

    def invalid_combo_positions(self):
        return any(val < 0 for val in [value for key, value in self.combo_positions_dict.items()])

    def valid_combo_salary(self):
        return self.combo_salary <= FanDuelLineup.max_salary

    def possible_stat_lines(self, version):
        '''
        This df includes the included values. We need this because in the end,
        we need to get the info about that player with that id.
        '''
        excludes = self.excludes or [0]
        return get_stat_lines_for_date(self.date, version, exclude=excludes)

    def optimize(self, version):
        '''
        Optimize the remaining parts of the lineup based on version
        '''
        df = self.possible_stat_lines(version)
        if df.empty:
            raise(LineupError({'message': 'Database returned no players to optimize with.'}))
        
        solve_df = df[~df.pid.isin(self.includes)]
        fin = solve(self.combo_positions_dict, self.remaining_salary(), solve_df)

        winner = fin[1]

        includes_df_indexes = df.loc[df['pid'].isin(self.includes)]
    
        if not includes_df_indexes.empty:
            winning_ids = np.hstack([winner[-1], includes_df_indexes.index.values])
        else:
            winning_ids = winner[-1]

        top_players = df.iloc[winning_ids]

        print("\n")
        print(top_players)

        print("\n")
        print("Combined player points:", sum(df.iloc[winning_ids].pts))
        print("Combined player salary:", sum(df.iloc[winning_ids].sal))
        print("\n")

        projected_salary = sum(df.iloc[winning_ids].sal)
        projected_points = sum(df.iloc[winning_ids].pts)

        retval = {}

        projections = {}
        projections['salary'] = projected_salary
        projections['points'] = projected_points
        retval['projections'] = projections

        top_pids = top_players['pid'].to_list()
        actual_points, actual_salary = get_actual_points_sal_for_ids(
            top_pids, self.date)
        actuals = {}
        actuals['salary'] = actual_salary
        actuals['points'] = actual_points
        retval['actuals'] = actuals

        top_player_projections = top_players.to_dict('records')
        top_pid_stat_lines = actor.find_stat_line_points_on_date_for_player_ids(self.date, tuple(top_pids))

        for sl in top_pid_stat_lines:
            for tp in top_player_projections:
                if sl['player_id'] == tp['pid']:
                    tp['act_fd_pts'] = float(sl['fd_points']) if sl['fd_points'] else 0
                    tp['act_dk_pts'] = float(sl['dk_points']) if sl['dk_points'] else 0
                    tp['act_mins'] = float(sl['minutes']) if sl['minutes'] else 0
                    break

        retval['players'] = top_player_projections


        return retval
