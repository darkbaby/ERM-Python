from ConnectionService import ConnectionService
from QueryProvider import QueryProvider

def connectionSetup():
    connection = ConnectionService('192.168.10.192', 'erm', 'Passw0rd', 'ERM')
    return connection

def dataForIntegratingSetup(connection):
    connection.connect()

    out_return_data = connection.getCursorVariable()
    parameter = {'OUT_ReturnData': out_return_data}
    connection.queryStoreProcedure(QueryProvider.PRC_SELECT_REQUIRED_EXCHANGE_RATE_AUTO, parameter)
    all_required_auto_integrate = []
    for row in out_return_data.getvalue():
        all_required_auto_integrate.append(row)

    out_return_data = connection.getCursorVariable()
    parameter = {'OUT_ReturnData': out_return_data}
    connection.queryStoreProcedure(QueryProvider.PRC_SELECT_REQUIRED_EXCHANGE_RATE_MANUAL, parameter)
    all_required_manual_integrate = []
    for row in out_return_data.getvalue():
        all_required_manual_integrate.append(row)
    # print(all_required_bank)

    parameter = None
    out_return_data = None
    connection.disconnect()

    result = []

    for i in all_required_auto_integrate:
        auto_dtl_id = i[0]
        currency_bank = i[1]
        currency_web = i[2]
        value = i[3]
        buying_rate = float("{0:.4f}".format(i[4]))
        selling_rate = float("{0:.4f}".format(i[5]))
        pair_type = i[6]
        ref_date = i[7]

        average_rate = float("{0:.4f}".format((buying_rate + selling_rate)/2))

        # print(buying_rate)
        # print(selling_rate)
        # print(average_rate)

        if pair_type == 2:
            base_currency = currency_web
            pair_currency = currency_bank
        elif pair_type == 1:
            base_currency = currency_bank
            pair_currency = currency_web

        resultRound = {
            INTEGRATING_DTL_DATA_OWNER_ID: auto_dtl_id,
            INTEGRATING_DTL_DATA_OWNER_TYPE: 'AUTO',
            INTEGRATING_DTL_DATA_VALUE: value,
            INTEGRATING_DTL_DATA_BUYING_RATE: buying_rate,
            INTEGRATING_DTL_DATA_SELLING_RATE: selling_rate,
            INTEGRATING_DTL_DATA_AVERAGE_RATE: average_rate,
        }

        isFound = False
        for item in result:
            itemBaseCurrency = item[INTEGRATING_HDR_DATA][INTEGRATING_HDR_DATA_BASE_CURRENCY]
            itemPairCurrency = item[INTEGRATING_HDR_DATA][INTEGRATING_HDR_DATA_PAIR_CURRENCY]
            if base_currency == itemBaseCurrency and pair_currency == itemPairCurrency:
                item[INTEGRATING_HDR_DATA][INTEGRATING_DTL_DATA].append(resultRound)
                isFound = True
                break;

        if not isFound:
            result.append({
                INTEGRATING_HDR_DATA: {
                    INTEGRATING_HDR_DATA_BASE_CURRENCY: base_currency,
                    INTEGRATING_HDR_DATA_PAIR_CURRENCY: pair_currency,
                    INTEGRATING_HDR_DATA_REF_DATE: ref_date,
                    INTEGRATING_DTL_DATA: [
                        resultRound
                    ]
                }
            })

    for i in all_required_manual_integrate:
        man_dtl_id = i[0]
        base_currency = i[1]
        pair_currency = i[2]
        value = i[3]
        buying_rate = float("{0:.4f}".format(i[4]))
        selling_rate = float("{0:.4f}".format(i[5]))
        ref_date = i[6]

        average_rate = float("{0:.4f}".format((buying_rate + selling_rate) / 2))

        resultRound = {
            INTEGRATING_DTL_DATA_OWNER_ID: man_dtl_id,
            INTEGRATING_DTL_DATA_OWNER_TYPE: 'MANUAL',
            INTEGRATING_DTL_DATA_VALUE: value,
            INTEGRATING_DTL_DATA_BUYING_RATE: buying_rate,
            INTEGRATING_DTL_DATA_SELLING_RATE: selling_rate,
            INTEGRATING_DTL_DATA_AVERAGE_RATE: average_rate,
        }

        isFound = False
        for item in result:
            itemBaseCurrency = item[INTEGRATING_HDR_DATA][INTEGRATING_HDR_DATA_BASE_CURRENCY]
            itemPairCurrency = item[INTEGRATING_HDR_DATA][INTEGRATING_HDR_DATA_PAIR_CURRENCY]
            if base_currency == itemBaseCurrency and pair_currency == itemPairCurrency:
                item[INTEGRATING_HDR_DATA][INTEGRATING_DTL_DATA].append(resultRound)
                isFound = True
                break;

        if not isFound:
            result.append({
                INTEGRATING_HDR_DATA: {
                    INTEGRATING_HDR_DATA_BASE_CURRENCY: base_currency,
                    INTEGRATING_HDR_DATA_PAIR_CURRENCY: pair_currency,
                    INTEGRATING_HDR_DATA_REF_DATE: ref_date,
                    INTEGRATING_DTL_DATA: [
                        resultRound
                    ]
                }
            })

    print(result)
    return result

