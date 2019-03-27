from ConnectionService import ConnectionService
from UtilityProvider import UtilityProvider
from QueryProvider import QueryProvider
from MailService import MailService
import configparser
import datetime
import os

def connectionSetup():
    # with open('../python-config.txt') as f:
        # content = f.read().splitlines()
    # connection = ConnectionService(content[0],content[1],content[2],content[3])
    # connection = ConnectionService('192.168.10.192', 'erm', 'Passw0rd', 'ERM')
    
    connection = ConnectionService(configparserObj.get('database', 'server'),
                                   configparserObj.get('database', 'username'),
                                   configparserObj.get('database', 'password'),
                                   configparserObj.get('database', 'port'),
                                   configparserObj.get('database', 'sid'))

    return connection

def dataForSendingSetup(connection):
    result = []

    connection.connect()

    out_return_data = connection.getCursorVariable()
    parameter = {'OUT_ReturnData': out_return_data }
    connection.queryStoreProcedure(QueryProvider.PRC_SELECT_MANUAL_FAIL, parameter)

    all_manual_fail = []
    for row in out_return_data.getvalue():
        all_manual_fail.append(row)

    resultManual = []
    for item in all_manual_fail:
        resultRound = {}
        resultRound[MANUAL_FAIL_PAIR_CURRENCY] = item[0]
        resultRound[MANUAL_FAIL_BASE_CURRENCY] = item[1]
        resultManual.append(resultRound)

    dateNumberERMFormat = UtilityProvider.convertDateTimeToNumberERMFormat(refDate)

    if dateNumberERMFormat > 2000 or True:
        out_return_data = connection.getCursorVariable()
        parameter = {'OUT_ReturnData': out_return_data}
        connection.queryStoreProcedure(QueryProvider.PRC_SELECT_SCRAPING_FAIL_NIGHT, parameter)

        all_scraping_fail = []
        for row in out_return_data.getvalue():
            all_scraping_fail.append(row)

        resultAuto = []
        for item in all_scraping_fail:
            resultRound = {}
            resultRound[SCRAPING_FAIL_BANK_NAME] = item[0]
            resultAuto.append(resultRound)

        totalScrapingRow = connection.queryStatementReturn(QueryProvider.QRY_SELECT_TOTAL_SCRAPING)
        global totalScraping
        for item in totalScrapingRow:
            totalScraping = item[0]
        global failScraping
        failScraping = len(resultAuto)
    else:
        out_return_data = connection.getCursorVariable()
        parameter = {'OUT_ReturnData': out_return_data}
        connection.queryStoreProcedure(QueryProvider.PRC_SELECT_SCRAPING_FAIL_NOON, parameter)

        all_scraping_fail = []
        for row in out_return_data.getvalue():
            all_scraping_fail.append(row)

        resultAuto = []
        for item in all_scraping_fail:
            resultRound = {}
            resultRound[SCRAPING_FAIL_BANK_NAME] = item[0]
            resultRound[SCRAPING_FAIL_COUNT] = item[1]
            resultAuto.append(resultRound)

    out_return_data = connection.getCursorVariable()
    parameter = {'OUT_ReturnData': out_return_data}
    connection.queryStoreProcedure(QueryProvider.PRC_SELECT_ALL_RECEIVERS, parameter)
    all_receivers = []
    for row in out_return_data.getvalue():
        all_receivers.append(row)

    global receiverList
    receiverList = []
    for item in all_receivers:
        if item[0] is not None or item[0]:
            receiverList.append(item[0])
            # pass
    receiverList.append('chotirote.k.esynergy@gmail.com')

    out_return_data = connection.getCursorVariable()
    parameter = {'OUT_ReturnData': out_return_data, 'IN_IsWeekday' : isWeekday}
    connection.queryStoreProcedure(QueryProvider.PRC_SELECT_SCRAPING_REMAINING,parameter)
    totalScrapingRow = []
    for row in out_return_data.getvalue():
        totalScrapingRow.append(row)
    global remainingScraping
    for item in totalScrapingRow:
        remainingScraping = item[0]

    parameter = None
    out_return_data = None
    connection.disconnect()

    result.append(resultManual)
    result.append(resultAuto)
    return result

