from db import conn
import pandas as pd

select_stat_lines_by_date = "select player_id as pid, fd_name as name, fd_positions as pos, fd_salary as sal, fd_points as pts from stat_lines sl, games g, players p where sl.game_id=g.id and sl.player_id=p.id and g.date='%s' and sl.fd_positions is not null and sl.fd_points is not null;"

def get_stat_lines_for_date(date):
    sql_str = select_stat_lines_by_date % date
    df = pd.read_sql_query(sql_str, conn)
    return df

if __name__ == '__main__':
    print(get_stat_lines_for_date('2019-01-01'))