from ConnectionService import ConnectionService
from QueryProvider import QueryProvider
from UtilityProvider import UtilityProvider
from WritingService import WritingService
from FTPService import FTPService
import configparser
import datetime
import os

def connectionSetup():
    # prevWorkingDirectory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # configparserObj = configparser.RawConfigParser()
    # configparserObj.read(prevWorkingDirectory + '/python-config.txt')
    connection = ConnectionService(configparserObj.get('database', 'server'),
                                   configparserObj.get('database', 'username'),
                                   configparserObj.get('database', 'password'),
                                   configparserObj.get('database', 'port'),
                                   configparserObj.get('database', 'sid'))

    # with open('../python-config.txt') as f:
    #     content = f.read().splitlines()
    # connection = ConnectionService(content[0],content[1],content[2],content[3])
    # connection = ConnectionService('192.168.10.192', 'erm', 'Passw0rd', 'ERM')
    return connection

def dataForGeneratingSetup(connection):
    connection.connect()

    out_return_data = connection.getCursorVariable()
    currentTimeNumber = UtilityProvider.convertDateTimeToNumberERMFormat(refDate)
    parameter = {'OUT_ReturnData': out_return_data, 'IN_CurrentTime': currentTimeNumber}
    connection.queryStoreProcedure(QueryProvider.PRC_SELECT_REQUIRED_DATA_HDR, parameter)

    all_required_data_hdr = []
    for row in out_return_data.getvalue():
        all_required_data_hdr.append(row)
    # print(all_required_bank)

    out_return_data = connection.getCursorVariable()
    parameter = {'OUT_ReturnData':out_return_data}
    connection.queryStoreProcedure(QueryProvider.PRC_SELECT_REQUIRED_DATA_DTL, parameter)
    all_required_data_dtl = []
    for row in out_return_data.getvalue():
        all_required_data_dtl.append(row)
    # print(all_required_setting_data)

    parameter = None
    out_return_data = None
    connection.disconnect()

    result = {}

    for i in range(0,len(all_required_data_hdr)):
        hdrID = all_required_data_hdr[i][0]
        fileName = all_required_data_hdr[i][1]
        refDateFileName = refDate.strftime("%Y%m%d%H%M%S")
        fileName = fileName + '_' + refDateFileName

        result[hdrID] = {GEN_RATE_FILE_NAME : fileName,
                         GEN_RATE_DTL : []}

    for i in range(0,len(all_required_data_dtl)):
        fkHDRID = all_required_data_dtl[i][0]
        baseCurrencyID = all_required_data_dtl[i][1]
        baseCurrency = all_required_data_dtl[i][2]
        pairCurrencyID = all_required_data_dtl[i][3]
        pairCurrency = all_required_data_dtl[i][4]
        pairCurrencyType = all_required_data_dtl[i][5]
        rateType = all_required_data_dtl[i][6]
        type = all_required_data_dtl[i][7]
        bankID = all_required_data_dtl[i][8]

        temp_json = {GEN_RATE_DTL_BASE_CUR_ID : baseCurrencyID,
                     GEN_RATE_DTL_BASE_CUR : baseCurrency,
                     GEN_RATE_DTL_PAIR_CUR_ID : pairCurrencyID,
                     GEN_RATE_DTL_PAIR_CUR : pairCurrency,
                     GEN_RATE_DTL_PAIR_TYPE : pairCurrencyType,
                     GEN_RATE_DTL_RATE_TYPE : rateType,
                     GEN_RATE_DTL_TYPE : type,
                     GEN_RATE_DTL_BANK_ID : bankID}

        if fkHDRID in result:
            result[fkHDRID][GEN_RATE_DTL].append(temp_json)

    # print(result)

    return result

