import os

class WritingService:

	def __init__(self,refDate):

		workingDirectory = os.path.dirname(os.path.abspath(__file__))

		if not os.path.exists(workingDirectory + '/data_generate'):
			os.mkdir(workingDirectory + '/data_generate')
			os.chmod(workingDirectory + '/data_generate', 0o777)

		year = refDate.year
		month = refDate.month
		day = refDate.day

		sYear = str(year)
		if month < 10:
			sMonth = str(month).rjust(2,'0')
		else:
			sMonth = str(month)
		if day < 10:
			sDay = str(day).rjust(2,'0')
		else:
			sDay = str(day)

		if not os.path.exists(workingDirectory + '/data_generate/' + sYear + sMonth):
			os.mkdir(workingDirectory + '/data_generate/' + sYear + sMonth)
			os.chmod(workingDirectory + '/data_generate/' + sYear + sMonth, 0o777)

		self.textPath = workingDirectory + '/data_generate/' + sYear + sMonth + '/'

	def setFileName(self,fileName):
		self.fileName = fileName

	def setColumnName(self,columnsName):
		self.columnsName = []
		self.columnsCount = len(columnsName)
		for i in range(0, self.columnsCount):
			self.columnsName.append(columnsName[i])

	def openFile(self):
		if os.path.exists(self.textPath + self.fileName + '.txt'):
			os.remove(self.textPath + self.fileName + '.txt')
		self.file = open(self.textPath + self.fileName + '.txt', 'w')
		os.chmod(self.textPath + self.fileName + '.txt',0o777)

	def closeFile(self):
		self.file.close()

	def displayColumnName(self):
		returnText = self.columnsName[0] + " " + self.columnsName[1] + " " + self.columnsName[2]
		return returnText

	def writeHeader(self,bufferWrite):
		for i in range(0,len(bufferWrite)):
			self.file.write(str(bufferWrite[i]) + os.linesep)

	def writeLineColumn(self):
		if self.file.closed:
			print('this file is closed')
			return
		elif self.columnsCount == 0:
			print('your data that you need to write is not correct (writeLineColumn)')
			return
		else:
			lineColumn = ""
			for i in range(0,self.columnsCount):
				columnString = str(self.columnsName[i])
				if i == self.columnsCount-1:
					lineColumn = lineColumn + columnString
				else:
					lineColumn = lineColumn + columnString + '\t'
			self.file.write(lineColumn + '\n')

	def writeLineValue(self, columnsValue):
		if self.file.closed:
			print('this file is closed')
			return
		elif len(columnsValue) != self.columnsCount:
			print('your data that you need to write is not correct (writeLineValue)')
			return
		else:
			lineValue = ""
			for i in range(0,len(columnsValue)):
				# columnString = str(columnsValue[i])
				columnString = str(columnsValue[i])
				# lineValue = lineValue + columnString
				# lineValue = lineValue + columnString.ljust(20)
				if i == len(columnsValue)-1:
					lineValue = lineValue + columnString
				else:
					lineValue = lineValue + columnString + '\t'
			self.file.write(lineValue + '\n')
			# return lineValue

	def getAbsoluteFilePath(self):
		return self.textPath + self.fileName + '.txt'