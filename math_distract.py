from pyepl import display
from pyepl import sound
from pyepl.keyboard import Key, KeyTrack
from pyepl import joystick
from pyepl.mouse import MouseRoller, MouseButton
from pyepl import keyboard
from pyepl import mechinput
from pyepl import hardware
from pyepl.textlog import LogTrack
from pyepl import exputils
from pyepl import convenience

import random
import math, numpy, pygame
from pyepl import timing

def eval_problem(terms, ops):
    """
    Construct a problem string and evaluate the answer.

    Inputs
    ------
    terms : tuple
        tuple of numbers to include as terms in the left-hand side
        of the equation.
    ops : tuple
        tuple of strings to include as operations. ops[i] gives the
        operation between terms[i] and term[i+1]. Operations are
        specified as their corresponding string symbol, and may
        include '+', '-', '*', and '/'.
    Outputs
    -------
    answer : int/float
        The result of combining the terms using the specified
        operators.
    prob_str : str
        The left-hand side of the equation in string form.
    """

    # generate the problem text
    prob_str = ''
    for i,x in enumerate(terms):
        # operation text
        if i > 0:
            prob_str += ' ' + ops[i-1] + ' '
        
        # following number
        prob_str += str(x)

    # solve the problem
    answer = eval(prob_str)

    return answer, prob_str

def gen_problem(n_terms, possible_terms, possible_ops,
                unique_terms=False):
    """
    Generate a random math problem.

    Inputs
    ------
    n_terms : int
    possible_terms : list of numbers
    possible_ops : list of strs
    unique_terms : bool

    Outputs
    -------
    terms : list
    ops : list
    """
    
    # choose the terms
    if unique_terms:
        # sample without replacement
        terms = random.sample(possible_terms, n_terms)
    else:
        # sample with replacement
        terms = []
        for i in range(n_terms):
            terms.extend(random.sample(possible_terms, 1))

    # sample with replacement from possible operators
    ops = []
    for i in range(n_terms - 1):
        ops.extend(random.sample(possible_ops, 1))

    return terms, ops

def gen_problem_set(n_problems, n_terms, possible_terms, 
                    possible_ops, unique_terms=False,
                    exclude_repeats=True):
    """
    Generate a set of math problems.

    Inputs
    ------
    n_problems : int
    n_terms : int
    possible_terms : list of numbers
    possible_ops : list of strs
    unique_terms : bool
    exclude_repeats : bool

    Outputs
    -------
    set_terms : list of lists of numbers
    set_ops : list of lists of strs
    set_answers : list of numbers
    """
    
    set_terms = []
    set_ops = []
    set_answers = []
    prev_answer = None
    for i in range(n_problems):
        bad_problem = True
        while bad_problem:
            # generate a random problem
            terms, ops = gen_problem(n_terms, possible_terms,
                                     possible_ops, unique_terms)
        
            # get the answer for the problem
            (answer, prob_str) = eval_problem(terms, ops)
        
            if exclude_repeats and (answer is prev_answer):
                # we had the same answer last time; try again
                continue
            
            # the problem passed all checks
            bad_problem = False
        prev_answer = answer

        # add problem information to the set
        set_terms.append(terms)
        set_ops.append(ops)
        set_answers.append(answer)

    return set_terms, set_ops, set_answers

def gen_proposed(answer, dev_vals, dev_probs=None, pos_only=False):
    """
    Generate a random proposed answer to a problem.

    Inputs
    ------
    answer : number
    dev_vals : list of numbers
    dev_probs : list of numbers
    pos_only : bool

    Outputs
    -------
    proposed : number
    """
    if dev_probs is None:
        # default is using each deviation equally often
        dev_probs = numpy.ones(len(dev_vals)) / len(dev_vals)

    # transform probilities of the different deviations, for ease of
    # randomly choosing between them
    dev_ranges = numpy.cumsum(dev_probs)

    good_answer = False
    max_tries = 1000
    n_tries = 0
    while not good_answer:
        if n_tries > max_tries:
            break

        # choose a random deviation to add to the actual answer
        dev_ind = numpy.nonzero(dev_ranges >= numpy.random.uniform(0,1))
        if isinstance(dev_ind, tuple):
            dev_ind = dev_ind[0]
        dev_ind = min(dev_ind)
        dev = dev_vals[dev_ind]

        # create a proposed answer
        proposed = answer + dev
        
        n_tries += 1
        if pos_only and proposed <= 0:
            # require a positive number; try again
            continue
        else:
            good_answer = True
    
    if not good_answer:
        raise standardError("Failed to generate an acceptible "
                            "proposed answer to a math problem.")

    return proposed