def StoringToIntegratingResultToDatabase(connection, dataForIntegrating):
    connection.connect()

    for item in dataForIntegrating:

        hdr_id = StoringExchangeRateHDR(connection,
                               item[INTEGRATING_HDR_DATA][INTEGRATING_HDR_DATA_BASE_CURRENCY],
                               item[INTEGRATING_HDR_DATA][INTEGRATING_HDR_DATA_PAIR_CURRENCY],
                               item[INTEGRATING_HDR_DATA][INTEGRATING_HDR_DATA_REF_DATE])

        for item2 in item[INTEGRATING_HDR_DATA][INTEGRATING_DTL_DATA]:
            dtl_id = StoringExchangeRateDTL(connection,
                                   hdr_id,
                                   item2[INTEGRATING_DTL_DATA_OWNER_ID],
                                   item2[INTEGRATING_DTL_DATA_OWNER_TYPE],
                                   item2[INTEGRATING_DTL_DATA_VALUE],
                                   item2[INTEGRATING_DTL_DATA_BUYING_RATE],
                                   item2[INTEGRATING_DTL_DATA_SELLING_RATE],
                                   item2[INTEGRATING_DTL_DATA_AVERAGE_RATE])

            UpdateFKRateAutoDTL(connection,
                                item2[INTEGRATING_DTL_DATA_OWNER_ID],
                                dtl_id)

    connection.commit()

    connection.disconnect()

def StoringExchangeRateHDR(connection, base_currency, pair_currency, ref_date):
    out_return_data = connection.getNumberVariable()
    parameter = {'OUT_ReturnData': out_return_data, 'IN_BaseCurrency': base_currency,
                 'IN_PairCurrency': pair_currency, 'IN_RefDate': ref_date}
    connection.queryStoreProcedure(QueryProvider.PRC_INSERT_EXCHANGE_RATE_HDR, parameter)
    return out_return_data.getvalue()

def StoringExchangeRateDTL(connection, hdr_id, owner_id, owner_type, value,
                           buying_rate, selling_rate, average_rate):
    out_return_data = connection.getNumberVariable()
    parameter = {'OUT_ReturnData': out_return_data, 'IN_HDRID': hdr_id, 'IN_OwnerID': owner_id,
                 'IN_OwnerType': owner_type, 'IN_Value': value,
                 'IN_BuyingRate': buying_rate, 'IN_SellingRate': selling_rate,
                 'IN_AverageRate': average_rate}
    connection.queryStoreProcedure(QueryProvider.PRC_INSERT_EXCHANGE_RATE_DTL, parameter)
    return out_return_data

def UpdateFKRateAutoDTL(connection, owner_id, fk_rate_dtl):
    parameter = {'IN_OwnerID': owner_id, 'IN_FKRateDTL': fk_rate_dtl}
    connection.queryStoreProcedure(QueryProvider.PRC_UPDATE_FK_RATE_DTL_AUTO, parameter)

def main():
    connection = connectionSetup()
    dataForIntegrating = dataForIntegratingSetup(connection)
    StoringToIntegratingResultToDatabase(connection, dataForIntegrating)

INTEGRATING_DTL_DATA = 'INTEGRATING_DTL_DATA'
INTEGRATING_DTL_DATA_OWNER_ID = 'INTEGRATING_DTL_DATA_OWNER_ID'
INTEGRATING_DTL_DATA_OWNER_TYPE = 'INTEGRATING_DTL_DATA_OWNER_TYPE'
INTEGRATING_DTL_DATA_VALUE = 'INTEGRATING_DTL_DATA_VALUE'
INTEGRATING_DTL_DATA_BUYING_RATE = 'INTEGRATING_DTL_DATA_BUYING_RATE'
INTEGRATING_DTL_DATA_SELLING_RATE = 'INTEGRATING_DTL_DATA_SELLING_RATE'
INTEGRATING_DTL_DATA_AVERAGE_RATE = 'INTEGRATING_DTL_DATA_AVERAGE_RATE'

INTEGRATING_HDR_DATA = 'INTEGRATING_HDR_DATA'
INTEGRATING_HDR_DATA_BASE_CURRENCY = 'INTEGRATING_HDR_DATA_BASE_CURRENCY'
INTEGRATING_HDR_DATA_PAIR_CURRENCY = 'INTEGRATING_HDR_DATA_PAIR_CURRENCY'
INTEGRATING_HDR_DATA_REF_DATE = 'INTEGRATING_HDR_DATA_REF_DATE'

if __name__ == '__main__':
        main()