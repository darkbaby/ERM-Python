from WritingService import WritingService
from ConnectionService import ConnectionService
from FirefoxService import FirefoxService
from PhantomjsService import PhantomjsService
from QueryProvider import QueryProvider
from UtilityProvider import UtilityProvider
from pyvirtualdisplay import Display
# from APIService import APIService
import configparser
import datetime
import time
import os
import sys

def connectionSetup():

    connection = ConnectionService(configparserObj.get('database', 'server'),
                                   configparserObj.get('database', 'username'),
                                   configparserObj.get('database', 'password'),
                                   configparserObj.get('database', 'port'),
                                   configparserObj.get('database', 'sid'))

    # with open(prevWorkingDirectory + '/python-config.txt') as f:
    #     content = f.read().splitlines()
    # connection = ConnectionService(content[0],content[1],content[2],content[3])
    # connection = ConnectionService('192.168.10.192', 'erm', 'Passw0rd', 'ERM')
    return connection

def dataForScrapingSetup(connection, keyID = -1):

    try:
        connection.connect()

        out_return_data = connection.getCursorVariable()
        currentTimeNumber = UtilityProvider.convertDateTimeToNumberERMFormat(refDate)

        if keyID == -1:
            if currentTimeNumber >= 2130 and currentTimeNumber < 2230:
                parameter = {'OUT_ReturnData': out_return_data, 'IN_CurrentTime': currentTimeNumber}
                connection.queryStoreProcedure(QueryProvider.PRC_SELECT_REQUIRED_EXTRA, parameter)
            else:
                parameter = {'OUT_ReturnData': out_return_data, 'IN_CurrentTime': currentTimeNumber}
                connection.queryStoreProcedure(QueryProvider.PRC_SELECT_REQUIRED_BANK, parameter)
        elif keyID == 0:
            parameter = {'OUT_ReturnData': out_return_data}
            connection.queryStoreProcedure(QueryProvider.PRC_SELECT_ALL_SETTING_HDR, parameter)
        else:
            parameter = {'OUT_ReturnData': out_return_data, 'IN_HdrID': keyID}
            connection.queryStoreProcedure(QueryProvider.PRC_SELECT_SPECIFIC_SETTING_HDR, parameter)

        all_required_bank = []
        for row in out_return_data.getvalue():
            all_required_bank.append(row)
        # print(all_required_bank)

        out_return_data = connection.getCursorVariable()
        parameter = {'OUT_ReturnData':out_return_data}
        connection.queryStoreProcedure(QueryProvider.PRC_SELECT_REQUIRED_SETTING, parameter)
        all_required_setting_data = []
        for row in out_return_data.getvalue():
            all_required_setting_data.append(row)
        # print(all_required_setting_data)

        out_return_data = connection.getCursorVariable()
        parameter = {'OUT_ReturnData': out_return_data}
        connection.queryStoreProcedure(QueryProvider.PRC_SELECT_REF_EXCHANGE_RATE, parameter)
        all_ref_exchange_rate = []
        for row in out_return_data.getvalue():
            all_ref_exchange_rate.append(row)

        parameter = None
        out_return_data = None
        connection.disconnect()

        result = {}

        for i in range(0,len(all_required_bank)):
            bankID = all_required_bank[i][0]
            bankURL = all_required_bank[i][1]
            bankName = all_required_bank[i][2]
            bankShortName = all_required_bank[i][3]
            bankPageType = all_required_bank[i][4]
            bankExtractType = all_required_bank[i][5]
            bankDateSelector = all_required_bank[i][6]
            bankDateFormat = all_required_bank[i][7]
            setHDRID = all_required_bank[i][8]
            pairCurrencyType = all_required_bank[i][9]
            bankCurrencyID = all_required_bank[i][10]
            bankBaseValue = all_required_bank[i][11]
            extractionDate = all_required_bank[i][12]

            if extractionDate == 'Weekday' and not isWeekday:
                continue
            elif extractionDate == 'Weekend' and isWeekday:
                continue

            if bankPageType == 2 or True:
                if 'PHANTOMJS_DATA' not in result:
                    result['PHANTOMJS_DATA'] = {}
                result['PHANTOMJS_DATA'][bankID] = {BANK_DATA : {BANK_DATA_URL : bankURL,
                                                                 BANK_DATA_NAME : bankName,
                                                                 BANK_DATA_SHORT_NAME : bankShortName,
                                                                 BANK_DATA_PAGE_TYPE : bankPageType,
                                                                 BANK_DATA_EXTRACT_TYPE : bankExtractType,
                                                                 BANK_DATA_DATE_SELECTOR : bankDateSelector,
                                                                 BANK_DATA_DATE_FORMAT : bankDateFormat,
                                                                 BANK_DATA_PAIR_CURRENCY_TYPE : pairCurrencyType,
                                                                 BANK_DATA_BANK_CURRENCY_ID : bankCurrencyID,
                                                                 BANK_DATA_BANK_BASE_VALUE : bankBaseValue,
                                                                 BANK_DATA_SET_HDR_ID : setHDRID},
                                                  SETTING_DATA : []}
            elif bankPageType == 1:
                if 'FIREFOX_DATA' not in result:
                    result['FIREFOX_DATA'] = {}
                result['FIREFOX_DATA'][bankID] = {BANK_DATA: {BANK_DATA_URL: bankURL,
                                                              BANK_DATA_NAME: bankName,
                                                              BANK_DATA_SHORT_NAME: bankShortName,
                                                              BANK_DATA_PAGE_TYPE: bankPageType,
                                                              BANK_DATA_EXTRACT_TYPE: bankExtractType,
                                                              BANK_DATA_DATE_SELECTOR: bankDateSelector,
                                                              BANK_DATA_DATE_FORMAT: bankDateFormat,
                                                              BANK_DATA_PAIR_CURRENCY_TYPE: pairCurrencyType,
                                                              BANK_DATA_BANK_CURRENCY_ID: bankCurrencyID,
                                                              BANK_DATA_BANK_BASE_VALUE: bankBaseValue,
                                                              BANK_DATA_SET_HDR_ID: setHDRID},
                                                    SETTING_DATA: []}

        for i in range(0,len(all_required_setting_data)):
            bankID = all_required_setting_data[i][0]
            currencyID = all_required_setting_data[i][1]
            currencyName = all_required_setting_data[i][2]
            currencyValue = all_required_setting_data[i][3]
            extractCurrency = all_required_setting_data[i][4]
            extractBuyingRate = all_required_setting_data[i][5]
            extractSellingRate = all_required_setting_data[i][6]
            temp_json = {SETTING_DATA_CURRENCY_ID : currencyID,
                         SETTING_DATA_CURRENCY_NAME : currencyName,
                         SETTING_DATA_CURRENCY_VALUE : currencyValue,
                         SETTING_DATA_EXTRACT_CURRENCY : extractCurrency,
                         SETTING_DATA_EXTRACT_BUYING_RATE : extractBuyingRate,
                         SETTING_DATA_EXTRACT_SELLING_RATE : extractSellingRate}

            if 'FIREFOX_DATA' in result:
                if bankID in result['FIREFOX_DATA']:
                    result['FIREFOX_DATA'][bankID][SETTING_DATA].append(temp_json)
                    continue

            if 'PHANTOMJS_DATA' in result:
                if bankID in result['PHANTOMJS_DATA']:
                    result['PHANTOMJS_DATA'][bankID][SETTING_DATA].append(temp_json)
                    continue

        # print(result)

        global refExchangeRate
        refExchangeRate = {}
        for i in range(0, len(all_ref_exchange_rate)):

            if all_ref_exchange_rate[i][4] not in refExchangeRate:
                refExchangeRate[all_ref_exchange_rate[i][4]] = []

            refExchangeRate[all_ref_exchange_rate[i][4]].append({
                REF_EXCHANGE_RATE_BUYING_RATE : all_ref_exchange_rate[i][0],
                REF_EXCHANGE_RATE_SELLING_RATE : all_ref_exchange_rate[i][1],
                REF_EXCHANGE_RATE_BASE_CURRENCY : all_ref_exchange_rate[i][2],
                REF_EXCHANGE_RATE_PAIR_CURRENCY : all_ref_exchange_rate[i][3]
            })

        return result
    except Exception as e:
        connection.disconnect()
        print(str(e))
        return {}