def prep_math_set(numVars=2, minNum=1, maxNum=9, maxProbs=100,
                  plusAndMinus=False, ansMod=[0,1,-1,10,-10],
                  ansProb=[.5,.125,.125,.125,.125],
                  tfProblems=False, uniqueVars=False,
                  excludeRepeats=True):
    """
    Prepare math problems based on standard configuration variables.

    Designed to work with the the variables used by vcdMathMod.py;
    also sets the same defaults.
    """
    
    # set options for math problem generation
    if plusAndMinus:
        possible_ops = ('+','-')
    else:
        possible_ops = ('+')
    possible_terms = range(minNum, maxNum + 1)

    # generate a set of math problems
    terms, ops, answers = gen_problem_set(maxProbs, numVars,
        possible_terms, possible_ops, uniqueVars, excludeRepeats)

    if tfProblems:
        # if only addition, proposed answers must be greater than 0
        pos_only = not plusAndMinus
        
        # check answer generation options
        if len(ansMod) != len(ansProb):
            raise ValueError("ansMod and ansProb must have the "
                             "same length.")
        elif sum(ansProb) != 1.0:
            raise ValueError("ansProb must sum to one.")

        # create a proposed answer for each problem
        proposed = []
        for i in range(maxProbs):
            mod_answer = gen_proposed(answers[i], ansMod, 
                                      ansProb, pos_only)
            proposed.append(mod_answer)
    else:
        # we don't need a proposed answer
        proposed = None

    return terms, ops, answers, proposed

def run_problem(terms, ops, answer, v, clock, mathlog, textSize,
                endTime, ans_but, trialNum=None, numberDuration=None,
                numberISI=None, tfProblems=False, tfKeys=None, 
                proposed=None, scoreDisplay=None, presentSeq=False):
    """
    Present a  math problem and record a response.
    """

    if tfProblems:
        # set the correct button press
        if proposed == answer:
            corRsp = tfKeys[0]
        else:
            corRsp = tfKeys[1]
        rstr = str(proposed)
    else:
        rstr = ''

    # display the current score
    if scoreDisplay is not None:
        ct = v.showProportional(scoreDisplay, .8, .1)

    # get problem text for presentation/logging
    probanswer, probtxt = eval_problem(terms, ops)
    
    if presentSeq:
        # present each term, without the operator(s). Assuming that
        # the operators are always the same, so they do not need to
        # be shown on each trial
        text = []
        s = []
        for x in terms:
            s.append(str(x))
            text.append(display.Text(str(x), size=textSize))
        s.append('=')
        text.append(display.Text('=', size=textSize))

        tt = None
        prestime = []
        for x in text:
            # remove the previous term
            if tt is not None:
                v.unshow(tt)
            
                # if ISI, show blank screen
                if numberISI > 0:
                    v.updateScreen(clock)
                    clock.delay(numberISI)

            # show the next term
            tt = v.showCentered(x)
            ts = v.updateScreen(clock)
            prestime.append(ts)
            clock.delay(numberDuration)

        # ISI before the proposed answer
        v.unshow(tt)
        if numberISI > 0:
            v.updateScreen(clock)
            clock.delay(numberISI)

        # we've logged the parts of the problem preceding the proposed
        # answer; the last log line is the time that the proposed
        # answer was presented, and the RT to respond to that
        rt = v.showCentered(display.Text(rstr, size=textSize))
        probstart = v.updateScreen(clock)
    else:
        # show the left-hand side
        pt = v.showProportional(display.Text(probtxt, size=textSize),
                                .5 - textSize, .5)

        # show the right-hand side (if applicable)
        rt = v.showRelative(display.Text(rstr, size=textSize),
                            display.RIGHT,pt)
        probstart = v.updateScreen(clock)

    # wait for keypress
    maxTimeLeft = endTime - clock.get()
    kret, resptime = ans_but.waitWithTime(maxDuration=maxTimeLeft,
                                          clock=clock)

    for i in range(len(prestime)):
        # log each term presentation
        mathlog.logMessage('TERM\t%d\t%s\t\t\t\t' % (trialNum, s[i]), 
                           prestime[i])

    # NWM: keypad entry and audio code are more complex, so leaving
    # them out for now. Code above should support those response
    # types, but they are not supported in code below
    if kret is None:
        timeout = True
        isCorrect = None
    elif tfProblems:            
        # check the answer
        timeout = False
        if kret.name == corRsp:
            isCorrect = 1
        else:
            isCorrect = 0
    else:
        raise ValueError('Keyboard and vocal responses currently not supported.')

    if kret is not None:
        # calc the RT as (RT, maxlatency)
        prob_rt = (resptime[0] - probstart[0],
                   resptime[1] + probstart[1])

        # if no trialNum, log the trial as -1
        if trialNum is None:
            trialNum = -1

        # log the problem presentation, accuracy, and reaction time
        mathlog.logMessage('PROB\t%d\t%r\t%r\t%d\t%ld\t%d' %
                           (trialNum, probtxt, rstr, isCorrect,
                            prob_rt[0], prob_rt[1]), probstart)
    else:
        # no response; still log the problem presentation
        mathlog.logMessage('PROB\t%d\t%r\t%r\t\t\t' %
                           (trialNum, probtxt, rstr), probstart)

    # clear the problem
    if presentSeq:
        v.unshow(rt)
    else:
        v.unshow(pt, rt)
    v.updateScreen(clock)

    return isCorrect, timeout, probstart

