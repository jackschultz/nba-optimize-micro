import psycopg2
conn = psycopg2.connect(database = "nba", user = "nbauser", password = "nbapassword", host = "localhost", port = "5432")
cursor = conn.cursor()
