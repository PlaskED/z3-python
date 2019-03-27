import unittest
from utils import createExpression, createVar
from mcdc_gen import MCDCgenerator

class TestMCDC(unittest.TestCase):

    def setUp(self):
        self.generator = MCDCgenerator()
        
    def tearDown(self):
        self.generator.solver.reset()

    def testLogicalNot(self):
        gen = self.generator
        varsToAdd = [('bool', 'A')]
        gen.addVariables(varsToAdd)
        exprToAdd = "Not(v['A'])"
        expression = createExpression(gen.variables, exprToAdd)
        res = gen.findSolutions(expression)
        expected = [{'A':True}, {'A':False}]
        self.assertEquals(len(res), 2)
        for exp in expected:
            self.assertTrue(exp in res)

    def testLogicalAnd(self):
        gen = self.generator
        varsToAdd = [('bool', 'A'), ('bool', 'B')]
        gen.addVariables(varsToAdd)
        exprToAdd = "And(v['A'],v['B'])"
        expression = createExpression(gen.variables, exprToAdd)
        res = gen.findSolutions(expression)
        expected = [
            {'A' : True, 'B' : True},
            {'A' : False, 'B' : True},
            {'A' : True, 'B' : False}]
        self.assertEquals(len(res), 3)
        for exp in expected:
            self.assertTrue(exp in res)

    def testLogicalOr(self):
        gen = self.generator
        varsToAdd = [('bool', 'A'), ('bool', 'B')]
        gen.addVariables(varsToAdd)
        exprToAdd = "Or(v['A'],v['B'])"
        expression = createExpression(gen.variables, exprToAdd)
        res = gen.findSolutions(expression)
        expected = [
            {'A':True},
            {'A':False,'B':False},
            {'A':False,'B':True}]
        for exp in expected:
            self.assertTrue(exp in res)

    def testNestedLogicalOr(self):
        gen = self.generator
        varsToAdd = [('bool', 'A'), ('bool', 'B'), ('bool', 'C')]
        gen.addVariables(varsToAdd)
        exprToAdd = "Or(v['A'], And(v['B'],v['C']))"
        expression = createExpression(gen.variables, exprToAdd)
        res = gen.findSolutions(expression)
        expected = [
            {'B' : True, 'C' : True},
            {'A' : False, 'B' : True, 'C' : False},
            {'A' : False, 'B' : False, 'C' : True},
            {'A' : True, 'B' : False, 'C' : False},
            {'A' : False, 'B' : False, 'C' : False},
            {'A' : True, 'B' : False, 'C' : True}]
        self.assertEquals(len(res), 6)
        for exp in expected:
            
            self.assertTrue(exp in res)

    def testNestedLogicalAnd(self):
        gen = self.generator
        varsToAdd = [('bool', 'A'), ('bool', 'B'), ('bool', 'C')]
        gen.addVariables(varsToAdd)
        exprToAdd = "And(Or(v['A'],v['B']),v['C'])"
        expression = createExpression(gen.variables, exprToAdd)
        res = gen.findSolutions(expression)
        expected = [
            {'A' : True, 'C' : True},
            {'A' : False, 'B' : False, 'C' : True},
            {'A' : True, 'C' : False},
            {'A' : False, 'C' : False},
            {'A' : False, 'B' : True, 'C' : True}]
        self.assertEquals(len(res), 5)
        for exp in expected:
            self.assertTrue(exp in res)

    def testComparators(self):
        gen = self.generator
        varsToAdd = [('int', 'u'), ('int', 'x'), ('int', 'y'), ('int', 'z')]
        gen.addVariables(varsToAdd)
        exprToAdd = "And(Or(v['u']==0, v['x']>5),Or(v['y']<6,v['z']==0))"
        expression = createExpression(gen.variables, exprToAdd)
        res = gen.findSolutions(expression)
        expected = [
            {'x' : 6, 'y' : 0},
            {'x' : 6, 'y' : 6, 'z' : 1},
            {'u' : 1, 'x' : 0, 'y' : 0},
            {'u' : 3, 'x' : 7, 'y' : 2},
            {'u' : 3, 'x' : 8, 'y' : 2, 'z' : 4},
            {'u' : 3, 'x' : 0, 'y' : 2},
            {'u' : 3, 'x' : 8, 'y' : 2, 'z' : 1},
            {'u' : 1, 'x' : 0, 'y' : 2}]
        self.assertEquals(len(res), 8)
        for exp in expected:
            self.assertTrue(exp in res)
    @unittest.skip('not implemented')
    def testMixedExpr(self):
        pass
    

if __name__ == '__main__':
    unittest.main()

# python solverz3.py --var int,u int,x int,y int,z --expr "And(Or(v['u']==0, v['x']>5),Or(v['y']<6,v['z']==0))"
