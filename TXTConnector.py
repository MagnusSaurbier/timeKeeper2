from logging import lastResort
import time, os
class TXTConnector:
    path = "files/"
    startFile = path+"start.txt"
    endFile = path+"end.txt"
    taskGroupFile = path+"taskGroup.txt"
    resetFile = path+"reset.txt"
    timeFormat = "%Y-%m-%d %H:%M:%S"
    fileLineSeparator = ", "
    def __init__(self):
        #create folder at path if not exists
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        #create files if not exists
        if not os.path.exists(self.startFile):
            open(self.startFile, "w")
        if not os.path.exists(self.endFile):
            open(self.endFile, "w")
        if not os.path.exists(self.taskGroupFile):
            open(self.taskGroupFile, "w")
        if not os.path.exists(self.resetFile):
            open(self.resetFile, "w")

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
        lines = self.readFile(self.startFile)
        return [self.getTimestamp(line[0]) for line in lines]

    def readEndTimesAndTasks(self):
        """returns list of endTimes as timestamps and list of Tasks"""
        lines = self.readFile(self.endFile)
        return [self.getTimestamp(line[0]) for line in lines], [line[1] for line in lines]

    def readTasksAndGroups(self):
        """returns list of tasks and list of groups"""
        lines = self.readFile(self.taskGroupFile)
        return [line[0] for line in lines], [line[1] for line in lines]

    def readUniqueTasks(self):
        """return list of unique tasks"""
        tasks, groups = self.readTasksAndGroups()
        return list(set(tasks))

    def readLastReset(self):
        """returns last reset as timestamp"""
        lines = self.readFile(self.resetFile)
        return self.getTimestamp(lines[-1][0])

    def addStart(self):
        """writes start now as datetime string to start file"""
        with open(self.startFile, "a") as f:
            f.write(self.getNow()+"\n")
    
    def addEnd(self, Task):
        """writes now as datetime string and task to end file"""
        with open(self.endFile, "a") as f:
            f.write(self.getNow()+self.fileLineSeparator+Task+"\n")

    def clockIsRunning(self):
        """returns true if clock is running"""
        with open(self.startFile, "r") as f:
            startLines = len(f.readlines())
        with open(self.endFile, "r") as f:
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
        with open(self.taskGroupFile, "a") as f:
            f.write(task+self.fileLineSeparator+group+"\n")    #write task to taskgroup

    def reset(self, worksum):
        """writes nowTime as datetime string and worksum to reset file"""
        with open(self.resetFile, "a") as f:
            f.write(self.getNow()+self.fileLineSeparator+str(worksum)+"\n")


    

# t = TXTConnector("test.txt")
# t.addStart()
