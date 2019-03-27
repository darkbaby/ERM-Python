import cx_Oracle as cx

class ConnectionService:

	def __init__(self, serverURL, username, password, schema):
		self.serverURL = serverURL
		self.username = username
		self.password = password
		self.schema = schema

	def connect(self):
		self.__connection = cx.connect(self.username + '/' + self.password + '@' + self.serverURL + '/' + self.schema)
		self.__cursor = self.__connection.cursor()

	def disconnect(self):
		self.__cursor.close()
		self.__connection.close()

	def getNumberVariable(self):
		return self.__cursor.var(cx.NUMBER)

	def getCursorVariable(self):
		return self.__cursor.var(cx.CURSOR)

	def commit(self):
		self.__connection.commit()

	def queryStatement(self,query):
		self.__cursor.execute(query)

	def queryStatementReturn(self,query):
		self.__cursor.execute(query)
		result = []
		for row in self.__cursor:
			result.append(row)
		return result

	def queryStoreProcedure(self,storeProcedureName,parameter):
		self.__cursor.callproc(storeProcedureName, [], parameter)