def sendEmail(dataForSending):
    mailServer = MailService()
    mailServer.login('rcl.erm.system@gmail.com', 'erm12345678')
    mailServer.setSender('rcl.erm.system@gmail.com')
    mailServer.setReceiver(receiverList)
    mailServer.setSubject('[ERM] Scraping Logs and Remaining of Manual ' + refDate.strftime('%d/%m/%Y %H:%M'))

    message = '<html><body>'
    message = message + '<h1 style="background-color:#ffd777;color:white;">EXCHANGE RATE MANAGEMENT</h1>'
    message = message + '<b>Dear</b><font> :Person in charge</font>'
    message = message + '<br>'
    message = message + '<b>Subject</b><font> :[ERM] Scraping Logs and Remaining of Manual ' + refDate.strftime('%d/%m/%Y %H:%M') + '</font>'
    message = message + '<br><br>'
    message = message + '<table  border="1px" style="width:250px;border-collapse: collapse;">'
    message = message + '<tbody>'
    message = message + '<tr><th colspan="2" bgcolor="#6699ff"><font size="3" color="black">Results of Scraping</font></th></tr>'
    message = message + '<tr>'
    message = message + '<td style="width:130px;" bgcolor="#99ccff"><font color="green"><b>Success</b></font></td>'
    message = message + '<td align="center"><font color="green">' + str(totalScraping-remainingScraping-failScraping) + '</font></td>'
    message = message + '</tr>'
    message = message + '<tr>'
    message = message + '<td style="width:130px;" bgcolor="#99ccff"><font color="red"><b>Fail</b></font></td>'
    message = message + '<td align="center"><font color="red">' + str(failScraping) + '</font></td>'
    message = message + '</tr>'
    message = message + '<tr>'
    message = message + '<td style="width:130px;" bgcolor="#99ccff"><font color="black"><b>Total</b></font></td>'
    message = message + '<td align="center"><font color="black">' + str(totalScraping) + '</font></td>'
    message = message + '</tr>'
    message = message + '<tr>'
    message = message + '<td style="width:130px;" bgcolor="#99ccff"><font color="black"><b>Remaining</b></font></td>'
    message = message + '<td align="center"><font color="black">' + str(remainingScraping) + '</font></td>'
    message = message + '</tr>'
    message = message + '</tbody></table>'
    message = message + '<br>'

    messageTableMaunal = '<table border="1px" style="width:250px;border-collapse: collapse;">'
    messageTableMaunal = messageTableMaunal + '<tbody>'
    messageTableMaunal = messageTableMaunal + '<tr><th colspan="2" bgcolor="#6699ff"><font size="3" color="black">Remaining of Manual Process</font></th></tr>'
    messageTableMaunal = messageTableMaunal + '<tr>'
    messageTableMaunal = messageTableMaunal + '<td bgcolor="#99ccff" align="center"><font color="black"><b>Base</b></font></td>'
    messageTableMaunal = messageTableMaunal + '<td bgcolor="#99ccff" align="center"><font color="black"><b>Pair</b></font></td>'
    messageTableMaunal = messageTableMaunal + '</tr>'


    for i in range(0,len(dataForSending)):
        if i == 0:
            # message = message + 'Manual Process\n'
            for item in dataForSending[i]:
                messageTableMaunal = messageTableMaunal + '<tr>'
                messageTableMaunal = messageTableMaunal + '<td align="center">' + item[MANUAL_FAIL_BASE_CURRENCY] + '</td>'
                messageTableMaunal = messageTableMaunal + '<td align="center">' + item[MANUAL_FAIL_PAIR_CURRENCY] + '</td>'
                messageTableMaunal = messageTableMaunal + '</tr>'

                # message = message + item[MANUAL_FAIL_PAIR_CURRENCY] + ' ' + item[MANUAL_FAIL_BASE_CURRENCY] + '\n'
            # message = message + '\n'
        # else:
            # message = message + 'Auto Process\n'
            # for item in dataForSending[i]:
                # message = message + item[SCRAPING_FAIL_BANK_NAME]
                # if SCRAPING_FAIL_COUNT in item:
                #     message = message + ' ' + str(item[SCRAPING_FAIL_COUNT]) + '\n'
                # else:
                #     message = message + '\n'
            # message = message + '\n'

    messageTableMaunal = messageTableMaunal + '</tbody></table>'
    messageTableMaunal = messageTableMaunal + '<br>'
    message = message + messageTableMaunal
    # message = message + '<span>For more detail, please visit the site: <i>192.168.10.63:8080/erm/logon</i></span>'
    # message = message + '<br>'
    message = message + '<div style="height:30px;background-color:#68dff0;"></div>'
    message = message + "&nbsp;"
    message = message + '</body></html>'

    mailServer.setMessage(message)
    mailServer.send()
    mailServer.quit()

def main():
    connection = connectionSetup()
    dataForSending = dataForSendingSetup(connection)
    sendEmail(dataForSending)
    print("END")

SCRAPING_FAIL_BANK_NAME = 'SCRAPING_FAIL_BANK_NAME'
SCRAPING_FAIL_COUNT = 'SCRAPING_FAIL_COUNT'

MANUAL_FAIL_BASE_CURRENCY = 'MANUAL_FAIL_BASE_CURRENCY'
MANUAL_FAIL_PAIR_CURRENCY = 'MANUAL_FAIL_PAIR_CURRENCY'

prevWorkingDirectory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
configparserObj = configparser.RawConfigParser()
configparserObj.read(prevWorkingDirectory + '/python-config.txt')

refDate = datetime.datetime.now();

# refDate = datetime.datetime.now(datetime.timezone.utc)
# refDate = refDate + datetime.timedelta(hours=8)
if refDate.today().weekday() < 5:
    isWeekday = 1
else:
    isWeekday = 0
workingDirectory = os.path.dirname(os.path.abspath(__file__))
totalScraping = 0
remainingScraping = 0
failScraping = 0
receiverList = []

if __name__ == '__main__':
    main()