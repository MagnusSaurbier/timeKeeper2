import tkinter
import tkinter.messagebox
import customtkinter
from TXTConnector import TXTConnector


customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    WIDTH = 800
    HEIGHT = 400
    surveyName = None
    questionFile = None
    answerFile = None
    dataFile = None
    task = None

    def __init__(self, passwdFile, dBase, host):
        super().__init__()
        self.title("TimeKeeper v4.0")
        #self.DBConnector = DBConnector(open(passwdFile, 'r').readlines()[0], dBase, host)
        self.DBConnector = TXTConnector()
        #self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.resizable(False, False)
        #self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ create two frames ============

        # configure grid layout (1x2)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # create customtkinterframe for the worktime menu with corner_radius 10
        self.worktime_menu = customtkinter.CTkFrame(master = self, corner_radius=10)
        self.worktime_menu.grid(row=0, column=0, sticky="nsew", padx = 10, pady = 10)
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
        self.button_frame.grid(row=1, column=0, sticky="nsew", pady = 10, padx = 10)
        self.button_frame.abbrechen_button = customtkinter.CTkButton(master=self.button_frame, text="Abrechnung", command=self.report)
        self.button_frame.abbrechen_button.grid(row=0, column=0, sticky="nsew", pady = 10, padx = 10)
        self.button_frame.reset_button = customtkinter.CTkButton(master=self.button_frame, text="Zurücksetzen", command=self.reset)
        self.button_frame.reset_button.grid(row=0, column=1, sticky="nsew", pady = 10, padx = 10)

    # make function to start the worktime and change the "start worktime" button to "stop worktime"
    def makeWorktimeButton(self):
        if self.DBConnector.clockIsRunning():
            self.worktime_menu.start_worktime_button.config(text="Stop Worktime")
            self.worktime_menu.start_worktime_button.config(command=self.stop_worktime)
            #place worktime label in worktime menu and update worktime
            self.worktime_menu.worktime_label.grid(row=1, column=0, sticky="nsew", pady = 10, padx = 10)
            self.update_worktime()
        else:
            self.worktime_menu.start_worktime_button.config(text="Start Worktime")
            self.worktime_menu.start_worktime_button.config(command=self.start_worktime)

    def start_worktime(self):
        self.DBConnector.addStart()
        #self.DBConnector.mydb.commit()
        self.makeWorktimeButton()
    # make function to end the worktime and change the "end worktime" button to "start worktime"
    def stop_worktime(self):
        self.worktime_menu.worktime_label.grid_forget()
        self.DBConnector.addEnd(self.task)
        #self.DBConnector.mydb.commit()
        self.makeWorktimeButton()

    # function to select the task, that creates a customtkinter toplevel window, in which a task from self.tasks can be selected via radionbuttons or a new task can be created
    def select_task(self):
        self.task_window = customtkinter.CTkToplevel(master=self)
        self.task_window.title("Select Task")
        # place task_window right next to self with a gap of 50 px
        self.task_window.geometry(f"+{self.winfo_x() + self.winfo_width() + 50}+{self.winfo_y()}")
        self.task_window.resizable(False, False)
        # place a radiobutton for each task in tasks
        self.task_window.task_radiobuttons = []
        # task_variable
        options = self.DBConnector.getTasks()
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
    # select the chosen task and colse window will
    def select_task_close(self):
        self.task = self.task_window.task_variable.get()
        # set select task button's text to the selected task
        self.worktime_menu.select_task_button.config(text=self.task)
        self.task_window.destroy()
    # to create a new task, create a toplevel, in which the "Name" and "Group" of the task can be entered
    def new_task(self):
        self.new_task_window = customtkinter.CTkToplevel(master=self)
        self.new_task_window.title("New Task")
        # place new_task_window right next to self.task_window with a gap of 50 px
        self.new_task_window.geometry(f"+{self.task_window.winfo_x() + self.task_window.winfo_width() + 50}+{self.task_window.winfo_y()}")
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
        self.reset_window.geometry(f"+{self.winfo_x() + self.winfo_width() + 50}+{self.winfo_y()}")
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
        self.DBConnector.insertReport(round(self.DBConnector.getWorkSum()/3600, 2))
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
        self.worktime_menu.worktime_label.config(text=f"aktuelle Schicht: {self.getCurrentWorkTime()}")
        self.after(10000, self.update_worktime)
    def getCurrentWorkTime(self):
        workSeconds = self.DBConnector.getCurrentWorkTime()
        return round(workSeconds/3600, 2)

    #create toplevel for report
    def report(self):
        self.report_window = customtkinter.CTkToplevel(master=self)
        self.report_window.title("Report")
        # place report_window right next to self with a gap of 50 px
        self.report_window.geometry(f"+{self.winfo_x() + self.winfo_width() + 50}+{self.winfo_y()}")
        self.report_window.resizable(False, False)
        self.report_window.report_frame = customtkinter.CTkFrame(master=self.report_window)
        self.report_window.report_frame.grid(row=0, column=0, sticky="nsew", padx = 10, pady = 10)
        report = self.DBConnector.report()
        wage = 15
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
        # create button to close the report window
        self.report_window.close_button = customtkinter.CTkButton(master=self.report_window.report_frame2, text="Close", command=self.report_window.destroy)
        self.report_window.close_button.grid(row=0, column=0, sticky="nsew", padx = 10, pady = 10)
        
        

 
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