def dataForWritingSetup(connection, dataForGenerating):
    connection.connect()

    result = {}
    for key,value in dataForGenerating.items():
        hdrID = key
        fileName = value[GEN_RATE_FILE_NAME]

        result[hdrID] = {}
        result[hdrID][WRITING_FILE_NAME] = fileName
        result[hdrID][WRITING_DTL] = []

        for item in value[GEN_RATE_DTL]:
            baseCurrencyID = item[GEN_RATE_DTL_BASE_CUR_ID]
            baseCurrency = item[GEN_RATE_DTL_BASE_CUR]
            pairCurrencyID = item[GEN_RATE_DTL_PAIR_CUR_ID]
            pairCurrency = item[GEN_RATE_DTL_PAIR_CUR]
            pairCurrencyType = item[GEN_RATE_DTL_PAIR_TYPE]
            rateType = item[GEN_RATE_DTL_RATE_TYPE]
            type = item[GEN_RATE_DTL_TYPE]
            bankID = item[GEN_RATE_DTL_BANK_ID]

            rateDate = refDate.strftime("%Y%m%d")

            rates = SelectBuyingAndSelling(connection, baseCurrencyID, pairCurrencyID,
                                           pairCurrencyType, bankID, refDate)

            rates_list = rates.fetchall()

            if len(rates_list) == 0 :
                temp_json = {WRITING_DTL_TYPE: type, WRITING_DTL_BASE_CUR: baseCurrency,
                             WRITING_DTL_PAIR_CUR: pairCurrency, WRITING_DTL_RATE_DATE: rateDate,
                             WRITING_DTL_RATE: '-', WRITING_DTL_BASE_VALUE: '-',
                             WRITING_DTL_PAIR_VALUE: '-'}
                result[hdrID][WRITING_DTL].append(temp_json)
            else:
                for item2 in rates_list:
                    buyingRate = item2[0]
                    sellingRate = item2[1]
                    baseValue = item2[2]
                    pairValue = item2[3]
                    averageRate = (buyingRate + sellingRate)/2

                    if rateType == '1':
                        temp_json = {WRITING_DTL_TYPE: type, WRITING_DTL_BASE_CUR: baseCurrency,
                                     WRITING_DTL_PAIR_CUR: pairCurrency, WRITING_DTL_RATE_DATE: rateDate,
                                     WRITING_DTL_RATE: buyingRate, WRITING_DTL_BASE_VALUE: baseValue,
                                     WRITING_DTL_PAIR_VALUE: pairValue}
                    elif rateType == '2':
                        temp_json = {WRITING_DTL_TYPE: type, WRITING_DTL_BASE_CUR: baseCurrency,
                                     WRITING_DTL_PAIR_CUR: pairCurrency, WRITING_DTL_RATE_DATE: rateDate,
                                     WRITING_DTL_RATE: sellingRate, WRITING_DTL_BASE_VALUE: baseValue,
                                     WRITING_DTL_PAIR_VALUE: pairValue}
                    elif rateType == '3':
                        temp_json = {WRITING_DTL_TYPE: type, WRITING_DTL_BASE_CUR: baseCurrency,
                                     WRITING_DTL_PAIR_CUR: pairCurrency, WRITING_DTL_RATE_DATE: rateDate,
                                     WRITING_DTL_RATE: averageRate, WRITING_DTL_BASE_VALUE: baseValue,
                                     WRITING_DTL_PAIR_VALUE: pairValue}

                    result[hdrID][WRITING_DTL].append(temp_json)

    rates = None
    connection.disconnect()

    return result

