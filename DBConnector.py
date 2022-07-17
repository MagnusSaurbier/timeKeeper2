import mysql.connector
class DBConnector:
    def __init__(self, passwd, database, host = "localhost", user = "root"): #bei Datenbank unter Host mit Nutzername und Password anmelden
        try: 
            self.mydb = mysql.connector.connect(buffered = True, host = host, user = user, passwd=passwd, database = database)
            self.cursor = self.mydb.cursor() #Cursor zum auführen von SQL-Befehlen erschaffen
        except Exception: raise ConnectionError
    
    def makeInsertSQL(self, table, cols, values):
        i = 0
        while i < len(values):
            values[i] = str(values[i])
            if values[i] == "" or values[i] == "nan":
                values.pop(i)
                cols.pop(i)
            else:
                i += 1
        colstring = ', '.join(cols)
        valuestring = "', '".join(values)
        return f"INSERT INTO {table} ({colstring}) VALUES ('{valuestring}');"

    def addStart(self):
        sql = "INSERT INTO beginn () VALUES ();"
        self.cursor.execute(sql)

    def addEnd(self, Task):
        sql = f"INSERT INTO ende (Task) VALUES ('{Task}');"
        self.cursor.execute(sql)

    def clockIsRunning(self):
        sql = "SELECT Max(id) FROM beginn;"
        self.cursor.execute(sql)
        maxStartId = self.cursor.fetchone()[0]
        if maxStartId == None: maxStartId = 0

        sql = "SELECT Max(id) FROM ende;"
        self.cursor.execute(sql)
        maxEndId = self.cursor.fetchone()[0]
        if maxEndId == None: maxEndId = 0
        
        return maxStartId > maxEndId

    def getWorkSum(self):
        sql = "SELECT SUM(TimestampDiff(SECOND, Startzeit, Endzeit)) As Worktime FROM beginn, ende WHERE beginn.id = ende.id and beginn.startzeit > (select max(Datum) FROM abrechnung);"
        self.cursor.execute(sql)
        worksum = self.cursor.fetchone()[0]
        return worksum if worksum else 0

    def getCurrentWorkTime(self):
        sql = "SELECT TimestampDiff(SECOND, Startzeit, current_timestamp()) as diff From beginn Order By beginn.id DESC LIMIT 1;"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]

    def getTasks(self):
        sql = "SELECT Task From task_group Group by Task;"
        self.cursor.execute(sql)
        tasks = self.cursor.fetchall()
        return [task[0] for task in tasks]
    def getTaskTimes(self):
        sql = "SELECT Task, SUM(TimestampDiff(SECOND, Startzeit, Endzeit)) As Worktime FROM beginn, ende WHERE beginn.id = ende.id group by ende.Task;"
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    def insertReport(self, hours):
        sql = f"INSERT INTO abrechnung (Stunden) VALUES ({hours});"
        self.cursor.execute(sql)
    def report(self):
        sql = f"SELECT cluster, SUM(TimestampDiff(SECOND, Startzeit, Endzeit)) As Worktime FROM beginn, ende, task_group AS tg WHERE beginn.id = ende.id AND ende.task = tg.task AND Endzeit > (select max(Datum) FROM abrechnung) group by tg.cluster;"
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    def insertTask(self, task, group):
        sql = f"INSERT INTO task_group (task, cluster) VALUES ('{task}', '{group}');"
        self.cursor.execute(sql)

