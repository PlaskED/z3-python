import logging

from z3 import *
from z3math import *
from classes import Variable, FuncCall, Assignment

"""
Takes a Variable or FuncCall and creates a z3 variable from it. 
Constants become TypeVals instead.
Assignments become varibales but have different logic later on than the normal variables.
"""
def createVar(var):
    if (isinstance(var, Variable)):
        if var.isConst():
            return createZ3Val(var.varType, var.constValue)
        elif var.isAssignment():
            return createZ3Var(var.varType, var.name)
        else:
            if len(var.varType) > 4 and var.varType[:5] == "Array":
                arrayType = t[5:]
                return Array(n, createZ3Sort(arrayType), createZ3Sort(arrayType))
            return createZ3Var(var.varType, var.name)
    elif (isinstance(var, FuncCall)):
        return createZ3Var(var.returnType, var.callName)
    else:
        raise TypeError(var)

"""Takes a FuncCall and creates a z3 expression from it"""
def createFunctionCall(v, funcCall):
    callName = funcCall.callName
    callExpressions = funcCall.expressions

    if len(callExpressions)==1:
        return v[callName]==createExpression(v, callExpressions[0])

    res = [v[callName]==createExpression(v, callExpressions[0])]
    for i in range(1,len(callExpressions)):
        res.append(And(Not(res[i-1]),v[callName]==createExpression(v, callExpressions[i])))
    return Or(res)

"""Takes a z3 ast variable and converts it's value to python type"""
def z3TypeToPython(var):
    if is_bool(var):
        return bool(var)
    elif is_int(var):
        return var.as_long()
    elif is_real(var):
        return var.as_decimal(10)
    elif is_string(var):
        return var.as_string()
    else:
        raise NotImplementedError(var)
"""
Takes a string expression in z3 format which may use 
any z3 variable defined in v. v should be a dictionary.
"""
def createExpression(v, expr):
    expr = eval(expr)
    return expr

"""
Takes a Assignment class and creates a z3 constraint
"""
def createAssignment(v, a):
    assert isinstance(a, Assignment)
    return v[a.name] == createExpression(v, a.assignment)

def createZ3Sort(sort):
    if sort == "int":
        return IntSort()
    if sort == "real":
        return RealSort()
    if sort == "bool":
        return BoolSort()
    if sort == "string":
        return StringSort()
    
    raise TypeError(sort)

def createZ3Val(sort, val):
    if sort == "int":
        return IntVal(val)
    if sort == "real":
        return RealVal(val)
    if sort == "bool":
        return BoolVal(val)
    if sort == "string":
        return StringVal(val)
    
    raise TypeError(sort)

def createZ3Var(t, n):
    if t == "int":
        return Int(n)
    if t == "real":
        return Real(n)
    if t == "bool":
        return Bool(n)
    if t == "string":
        return String(n)
    
    raise TypeError(t)
    
def pPrintDict(d):
  res = '{'
  for k, v in sorted(d.items()):
    res += "'{}' : {}, ".format(k, v)
  res = res[:-2]
  res += '}'
  return res

def showLog():
    levels = [logging.INFO, logging.DEBUG]
    return logging.getLogger().getEffectiveLevel() in levels

def printTruthTable(solutions, variables, spacing=10):
    if len(solutions) == 0:
        return
    N = len(variables) + 1
    infoRow = [x for x in sorted(variables.keys())]

    line = ' # '
    for entry in infoRow:
        indent = (spacing-len(entry))/2
        pre = (indent-1)*' '
        after = indent*' '
        line += '|{}{}{}'.format(pre, str(entry), after)
    line += '|'
    print line

    print len(line)*'-'
    nr = 0
    for assigns in solutions:
        nr += 1
        after = 3-len(str(nr))
        line = "{}{}".format(str(nr), after*' ')
        for k in sorted(variables.keys()):
          if k not in assigns.keys():
            indent = (spacing-2)/2
            pre = (indent-2)*' '
            after = indent*' '
            line += '|{}{}{}'.format(pre, '**', after)
          else:
            indent = (spacing-len(str(assigns[k])))/2
            rest = (spacing-len(str(assigns[k])))%2
            pre = (indent+rest-2)*' '
            after = indent*' '
            line += '|{}{}{}'.format(pre, str(assigns[k]), after)
        line += '|'
        print line
