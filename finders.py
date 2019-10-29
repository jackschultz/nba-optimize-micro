from db import conn, cursor

import pandas as pd

select_stat_lines_by_date = "select player_id as pid, fd_name as name, fd_positions as pos, fd_salary as sal, fd_points as pts from stat_lines sl, games g, players p where sl.game_id=g.id and sl.player_id=p.id and g.date='%s' and sl.fd_positions is not null and sl.fd_points is not null and sl.player_id not in %s and sl.active;"

select_main_str = f"select sum(fd_points), sum(fd_salary) from stat_line_points where player_id in %s and date='%s';"


query_string_self_projection = '''
SELECT
	slp.player_id AS pid,
	slp.name AS name,
	slp.fd_positions AS pos,
	slp.fd_salary AS sal,
	proj.fd_points AS pts
FROM
	stat_line_points slp,
	projections proj
WHERE
	proj.source = 'self'
	AND proj.stat_line_id = slp.stat_line_id
	AND proj.version = %s
	AND slp.date = %s
	AND slp.fd_positions IS NOT NULL
	AND proj.fd_points IS NOT NULL
	AND proj.minutes > 0.0
	AND slp.player_id not in %s
	AND slp.active;
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


def get_stat_lines_for_date(date, version, exclude=[0]):
    params = (version, date, tuple(exclude),)
    df = pd.read_sql_query(query_string_self_projection, conn, params=params)
    print(df)
    return df

player_columns = ['id', 'dk_name', 'fd_name',
                  'br_name', 'rg_name', 'current_team_id', 'fte_name']

stat_line_points_columns = ["name", "abbrv", "date", "minutes", "dk_positions", "dk_salary", "dk_points", "dkpp36", "fd_salary", "fd_positions", "fd_points", "fdpp36", "player_id", "stat_line_id", "season"]


def find_player_by_id(pid):
    sql_str = f'select * from players where id={pid}'
    cursor.execute(sql_str)
    player_info = cursor.fetchone()
    if not player_info:
        return None
    return dict(zip(player_columns, player_info))

def find_stat_line_on_date_for_player(date, pid):
    sql_str = f"select * from stat_line_points where date = '{date}' and player_id = {pid}"
    cursor.execute(sql_str)
    stat_line_points_info = cursor.fetchone()
    if not stat_line_points_info:
        return None
    return dict(zip(stat_line_points_columns, stat_line_points_info))


