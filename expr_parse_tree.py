from z3 import *

CONNECTIVE_OPS = [Z3_OP_NOT,Z3_OP_AND,Z3_OP_OR,Z3_OP_IMPLIES,Z3_OP_IFF,Z3_OP_ITE]
REL_OPS = [Z3_OP_EQ,Z3_OP_LE,Z3_OP_LT,Z3_OP_GE,Z3_OP_GT]
OPERATORS = CONNECTIVE_OPS + REL_OPS

# var is tuple (type, name)
def createVar(var):
  t = var[0]
  n = var[1]
  if t=="int":
    return Int('%s' % n)
  elif t=="bool":
    return Bool('%s' % n)
  elif t=="real":
    return Real('%s' % n)
  raise NotImplementedError(varType)

def createExpression(v, expr):
  return eval(expr)

# creates a constraint which allow only key variable to change
def createCounterConstraint(key, variables, model):
  constraints = []
  for k, v in variables.iteritems():
    if k==key:
      x = v
      constraints.append(Not(x == model[x]))
    else:
      x = v
      constraints.append(x == model[x])
  return constraints

def modelToDict(model):
  return {x.name():model[x] for x in model}

def pPrintDict(d):
  res = ""
  for k, v in sorted(d.items()):
    res += "{} : {}, ".format(k, v)

  return res[:-1]

def block_model(s):
  m = s.model()
  s.add(Or([ f() != m[f] for f in m.decls() if f.arity() == 0]))  

def isOperand(self):
  node = self.value
  t = node.kind()
  return is_bool(node) and (is_var(node) or (is_app(node) and t not in OPERATORS))

def isOperator(self):
  return not self.isOperand()

class Node: 
  def __init__(self, value): 
    self.value = value 
    self.left = None
    self.right = None

  def __str__(self):
    if self.value.decl() is not None:
      return str(self.value.decl())
    return str(self.value)

  def insert(self, node):    
    if self.left is None:
      self.left = Node(node)
      for child in self.left.value.children():
        self.left.insert(child)
    elif self.right is None:
      self.right = Node(node)
      for child in self.right.value.children():
        self.right.insert(child)
    else:
      self.left.insert(node)

  def printTree(self, level=0, indent=0):
    if level==0:
      line = str(self)
      indent = len(line)
    else:
      space = (level+indent) * ' '
      dotted = level * '-'
      line = "{}|{}{}".format(space, dotted, str(self))
      #line = "{}|{}".format(space,  str(self))
      indent += len(str(self))
      
    if self.right:
      self.right.printTree(level+1, indent)
    print line
    if self.left:
      self.left.printTree(level+1, indent)

# Returns root of constructed tree
def constructTree(variables, expr): 
    root = Node(expr)
    print "constructing tree from ", expr

    for child in expr.children():
      root.insert(child)

    s = Solver()
    

    return root

variables = {x[1]:createVar(x) for x in [['bool','A'], ['bool','B'], ['bool','C']]}
expr = createExpression(variables, "And(Or(v['A'],v['B']), v['C'])")
r = constructTree(variables, expr)
r.printTree()
