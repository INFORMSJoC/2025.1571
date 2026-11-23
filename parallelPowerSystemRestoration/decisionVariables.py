# Decision variables for the PPSR formulations.

from gurobipy import *

from parallelPowerSystemRestoration.parameterAndSetCreation import *


def defineVariables(model):
    radiusVariables(model)
    assignmentVariables(model)
    singleCommodityFlowVariables(model)
    arcSelectionVariables(model)
    startTimeVariables(model)

def defineSingleRadiusVariables(model):
    singleRadiusStartVars(model)
    assignmentVariables(model)
    singleCommodityFlowVariables(model)
    arcSelectionVariables(model)


def radiusVariables(model):
    # #  radius variables
    for rad in radiusSet:
        radius[rad] = model.addVar(vtype=GRB.BINARY, lb=0, ub=1, name='u[%g]' % rad)
    # print("radius variables")


def assignmentVariables(model):
    assignmentVars = []
    assignmentVar_names = []
    for i in GForPowerConstraints.nodes():
        for b in BSForPowerConstraints:
            assignmentVars += [(i, b)]
            assignmentVar_names += ['a[%s,%s]' % (i, b)]
            assign[i, b] = model.addVar(vtype=GRB.BINARY, name='a[%s,%s]' % (i, b))


def singleCommodityFlowVariables(model):
    flowSCVars = []
    flowSCNames = []
    for b in BSGenerators:
        for (i, j) in G.edges():
            flowSCVars += [(i, j, b)]
            flowSCNames += ['f[%s,%s,%s]' % (i, j, b)]
            flow[i, j, b] = model.addVar(vtype=GRB.INTEGER, lb=-GRB.INFINITY, ub=GRB.INFINITY,
                                         name='f[%s,%s,%s]' % (i, j, b))


def arcSelectionVariables(model):
    yVars = []
    yVarNames = []
    for b in BSGenerators:
        for (i, j) in G.edges():
            yVars += [(i, j, b)]
            yVarNames += ['y[%s,%s,%s]' % (i, j, b)]
            arc[i, j, b] = model.addVar(vtype=GRB.BINARY, name='y[%s,%s,%s]' % (i, j, b))


def startTimeVariables(model):
    startVars = []
    startVarNames = []
    for b in BSGenerators:
        for i in NBSForPowerConstraints:
            for t in range(1, timeHorizon + 1):
                startVars += [(b, i, t)]
                startVarNames += ['start[%s,%s,%s]' % (b, i, t)]
                start[b, i, t] = model.addVar(vtype=GRB.BINARY, name='w[%s,%s,%s]' % (b, i, t))

    for b in BSGenerators:
        for i in CLsForPowerConstraints:
            for t in range(LB, timeHorizon + 1):
                startVars += [(b, i, t)]
                startVarNames += ['start[%s,%s,%s]' % (b, i, t)]
                start[b, i, t] = model.addVar(vtype=GRB.BINARY, name='w[%s,%s,%s]' % (b, i, t))


def singleRadiusStartVars(model):
    singleRadiusStartVars = []
    singleRadiusStartVarNames = []
    for b in BSGenerators:
        for i in NBSForPowerConstraints:
            for t in range(1, timeHorizon + 1):
                singleRadiusStartVars += [(b, i, t)]
                singleRadiusStartVarNames += ['start[%s,%s,%s]' % (b, i, t)]
                start[b, i, t] = model.addVar(vtype=GRB.BINARY, name='w[%s,%s,%s]' % (b, i, t))


def eliminationSingleRadiusStartVars(model):
    eliminationStartVars = []
    liminationStartVarNames = []
    print('creating heuristic-based start-up variables')
    for (b, i, t) in feasibleStartTimesPerBS:
        eliminationStartVars += [(b, i, t)]
        liminationStartVarNames += ['start[%s,%s,%s]' % (b, i, t)]
        start[b, i, t] = model.addVar(vtype=GRB.BINARY, name='w[%s,%s,%s]' % (b, i, t))
    print('heuristic-based start-up variables created')
