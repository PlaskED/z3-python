from z3 import *
import sys, logging
from copy import deepcopy
from utils import createVar, createExpression, createFunctionCall, \
    createAssignment, pPrintDict, showLog, z3TypeToPython

class MCDCgenerator:
    def __init__(self, _variables, _expressions, _funcCalls, _dataTypes, _parallel=False):
        self.solver = Solver()
        _constants = [var for var in _variables if var.isConst()]
        _assignments = [var for var in _variables if var.isAssignment()]
        self.variables = self.convertVariables(_variables, _constants, _assignments, _funcCalls)
        self.funcCalls = self.convertFunctionCalls(_funcCalls)
        self.assignments = self.convertAssignments(_assignments)
        self.expressions = self.convertExpressions(_expressions)
        self.skipVar = self.createSkipFilter(_constants + _assignments, _funcCalls)
        logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
        self.logger = logging.getLogger()
        set_param('parallel.enable', _parallel)
        self.N = len(_variables)-len(_constants)-len(_assignments)+1
        self.maxSolutions = 2*self.N

    def __str__(self):
        res = "variables: {}\nexpressions: {}\nassignments: {}\nfuncCalls {}\nskipVar: {}\nN: {}".format(
            {k:v for k,v in self.variables.items()},self.expressions, \
            self.assignments, [x for x in self.funcCalls], \
            self.skipVar.keys(), self.N)
        res.replace(r'\n', '\n')
        return res
        
    def setLogLevel(self, level):
        self.logger.setLevel(level)

    def createSkipFilter(self, _constants, _funcCalls):
        res = {var.name:var.name for var in _constants}
        res.update({f.callName:f.callName for f in _funcCalls})
        return res
    
    def convertVariables(self, _variables, _constants, _assignments, _funcCalls):
        res = {var.name:createVar(var) for var in _constants}
        res.update({var.name:createVar(var) for var in _assignments})
        res.update({var.name:createVar(var) for var in _variables})
        res.update({f.callName:createVar(f) for f in _funcCalls})
        return res

    def convertExpressions(self, _expr):
        return [createExpression(self.variables, e) for e in _expr]

    def convertAssignments(self, _assignments):
        return [createAssignment(self.variables, a) for a in _assignments]
    
    def convertFunctionCalls(self, _functionCalls):
        return [createFunctionCall(self.variables, fc) for fc in _functionCalls]

    def convertDataTypes(self, _dataTypes):
        dts = {x:Datatype(x) for x in _dataTypes.keys()}
        res = {x:createDataType(x, dts, _dataTypes) for x in dts.keys()}
        return res
                
    def modelToDict(self, solver):
        model = solver.model()
        return {x.name():model[x] for x in model if x.name() not in self.skipVar}
        
    # returns a constraint pair for finding independence pairs
    def createPairConstraint(self, key, assigns, expr):
        constraint = ([],[])
        for k, v in assigns.iteritems():
            if k==key:
                x = self.variables[k]
                constraint[0].append(x == assigns[k])
                constraint[1].append(Not(x == assigns[k]))
            else:
                x = self.variables[k]
                constraint[0].append(x == assigns[k])
                constraint[1].append(x == assigns[k])
        constraint[0].append(expr)
        constraint[1].append(Not(expr))
        return constraint

    def blockAssigns(self, assigns):
        constraint = []
        for k, v in assigns.iteritems():
            constraint.append(self.variables[k]==assigns[k])
        self.solver.add(Not(And(constraint)))

    def findSolutions(self):
        s = self.solver
        # When a variable has been proven to independently
        # affect the decision outcome we set values to false:
        # if decision true: key[0]=False else: key[1]=False
        solutions = []

        s.add(self.funcCalls)
        s.add(self.assignments)

        for expr in self.expressions:
            foundSolutions = 0
            unproven = {key:[True, True] for key in deepcopy(self.variables.keys()) if key not in self.skipVar}
            first = True
            s.push()
            s.add(expr)
            self.logger.info(s)

            while s.check()==sat:
                try_solution = self.modelToDict(s)
                # Pop first context so we have no constraints
                if first:
                  s.pop()
                  first = False

                solution1 = None
                solution2 = None
                
                for i in unproven.keys():
                    s.push()
                    pairConstraint = self.createPairConstraint(i, try_solution, expr)
                    s.add(pairConstraint[0])
                    if s.check()==sat:
                        new_sol = self.modelToDict(s)
                        if new_sol != solution1 and unproven[i][0]:
                            self.logger.debug("Found solution proving {}=>True: {}".format(i, new_sol))
                            unproven[i][0] = False
                            solution1 = deepcopy(new_sol)
                    s.pop()
                    s.push()
                    s.add(pairConstraint[1])
                    if s.check()==sat:
                        new_sol = self.modelToDict(s)
                        if new_sol != solution2 and unproven[i][1]:
                            self.logger.debug("Found solution proving {}=>False: {}".format(i, new_sol))
                            unproven[i][1] = False
                            solution2 = deepcopy(new_sol)
                    s.pop()

                    if solution1 != None and solution1 not in solutions:
                        foundSolutions += 1
                        solutions.append(solution1)
                        s.push()
                        self.blockAssigns(solution1)
                        self.logger.debug("Added solution1: {}".format(pPrintDict(solution1)))

                    if solution2 != None and solution2 not in solutions:
                        foundSolutions += 1
                        solutions.append(solution2)
                        s.push()
                        self.blockAssigns(solution2)
                        self.logger.debug("Added solution2: {}".format(pPrintDict(solution2)))

                if len(solutions) >= self.N:
                    if solution1 is None and solution2 is None:
                        break
            self.logger.debug("Current solutions: {}".format([pPrintDict(x) for x in solutions]))

            if (s.num_scopes() >= foundSolutions):
                self.logger.info("will pop %s times", foundSolutions)
                for i in range(foundSolutions):
                    s.pop()
                s.add(Not(expr))
        return solutions
    
    
