from wordConnector import WordConnector
import time, datetime
class TimeKeeper:
    bill_template_path = "/Users/magnussaurbier/Documents/Arbeit/Rechnungen/Vorlagen/Rechnungsvorlage.docx"
    def __init__(self, master):
        self.master = master
        self.wordConnector = WordConnector()
    def saveAbrechnung(self):
        x = "None"
        #c: configDict
        c = self.master.DBConnector.readConfigFile()
        c["bill_nr"] = str(int(c["bill_nr"]) + 1)
        valueDic = {
            "__date__":time.strftime("%d.%m.%y"),
            "__Client_Name__":c["client"],
            "__Client_Street_Nr__":c["client_street"],
            "__Client_Place__":c["client_place"],
            "__Bill_Nr__":self.master.DBConnector.countResets(),
            "__Job__":c["job"],
            "__Time_of_Job__":f"{datetime.datetime.strftime(datetime.datetime.fromtimestamp(self.master.DBConnector.readLastReset()),'%d.%m.%y')}-{time.strftime('%d.%m.%y')}",
            "__Sum_Price__":x,
        }
        positionDic = {

        }
        self.master.DBConnector.writeConfigFile(c)
        self.wordConnector.editBill(
            docPath=self.bill_template_path,
            wage = float(self.master.DBConnector.readConfigFile()["wage"]),
            valueDic = valueDic, positions = self.master.DBConnector.report())
