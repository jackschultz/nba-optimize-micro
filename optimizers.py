from calculate import solve
from finders import get_stat_lines_for_date

def standard(date, site='fd'):
    #in the future, if there are different rules or you have a keeper player
    #who is alreay set in a position, we can change this and still get a valid
    #lineup
    combo_positions_dict = {'PG': 2, 'SG': 2, 'SF': 2, 'PF': 2, 'C': 1}

    df = get_stat_lines_for_date(date)

    fin = solve(combo_positions_dict, df)
    winner = fin[1]
    winning_ids = winner[-1]

    #print(df.iloc[winning_ids])

    top_players = df.iloc[winning_ids]
    print("\n")
    print(top_players)

    print("\n")
    print("Combined player points:", sum(df.iloc[winning_ids].pts))
    print("Combined player salary:", sum(df.iloc[winning_ids].sal))
    print("\n")

    combined_salary = sum(df.iloc[winning_ids].sal)
    combined_points = sum(df.iloc[winning_ids].pts)

    retval = {}
    retval['combined_salary'] = combined_salary
    retval['combined_points'] = combined_points
    retval['players'] = top_players.to_dict('records')

    return retval

if __name__ == '__main__':
    standard('2019-01-03')