def write(dataForWriting, dataForStoring):
    global uploadFileNameList
    uploadFileNameList = []

    writingService = WritingService(refDate)

    for key, value in dataForWriting.items():
        hdrID = key
        fileName = value[WRITING_FILE_NAME]

        # bankShortName = value[WRITING_DATA_BANK_SHORT_NAME]
        # refDateFileName = value[WRITING_DATA_BANK_REF_DATE].strftime("%Y%m%d%H%M%S")
        # refDateFileResource = value[WRITING_DATA_BANK_REF_DATE].strftime("%Y/%m/%d%H:%M:%S")

        writingService.setFileName(fileName)
        # writingService.setColumnName(['Type', 'Base Currency', 'Pair Currency', 'Rate Date', 'Rate'])
        writingService.setColumnName(['Type', 'Pair Currency', 'Base Currency', 'Rate Date', 'Rate', '(Leave Blank)', 'Currency unit of Pair & Base currency'])
        writingService.openFile()

        # writingService.writeHeader(
        #     [bankName, 'Date : ' + refDateFileResource[:10], 'Time : ' + refDateFileResource[-8:]])

        # writingService.writeLineColumn()

        for i in value[WRITING_DTL]:
            type = i[WRITING_DTL_TYPE]
            baseCurrency = i[WRITING_DTL_BASE_CUR]
            pairCurrency = i[WRITING_DTL_PAIR_CUR]
            rateDate = i[WRITING_DTL_RATE_DATE]
            if i[WRITING_DTL_RATE] == '-':
                rate = '-'
            else:
                rate = "{0:.5f}".format(i[WRITING_DTL_RATE])
            # currencyUnitOfPairAndBase = str(i[WRITING_DTL_BASE_VALUE]) + ':' + str(i[WRITING_DTL_PAIR_VALUE])
            currencyUnitOfPairAndBase = str(i[WRITING_DTL_PAIR_VALUE]) + ':' + str(i[WRITING_DTL_BASE_VALUE])

            # writingService.writeLineValue([type, baseCurrency, pairCurrency, rateDate, rate])
            writingService.writeLineValue([type, pairCurrency, baseCurrency, rateDate, rate, '', currencyUnitOfPairAndBase])

        writingService.closeFile()

        # uploadFileNameList.append(workingDirectory + '/' + writingService.getAbsoluteFilePath())
        uploadFileNameList.append(writingService.getAbsoluteFilePath())

        # dataForStoring[hdrID][STORING_FILE_PATH] = workingDirectory + '/' + writingService.getAbsoluteFilePath()
        dataForStoring[hdrID][STORING_FILE_PATH] = writingService.getAbsoluteFilePath()
        storingFilePathSplit = dataForStoring[hdrID][STORING_FILE_PATH].split('/')
        dataForStoring[hdrID][STORING_FILE_NAME] = storingFilePathSplit[len(storingFilePathSplit)-1]


def dataForStoringSetup(dataForGenerating):
    result = {}
    for key, value in dataForGenerating.items():
        hdrID = key
        result[hdrID] = {}
        result[hdrID][STORING_FILE_PATH] = None
        result[hdrID][STORING_FILE_NAME] = None
        result[hdrID][STORING_ADD_DATE] = refDate
        # result.append(resultRound)

    return result

def StoringDatabase(connection, dataForStoring):

    connection.connect()

    for key,value in dataForStoring.items():

        fileOwner = key
        filePath = value[STORING_FILE_PATH]
        fileName = value[STORING_FILE_NAME]
        addDate = value[STORING_ADD_DATE]
        StoringAttachFile(connection,fileOwner,filePath,fileName,addDate)

    connection.commit()
    connection.disconnect()

def SelectBuyingAndSelling(connection, baseCurrencyID, pairCurrencyID,
                           pairCurrencyType, bankID, rateDate):
    out_return_data = connection.getCursorVariable()
    parameter = {'OUT_ReturnData': out_return_data, 'IN_BaseCurrency': baseCurrencyID,
                 'IN_PairCurrency' : pairCurrencyID, 'IN_PairCurrencyType': pairCurrencyType,
                 'IN_BankID': bankID, 'IN_RateDate' : rateDate}
    connection.queryStoreProcedure(QueryProvider.PRC_SELECT_EXC_R_FOR_WRITING,parameter)
    return out_return_data.getvalue()

def StoringAttachFile(connection, fileOwner, filePath, fileName, addDate):
    parameter = {'IN_FileOwner': fileOwner, 'IN_FilePath': filePath, 'IN_FileName': fileName,
                 'IN_AddDate': addDate}
    connection.queryStoreProcedure(QueryProvider.PRC_INSERT_GEN_RATE_FILE, parameter)

def FTPSetup():
    # prevWorkingDirectory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # configparserObj = configparser.RawConfigParser()
    # configparserObj.read(prevWorkingDirectory + '/python-config.txt')

    remoteDirArr = configparserObj.get('ftp', 'path').split('/')

    ftpService = FTPService(configparserObj.get('ftp', 'server'),
                            configparserObj.get('ftp', 'username'),
                            configparserObj.get('ftp', 'password'))

    if ftpService.host == None or not ftpService.host:
        return None

    # with open('../python-ftp.txt') as f:
    #     content = f.read().splitlines()
    # remoteDirArr = content[3].split('/')
    # ftpService = FTPService(content[0], content[1], content[2])
    ftpService.login()

    if ftpService.isConnected:
        if ftpService.checkExistDirectory(remoteDirArr[1]):
            if not ftpService.changeDirectory(remoteDirArr[1]):
                return None
            else:
                return ftpService
        else:
            ftpService.createDirectory(remoteDirArr[1])
            if not ftpService.changeDirectory(remoteDirArr[1]):
                return None
            else:
                return ftpService
    else:
        return None