def scrap(dataForScraping):

    result = {}

    firefoxService = None
    phantomjsService = None
    scrapingService = None

    try:

        for driverName,data in dataForScraping.items():

            if driverName == 'FIREFOX_DATA':
                firefoxService = FirefoxService(refDate)
                scrapingService = firefoxService
            elif driverName == 'PHANTOMJS_DATA':
                phantomjsService = PhantomjsService(refDate)
                scrapingService = phantomjsService
            #scrapingService.setTimeout(30)
            for key, value in data.items():

                scrapingService.openNewTab()

            #when initialize instant of webdriver, it's always have 1 tab at begin, so we need to close that when we open new tab according to length of array
            time.sleep(2)
            scrapingService.close()

            scrapingService.switchToTabIndex(0)
            for key, value in data.items():

                scrapingService.setURL(value[BANK_DATA][BANK_DATA_URL])
                scrapingService.scrap()

                scrapingService.switchToTabIndex(scrapingService.getCurrentWindowIndex() + 1)

            print('start time sleep')

            time.sleep(20 + (3*len(data)))

            scrapingService.switchToTabIndex(0)
            isFirstRound = True
            for key, value in data.items():

                bankID = key
                bankName = value[BANK_DATA][BANK_DATA_NAME]
                bankShortName = value[BANK_DATA][BANK_DATA_SHORT_NAME]
                bankDateFormat = value[BANK_DATA][BANK_DATA_DATE_FORMAT]
                setHDRID = value[BANK_DATA][BANK_DATA_SET_HDR_ID]
                bankExtractType = value[BANK_DATA][BANK_DATA_EXTRACT_TYPE]
                pairCurrencyType = value[BANK_DATA][BANK_DATA_PAIR_CURRENCY_TYPE]
                bankCurrencyID = value[BANK_DATA][BANK_DATA_BANK_CURRENCY_ID]
                bankBaseValue = value[BANK_DATA][BANK_DATA_BANK_BASE_VALUE]
                requiredTag = 'td'
                scrapingService.setExtractionType(bankExtractType, requiredTag)

                print(bankName)

                if 'problem' in scrapingService.getTitleOfPage().lower():
                    result[bankID] = {SCRAP_DATA_BANK: {SCRAP_DATA_BANK_NAME: bankName,
                                                        SCRAP_DATA_BANK_SHORT_NAME: bankShortName,
                                                        SCRAP_DATA_BANK_IMG_PATH_FILE: None,
                                                        SCRAP_DATA_BANK_PAIR_CURRENCY_TYPE: pairCurrencyType,
                                                        SCRAP_DATA_BANK_CURRENCY_ID: bankCurrencyID,
                                                        SCRAP_DATA_BANK_BASE_VALUE: bankBaseValue,
                                                        SCRAP_DATA_BANK_SET_HDR_ID: setHDRID},
                                      SCRAP_DATA_CURRENCY: [],
                                      SCRAP_DATA_LOG: {SCRAP_DATA_LOG_STATUS: 'FAIL',
                                                       SCRAP_DATA_LOG_DESCRIPTION: 'url is no longer usable or response from url need more time to proceed'}}
                    print('url is no longer usable or response from url need more time to proceed')
                    scrapingService.switchToTabIndex(scrapingService.getCurrentWindowIndex() + 1)
                    continue

                if bankExtractType == 1:
                    dateNowPageFormat = UtilityProvider.convertDateToString(refDate, bankDateFormat)
                    dateFromPage = scrapingService.getField(value[BANK_DATA][BANK_DATA_DATE_SELECTOR])
                elif bankExtractType == 2:
                    dateNowPageFormat = UtilityProvider.convertDateToString(refDate, bankDateFormat)
                    # cssSelectorForSending = [dateNowPageFormat,0]
                    dateFromPage = scrapingService.searchDateOnPage(dateNowPageFormat)

                if dateFromPage == None:
                    if bankExtractType == 1:
                        result[bankID] = {SCRAP_DATA_BANK: {SCRAP_DATA_BANK_NAME: bankName,
                                                            SCRAP_DATA_BANK_SHORT_NAME: bankShortName,
                                                            SCRAP_DATA_BANK_IMG_PATH_FILE: None,
                                                            SCRAP_DATA_BANK_PAIR_CURRENCY_TYPE: pairCurrencyType,
                                                            SCRAP_DATA_BANK_CURRENCY_ID: bankCurrencyID,
                                                            SCRAP_DATA_BANK_BASE_VALUE: bankBaseValue,
                                                            SCRAP_DATA_BANK_SET_HDR_ID: setHDRID},
                                          SCRAP_DATA_CURRENCY: [],
                                          SCRAP_DATA_LOG: {SCRAP_DATA_LOG_STATUS: 'FAIL',
                                                           SCRAP_DATA_LOG_DESCRIPTION: 'url is wrong or css selector of date is no longer usable'}}
                        print('url is wrong or css selector of date is no longer usable')
                        scrapingService.switchToTabIndex(scrapingService.getCurrentWindowIndex() + 1)
                    elif bankExtractType == 2:
                        result[bankID] = {SCRAP_DATA_BANK: {SCRAP_DATA_BANK_NAME: bankName,
                                                            SCRAP_DATA_BANK_SHORT_NAME: bankShortName,
                                                            SCRAP_DATA_BANK_IMG_PATH_FILE: None,
                                                            SCRAP_DATA_BANK_PAIR_CURRENCY_TYPE: pairCurrencyType,
                                                            SCRAP_DATA_BANK_CURRENCY_ID: bankCurrencyID,
                                                            SCRAP_DATA_BANK_BASE_VALUE: bankBaseValue,
                                                            SCRAP_DATA_BANK_SET_HDR_ID: setHDRID},
                                          SCRAP_DATA_CURRENCY: [],
                                          SCRAP_DATA_LOG: {SCRAP_DATA_LOG_STATUS: 'FAIL',
                                                           SCRAP_DATA_LOG_DESCRIPTION: 'url or date format is wrong or date on page is not updated'}}
                        print('url or date format is wrong or date on page is not updated')
                        scrapingService.switchToTabIndex(scrapingService.getCurrentWindowIndex() + 1)
                    continue

                if dateNowPageFormat.lower() not in dateFromPage.lower():
                    result[bankID] = {SCRAP_DATA_BANK: {SCRAP_DATA_BANK_NAME: bankName,
                                                        SCRAP_DATA_BANK_SHORT_NAME: bankShortName,
                                                        SCRAP_DATA_BANK_IMG_PATH_FILE: None,
                                                        SCRAP_DATA_BANK_PAIR_CURRENCY_TYPE: pairCurrencyType,
                                                        SCRAP_DATA_BANK_CURRENCY_ID: bankCurrencyID,
                                                        SCRAP_DATA_BANK_BASE_VALUE: bankBaseValue,
                                                        SCRAP_DATA_BANK_SET_HDR_ID: setHDRID},
                                      SCRAP_DATA_CURRENCY: [],
                                      SCRAP_DATA_LOG: {SCRAP_DATA_LOG_STATUS: 'FAIL',
                                                       SCRAP_DATA_LOG_DESCRIPTION: 'data on page is not according to present'}}
                    print('data on page isnt according to present')
                    scrapingService.switchToTabIndex(scrapingService.getCurrentWindowIndex() + 1)
                    continue

                isError = False
                result_each_bank_currency = []
                for item in value[SETTING_DATA]:
                    currencyID = item[SETTING_DATA_CURRENCY_ID]
                    currencyName = item[SETTING_DATA_CURRENCY_NAME]
                    currencyValue = item[SETTING_DATA_CURRENCY_VALUE]

                    if bankExtractType == 1:
                        if item[SETTING_DATA_EXTRACT_CURRENCY] != None:
                            currencyNameFromPage = scrapingService.getField(item[SETTING_DATA_EXTRACT_CURRENCY])
                            if currencyNameFromPage == None or currencyName not in currencyNameFromPage:
                                log_description = 'can not find correct currency ' + currencyName
                                isError = True
                                break
                        cssSelectorForBuyingRate = item[SETTING_DATA_EXTRACT_BUYING_RATE]
                        cssSelectorForSellingRate = item[SETTING_DATA_EXTRACT_SELLING_RATE]
                        if cssSelectorForBuyingRate == None or cssSelectorForBuyingRate.strip() == '':
                            buyingRateValue = '0'
                        else:
                            buyingRateValue = scrapingService.getField(cssSelectorForBuyingRate).strip().replace(',', '')
                        if cssSelectorForSellingRate == None or cssSelectorForSellingRate.strip() == '':
                            sellingRateValue = '0'
                        else:
                            sellingRateValue = scrapingService.getField(cssSelectorForSellingRate).strip().replace(',', '')

                    elif bankExtractType == 2:
                        cssSelectorForSending = [currencyName,0]
                        currencyNameFromPage = scrapingService.getField(cssSelectorForSending)
                        if currencyNameFromPage == None or currencyName not in currencyNameFromPage:
                            log_description = 'can not find correct currency ' + currencyName
                            isError = True
                            break

                        cssSelectorForBuyingRate = item[SETTING_DATA_EXTRACT_BUYING_RATE]
                        cssSelectorForSellingRate = item[SETTING_DATA_EXTRACT_SELLING_RATE]
                        if cssSelectorForBuyingRate == None or cssSelectorForBuyingRate.strip() == '':
                            buyingRateValue = '0'
                        else:
                            cssSelectorForSending = [currencyName, int(cssSelectorForBuyingRate)]
                            buyingRateValue = scrapingService.getField(cssSelectorForSending).strip().replace(',', '')
                        if cssSelectorForSellingRate == None or cssSelectorForSellingRate.strip() == '':
                            sellingRateValue = '0'
                        else:
                            cssSelectorForSending = [currencyName, int(cssSelectorForSellingRate)]
                            sellingRateValue = scrapingService.getField(cssSelectorForSending).strip().replace(',', '')

                    if buyingRateValue != None and sellingRateValue != None:
                        if not UtilityProvider.isNumeric(buyingRateValue):
                            log_description = 'buying rate value of ' + currencyName + ' is not a number'
                            isError = True
                            break
                        if not UtilityProvider.isNumeric(sellingRateValue):
                            log_description = 'selling rate value of ' + currencyName + ' is not a number'
                            isError = True
                            break

                        # buyingRateValueNumeric = round(float(buyingRateValue),5)
                        # sellingRateValueNumeric = round(float(sellingRateValue),5)
                        # maxDiff = sellingRateValueNumeric*0.15
                        # if buyingRateValueNumeric < sellingRateValueNumeric-maxDiff:
                        #     log_description = 'buying rate value of ' + currencyName + ' is lower than selling rate over 15%'
                        #     isError = True
                        #     break

                        if bankID in refExchangeRate:
                            for i in range(0,len(refExchangeRate[bankID])):
                                if refExchangeRate[bankID][i][REF_EXCHANGE_RATE_PAIR_CURRENCY] == bankCurrencyID and refExchangeRate[bankID][i][REF_EXCHANGE_RATE_BASE_CURRENCY] == currencyID:
                                    refBuyingRateValueNumeric = round(float(refExchangeRate[bankID][i][REF_EXCHANGE_RATE_BUYING_RATE]), 5)
                                    refSellingRateValueNumeric = round(float(refExchangeRate[bankID][i][REF_EXCHANGE_RATE_SELLING_RATE]), 5)
                                    buyingRateValueNumeric = round(float(buyingRateValue),5)
                                    sellingRateValueNumeric = round(float(sellingRateValue),5)
                                    diffBuyingRate = abs(refBuyingRateValueNumeric - buyingRateValueNumeric)
                                    diffSellingRate = abs(refSellingRateValueNumeric - sellingRateValueNumeric)
                                    if diffBuyingRate > refBuyingRateValueNumeric*0.03 and buyingRateValueNumeric != 0 and refBuyingRateValueNumeric != 0:
                                        log_description = 'buying rate value of ' + currencyName + ' be different with reference buying rate more than 3%'
                                        isError = True
                                        break
                                    if diffSellingRate > refSellingRateValueNumeric*0.03 and sellingRateValueNumeric != 0 and refSellingRateValueNumeric != 0:
                                        log_description = 'selling rate value of ' + currencyName + ' be different with reference selling rate more than 3%'
                                        isError = True
                                        break

                        #success case
                        result_round = {SCRAP_DATA_CURRENCY_ID: currencyID,
                                        SCRAP_DATA_CURRENCY_NAME: currencyName,
                                        SCRAP_DATA_CURRENCY_VALUE: currencyValue,
                                        SCRAP_DATA_CURRENCY_BUYING_RATE: buyingRateValue,
                                        SCRAP_DATA_CURRENCY_SELLING_RATE: sellingRateValue}
                        result_each_bank_currency.append(result_round)
                        #end success case

                    elif buyingRateValue == None and sellingRateValue == None:
                        log_description = 'can not find both buying rate and selling rate of ' + currencyName
                        isError = True
                        break
                    elif buyingRateValue == None:
                        log_description = 'can not find buying rate of ' + currencyName
                        isError = True
                        break
                    elif sellingRateValue == None:
                        log_description = 'can not find selling rate of ' + currencyName
                        isError = True
                        break

                if isError:
                    result[bankID] = {SCRAP_DATA_BANK: {SCRAP_DATA_BANK_NAME: bankName,
                                                        SCRAP_DATA_BANK_SHORT_NAME: bankShortName,
                                                        SCRAP_DATA_BANK_IMG_PATH_FILE: None,
                                                        SCRAP_DATA_BANK_PAIR_CURRENCY_TYPE: pairCurrencyType,
                                                        SCRAP_DATA_BANK_CURRENCY_ID: bankCurrencyID,
                                                        SCRAP_DATA_BANK_BASE_VALUE: bankBaseValue,
                                                        SCRAP_DATA_BANK_SET_HDR_ID: setHDRID},
                                      SCRAP_DATA_CURRENCY: result_each_bank_currency,
                                      SCRAP_DATA_LOG: {SCRAP_DATA_LOG_STATUS: 'FAIL',
                                                       SCRAP_DATA_LOG_DESCRIPTION: log_description}}
                else:
                    refDateFileName = useDate.strftime("%Y%m%d%H%M%S")
                    imgPathFile = scrapingService.getScreenShot(refDateFileName + bankShortName)
                    tempDeletingFilesName.append(imgPathFile)

                    result[bankID] = {SCRAP_DATA_BANK: {SCRAP_DATA_BANK_NAME: bankName,
                                                        SCRAP_DATA_BANK_SHORT_NAME: bankShortName,
                                                        SCRAP_DATA_BANK_IMG_PATH_FILE: imgPathFile,
                                                        SCRAP_DATA_BANK_PAIR_CURRENCY_TYPE: pairCurrencyType,
                                                        SCRAP_DATA_BANK_CURRENCY_ID: bankCurrencyID,
                                                        SCRAP_DATA_BANK_BASE_VALUE: bankBaseValue,
                                                        SCRAP_DATA_BANK_SET_HDR_ID: setHDRID},
                                      SCRAP_DATA_CURRENCY: result_each_bank_currency,
                                      SCRAP_DATA_LOG: {SCRAP_DATA_LOG_STATUS: 'SUCCESS',
                                                       SCRAP_DATA_LOG_DESCRIPTION: 'GET RATE SUCCESSFUL'}}

                scrapingService.switchToTabIndex(scrapingService.getCurrentWindowIndex() + 1)

            scrapingService.quit()

    except Exception as e:
        print(e)
        if scrapingService != None:
            scrapingService.quit()
        if firefoxService != None:
            firefoxService.quit()
        if phantomjsService != None:
            phantomjsService.quit()

    return result

