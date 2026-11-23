# # Decision variables for the GSS formulations.
# Define the type, bound and name of the decision variables through functions
from gurobipy import *
from parallelPowerSystemRestoration.parameterAndSetCreation import *
# from parallelPowerSystemRestoration.GSSModels.timeDependentInput import *
# from parallelPowerSystemRestoration.GSSModels.timeIndependentInput import *


def radiusVars(model):
    #  radius variables
    print("radius set:", radiusSet)
    for rad in radiusSet:
        radius[rad] = model.addVar(vtype=GRB.BINARY, lb=0, ub=1, name='u[%g]' % rad)
    # print("radius variables")


def continuousRadiusVars(model):
    #  continuous radius variables
    for rad in radiusSet:
        radius[rad] = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1, name='u[%g]' % rad)
    # print("continuous radius variables")


def startVarsGSS(model, LB, timeHorizon):
    start_vars = []
    start_names = []

    for i in NBSForPowerConstraints:
        for t in range(1, timeHorizon + 1):
            start_vars += [(i, t)]
            start_names += ['start[%s,%s]' % (i, t)]
            start[i, t] = model.addVar(vtype=GRB.BINARY, name='w[%s,%s]' % (i, t))
    for i in CLsForPowerConstraints:
        for t in range(LB, timeHorizon + 1):
            start_vars += [(i, t)]
            start_names += ['start[%s,%s]' % (i, t)]
            start[i, t] = model.addVar(vtype=GRB.BINARY, name='w[%s,%s]' % (i, t))


def startVarsSingleRadiusGSS(model, timeHorizon):
    start_vars = []
    start_names = []
    for i in NBSForPowerConstraints:
        for t in range(1, timeHorizon + 1):
            start_vars += [(i, t)]
            start_names += ['start[%s,%s]' % (i, t)]
            start[i, t] = model.addVar(vtype=GRB.BINARY, name='w[%s,%s]' % (i, t))


def continuousStartVarsSingleRadiusGSS(model, timeHorizon):
    start_vars = []
    start_names = []
    for i in NBSForPowerConstraints:
        for t in range(1, timeHorizon + 1):
            start_vars += [(i, t)]
            start_names += ['start[%s,%s]' % (i, t)]
            start[i, t] = model.addVar(vtype=GRB.CONTINUOUS, name='w[%s,%s]' % (i, t))


def auxiliaryVariablesGSS(model, timeHorizon):
    auxiliary_vars = []
    for t in range(1, timeHorizon + 1):
        auxiliary_vars += [t]
        auxiliary[t] = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name='aux[%g]' % t)
