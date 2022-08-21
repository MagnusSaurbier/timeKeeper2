from logging import lastResort
import time, os
class TXTConnector:
    filesPath = "files/"
    workPath = ""
    startFile = "start.txt"
    endFile = "end.txt"
    taskGroupFile = "taskGroup.txt"
    resetFile = "reset.txt"
    timeFormat = "%Y-%m-%d %H:%M:%S"
    fileLineSeparator = ", "

    interruptedString = "__INTERRUPTED__"
    def __init__(self, master):
        self.master = master
        self.workPath = self.getLatestWork()
        print(self.workPath)
        #create folder at path if not exists
        if not os.path.exists(self.filesPath+self.workPath):
            os.makedirs(self.filesPath+self.workPath)
        #create files if not exists
        if not os.path.exists(self.getStartFile()):
            open(self.getStartFile(), "w")
        if not os.path.exists(self.getEndFile()):
            open(self.getEndFile(), "w")
        if not os.path.exists(self.getTaskGroupFile()):
            open(self.getTaskGroupFile(), "w")
        if not os.path.exists(self.getResetFile()):
            open(self.getResetFile(), "w")

    def getLatestWork(self):
        """returns work that has been worked on in last shift"""
        # scan get all folders in files path
        folders = self.getAllWork()
        # if no folders exist, return 0
        if len(folders) == 0:
            return 0
        # latest endTime
        latestEndTime = 0
        # latest endTime folder
        latestEndTimeFolder = ""
        # iterate through all directories
        for folder in folders:
            self.workPath = f"{folder}/"
            # get last entry in endFile
            endTimes, tasks = self.readEndTimesAndTasks()
            # if endFile is empty, continue
            if len(endTimes) == 0:
                continue
            # if endTime is after latestEndTime, set latestEndTime to endTime and latestEndTimeFolder to workPath
            
            if endTimes[-1] > latestEndTime:
                latestEndTime = endTimes[-1]
                latestEndTimeFolder = self.workPath
        print(latestEndTimeFolder)
        # if latestEndTime is 0, return None
        if latestEndTime == 0:
            return None
        # else return latestEndTimeFolder
        return latestEndTimeFolder

    def getAllWork(self):
        """returns all folders in files path"""
        return [f for f in os.listdir(self.filesPath) if os.path.isdir(self.filesPath+f)]

    def createWork(self, workName):
        """creates new work folder with name workName"""
        self.workPath = workName+"/"
        os.makedirs(self.filesPath+self.workPath)
        open(self.getStartFile(), "w")
        open(self.getEndFile(), "w")
        open(self.getTaskGroupFile(), "w")
        open(self.getResetFile(), "w")
    
    def getStartFile(self):
        """returns path to start file"""
        return self.filesPath+self.workPath+self.startFile
    def getEndFile(self):
        """returns path to end file"""
        return self.filesPath+self.workPath+self.endFile
    def getTaskGroupFile(self):
        """returns path to task group file"""
        return self.filesPath+self.workPath+self.taskGroupFile
    def getResetFile(self):
        """returns path to reset file"""
        return self.filesPath+self.workPath+self.resetFile

    def getNow(self):
        """returns current datetime as string"""
        return str(time.strftime(self.timeFormat))

    def getTimestamp(self, datetime_string):
        """returns timestamp of datetime string"""
        return time.mktime(time.strptime(datetime_string, self.timeFormat))

    def readFile(self, file):
        """returns list of lines as tuples"""
        with open(file, "r") as f:
            lines = f.readlines()
        return [line.replace("\n", "").split(self.fileLineSeparator) for line in lines]

    def readStartTimes(self):
        """returns list of start times as timestamps"""
        lines = self.readFile(self.getStartFile())
        return [self.getTimestamp(line[0]) for line in lines]

    def readEndTimesAndTasks(self):
        """returns list of endTimes as timestamps and list of Tasks"""
        lines = self.readFile(self.getEndFile())
        return [self.getTimestamp(line[0]) for line in lines], [line[1] for line in lines]

    def readTasksAndGroups(self):
        """returns list of tasks and list of groups"""
        lines = self.readFile(self.getTaskGroupFile())
        return [line[0] for line in lines], [line[1] for line in lines]

    def readUniqueTasks(self):
        """return list of unique tasks"""
        tasks, groups = self.readTasksAndGroups()
        return list(set(tasks))

    def readLastReset(self):
        """returns last reset as timestamp"""
        lines = self.readFile(self.getResetFile())
        if len(lines) == 0:
            return 0
        return self.getTimestamp(lines[-1][0])

    def addStart(self):
        """writes start now as datetime string to start file"""
        with open(self.getStartFile(), "a") as f:
            f.write(self.getNow()+"\n")
    
    def addEnd(self, Task):
        """writes now as datetime string and task to end file"""
        with open(self.getEndFile(), "a") as f:
            f.write(self.getNow()+self.fileLineSeparator+Task+"\n")

    def clockIsRunning(self):
        """returns true if clock is running"""
        with open(self.getStartFile(), "r") as f:
            startLines = len(f.readlines())
        with open(self.getEndFile(), "r") as f:
            endLines = len(f.readlines())
        return startLines > endLines

    def getWorkSum(self):
        """returns sum of all worktimes after last reset"""
        startTimes = self.readStartTimes()
        endTimes, tasks = self.readEndTimesAndTasks()
        lastReset = self.readLastReset()
        return sum([(endTimes[i]-startTimes[i] if endTimes[i] > lastReset else 0)  for i in range(len(endTimes))])

    def getCurrentWorkTime(self):
        """return difference between current time and last start time"""
        startTimes = self.readStartTimes()
        return time.time()-startTimes[-1]

    def report(self):
        """return list of taskgroups and their worktimes"""
        tasks, taskGroups = self.readTasksAndGroups()
        workTimes = [self.getWorkTime(task) for task in tasks]
        i = 0
        while i < len(workTimes):
            if workTimes[i] == 0:
                workTimes.pop(i)
                taskGroups.pop(i)
                tasks.pop(i)
            else:
                j = i + 1
                while j < len(taskGroups):
                    if taskGroups[j] == taskGroups[i]:
                        workTimes[i] += workTimes[j]
                        workTimes.pop(j)
                        taskGroups.pop(j)
                        tasks.pop(j)
                    else:
                        j += 1
                i += 1
        return list(zip(taskGroups, workTimes))

    def getWorkTime(self, task):
        """return worktime of task"""
        startTimes = self.readStartTimes()
        endTimes, tasks = self.readEndTimesAndTasks()
        lastReset = self.readLastReset()
        return sum([(endTimes[i]-startTimes[i] if tasks[i] == task and endTimes[i] > lastReset else 0)  for i in range(len(endTimes))])

    def insertTask(self, task, group):
        """insert task and group into taskgroup"""
        with open(self.getTaskGroupFile(), "a") as f:
            f.write(task+self.fileLineSeparator+group+"\n")    #write task to taskgroup

    def reset(self, worksum):
        """writes nowTime as datetime string and worksum to reset file"""
        with open(self.getResetFile(), "a") as f:
            f.write(self.getNow()+self.fileLineSeparator+str(worksum)+"\n")

    def deleteLastEndTime(self):
        """deletes last end time"""
        with open(self.getEndFile, "r") as f:
            lines = f.readlines()
        with open(self.getEndFile, "w") as f:
            for line in lines[:-1]:
                f.write(line)
    

# t = TXTConnector("test.txt")
# t.addStart()
