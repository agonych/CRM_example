# Use PyMySQL as drop-in replacement for mysqlclient (no C compilation on Windows)
import pymysql
pymysql.install_as_MySQLdb()
