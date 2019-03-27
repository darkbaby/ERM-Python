import cx_Oracle as cx

class ConnectionService:

	def __init__(self, serverURL, username, password, port, schema):
		self.serverURL = serverURL
		self.username = username
		self.password = password
		self.port = port
		self.schema = schema

	def connect(self):
		self.__connection = cx.connect(self.username + '/' + self.password + '@' + self.serverURL + ':' + self.port + '/' + self.schema)
		self.__connection.autocommit = False
		self.__cursor = self.__connection.cursor()

	def disconnect(self):
		if hasattr(self,'__cursor'):
			self.__cursor.close()
		if hasattr(self,'__connection'):
			self.__connection.close()

	def getNumberVariable(self):
		return self.__cursor.var(cx.NUMBER)

	def getCursorVariable(self):
		return self.__cursor.var(cx.CURSOR)

	def commit(self):
		self.__connection.commit()

	def rollback(self):
		if hasattr(self,'__connection'):
			self.__connection.rollback()

	def queryStatement(self,query):
		# query = 'SELECT * FROM ERM_TEST'
		self.__cursor.execute(query)
		# for row in self.cursor:
		# 	print (row)
		return

	def queryStatementReturn(self,query):
		self.__cursor.execute(query)
		result = []
		for row in self.__cursor:
			result.append(row)
		return result

	def queryStoreProcedure(self,storeProcedureName,parameter):
		self.__cursor.callproc(storeProcedureName, [], parameter)
