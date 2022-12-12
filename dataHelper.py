from TXTConnector import TXTConnector
def replaceTasksWithGroup():
    t = TXTConnector(None)
    # read tasks and groups from file
    tasks, groups = t.readTasksAndGroups()
    # replace tasks with groups
    # endTimes, endTasks = t.readEndTimesAndTasks()
    with open(t.getEndFile(), "r") as f:
        lines = f.readlines()
        endTimes = [line.split(t.fileLineSeparator)[0] for line in lines]
        endTasks = [line.split(t.fileLineSeparator)[1].replace("\n", "") for line in lines]
    endGroups = [groups[tasks.index(task)] for task in endTasks]
    # write new tasks to file
    with open("endTest.txt", "w") as f:
        for i in range(len(endTasks)):
            f.write(endTimes[i]+t.fileLineSeparator+endGroups[i]+t.fileLineSeparator+endTasks[i]+"\n")
    print("done")
replaceTasksWithGroup()