from wordConnector import WordConnector
import datetime
class TimeKeeper:
    bill_template_path = "/Users/magnussaurbier/Documents/Arbeit/Rechnungen/Vorlagen/Rechnungsvorlage.docx"
    def __init__(self, master):
        self.master = master
        self.wordConnector = WordConnector()
    def saveAbrechnung(self):
        x = "None"
        valueDic = {
            "__date__":self.master.txtConnector.getNow(),
            "__Client_Name__":x,
            "__Client_Street_Nr__":x,
            "__Client_Place__":x,
            "__Bill_Nr__":x,
            "__Job__":x,
            "__Time_of_Job__":f"{self.master.txtConnector.readLastReset()}-{self.master.txtConnector.getNow()}",
            "__Sum_Price__":x,
        }
        self.wordConnector.editBill(docPath=self.bill_template_path, valueDic = valueDic)