def dataForWritingSetup(scrapingResult):

    result = {}

    for key,value in scrapingResult.items():

        if value[SCRAP_DATA_LOG][SCRAP_DATA_LOG_STATUS] == 'FAIL':
            continue

        bankID = key
        bankName = value[SCRAP_DATA_BANK][SCRAP_DATA_BANK_NAME]
        bankShortName = value[SCRAP_DATA_BANK][SCRAP_DATA_BANK_SHORT_NAME]
        refDate = useDate

        if bankID not in result:
            result[bankID] = {WRITING_DATA_BANK_NAME : bankName,
                              WRITING_DATA_BANK_SHORT_NAME : bankShortName,
                              WRITING_DATA_BANK_REF_DATE: refDate,
                              WRITING_DATA_CURRENCY : {}}

        for item in value[SCRAP_DATA_CURRENCY]:
            currencyName = item[SCRAP_DATA_CURRENCY_NAME]
            currencyValue = item[SCRAP_DATA_CURRENCY_VALUE]
            buyingRate = "{0:.5f}".format(round(float(item[SCRAP_DATA_CURRENCY_BUYING_RATE]),5))
            sellingRate = "{0:.5f}".format(round(float(item[SCRAP_DATA_CURRENCY_SELLING_RATE]),5))

            if currencyName not in result[bankID][WRITING_DATA_CURRENCY]:
                result[bankID][WRITING_DATA_CURRENCY][currencyName] = {WRITING_DATA_CURRENCY_VALUE: currencyValue,
                                                                       WRITING_DATA_CURRENCY_BUYING_RATE: None,
                                                                       WRITING_DATA_CURRENCY_SELLING_RATE: None}

            result[bankID][WRITING_DATA_CURRENCY][currencyName][WRITING_DATA_CURRENCY_BUYING_RATE] = buyingRate
            result[bankID][WRITING_DATA_CURRENCY][currencyName][WRITING_DATA_CURRENCY_SELLING_RATE] = sellingRate

    return result

