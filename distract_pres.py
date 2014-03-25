#!/usr/bin/python

from pyepl.locals import *

# other modules
import os
import sys
import shutil
import math_distract as math
import prep_math as prep

def prepare(exp, config):
    """
    Prepare a number of problem sets.
    """
    
    # get the state
    state = exp.restoreState()
    
    # create a number of problem sets
    terms = []
    ops = []
    answers = []
    proposed = []
    for i in range(config.numSets):
        set_config = prep.prep_math_set(config.numVars,
            config.minNum, config.maxNum, config.maxProbs, 
            config.plusAndMinus, config.ansMod, config.ansProb,
            config.tfProblems, config.uniqueVars, 
            config.excludeRepeats)
        terms.append(set_config[0])
        ops.append(set_config[1])
        answers.append(set_config[2])
        proposed.append(set_config[3])

    # save the prepared data
    exp.saveState(state, terms=terms, ops=ops, answers=answers,
                  proposed=proposed, setNum=0, tcorrect=0)

def run(exp, config):    
    """
    Run some math distraction periods.
    """
    
    # get the state
    state = exp.restoreState()

    # create tracks
    video = VideoTrack("video")
    audio = AudioTrack("audio")
    keyboard = KeyTrack("keyboard")
    log = LogTrack("session")
    mathlog = LogTrack("math")
    clock = PresentationClock()

    # prep buttons
    tfkeys = config.tfKeys
    tf_bc = ButtonChooser(Key(tfkeys[0]), Key(tfkeys[1]))
    
    # prep displays
    fix = Text('+', size=config.fixHeight)

    # set the font
    setDefaultFont(Font(config.defaultFont))

    # prepare the screen
    video.clear("black")
    video.updateScreen(clock)

    while state.setNum < config.numSets:
        # run set
        i = state.setNum
        if not state.proposed is None:
            set_proposed = state.proposed[i]
        else:
            set_proposed = None
        out = math.run_math_set(state.terms[i], state.ops[i], 
                                state.answers[i],
                                set_proposed, clock = clock, 
                                mathlog = mathlog,
                                minProblemTime = config.minProblemTime,
                                textSize = config.textSize,
                                maxDistracterLimit = config.maxDistractorLimit,
                                trialNum = state.setNum,
                                tf_bc = tf_bc,
                                tfKeys = tfkeys,
                                fixation = fix,
                                presentSeq = config.presentSeq,
                                numberDuration = config.numberDuration,
                                showEquals = config.showEquals,
                                numberISI = config.numberISI,
                                probISI = config.probISI,
                                probJitter = config.probJitter)
        (nCorrect, nProblems, startTime, probTimes, fixDisp) = out

        # log the problem set
        log.logMessage('%s\t%d\t%d\t%d' % 
                       ('DISTRACTOR', state.setNum, nProblems, nCorrect),
                        startTime)

        # ISI between sets
        if fixDisp is not None:
            stim = video.replace(fixDisp, Text('*', size=config.textSize))
        else:
            stim = video.showCentered(Text('*', size=config.textSize))
        ts = video.updateScreen(clock)
        clock.delay(config.setISI, config.setJitter)
        video.unshow(stim)
        log.logMessage('%s\t%d\t\t' % ('FIX', state.setNum), ts)

        # move to the next set
        state.setNum += 1
        exp.saveState(state)

    # update the screen
    video.updateScreen(clock)
    
    # done
    timestamp = waitForAnyKey(clock,Text(
        "Thank you!\nYou have completed the session."))
    log.logMessage('SESS_END', timestamp)
    
    # catch up
    clock.wait() 

# only do this if the experiment is run as a stand-alone program (not
# imported as a library)
if __name__ == "__main__":
    
    # start PyEPL
    exp = Experiment()
    exp.parseArgs()
    exp.setup()
    
    # allows users to break out of experiment with escape-F1 (default
    # keys)
    exp.setBreak()
    
    # get subject configuration
    config = exp.getConfig()
	
    # if there was no saved state, run the prepare function
    if not exp.restoreState():
	prepare(exp, config)
	    
    # run the experiment
    run(exp, config)
