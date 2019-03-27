from ConnectionService import ConnectionService

def main():
    with open('../python-config.txt') as f:
        content = f.read().splitlines()
    connection = ConnectionService(content[0],content[1],content[2],content[3])
    # connection = ConnectionService('192.168.10.192', 'erm', 'Passw0rd', 'ERM')
    try:
        connection.connect()
        connection.queryStatement("DELETE FROM ERM_EXTRACT_REP WHERE 1=1")
        connection.commit()
        connection.disconnect()
    except:
        connection.rollback()
        connection.disconnect()

if __name__ == '__main__':
    main()