def write(dataForWriting, dataForStoring):

    writingService = WritingService(refDate)

    for key, value in dataForWriting.items():
        bankID = key
        bankName = value[WRITING_DATA_BANK_NAME]
        bankShortName = value[WRITING_DATA_BANK_SHORT_NAME]
        refDateFileName = value[WRITING_DATA_BANK_REF_DATE].strftime("%Y%m%d%H%M%S")
        refDateFileResource = value[WRITING_DATA_BANK_REF_DATE].strftime("%Y/%m/%d%H:%M:%S")

        writingService.setFileName(refDateFileName + bankShortName)
        writingService.setColumnName(['Currency', 'Value', 'Buying Rates', 'Selling Rates'])
        writingService.openFile()

        writingService.writeHeader([bankName, 'Rate Date : ' + refDateFileResource[:10], 'Time : ' + refDateFileResource[-8:]])
        writingService.writeLineColumn()

        for key2, value2 in value[WRITING_DATA_CURRENCY].items():
            currencyName = key2
            value = value2[WRITING_DATA_CURRENCY_VALUE]
            buyingRate = value2[WRITING_DATA_CURRENCY_BUYING_RATE]
            sellingRate = value2[WRITING_DATA_CURRENCY_SELLING_RATE]
            writingService.writeLineValue([currencyName,value,buyingRate,sellingRate])

        writingService.closeFile()

        dataForStoring[bankID][STORING_DATA_HDR_TEXT_PATH_FILE] = writingService.getAbsoluteFilePath()
        tempDeletingFilesName.append(writingService.getAbsoluteFilePath())

