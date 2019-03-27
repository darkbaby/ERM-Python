from WritingService import WritingService
from ConnectionService import ConnectionService
from FirefoxService import FirefoxService
from PhantomjsService import PhantomjsService
from QueryProvider import QueryProvider
from UtilityProvider import UtilityProvider
from pyvirtualdisplay import Display
import datetime
import time
import os
import sys

def scrap(data):
    result = []
    errorResult = ""

    scrapingService = PhantomjsService(refDate, False)
    scrapingService.setURL(data["url"])
    scrapingService.setTimeout(35)
    isSuccessful = scrapingService.scrap()

    if isSuccessful:
        time.sleep(10)

        scrapingService.setExtractionType(int(data["extractionType"]), 'td')

        if scrapingService.getExtractionType() == 1:
            for i in range(0, len(data["cssSelector"])):
                result.append([])
                for j in range(0, len(data["cssSelector"][i])):
                    if data["cssSelector"][i][j] != "":
                        fieldValue = scrapingService.getField(data["cssSelector"][i][j])
                        if fieldValue == None or fieldValue.strip() == '':
                            result[i].append("No Data")
                        else:
                            fieldValue = fieldValue.strip().replace(',', '')
                            if fieldValue.replace(".", '', 1).isdigit():
                                if j == 0:
                                    result[i].append("Data Incorrect")
                                else:
                                    result[i].append(fieldValue)
                            else:
                                if j == 0:
                                    result[i].append(fieldValue)
                                else:
                                    result[i].append("Data Incorrect")
                    else:
                        result[i].append("")
        elif scrapingService.getExtractionType() == 2:
            for i in range(0, len(data["cssSelector"])):
                result.append([])
                for j in range(1, len(data["cssSelector"][i])):
                    if data["cssSelector"][i][j] != "":
                        currencyName = data["cssSelector"][i][0]
                        cssSelectorForSending = [currencyName, int(data["cssSelector"][i][j])]
                        fieldValue = scrapingService.getField(cssSelectorForSending)
                        if fieldValue == None or fieldValue.strip() == '':
                            result[i].append("No Data")
                        else:
                            fieldValue = fieldValue.strip().replace(',', '')
                            if fieldValue.replace(".", '', 1).isdigit():
                                result[i].append(fieldValue)
                            else:
                                result[i].append("Data Incorrect")
                    else:
                        result[i].append("")
        else:
            errorResult = "extraction type is wrong, cant do another process"
    else:
        errorResult = "cant open the webpage, please check the url and try again after few minutes"

    if scrapingService != None:
        scrapingService.quit()

    if errorResult != "" :
        return errorResult
    else:
        return result

def writeOutputFile(data, fileName):
    if type(data) is not str:
        with open(fileName, "w") as target:
            target.write("0" + '\n')
            for lineItem in data:
                valueToWrite = ""
                for item in lineItem:
                    valueToWrite += item + ","
                if valueToWrite != "":
                    valueToWrite = valueToWrite[:-1]
                    target.write(valueToWrite + '\n')
                else :
                    target.write('\n')
    else:
        with open(fileName, "w") as target:
            target.write("1" + '\n')
            target.write(data)

def readInputFile(fileName):
    with open(fileName) as f:
        content = f.read().splitlines()

    data = {}
    data["extractionType"] = ""
    data["url"] = ""
    data["cssSelector"] = []
    for i in range(0,len(content)):
        if i == 0:
            data["extractionType"] = content[i]
        elif i == 1:
            data["url"] = content[i]
        else:
            data["cssSelector"].append(content[i].split(','))

    return data

def main():
    try:
        if len(sys.argv) != 2:
        # if len(sys.argv) != 1:
            print("need file name to read")
        else:
            data = readInputFile(sys.argv[1])
            # data = readInputFile("D:\\workspace\\python-batch\\python-scraping\\test.txt")

            dataForWriting = scrap(data)
            writeOutputFile(dataForWriting, sys.argv[1])
            # writeOutputFile(dataForWriting, "D:\\workspace\\python-batch\\python-scraping\\test.txt")

    except Exception as e:
        with open(sys.argv[1], "w") as target:
            target.write("1" + '\n')
            target.write(str(e))

    print("end")
    sys.exit()

refDate = datetime.datetime.now(datetime.timezone.utc)
refDate = refDate + datetime.timedelta(hours=8)

if __name__ == '__main__':
    main()