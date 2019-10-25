from db import conn, cursor
import pandas as pd

select_stat_lines_by_date = "select player_id as pid, fd_name as name, fd_positions as pos, fd_salary as sal, fd_points as pts from stat_lines sl, games g, players p where sl.game_id=g.id and sl.player_id=p.id and g.date='%s' and sl.fd_positions is not null and sl.fd_points is not null and sl.player_id not in %s and sl.active;"

select_main_str = f"select sum(fd_points), sum(fd_salary) from stat_line_points where player_id in %s and date='%s';"

query_string = '''
SELECT
	p.id AS pid,
	p.fd_name AS name,
	sl.fd_positions AS pos,
	sl.fd_salary AS sal,
	-- proj.fd_points AS pts
        (proj.bulk->>'fd_pts_ceil')::float as pts
FROM
	stat_lines sl,
	games g,
	players p,
	projections proj
WHERE
	sl.game_id = g.id
	AND proj.source = 'rg'
        and proj.bulk->>'fd_pts_ceil' is not null
	AND proj.stat_line_id = sl.id
	AND sl.player_id = p.id
	AND g.date = '%s'
	AND sl.fd_positions IS NOT NULL
	AND sl.fd_points IS NOT NULL
	AND sl.player_id NOT IN %s
	AND sl.active;
'''

def get_actual_points_sal_for_ids(player_ids, date):
	if not player_ids:
		raise ValueError('No player ids.')
	asdf = select_main_str % (tuple(player_ids), date)
	cursor.execute(asdf)
	points, salary = cursor.fetchone()
	print('actual info')
	print('done actual info')
	return float(points), salary


def get_stat_lines_for_date(date, exclude=[]):

    asdf = f"select player_id as pid, fd_name as name, fd_positions as pos, fd_salary as sal, fd_points as pts from stat_lines sl, games g, players p where sl.game_id=g.id and sl.player_id=p.id and g.date='%s' and sl.fd_positions is not null and sl.fd_points is not null{' and sl.player_id not in %s' if exclude else ''};"
    vals = (date, tuple(exclude)) if exclude else (date)
    sql_str = asdf % vals
    sql_str = query_string % (date, tuple(exclude))

    df = pd.read_sql_query(sql_str, conn)
    return df

if __name__ == '__main__':
    print(get_stat_lines_for_date('2019-01-01'))