def dataForStoringSetup(scrapingResult):
    result = {}
    for key, value in scrapingResult.items():

        bankID = key
        bankName = value[SCRAP_DATA_BANK][SCRAP_DATA_BANK_NAME]
        bankShortName = value[SCRAP_DATA_BANK][SCRAP_DATA_BANK_SHORT_NAME]
        imgPathFile = value[SCRAP_DATA_BANK][SCRAP_DATA_BANK_IMG_PATH_FILE]
        pairCurrencyType = value[SCRAP_DATA_BANK][SCRAP_DATA_BANK_PAIR_CURRENCY_TYPE]
        bankCurrencyID = value[SCRAP_DATA_BANK][SCRAP_DATA_BANK_CURRENCY_ID]
        bankBaseValue = value[SCRAP_DATA_BANK][SCRAP_DATA_BANK_BASE_VALUE]
        setHDRID = value[SCRAP_DATA_BANK][SCRAP_DATA_BANK_SET_HDR_ID]
        logStatus = value[SCRAP_DATA_LOG][SCRAP_DATA_LOG_STATUS]
        logDescription = value[SCRAP_DATA_LOG][SCRAP_DATA_LOG_DESCRIPTION]

        result[bankID] = {STORING_DATA_HDR_TYPE: 'AUTO',
                          STORING_DATA_HDR_RATE_DATE: useDate,
                          STORING_DATA_HDR_IMG_PATH_FILE: imgPathFile,
                          STORING_DATA_HDR_TEXT_PATH_FILE: None,
                          STORING_DATA_HDR_ADD_DATE : refDate,
                          STORING_DATA_HDR_PAIR_CURRENCY_TYPE : pairCurrencyType,
                          STORING_DATA_DTL: [],
                          STORING_DATA_LOG: {
                              STORING_DATA_LOG_ADD_DATE: refDate,
                              STORING_DATA_LOG_DESCRIPTION: logDescription,
                              STORING_DATA_LOG_STATUS: logStatus,
                              STORING_DATA_LOG_SET_HDR_ID: setHDRID
                          }}

        if logStatus != 'SUCCESS':
            continue

        for item in value[SCRAP_DATA_CURRENCY]:

            scrapCurrencyID = item[SCRAP_DATA_CURRENCY_ID]
            scrapCurrencyName = item[SCRAP_DATA_CURRENCY_NAME]
            scrapCurrencyValue = item[SCRAP_DATA_CURRENCY_VALUE]
            scrapBuyingRate = item[SCRAP_DATA_CURRENCY_BUYING_RATE]
            scrapSellingRate = item[SCRAP_DATA_CURRENCY_SELLING_RATE]

            resultRound = {}
            resultRound[STORING_DATA_DTL_BASE_VALUE] = bankBaseValue
            resultRound[STORING_DATA_DTL_VALUE] = scrapCurrencyValue
            resultRound[STORING_DATA_DTL_BUYING_RATE] = scrapBuyingRate
            resultRound[STORING_DATA_DTL_SELLING_RATE] = scrapSellingRate
            resultRound[STORING_DATA_DTL_PAIR_CURRENCY] = scrapCurrencyID
            resultRound[STORING_DATA_DTL_BASE_CURRENCY] = bankCurrencyID
            resultRound[STORING_DATA_DTL_RECORD_STATUS] = 'A'
            resultRound[STORING_DATA_DTL_ADD_DATE] = refDate

            result[bankID][STORING_DATA_DTL].append(resultRound)

    return result

