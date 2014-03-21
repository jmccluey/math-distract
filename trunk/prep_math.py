
import random, math, numpy

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
