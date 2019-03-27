import sys, logging, argparse, timeit
from itertools import islice
import json
from utils import printTruthTable, showLog, z3TypeToPython
from classes import FuncCall, Variable, Constant, Assignment, DataType, DataMember
from mcdc_gen import MCDCgenerator

logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
logger = logging.getLogger()

def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())

def calculate(variables, expressions, funcCalls, dataTypes, parallel=False):
  generator = MCDCgenerator(variables, expressions, funcCalls, dataTypes, parallel)
  generator.setLogLevel(logger.getEffectiveLevel())

  logger.debug(generator)

  if showLog():
    start = timeit.timeit()

  solutions = generator.findSolutions()
    
  if showLog():
    end = timeit.timeit()
    logger.info("Time elapsed: {}ms".format(end - start))

  if showLog():
    printTruthTable(solutions, generator.variables)

  return solutions

def chunks(l, n):
  n = max(1, n)
  return (l[i:i+n] for i in xrange(0, len(l), n))

def main(variables, expressions, funcCalls, dataTypes, parallel=False):
  results = calculate(variables, expressions, funcCalls, dataTypes, parallel)
  logger.info("found {} test cases".format(len(results)))
  for r in results:
    for k,v in r.iteritems():
      r[k] = z3TypeToPython(v)
  return results
    
if __name__== "__main__":
  parser = argparse.ArgumentParser(description='Find test cases satisfying given expressions.')
  parser.add_argument('-v', '--verbose', dest='verbosity', action='count',
                  help='enable INFO or DEBUG logger messages depending on verbosity level')
  parser.add_argument('-p', '--parallel', dest='parallel', action='store_const',
                  const=True, default=False,
                  help='run subgoals in parallel (default: no parallel subgoals)')
  parser.add_argument('--var', nargs='+',
                  help='one or more variables and their id, for example: int,x bool,y real,z')
  parser.add_argument('-a', '--assign', nargs='+', default=[],
                      help='one or more assignments which can be used to solve expressions and are skipped when proving each variable, for example: int,x,\"v[\'t\']+3\". Format is (type, name, assignment)')
  parser.add_argument('-e', '--expr', nargs='+',
                  help="one or more expressions to solve SAT for, for example: \"And(v['x']==3, v['y']>v['x'])\"")
  parser.add_argument('-c', '--const', nargs='+', default=[],
                  help="one or more constants to pass to solver, for example: real,M_PI,3.14")
  parser.add_argument('-fcd', '--funcCallDef', nargs='+', default=[],
                      help="one or more function call defintions to pass to solver, for example: int,\"Foo(int)\". Format is (returnType, funcCall)")
  parser.add_argument('-fce', '--funcCallExpr', nargs='+', default=[],
                      help="one or more function call expressions to pass to solver, for example: \"Foo(int)\",\"5>v['t']\". Format is (funcCall, expr)")
  parser.add_argument('-td', '--typeDecl', nargs='+', default=[],
                      help="one or more types to have the solver declare, for example: Foo,var,Bar. Format is (typeName, memberName, memberType)")
 
  args = parser.parse_args()
  parallel = args.parallel
  verbosity = args.verbosity
  tmp = [x.split(',', 1) for x in list(set(args.var))]
  variables = [Variable(y[0],y[1]) for y in tmp]
  variables += [Constant(y[0], y[1], y[2]) for y in [x.split(',', 2) for x in args.const]]
  variables += [Assignment(y[0], y[1], y[2]) for y in [x.split(',', 2) for x in args.assign]]
  
  expr = args.expr

  funcCallDef = {y[1]:[y[0]] for y in [x.split(',', 1) for x in args.funcCallDef]} 
  for x in [x.split(',', 1) for x in args.funcCallExpr]:
    funcCallDef[x[0]].append(x[1])

  funcCalls = [FuncCall(v[0], k, v[1:]) for k,v in funcCallDef.items()]

  dataTypes = {}
  for x in [x.split(",") for x in args.typeDecl]:
    members = [DataMember(y[0], y[1]) for y in chunk(x[1:],2)]
    dataTypes[x[0]] = DataType(x[0], members)
  
  if verbosity == 2:
    logger.setLevel(logging.DEBUG)
  elif verbosity == 1:
    logger.setLevel(logging.INFO)

  result = main(variables, args.expr, funcCalls, dataTypes, parallel)
  
  print json.dumps(result, separators=(',', ':'))


####
# example calling from command line with 2 int variables and a expr to be satisfied

# Logical AND: python solverz3.py --var bool,A bool,B --expr "And(v['A'],v['B'])"

# python solverz3.py --var int,u int,x int,y int,z --expr "And(Or(v['u']==0, v['x']>5),Or(v['y']<6,v['z']==0))"
# python solverz3.py --var int,t -e "And(v['fun_0'], v['fun_1']))" -fc fun_0,"v['t']>=5","v['t']<10" fun_1,"(3>=5)","(3<10)"

####