def uploadFTP():
    ftp = FTPSetup()
    if ftp != None:
        for item in uploadFileNameList:
            fileName = item.split('/')
            fileName = fileName[len(fileName)-1]
            file = open(item, 'rb')
            ftp.uploadFile(fileName,file)
            file.close()


def main():
    # try:
    connection = connectionSetup()
    dataForGenerating = dataForGeneratingSetup(connection)
    dataForWriting = dataForWritingSetup(connection, dataForGenerating)
    dataForStoring = dataForStoringSetup(dataForGenerating)
    write(dataForWriting, dataForStoring)
    StoringDatabase(connection, dataForStoring)
    uploadFTP()
    print("END")
    # except Exception as e:
    #     print("EXCEPTION FOUND")
    #     print(e);

GEN_RATE_FILE_NAME = 'GEN_RATE_FILE_NAME'
GEN_RATE_DTL = 'GEN_RATE_DTL'
GEN_RATE_DTL_BASE_CUR_ID = 'GEN_RATE_DTL_BASE_CUR_ID'
GEN_RATE_DTL_BASE_CUR = 'GEN_RATE_DTL_BASE_CUR'
GEN_RATE_DTL_PAIR_CUR_ID = 'GEN_RATE_DTL_PAIR_CUR_ID'
GEN_RATE_DTL_PAIR_CUR = 'GEN_RATE_DTL_PAIR_CUR'
GEN_RATE_DTL_PAIR_TYPE = 'GEN_RATE_DTL_PAIR_TYPE'
GEN_RATE_DTL_RATE_TYPE = 'GEN_RATE_DTL_RATE_TYPE'
GEN_RATE_DTL_TYPE = 'GEN_RATE_DTL_TYPE'
GEN_RATE_DTL_BANK_ID = 'GEN_RATE_DTL_BANK_ID'

WRITING_FILE_NAME = 'WRITING_FILE_NAME'
WRITING_DTL = 'WRITING_DTL'
WRITING_DTL_TYPE = 'WRITING_DTL_TYPE'
WRITING_DTL_BASE_CUR = 'WRITING_DTL_BASE_CUR'
WRITING_DTL_PAIR_CUR = 'WRITING_DTL_PAIR_CUR'
WRITING_DTL_RATE_DATE = 'WRITING_DTL_RATE_DATE'
WRITING_DTL_RATE = 'WRITING_DTL_RATE'
WRITING_DTL_BASE_VALUE = 'WRITING_DTL_BASE_VALUE'
WRITING_DTL_PAIR_VALUE = 'WRITING_DTL_PAIR_VALUE'

STORING_FILE_OWNER = 'STORING_FILE_OWNER'
STORING_FILE_PATH = 'STORING_FILE_PATH'
STORING_FILE_NAME = 'STORING_FILE_NAME'
STORING_ADD_DATE = 'STORING_ADD_DATE'

prevWorkingDirectory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
configparserObj = configparser.RawConfigParser()
configparserObj.read(prevWorkingDirectory + '/python-config.txt')
if configparserObj.get('etc', 'useMachineTime').lower() == 'false' :
    refDate = datetime.datetime.now(datetime.timezone.utc)
    refDate = refDate + datetime.timedelta(hours=8)
    useDate = refDate + datetime.timedelta(hours=24)
else:
    refDate = datetime.datetime.now()
    useDate = refDate + datetime.timedelta(hours=24)

# refDate = datetime.datetime.now(datetime.timezone.utc)
# refDate = refDate + datetime.timedelta(hours=8)

# workingDirectory = os.path.dirname(os.path.abspath(__file__))

uploadFileNameList = []

if __name__ == '__main__':
    main()