def StoreScrapingResultToDatabase(connection, dataForStoring):
        for key,value in dataForStoring.items():

            bankID = int(key)
            type = value[STORING_DATA_HDR_TYPE]
            rateDate = value[STORING_DATA_HDR_RATE_DATE]
            pairCurrencyType = value[STORING_DATA_HDR_PAIR_CURRENCY_TYPE]
            imgPathFile = value[STORING_DATA_HDR_IMG_PATH_FILE]
            textPathFile = value[STORING_DATA_HDR_TEXT_PATH_FILE]
            hdrAddDate = value[STORING_DATA_HDR_ADD_DATE]
            logStatus = value[STORING_DATA_LOG][STORING_DATA_LOG_STATUS]
            logDescription = value[STORING_DATA_LOG][STORING_DATA_LOG_DESCRIPTION]
            logAddDate = value[STORING_DATA_LOG][STORING_DATA_LOG_ADD_DATE]
            logSetHDRID = value[STORING_DATA_LOG][STORING_DATA_LOG_SET_HDR_ID]

            if logStatus != 'SUCCESS':
                StoreExtractRepeat(connection, logSetHDRID)
                logID = StoreHistLog(connection, logSetHDRID, logStatus, logDescription, logAddDate, None)
                continue
            else:
                RemoveExtractRepeat(connection, logSetHDRID)
                hdrID = StoreExchangeRateHDR(connection, rateDate, type, pairCurrencyType, hdrAddDate)
                imgPathFileSplit = imgPathFile.split('/')
                imgFileName = imgPathFileSplit[len(imgPathFileSplit) - 1]
                textPathFileSplit = textPathFile.split('/')
                textFileName = textPathFileSplit[len(textPathFileSplit) - 1]
                StoreAttachFile(connection, imgPathFile, hdrID, imgFileName)
                StoreAttachFile(connection, textPathFile, hdrID, textFileName)
                StoreExchangeRateBank(connection, hdrID, bankID)
                logID = StoreHistLog(connection, logSetHDRID, logStatus, logDescription, logAddDate, hdrID)

            for item in value[STORING_DATA_DTL]:
                dtlAddDate = item[STORING_DATA_DTL_ADD_DATE]
                currencyID = item[STORING_DATA_DTL_PAIR_CURRENCY]
                currencyBaseValue = item[STORING_DATA_DTL_BASE_VALUE]
                currencyValue = item[STORING_DATA_DTL_VALUE]
                buyingRate = item[STORING_DATA_DTL_BUYING_RATE]
                sellingRate = item[STORING_DATA_DTL_SELLING_RATE]
                bankCurrencyID = item[STORING_DATA_DTL_BASE_CURRENCY]
                recordStatus = item[STORING_DATA_DTL_RECORD_STATUS]

                # if pairCurrencyType == 1:
                #     dtl_id = StoreExchangeRateDTL(connection, hdrID, currencyValue, buyingRate, sellingRate,
                #                                   currencyID, bankCurrencyID, recordStatus, dtlAddDate)
                # else:
                dtl_id = StoreExchangeRateDTL(connection, hdrID, currencyBaseValue, currencyValue, buyingRate, sellingRate,
                                              bankCurrencyID, currencyID, recordStatus, dtlAddDate)

def StoreExchangeRateHDR(connection, rateDate, type, pairCurrencyType, addDate):
    out_return_data = connection.getNumberVariable()
    parameter = {'OUT_ReturnData': out_return_data, 'IN_RateDate': rateDate,
                 'IN_PairCurrencyType' : pairCurrencyType, 'IN_Type': type,
                 'IN_AddDate': addDate, 'IN_DelegateUser' : delegateUser}
    connection.queryStoreProcedure(QueryProvider.PRC_INSERT_EXCHANGE_RATE_HDR,parameter)
    return out_return_data.getvalue()

def StoreAttachFile(connection, pathFile, hdrID, fileName):
    parameter = {'IN_FilePath' : pathFile , 'IN_FileOwner': hdrID, 'IN_TypeName': 'AUTO',
                 'IN_FileName' : fileName}
    connection.queryStoreProcedure(QueryProvider.PRC_INSERT_ATTACH_FILE, parameter)

