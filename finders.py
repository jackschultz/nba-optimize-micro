from db import conn, cursor

import pandas as pd

select_stat_lines_by_date = "select player_id as pid, fd_name as name, fd_positions as pos, fd_salary as sal, fd_points as pts from stat_lines sl, games g, players p where sl.game_id=g.id and sl.player_id=p.id and g.date='%s' and sl.fd_positions is not null and sl.fd_points is not null and sl.player_id not in %s and sl.active;"

select_main_str = f"select sum(fd_points), sum(fd_salary) from stat_line_points where player_id in %s and date='%s';"



query_string = '''
SELECT
	slp.player_id AS pid,
	slp.name,
	slp.fd_positions AS pos,
	slp.fd_salary AS sal,
	((proj.minutes / 36.0) * slp.fdpp36) AS pts
FROM
	stat_line_points slp,
	projections proj
WHERE
	proj.stat_line_id = slp.slid
	AND proj. "source" = 'fte'
	AND slp.date = '%s'
	AND slp.fdpp36 IS NOT NULL
	AND slp.player_id NOT IN %s;
'''

query_string = '''
SELECT
	slp.player_id AS pid,
	slp.name,
	slp.fd_positions AS pos,
	slp.fd_salary AS sal,
	((proj.minutes / 36.0) * slp.avgfdpp36) AS pts
FROM
	slpp slp,
	projections proj
WHERE
	proj.stat_line_id = slp.slid
	AND proj. "source" = 'self'
	AND slp.date = '%s'
	AND slp.avgfdpp36 IS NOT NULL
	AND proj.minutes IS NOT NULL
	AND proj.active
	AND slp.player_id NOT IN %s;
'''


query_string_self_projection = '''
SELECT
	p.id AS pid,
	p.fd_name AS name,
	sl.fd_positions AS pos,
	sl.fd_salary AS sal,
	proj.fd_points AS pts
FROM
	stat_lines sl,
	games g,
	players p,
	projections proj
WHERE
	sl.game_id = g.id
	AND proj.source = 'self'
	AND proj.stat_line_id = sl.id
	AND proj.version = '%s'
	AND sl.player_id = p.id
	AND g.date = '%s'
	AND sl.fd_positions IS NOT NULL
	AND proj.fd_points IS NOT NULL
	AND proj.minutes > 0.0
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
	if points:
		points = float(points)
	return points, salary


def get_stat_lines_for_date(date, version, exclude=[]):
	vals = (date, tuple(exclude)) if exclude else (date)
	sql_str = query_string_self_projection % (version, date, tuple(exclude))
	df = pd.read_sql_query(sql_str, conn)
	print(df)
	return df

if __name__ == '__main__':
    print(get_stat_lines_for_date('2019-01-01'))
