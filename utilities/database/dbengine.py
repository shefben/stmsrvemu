import threading

import globalvars

from sqlalchemy import create_engine, Table, MetaData, text, inspect
from sqlalchemy.sql import select, insert, update, delete, Select, Insert, Update, Delete, func
from datetime import datetime

from .base_dbdriver import BaseDatabaseDriver


class DatabaseDriver(BaseDatabaseDriver) :
	def __init__(self) :
		super( ).__init__( )
		self.engine = None
		self.lock = threading.Lock( )
		self.current_connection = None

	def connect(self, connection_string) :
		with self.lock :
			self.engine = create_engine(connection_string, pool_pre_ping=True)

	def check_table_exists(self, table_name) :
		inspector = inspect(self.engine)
		return table_name in inspector.get_table_names( )



	def disconnect(self) :
		if self.current_connection :
			self.current_connection.close( )
			self.current_connection = None
		if self.engine :
			self.engine.dispose( )

	def get_current_connection(self) :
		with self.lock :
			if self.current_connection is None or self.current_connection.closed :
				self.current_connection = self.engine.connect( )
			return self.current_connection

	def execute_query(self, query, params=None) :
		with self.lock :
			with self.engine.connect( ) as connection :
				result = None
				if isinstance(query, str) :
					query = text(query)  # Handle raw SQL string
					try:
						result = connection.execute(query, params or {}).fetchall( )
					except:
						# If we are here, it means the statement was most likely an update statement and that doesnt get a reutn
						pass
				elif isinstance(query, Select):
					result = connection.execute(query).fetchall()  # Handle SELECT queries
				elif isinstance(query, (Insert, Update, Delete)):
					result = connection.execute(query)  # Handle INSERT, UPDATE, DELETE
					connection.commit()  # Commit the transaction
					return result.rowcount  # Return the number of rows affected

				if result is not None :
					return result
				else :
					raise TypeError("Unsupported query type")

	def insert_data(self, orm_class, data):
		# Access the table object associated with the ORM class
		table = orm_class.__table__
		# Create the insert statement
		ins = table.insert().values(**data)
		# Execute the query
		self.execute_query(ins)

	def select_data(self, orm_class, where_clause=None):
		table = orm_class.__table__
		select_statement = select(table.c).where(where_clause) if where_clause else select(table.c)
		return self.execute_query(select_statement)

	def update_data(self, orm_class, where_clause, new_values) :
		table = orm_class.__table__
		upd = table.update( ).where(where_clause).values(**new_values)
		self.execute_query(upd)

	def remove_data(self, orm_class, data) :
		table = orm_class.__table__
		# Construct a WHERE clause for the delete statement
		conditions = [getattr(orm_class, key) == value for key, value in data.items()]
		rem = table.delete().where(*conditions)
		self.execute_query(rem)

	def get_rows_by_date(self, orm_class, date_column, order='asc') :
		table = orm_class.__table__
		sel = select([table]).order_by(date_column if order == 'asc' else date_column.desc( ))
		return self.execute_query(sel)

	def get_next_available_id(self, table, id_column='UniqueID') :
		sel = select([func.max(table.c[id_column])])
		max_id = self.execute_query(sel).scalar( ) or 0
		return max_id + 1


def get_db_config(dbtype) :
	config = globalvars.config
	if isinstance(dbtype, MySQLDriver) :
		return f"mysql+pymysql://{config['mysql_username']}:{config['mysql_password']}@{config['mysql_host']}:{config['mysql_port']}/{config['database']}"
	else :  # Can only be SQLite
		db_name = config['database']
		if not db_name.endswith('.db') :
			db_name += '.db'
		return f"sqlite:///{db_name}"


class MySQLDriver(DatabaseDriver) :
	def connect(self) :
		super( ).connect(get_db_config(self))


class SQLiteDriver(DatabaseDriver) :
	def connect(self) :
		super( ).connect(get_db_config(self))


def create_database_driver(db_type) :
	if db_type.lower( ) == 'mysql' :
		return MySQLDriver( )
	elif db_type.lower( ) == 'sqlite' or db_type.lower( ) == 'sqllite' :
		return SQLiteDriver( )
	else :
		raise ValueError("Unsupported database type. Please Change emulator.ini: database=mysql or database=sqlite")


"""db_driver = create_database_driver('mysql', 'mysql+pymysql://user:password@host:port/dbname')
db_driver.connect()"""