def StoreExchangeRateDTL(connection, hdrID, baseValue, value, buyingRate, sellingRate, baseCurrency, pairCurrency,
                         recordStatus, addDate):
    out_return_data = connection.getNumberVariable()
    parameter = {'OUT_ReturnData': out_return_data, 'IN_HDRID': hdrID,
                 'IN_BaseValue': baseValue, 'IN_Value': value,
                 'IN_BuyingRate': buyingRate, 'IN_SellingRate': sellingRate, 'IN_BaseCurrency': baseCurrency,
                 'IN_PairCurrency': pairCurrency,
                 'IN_RecordStatus': recordStatus, 'IN_AddDate' : addDate,
                 'IN_DelegateUser': delegateUser}
    connection.queryStoreProcedure(QueryProvider.PRC_INSERT_EXCHANGE_RATE_DTL,parameter)
    return out_return_data.getvalue()

def StoreExchangeRateBank(connection, hdrID, bankID):
    parameter = {'IN_HDRID': hdrID, 'IN_BankID': bankID}
    connection.queryStoreProcedure(QueryProvider.PRC_INSERT_EXCHANGE_RATE_BANK, parameter)

def StoreHistLog(connection, setHDRID, logStatus, logDescription, logAddDate, hdrID):
    out_return_data = connection.getNumberVariable()
    parameter = {'OUT_ReturnData' : out_return_data,
                 'IN_SetHDRID' : setHDRID, 'IN_LogModule' : 'ERM',
                 'IN_LogStatus' : logStatus, 'IN_LogDescription' : logDescription,
                 'IN_AddDate' : logAddDate, 'IN_HDRID': hdrID,
                 'IN_DelegateUser' : delegateUser}
    connection.queryStoreProcedure(QueryProvider.PRC_INSERT_HIST_LOG, parameter)
    return out_return_data.getvalue()

def StoreExtractRepeat(connection, setHDRID):
    parameter = {'IN_SetHDRID' : setHDRID}
    connection.queryStoreProcedure(QueryProvider.PRC_INSERT_AND_UPDATE_EXTRACT_REP,parameter)

def RemoveExtractRepeat(connection, setHDRID):
    parameter = {'IN_SetHDRID' : setHDRID}
    connection.queryStoreProcedure(QueryProvider.PRC_DELTE_EXTRACT_REP,parameter)

def main():
    # display = Display(visible=0,size=(1600,900))
    # display.start()
    connection = connectionSetup()

    if len(sys.argv) == 3 and sys.argv[1].isdigit() :
        global  delegateUser
        delegateUser = sys.argv[2]
        dataForScraping = dataForScrapingSetup(connection, int(sys.argv[1]))
    else:
        dataForScraping = dataForScrapingSetup(connection)

    resultFromScraping = scrap(dataForScraping)
    # display.stop()
    dataForStoring = dataForStoringSetup(resultFromScraping)
    dataForWriting = dataForWritingSetup(resultFromScraping)

    try:
        write(dataForWriting, dataForStoring)
        connection.connect()
        StoreScrapingResultToDatabase(connection, dataForStoring)
        connection.commit()
        connection.disconnect()

    except Exception as e:
        print(e)
        print("EXCEPTION FOUND")
        for i in tempDeletingFilesName:
            if os.path.exists(i):
                os.remove(i)
        connection.rollback()
        connection.disconnect()

    print("END")

BANK_DATA = 'BANK_DATA'
BANK_DATA_URL = 'BANK_DATA_URL'
BANK_DATA_NAME = 'BANK_DATA_NAME'
BANK_DATA_SHORT_NAME = 'BAnK_DATA_SHORT_NAME'
BANK_DATA_PAGE_TYPE = 'BANK_DATA_PAGE_TYPE'
BANK_DATA_EXTRACT_TYPE = 'BANK_DATA_EXTRACT_TYPE'
BANK_DATA_DATE_SELECTOR = 'BANK_DATA_DATE_SELECTOR'
BANK_DATA_DATE_FORMAT = 'BANK_DATA_DATE_FORMAT'
BANK_DATA_PAIR_CURRENCY_TYPE = 'BANK_DATA_PAIR_CURRENCY_TYPE'
BANK_DATA_BANK_CURRENCY_ID = 'BANK_DATA_BANK_CURRENCY_ID'
BANK_DATA_BANK_BASE_VALUE = 'BANK_DATA_BANK_BASE_VALUE'
BANK_DATA_SET_HDR_ID = 'BANK_DATA_SET_HDR_ID'

SETTING_DATA = 'SETTING_DATA'
SETTING_DATA_CURRENCY_ID = 'SETTING_DATA_CURRENCY_ID'
SETTING_DATA_CURRENCY_NAME = 'SETTING_DATA_CURRENCY_NAME'
SETTING_DATA_CURRENCY_VALUE = 'SETTING_DATA_CURRENCY_VALUE'
SETTING_DATA_EXTRACT_CURRENCY = 'SETTING_DATA_EXTRACT_CURRENCY'
SETTING_DATA_EXTRACT_BUYING_RATE = 'SETTING_DATA_EXTRACT_BUYING_RATE'
SETTING_DATA_EXTRACT_SELLING_RATE = 'SETTING_DATA_EXTRACT_SELLING_RATE'

