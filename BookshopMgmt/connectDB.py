import MySQLdb

def connection():
	conn = MySQLdb.connect(host = "localhost",
							user = "root",
							passwd = "avneet",
							db = "mydatabase")
	c = conn.cursor()
	return c,conn