def run_math_set(terms, ops, answers, proposed=None,
                 clock = None,
                 mathlog = None,
                 minProblemTime = 2000,
                 textSize = None,
                 correctBeepDur = 500,
                 correctBeepFreq = 400,
                 correctBeepRF = 50,
                 incorrectBeepDur = 500,
                 incorrectBeepFreq = 200,
                 incorrectBeepRF = 50,
                 tf_bc = None,
                 tfKeys = None,
                 maxDistracterLimit = 10000,
                 trialNum = None,
                 fixation = None,
                 presentSeq = False,
                 numberDuration = 800,
                 numberISI = 0,
                 probISI = 500,
                 probJitter = 0):
    """
    Run a math distraction period.

    Inputs
    ------
    terms
    ops
    answers
    proposed
    clock
    mathlog
    minProblemTime
        Minimum time (in ms) to allow the participant to respond
        once the entire problem has been displayed. If, after the
        last problem, there is less than this amount of time left
        in the period, a new problem will not be displayed
    textSize
    maxDistracterLimit
        Limit to the length of the distraction period (in ms)
    trialNum
        Number of the current trial (just used for logging)
    tf_bc
        Button choose for true/false responses
    tfKeys
        Tuple of Key objects, where tfKeys[0] gives the "true"
        key, and tfKeys[1] gives the "false" key
    fixation
        Showable to present if there isn't time for another problem,
        but there is still time left in the distraction period
    presentSeq
        If true, the terms in each problem will be presented on the
        screen sequentially; the operators will not be displayed,
        just the terms, followed by an equal sign
    numberDuration
        For sequential presentation, the time (in ms) to show each
        term on the screen
    numberISI
        For sequential presentation, the time (in ms) in between
        each term
    probISI
        Length (in ms) of the pause between problems
    probJitter
        Maximum jitter (in ms) to add to the problem ISI.
    """

    # set up tracks
    v = display.VideoTrack.lastInstance()  
    a = sound.AudioTrack.lastInstance()
    k = keyboard.KeyTrack.lastInstance()
    if mathlog is None:
        mathlog = LogTrack('math_distract')

    # beeps for feedback
    correctBeep = sound.Beep(correctBeepFreq, correctBeepDur,
                             correctBeepRF)
    incorrectBeep = sound.Beep(incorrectBeepFreq, incorrectBeepDur,
                               incorrectBeepRF)

    # start timing
    if clock is None:
        clock = exputils.PresentationClock()
    start_time = clock.get()
    
    if trialNum is None:
        trialNum = -1

    # log the time on the clock after fixation, etc.
    mathlog.logMessage('MATH START\t%d\t\t\t\t\t' % (trialNum), start_time)

    # set response type
    if not tf_bc is None:
        # must indicate whether the shown answer is correct
        tfProblems = True
    else:
        # must type the answer
        tfProblems = False

    # set response buttons
    if tfProblems:
        # some user-specified pair of buttons
        ans_but = tf_bc
    else:
        # type the number using the keyboard or keypad
        ans_but = k.keyChooser('0','1','2','3','4',
                               '5','6','7','8','9','-','RETURN',
                               '[0]','[1]','[2]','[3]','[4]',
                               '[5]','[6]','[7]','[8]','[9]',
                               '[-]','ENTER','[*]')

    maxDistracterLimit = int(maxDistracterLimit)
    if presentSeq:
        # adjust the minumum time required for a problem to be presented
        numVars = len(terms[0])
        minProblemTime += (numberDuration + numberISI) * (numVars + 1)

    endTime = start_time + maxDistracterLimit
    if (endTime - clock.get()) > (minProblemTime + probISI + probJitter):
        # we'll present at least one problem; so add the maximum ISI to
        # minProblemTime, since it will apply to all problems after
        # the first
        minProblemTime += probISI + probJitter
    
    # do problems until there isn't time left to present another one
    curProb = 0
    nCorrect = 0
    nProblems = 0
    probTimes = []
    while ((endTime - clock.get()) > minProblemTime):
        if curProb > (len(terms) - 1):
            # we have run out of problems!
            print 'Warning: insufficient problems for distraction period'
            break

        if curProb > 0:
            # pause briefly before displaying the next problem
            clock.delay(probISI, probJitter)
            
        if tfProblems:
            curProposed = proposed[curProb]
        else:
            curProposed = None
        
        # present the problem, record a response
        isCorrect, timeout, probstart = run_problem(terms[curProb], 
            ops[curProb], answers[curProb], v, clock, mathlog,
            textSize, endTime, ans_but, trialNum=trialNum,
            numberDuration=numberDuration,
            numberISI=numberISI,
            tfProblems=tfProblems, tfKeys=tfKeys,
            proposed=curProposed, presentSeq=presentSeq)
        probTimes.append(probstart)

        # the problem has to have been presented at least
        nProblems += 1

        # give feedback (only if we did not run out of time)
        if not timeout:
            if isCorrect:
                # correct beep
                #pTime = a.play(correctBeep, t=clock, doDelay=False)
                # need to add an option to specify whether they want
                # beeps or not
                pass
            else:
                # incorrect beep
                pTime = a.play(incorrectBeep, t=clock, doDelay=False)
        curProb += 1
        if not timeout and isCorrect:
            nCorrect += 1

    # we did not have enough time to present another problem, so we're
    # done with the math
    remaining = endTime - clock.get()
    if (fixation is not None) and (remaining > (probISI + probJitter)):
        # if there is time, show a blank screen just like we would if
        # there were still math problems; the participant will still
        # be bracing for a new problem, and won't relax until the
        # fixation appears
        clock.delay(probISI, probJitter)
        remaining = endTime - clock.get()
    
    if remaining > 0:
        if fixation is not None:
            # show fixation for the remaining time, log the start of a
            # period where the participant is just resting and not
            # doing problems
            fix = v.showCentered(fixation)
            ts = v.updateScreen(clock)
            clock.delay(remaining)

            mathlog.logMessage('REST\t%d\t\t\t\t\t' % (trialNum), ts)
        else:
            fix = None
            clock.delay(remaining)
    else:
        fix = None

    # log the time on the clock after fixation, etc.
    mathlog.logMessage('MATH END\t%d\t\t\t\t\t' % (trialNum), clock.get())

    return nCorrect, nProblems, start_time, probTimes, fix
 
