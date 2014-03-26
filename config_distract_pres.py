
# math problem options
numSets = 10
numVars = 3
minNum = 1
maxNum = 9
maxProbs = 10
plusAndMinus = False
ansMod = [0,1,-1,2,-1]
ansProb = [.5,.125,.125,.125,.125]
tfProblems = True
uniqueVars = True
excludeRepeats = True

# text
defaultFont = '../fonts/Verdana.ttf'
fixHeight = .08
textSize = .1

# presentation options
# maximum rest time with no problems (number ISI is 0):
# (allocated ISI - actual ISI) + term 1 + term 2 + '=' + [min resp time]
# (500 - [300-500]) + 400 + 400 + 400 + 400 =
# [0-200] + 400 + 400 + 400 + 400 = [1600-1800]

# note: the actual ISI doesn't contribute to the rest, since it isn't
# clear to the participant at that point that they have reached a rest
# point

# so, for example, participants are distracted for at least 6.6
# seconds out of the 8.5 second distraction period. The actual
# distribution of times will depend on the specific timing parameters
displayCorrect = False
presentSeq = True
showEquals = False
maxDistractorLimit = 7500
minProblemTime = 400
numberDuration = 500
numberISI = 0
probISI = 200
probJitter = 200
setISI = 2000
setJitter = 0

# responses
tfKeys = ['N','M']