SCRAP_DATA_BANK = 'SCRAP_DATA_BANK'
SCRAP_DATA_BANK_NAME = 'SCRAP_DATA_BANK_NAME'
SCRAP_DATA_BANK_SHORT_NAME = 'SCRAP_DATA_BANK_SHORT_NAME'
SCRAP_DATA_BANK_IMG_PATH_FILE = 'SCRAP_DATA_PATH_FILE'
SCRAP_DATA_BANK_PAIR_CURRENCY_TYPE = 'SCRAP_DATA_BANK_PAIR_CURRENCY_TYPE'
SCRAP_DATA_BANK_CURRENCY_ID = 'SCRAP_DATA_BANK_CURRENCY_ID'
SCRAP_DATA_BANK_BASE_VALUE = 'SCRAP_DATA_BANK_BASE_VALUE'
SCRAP_DATA_BANK_SET_HDR_ID = 'SCRAP_DATA_BANK_SET_HDR_ID'
SCRAP_DATA_CURRENCY = 'SCRAP_DATA_BANK_CURRENCY'
SCRAP_DATA_CURRENCY_ID = 'SCRAP_DATA_CURRENCY_ID'
SCRAP_DATA_CURRENCY_NAME = 'SCRAP_DATA_CURRENCY_NAME'
SCRAP_DATA_CURRENCY_VALUE = 'SCRAP_DATA_CURRENCY_VALUE'
SCRAP_DATA_CURRENCY_BUYING_RATE = 'SCRAP_DATA_CURRENCY_BUYING_RATE'
SCRAP_DATA_CURRENCY_SELLING_RATE = 'SCRAP_DATA_CURRENCY_SELLING_RATE'
SCRAP_DATA_LOG = 'SCRAP_DATA_LOG'
SCRAP_DATA_LOG_STATUS = 'SCRAP_DATA_LOG_STATUS'
SCRAP_DATA_LOG_DESCRIPTION = 'SCRAP_DATA_LOG_DESCRIPTION'

STORING_DATA_HDR_RATE_DATE = 'STORING_DATA_HDR_RATE_DATE'
STORING_DATA_HDR_TYPE = 'STORING_DATA_HDR_TYPE'
STORING_DATA_HDR_PAIR_CURRENCY_TYPE = 'STORING_DATA_HDR_PAIR_CURRENCY_TYPE'
STORING_DATA_HDR_IMG_PATH_FILE = 'STORING_DATA_HDR_IMG_PATH_FILE'
STORING_DATA_HDR_TEXT_PATH_FILE = 'STORING_DATA_HDR_TEXT_PATH_FILE'
STORING_DATA_HDR_ADD_DATE = 'STORING_DATA_HDR_ADD_DATE'
STORING_DATA_DTL = 'STORING_DATA_DTL'
STORING_DATA_DTL_BASE_VALUE = 'STORING_DATA_DTL_BASE_VALUE'
STORING_DATA_DTL_VALUE = 'STORING_DATA_DTL_VALUE'
STORING_DATA_DTL_BUYING_RATE = 'STORING_DATA_DTL_BUYING_RATE'
STORING_DATA_DTL_SELLING_RATE = 'STORING_DATA_DTL_SELLING_RATE'
STORING_DATA_DTL_BASE_CURRENCY = 'STORING_DATA_DTL_BASE_CURRENCY'
STORING_DATA_DTL_PAIR_CURRENCY = 'STORING_DATA_DTL_PAIR_CURRENCY'
STORING_DATA_DTL_RECORD_STATUS = 'STORING_DATA_DTL_RECORD_STATUS'
STORING_DATA_DTL_ADD_DATE = 'STORING_DATA_DTL_ADD_DATE'
STORING_DATA_LOG = 'STORING_DATA_LOG'
STORING_DATA_LOG_STATUS = 'STORING_DATA_LOG_STATUS'
STORING_DATA_LOG_DESCRIPTION = 'STORING_DATA_LOG_DESCRIPTION'
STORING_DATA_LOG_ADD_DATE = 'STORING_DATA_LOG_ADD_DATE'
STORING_DATA_LOG_SET_HDR_ID = 'STORING_DATA_LOG_SETTING_HDR'

WRITING_DATA_BANK = 'WRITING_DATA_BANK'
WRITING_DATA_BANK_NAME = 'WRITING_DATA_BANK_NAME'
WRITING_DATA_BANK_SHORT_NAME = 'WRITING_DATA_BANK_SHORT_NAME'
WRITING_DATA_BANK_REF_DATE = 'WRITING_DATA_BANK_REF_DATE'
WRITING_DATA_CURRENCY = 'WRITING_DATA_CURRENCY'
WRITING_DATA_CURRENCY_VALUE = 'WRITING_DATA_CURRENCY_VALUE'
WRITING_DATA_CURRENCY_BUYING_RATE = 'WRITING_DATA_CURRENCY_BUYING_RATE'
WRITING_DATA_CURRENCY_SELLING_RATE = 'WRITING_DATA_CURRENCY_SELLING_RATE'

REF_EXCHANGE_RATE_BASE_CURRENCY = 'REF_EXCHANGE_RATE_BASE_CURRENCY'
REF_EXCHANGE_RATE_PAIR_CURRENCY = 'REF_EXCHANGE_RATE_PAIR_CURRENCY'
REF_EXCHANGE_RATE_BUYING_RATE = 'REF_EXCHANGE_RATE_BUYING_RATE'
REF_EXCHANGE_RATE_SELLING_RATE = 'REF_EXCHANGE_RATE_SELLING_RATE'

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

if refDate.today().weekday() < 5:
    isWeekday = True
else:
    isWeekday = False
workingDirectory = os.path.dirname(os.path.abspath(__file__))
tempDeletingFilesName = []
refExchangeRate = {}
delegateUser = 'system'

if __name__ == '__main__':
    orig_stdout = sys.stdout
    dirYearMonth = refDate.strftime('%Y%m%d')
    if not os.path.exists(workingDirectory + '/data_log'):
        os.mkdir(workingDirectory + '/data_log')
        os.chmod(workingDirectory + '/data_log', 0o777)
    if not os.path.exists(workingDirectory + '/data_log/' + dirYearMonth):
        os.mkdir(workingDirectory + '/data_log/' + dirYearMonth)
        os.chmod(workingDirectory + '/data_log/' + dirYearMonth, 0o777)
    logFileName = workingDirectory + '/data_log/' + dirYearMonth + '/' + refDate.strftime('%H%M%S') + '.log'
    f = open(logFileName, 'w')
    os.chmod(logFileName, 0o777)
    sys.stdout = f
    print(refDate)

    main()

    sys.stdout = orig_stdout
    f.close()