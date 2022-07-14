import time, os
class TXTConnector:
    path = "files/"
    startFile = path+"start.txt"
    endFile = path+"end.txt"
    taskGroupFile = path+"taskGroup.txt"
    resetFile = path+"reset.txt"
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

    def addStart(self):
        with open(self.startFile, "a") as f:
            # note current time
            f.write(str(time.time())+"\n")
    def addEnd(self, Task):
        with open(self.endFile, "a") as f:
            # note current time
            f.write(str(time.time())+", "+Task+"\n")
    def clockIsRunning(self):
        #check whether number of lines in start is greater than number of lines in end
        with open(self.startFile, "r") as f:
            startLines = len(f.readlines())
        with open(self.endFile, "r") as f:
            endLines = len(f.readlines())
        return startLines > endLines
    def getWorkSum(self):
        #return sum of differences between start and end times
        with open(self.startFile, "r") as f:
            startLines = f.readlines()
        with open(self.endFile, "r") as f:
            endLines = f.readlines()
        startTimes = [float(line.split(",")[0]) for line in startLines]
        endTimes = [float(line.split(",")[0]) for line in endLines]
        return sum([endTimes[i]-startTimes[i] for i in range(len(startTimes))])
    def getCurrentWorkTime(self):
        #return difference between current time and last start time
        with open(self.startFile, "r") as f:
            startLines = f.readlines()
        startTimes = [float(line.split(",")[0]) for line in startLines]
        return time.time()-startTimes[-1]
    def getTasks(self):
        #return list of tasks
        with open(self.taskGroupFile, "r") as f:
            endLines = f.readlines()
        tasks = [line.split(",")[1].strip() for line in endLines]
        return list(set(tasks))
    def report(self):
        #return list of taskgroups and their worktimes
        with open(self.taskGroupFile, "r") as f:
            taskGroupLines = f.readlines()
        taskGroups = [line.split(",")[0].strip() for line in taskGroupLines]
        tasks = [line.split(",")[1].strip() for line in taskGroupLines]
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
        print(workTimes, taskGroups, tasks)
        return list(zip(taskGroups, workTimes))
    def getWorkTime(self, task):
        #return worktime of task
        with open(self.endFile, "r") as f:
            endLines = f.readlines()
        with open(self.startFile, "r") as f:
            startLines = f.readlines()
        tasks = [line.split(",")[1].strip() for line in endLines]
        startTimes = [float(line.split(",")[0]) for line in startLines]
        endTimes = [float(line.split(",")[0]) for line in endLines]
        startTimes = [startTimes[i] for i in range(len(tasks)) if tasks[i] == task]
        endTimes = [endTimes[i] for i in range(len(tasks)) if tasks[i] == task]
        return sum([endTimes[i]-startTimes[i] for i in range(len(startTimes))])
    def insertTask(self, task, group):
        #insert task into taskgroup
        with open(self.taskGroupFile, "a") as f:
            f.write(group+","+task+"\n")    #write task to taskgroup
    def reset(self, worksum):
        with open(self.resetFile, "a") as f:
            f.write(f"{time.time()},{worksum}\n")

# t = TXTConnector("test.txt")
# t.addStart()
