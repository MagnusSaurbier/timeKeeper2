from telnetlib import WONT
from docx import Document
class WordConnector:
    def __init__(self):
        x = "blub"
        self.valueDic = {
            "__date__":x,
            "__Client_Name__":x,
            "__Client_Street_Nr__":x,
            "__Client_Place__":x,
            "__Bill_Nr__":x,
            "__Job__":x,
            "__Time_of_Job__":x,
            "__Sum_Price__":x,
        }
    def editBill(self, docPath, valueDic):
        document = Document(docPath)
        
        for p in document.paragraphs:
            if p.text != "": print(p.text)

        for p in document.paragraphs:
            for key in self.valueDic:
                print(key, ",", p.text)
                
                p.text = p.text.replace(key, valueDic[key])

        document.save(docPath[:-5]+"_copy.docx")