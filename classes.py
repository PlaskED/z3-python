class FuncCall:
    def __init__(self, returnType, callName, expressions):
        assert len(expressions) > 0
        self.returnType = returnType
        self.callName = callName
        self.expressions = expressions
        
    def __str__(self):
        return "FuncCall {},{},{}".format(self.returnType, self.callName, self.expressions)

class Variable:
    def __init__(self, varType, name, constValue = None, assignment = None):
        self.varType = varType
        self.name = name
        self.constValue = constValue
        self.assignment = assignment

    def isConst(self):
        return self.constValue is not None

    def isAssignment(self):
        return self.assignment is not None
        
    def __str__(self):
        return "Variable {},{},{},{}".format(self.varType, self.name, self.constValue, self.assignment)

class Constant(Variable):
    def __init__(self, varType, name, constValue):
        Variable.__init__(self, varType, name, constValue)
        
    def __str__(self):
        return "Constant {},{},{}".format(self.varType, self.name, self.constValue)

class Assignment(Variable):
    def __init__(self, varType, name, assignment):
        Variable.__init__(self, varType, name, None, assignment)

    def __str__(self):
        return "Assignment {},{},{}".format(self.varType, self.name, self.assignment)

class DataMember:
    def __init__(self, name, typeName):
        self.name = name
        self.typeName = typeName
        
    def __str__(self):
        return "DataMember {},{}".format(self.typeName, self.name)
        
class DataType:
    def __init__(self, typeName, members):
        self.typeName = typeName
        self.members = members
        
    def __str__(self):
        return "DataType {},{}".format(self.typeName, [str(x) for x in self.members])
