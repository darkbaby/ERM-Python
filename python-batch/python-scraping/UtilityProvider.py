from datetime import datetime
import re
import platform
import socket

class UtilityProvider:

    @staticmethod
    def convertDateToString(targetDateTime, format):

        dCapture = re.match(r"^[a-zA-Z0-9]+([^a-zA-Z0-9]+)[a-zA-Z0-9]+([^a-zA-Z0-9]+)", format)
        sCapture = re.match(r"^([a-zA-Z0-9]+)[^a-zA-Z0-9]+([a-zA-Z0-9]+)[^a-zA-Z0-9]+([a-zA-Z0-9]+)", format)

        if dCapture == None or sCapture == None:
            return datetime.now().strftime("%d-%m-%Y")
        else:
            delimeter_spliting = dCapture.groups()
            format_spliting = sCapture.groups()
            if None in delimeter_spliting or None in format_spliting:
                return datetime.now().strftime("%d-%m-%Y")

        # format_spliting = []
        # delimeterPool = [' ','/','-','.']
        # delimeter = ''
        # for i in delimeterPool:
        #     format_spliting = format.split(i)
        #     if len(format_spliting) == 3:
        #         delimeter = i
        #         break

        # if delimeter == '':
        if False:
            return datetime.now().strftime("%d-%m-%Y")
        else:
            if platform.system() == 'Linux':
                day_choices = {'dd' : '%d', 'd' : '%-d'}

                month_choices = {'m' : '%-m', 'mm' : '%m', 'mmm' : '%b', 'mmmm' : '%B'}

                year_choices = {'yy' : '%y', 'yyyy' : '%Y'}
            else:
                day_choices = {'dd': '%d', 'd': '%#d'}

                month_choices = {'m': '%#m', 'mm': '%m', 'mmm': '%b', 'mmmm': '%B'}

                year_choices = {'yy': '%y', 'yyyy': '%Y'}

            newFormat = ''

            for i in range(0,len(format_spliting)):
                concatString = ''
                if format_spliting[i][0] == 'd':
                    concatString = day_choices.get(format_spliting[i], '%d')
                elif format_spliting[i][0] == 'm':
                    concatString = month_choices.get(format_spliting[i], '%m')
                elif format_spliting[i][0] == 'y':
                    concatString = year_choices.get(format_spliting[i], '%Y')

                if i < 2:
                    # newFormat = newFormat + concatString + delimeter
                    newFormat = newFormat + concatString + delimeter_spliting[i]
                else:
                    newFormat = newFormat + concatString

            # newFormat = newFormat[:-1]

            # stringDateTime = targetDateTime.strftime(newFormat)

            return targetDateTime.strftime(newFormat)

    @staticmethod
    def convertStringToTime(targetString):
        return datetime.strptime(targetString,'%H%M')

    @staticmethod
    def convertDateTimeToNumberERMFormat(targetDateTime):
        hour = targetDateTime.hour
        minute = targetDateTime.minute

        sHour = str(hour)
        if minute < 10:
            sMinute = str(minute).rjust(2,'0')
        else:
            sMinute = str(minute)

        return int(sHour + sMinute)

    @staticmethod
    def isNumeric(targetString):

        return targetString.replace('.','',1).isdigit()

    @staticmethod
    def checkPortAvailable(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = False
        try:
            sock.bind(("0.0.0.0", port))
            result = True
        except:
            print('Port is in use')
        sock.close()
        return result
