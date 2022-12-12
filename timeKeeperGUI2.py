import fcntl
import os
from re import M
import sys
from threading import currentThread
from timeKeeper import TimeKeeper

fh=0
def run_once():
    global fh
    fh=open(os.path.realpath(__file__),'r')
    try:
        fcntl.flock(fh,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except:
        os._exit(0)

run_once()

import time
try:
    import tkinter
    import tkinter.messagebox
    import customtkinter
except ImportError:
    print("please install tkinter and customtkinter using\npip install tkinter\npip install customtkinter\nin the command prompt")
from TXTConnector import TXTConnector


customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    task = None
    defaultWage = 15

    def __init__(self, passwdFile, dBase, host):
        super().__init__()
        self.title("TimeKeeper v5.0")
        self.timeKeeper = TimeKeeper(self)
        self.DBConnector:TXTConnector = TXTConnector(self)
        self.resizable(False, False)
        #self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ create two frames ============

        # configure grid layout (1x2)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # create button to select work 
        self.work_frame = customtkinter.CTkFrame(master=self, corner_radius=10)
        self.work_frame.grid(row = 0, column = 0, sticky="nsew", pady = 10, padx = 10)
        self.work_button = customtkinter.CTkButton(master=self.work_frame, text=self.DBConnector.workPath.replace("/", ""), command=self.select_work)
        self.work_button.grid(row=0, column=0, sticky="nsew", pady = 10, padx = 10)
        self.wage_label = customtkinter.CTkLabel(master=self.work_frame, text = "wage:")
        self.wage_label.grid(row=0, column=1, sticky="nsew", pady = 10, padx = 10)
        self.wage_entry = customtkinter.CTkEntry(master=self.work_frame, text=self.readWage())
        self.wage_entry.grid(row=0, column=2, sticky="nsew", pady = 10, padx = 10)
        self.bind("<Return>", lambda event: self.writeWage(self.wage_entry.get()))

        # create customtkinterframe for the worktime menu with corner_radius 10
        self.worktime_menu = customtkinter.CTkFrame(master=self, corner_radius=10)
        self.worktime_menu.grid(row=1, column=0, sticky="nsew", padx = 10, pady = 10)
        # create the buttons "start worktime" and "select task" inside of the workitme frame separated by 10 px in every direction
        
        self.worktime_menu.start_worktime_button = customtkinter.CTkButton(master=self.worktime_menu)
        self.worktime_menu.worktime_label = customtkinter.CTkLabel(master=self.worktime_menu, text="Worktime: 0:00:00")
        self.worktime_menu.start_worktime_button.grid(row=0, column=0, sticky="nsew", pady = 10, padx = 10)
        self.makeWorktimeButton()

        self.worktime_menu.select_task_button = customtkinter.CTkButton(master=self.worktime_menu, text="Select Task", command=self.select_task)
        self.worktime_menu.select_task_button.grid(row=0, column=1, sticky="nsew", pady = 10, padx = 10)
        # create worktime label in worktime menu

        # create customtkinterframe for Buttons "Abrechnung" and "Zurücksetzen"
        self.button_frame = customtkinter.CTkFrame(master=self, corner_radius=10)
        self.button_frame.grid(row=2, column=0, sticky="nsew", pady = 10, padx = 10)
        self.button_frame.abbrechen_button = customtkinter.CTkButton(master=self.button_frame, text="Abrechnung", command=self.report)
        self.button_frame.abbrechen_button.grid(row=0, column=0, sticky="nsew", pady = 10, padx = 10)
        self.button_frame.reset_button = customtkinter.CTkButton(master=self.button_frame, text="Zurücksetzen", command=self.reset)
        self.button_frame.reset_button.grid(row=0, column=1, sticky="nsew", pady = 10, padx = 10)

        self.load_work(self.DBConnector.workPath.replace("/", ""))

    # make function to start the worktime and change the "start worktime" button to "stop worktime"
    def makeWorktimeButton(self):
        if self.DBConnector.clockIsRunning():
            self.worktime_menu.start_worktime_button.configure(text="Stop Worktime")
            self.worktime_menu.start_worktime_button.configure(command=self.stop_worktime)
            #place worktime label in worktime menu and update worktime
            self.worktime_menu.worktime_label.grid(row=1, column=0, sticky="nsew", pady = 10, padx = 10)
            # disable select work button
            self.work_button.configure(state="disabled")
            self.update_worktime()
        else:
            self.worktime_menu.start_worktime_button.configure(text="Start Worktime")
            self.worktime_menu.start_worktime_button.configure(command=self.start_worktime)
            # enable select work button
            self.work_button.configure(state="normal")

    def start_worktime(self):
        if not self.DBConnector.clockIsRunning():
            self.DBConnector.addStart()
            #self.DBConnector.mydb.commit()
            self.makeWorktimeButton()
        else:
            self.makeWorktimeButton()
    # make function to end the worktime and change the "end worktime" button to "start worktime"
    def stop_worktime(self):
        #return error if no task selected
        if self.task == None:
            #create messagebox
            tkinter.messagebox.showerror("Error", "Please select a task first!")
            return
        if not self.DBConnector.clockIsRunning():
            # error: clock is not running
            tkinter.messagebox.showerror("Error", "Clock is not running!")
            return
        # add end time to database
        self.worktime_menu.worktime_label.grid_forget()
        self.DBConnector.addEnd(self.task)
        #self.DBConnector.mydb.commit()
        self.makeWorktimeButton()

    def select_work(self):
        # create popup window to select work
        self.work_menu = customtkinter.CTkToplevel(master=self)
        self.work_menu.resizable(False, False)
        self.work_menu.title("Select Work")

        # new work button
        self.work_menu.new_work_button = customtkinter.CTkButton(master=self.work_menu, text="New Work", command=self.new_work)
        self.work_menu.new_work_button.grid(row=0, column=0, sticky="nsew", pady = 10, padx = 10)

        self.work_menu.work_var = tkinter.StringVar(value = self.DBConnector.workPath)
        # radiobuttons to select work from database (getAllWork())
        self.work_menu.work_radiobuttons = []
        for work in self.DBConnector.getAllWork():
            self.work_menu.work_radiobuttons.append(customtkinter.CTkRadioButton(master=self.work_menu, text=work, variable=self.work_menu.work_var, value=work))
            self.work_menu.work_radiobuttons[-1].grid(row=len(self.work_menu.work_radiobuttons), column=0, sticky="nsew", pady = 10, padx = 10)
        
        # create button to select work
        self.work_menu.select_button = customtkinter.CTkButton(master=self.work_menu, text="Select", command=self.select_work_button)
        self.work_menu.select_button.grid(row=len(self.work_menu.work_radiobuttons)+1, column=0, sticky="nsew", pady = 10, padx = 10)

        # select work on RETURN
        self.work_menu.bind("<Return>", lambda event: self.select_work_button())

    def new_work(self):
        # create popup window to create new work
        self.new_work_menu = customtkinter.CTkToplevel(master=self)
        self.new_work_menu.resizable(False, False)
        self.new_work_menu.title("New Work")

        # create entry to create new work
        self.new_work_menu.entries = {
            "title":None,
            "job":None,
            "worker":None,
            "wage":None,
            "client":None,
            "client_address":None,
            "client_street":None,
            "client_place":None,
        }

        for i,key in enumerate(self.new_work_menu.entries):
            customtkinter.CTkLabel(master = self.new_work_menu, text = key+":").grid(row=i, column=0, pady = 10, padx = 10)
            self.new_work_menu.entries[key] = self.new_work_menu.work_entry = customtkinter.CTkEntry(master=self.new_work_menu)
            self.new_work_menu.entries[key].grid(row=i, column=1, sticky="nsew", pady = 10, padx = 10)

        # create button to create new work
        self.new_work_menu.create_button = customtkinter.CTkButton(master=self.new_work_menu, text="Create", command=self.create_work)
        self.new_work_menu.create_button.grid(row=i+1, column=0, sticky="nsew", pady = 10, padx = 10)
    
    def create_work(self):
        # create new work in database
        work = self.new_work_menu.work_entry.get()
        configDict = {}
        for key in self.new_work_menu.entries:
            configDict[key] = self.new_work_menu.entries[key].get()
        self.DBConnector.createWork(configDict)
        self.load_work(work)

        # close popup window
        self.new_work_menu.destroy()
        self.work_menu.destroy()

    def load_work(self, work):
        self.DBConnector.workPath = f"{work}/"
        self.wage_entry.delete(0, tkinter.END)
        self.wage_entry.insert(0, str(self.DBConnector.readConfigFile()["wage"]))
        self.DBConnector.cleanWork()
        # set select work button to selected work
        self.work_button.configure(text=f"{self.DBConnector.workPath[:-1]}")
        # set task to task that has been last worked on
        a = self.DBConnector.readEndTimesAndTasks()[1]
        self.task = a[-1] if a else None
        self.worktime_menu.select_task_button.configure(text = self.task)
        # update worktime button
        self.makeWorktimeButton()

    def select_work_button(self):
        print("Select work")
        # get selected work
        self.load_work(self.work_menu.work_var.get())
        # close popup window
        self.work_menu.destroy()

    # function to select the task, that creates a customtkinter toplevel window, in which a task from self.tasks can be selected via radionbuttons or a new task can be created
    def select_task(self):
        self.task_window = customtkinter.CTkToplevel(master=self)
        self.task_window.title("Select Task")
        # place task_window right next to self with a gap of 50 px
        #self.task_window.geometry(f"+{self.winfo_x() + self.winfo_width() + 50}+{self.winfo_y()}")
        self.task_window.resizable(False, False)
        # place a radiobutton for each task in tasks
        self.task_window.task_radiobuttons = []
        # task_variable
        options = self.DBConnector.readGroups()
        # if self.task in options: v = options.index(self.task)
        # else: v = 0
        v = self.task
        self.task_window.task_variable = tkinter.StringVar(value = v)
        for task in options:
            self.task_window.task_radiobuttons.append(customtkinter.CTkRadioButton(master=self.task_window, text=task, variable=self.task_window.task_variable, value=task))
            self.task_window.task_radiobuttons[-1].grid(row=len(self.task_window.task_radiobuttons), column=0, sticky="nsew", padx = 10, pady = 10)
        # create a button to create a new task
        self.task_window.new_task_button = customtkinter.CTkButton(master=self.task_window, text="New Task", command=self.new_task)
        self.task_window.new_task_button.grid(row=0, column=0, sticky="nsew", pady = 10, padx = 10)
        # create a button to close the window
        self.task_window.close_button = customtkinter.CTkButton(master=self.task_window, text="Select", command=self.select_task_close)
        self.task_window.close_button.grid(row=len(self.task_window.task_radiobuttons)+1, column=0, sticky="nsew", pady = 10, padx = 10)
        self.task_window.bind("<Return>", lambda event: self.select_task_close())
    # select the chosen task and colse window will

    def select_task_close(self):
        self.task = self.task_window.task_variable.get()
        # set select task button's text to the selected task
        self.worktime_menu.select_task_button.configure(text=self.task)
        self.task_window.destroy()
    # to create a new task, create a toplevel, in which the "Name" and "Group" of the task can be entered
    def new_task(self):
        self.new_task_window = customtkinter.CTkToplevel(master=self)
        self.new_task_window.title("New Task")
        # place new_task_window right next to self.task_window with a gap of 50 px
        #self.new_task_window.geometry(f"+{self.task_window.winfo_x() + self.task_window.winfo_width() + 50}+{self.task_window.winfo_y()}")
        self.new_task_window.resizable(False, False)
        # create a label and a entry for the name of the task
        self.new_task_window.name_label = customtkinter.CTkLabel(master=self.new_task_window, text="Name:")
        self.new_task_window.name_label.grid(row=0, column=0, sticky="nsew", padx = 10, pady = 10)
        self.new_task_window.name_entry = customtkinter.CTkEntry(master=self.new_task_window)
        self.new_task_window.name_entry.grid(row=0, column=1, sticky="nsew", padx = 10, pady = 10)
        # create a label and a entry for the group of the task
        self.new_task_window.group_label = customtkinter.CTkLabel(master=self.new_task_window, text="Group:")
        self.new_task_window.group_label.grid(row=1, column=0, sticky="nsew", padx = 10, pady = 10)
        self.new_task_window.group_entry = customtkinter.CTkEntry(master=self.new_task_window)
        self.new_task_window.group_entry.grid(row=1, column=1, sticky="nsew", padx = 10, pady = 10)
        # create a button to create the task
        self.new_task_window.create_button = customtkinter.CTkButton(master=self.new_task_window, text="Create", command=self.create_task)
        self.new_task_window.create_button.grid(row=2, column=0, sticky="nsew", padx = 10, pady = 10)
        self.new_task_window.bind("<Return>", lambda event: self.create_task())
        # create a button to close the window
        self.new_task_window.close_button = customtkinter.CTkButton(master=self.new_task_window, text="Close", command=self.new_task_window.destroy)
        self.new_task_window.close_button.grid(row=2, column=1, sticky="nsew", padx = 10, pady = 10)
    
    # create a new task
    def create_task(self):
        #insert the Task into the DBConnector with Taskname and Group from the entrys
        self.DBConnector.insertTask(self.new_task_window.name_entry.get(), self.new_task_window.group_entry.get())
        self.task_window.task_variable.set(self.new_task_window.name_entry.get())
        self.new_task_window.destroy()
        self.select_task_close()
        #commit
        #self.DBConnector.mydb.commit()
    #reset worktime
    def reset(self):
        # make toplevel with yes/no buttons in it
        self.reset_window = customtkinter.CTkToplevel(master=self)
        self.reset_window.title("Reset Worktime")
        # place reset_window right next to self with a gap of 50 px
        #self.reset_window.geometry(f"+{self.winfo_x() + self.winfo_width() + 50}+{self.winfo_y()}")
        self.reset_window.resizable(False, False)
        # create a label
        self.reset_window.label = customtkinter.CTkLabel(master=self.reset_window, text="Are you sure you want to reset the worktime?")
        self.reset_window.label.grid(row=0, column=0, sticky="nsew", padx = 10, pady = 10)
        #create frame with yes/no buttons
        self.reset_window.yes_no_frame = customtkinter.CTkFrame(master=self.reset_window)
        self.reset_window.yes_no_frame.grid(row=1, column=0, sticky="nsew", padx = 10, pady = 10)
        # create yes/no buttons
        self.reset_window.yes_button = customtkinter.CTkButton(master=self.reset_window.yes_no_frame, text="Yes", command=self.reset_worktime)
        self.reset_window.yes_button.grid(row=0, column=0, sticky="nsew", padx = 10, pady = 10)
        self.reset_window.no_button = customtkinter.CTkButton(master=self.reset_window.yes_no_frame, text="No", command=self.reset_window.destroy)
        self.reset_window.no_button.grid(row=0, column=1, sticky="nsew", padx = 10, pady = 10)

    # insert a report to reset the worktime
    def reset_worktime(self):
        self.DBConnector.reset(round(self.DBConnector.getWorkSum()/3600, 2))
        #self.DBConnector.mydb.commit()
        self.reset_window.destroy()
    # show the settings window
    def settings(self):
        pass
    # show the about window
    def about(self):
        pass
    # show the help window
    def help(self):
        pass
    # show the about window
    def quit(self):
        self.master.destroy()

    #function to update worktime label
    def update_worktime(self):
        self.worktime_menu.worktime_label.configure(text=f"aktuelle Schicht: {self.getCurrentWorkTime()}h")
        self.after(10000, self.update_worktime)
    def getCurrentWorkTime(self):
        workSeconds = self.DBConnector.getCurrentWorkTime()
        return round(workSeconds/3600, 2)
    
    def getWage(self):
        if self.wage_entry.get() != None:
            return float(self.wage_entry.get())
        else:
            tkinter.messagebox.showerror("Insert Wage!")
            return False
    def readWage(self):
        config = self.DBConnector.readConfigFile()
        if "wage" in config:
            return config["wage"]
        else:
            return self.defaultWage
    def writeWage(self, wage):
        print("write")
        config = self.DBConnector.readConfigFile()
        config["wage"] = wage
        self.DBConnector.writeConfigFile(config)

    #create toplevel for report
    def report(self):
        self.report_window = customtkinter.CTkToplevel(master=self)
        self.report_window.title("Report")
        # place report_window right next to self with a gap of 50 px
        #self.report_window.geometry(f"+{self.winfo_x() + self.winfo_width() + 50}+{self.winfo_y()}")
        self.report_window.resizable(False, False)
        self.report_window.report_frame = customtkinter.CTkFrame(master=self.report_window)
        self.report_window.report_frame.grid(row=0, column=0, sticky="nsew", padx = 10, pady = 10)
        report = self.DBConnector.report()
        wage = self.getWage()
        if not wage: return False
        moneysum = 0
        timesum = 0
        # create list of report labels
        self.report_window.report_labels = []
        # for each cluster append a Label to a list of labels that presents name, time and money
        for i in range(len(report)):
            name = report[i][0]
            time = report[i][1]/3600
            money1 = time*wage
            money2 = round(time)*wage
            # create label to present name
            self.report_window.report_labels.append(customtkinter.CTkLabel(master=self.report_window.report_frame, text=f"{name}"))
            self.report_window.report_labels[3*i].grid(row=i, column=0, sticky="nsew", padx = 10, pady = 10)
            # create label to present time
            self.report_window.report_labels.append(customtkinter.CTkLabel(master=self.report_window.report_frame, text=f"{round(time)}h"))
            self.report_window.report_labels[3*i+1].grid(row=i, column=1, sticky="nsew", padx = 10, pady = 10)
            # create label to present money
            self.report_window.report_labels.append(customtkinter.CTkLabel(master=self.report_window.report_frame, text=f"{money2}€"))
            self.report_window.report_labels[3*i+2].grid(row=i, column=2, sticky="nsew", padx = 10, pady = 10)
            moneysum += money1
            timesum += time

        # create new frame to present total time and money
        self.report_window.report_frame2 = customtkinter.CTkFrame(master=self.report_window)
        self.report_window.report_frame2.grid(row=1, column=0, sticky="nsew", padx = 10, pady = 10)
        # create label to present total time as total_time_label
        self.report_window.total_time_label = customtkinter.CTkLabel(master=self.report_window.report_frame2, text=f"Gesamtzeit: {round(timesum)}h")
        self.report_window.total_time_label.grid(row=0, column=1, sticky="nsew", padx = 10, pady = 10)
        # create label to present total money as total_money_label
        self.report_window.total_money_label = customtkinter.CTkLabel(master=self.report_window.report_frame2, text=f"Gesamtgehalt: {round(moneysum)}€")
        self.report_window.total_money_label.grid(row=0, column=2, sticky="nsew", padx = 10, pady = 10)
        
        #Buttons
        self.report_window.report_frame3 = customtkinter.CTkFrame(master=self.report_window)
        self.report_window.report_frame3.grid(row=2, column=0, sticky="nsew", padx = 10, pady = 10)

        self.report_window.close_button = customtkinter.CTkButton(master=self.report_window.report_frame3, text="Close", command=self.report_window.destroy)
        self.report_window.close_button.grid(row=0, column=0, sticky="nsew", padx = 10, pady = 10)

        self.report_window.save_button = customtkinter.CTkButton(master=self.report_window.report_frame3, text="Save", command=self.saveAbrechnung)
        self.report_window.save_button.grid(row=0, column=1, sticky="nsew", padx = 10, pady = 10)
    
    def saveAbrechnung(self):
        self.report_window.destroy()
        self.timeKeeper.saveAbrechnung()
    
    def change_mode(self):
        if self.switch_2.get() == 1:
            customtkinter.set_appearance_mode("dark")
        else:
            customtkinter.set_appearance_mode("light")

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

if __name__ == "__main__":
    app = App("passwd.txt", "timekeeper", "localhost")
    app.start()