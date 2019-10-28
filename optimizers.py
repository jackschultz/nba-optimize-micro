from calculate import solve
from finders import get_stat_lines_for_date, get_actual_points_sal_for_ids


class OptimizeError(Exception):
    def __init__(self, errvals):
        self.errvals = errvals
        self.code = 400


def validate_cludes(include, exclude):
    matches = set(include) & set(exclude)
    if len(matches) > 0:
        message = 'Same players id(s) in both include and exclude'
        ids = list(matches)
        return {'message': message, 'vals': ids}
    return None


def standard(date, projection_version='', site='fd', exclude=[0], include=[]):
    # in the future, if there are different rules or you have a keeper player
    # who is alreay set in a position, we can change this and still get a valid
    # lineup
    # Defaulting exclude to [0] so we always have an array with values for the query

    errors = validate_cludes(include, exclude)
    if errors:
        raise OptimizeError(errors)

    combo_positions_dict = {'PG': 2, 'SG': 2, 'SF': 2, 'PF': 2, 'C': 1}

    remove_players = (exclude + include) or [0] # no ids of 0 in the db, so we can query for not in
    df = get_stat_lines_for_date(
        date, projection_version, exclude=remove_players)

    fin = solve(combo_positions_dict, df)
    winner = fin[1]
    winning_ids = winner[-1]

    # print(df.iloc[winning_ids])

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
        top_pids, date)
    actuals = {}
    actuals['salary'] = actual_salary
    actuals['points'] = actual_points
    retval['actuals'] = actuals

    retval['players'] = top_players.to_dict('records')

    return retval


if __name__ == '__main__':
    standard('2019-01-03')
