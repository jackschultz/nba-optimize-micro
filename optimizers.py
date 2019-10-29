from finders import get_stat_lines_for_date, get_actual_points_sal_for_ids, find_stat_line_on_date_for_player

from lineups import FanDuelLineup, LineupError

class OptimizeError(Exception):
    def __init__(self, errvals):
        self.errvals = errvals
        self.code = 400

def standard(date, projection_version='', site='fd', excludes=[0], includes=[]):
    # in the future, if there are different rules or you have a keeper player
    # who is alreay set in a position, we can change this and still get a valid
    # lineup
    # Defaulting excludes to [0] so we always have an array with values for the query

    try:
        lineup = FanDuelLineup(date, excludes=excludes, includes=includes)
        return lineup.optimize(projection_version)
    except LineupError as err:
        raise OptimizeError(err.errvals)
