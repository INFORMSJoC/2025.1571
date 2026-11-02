from gurobipy import *
from parallelPowerSystemRestoration.SCFModels.VariableEliminationModels.parameterAndSetCreationForElimination import *

def defineVariables(model):

    radiusVars(model)
    assignmentVars(model)
    singleCommodityFlowVars(model)
    arcAssignmentVars(model)
    startVars(model)

def defineSingleRadiusVariables(model):

    assignmentVars(model)
    singleCommodityFlowVars(model)
    arcAssignmentVars(model)
    startVarsSingleRadiusHeuristic(model)
    print('variables created')


def radiusVars(model):
    # #  radius variables
    for rad in radius_set:
        radius[rad] = model.addVar(vtype=GRB.BINARY, lb=0, ub=1, name='u[%g]' % rad)
    # print("radius variables")

def assignmentVars(model):
    x_vars = []
    x_names = []
    for v in GForPowerConstraints.nodes():
        for gen in BSForPowerConstraints:
            x_vars += [(v,gen)]
            x_names += ['a[%s,%s]'%(v,gen)]
            assign[v,gen] = model.addVar(vtype = GRB.BINARY, name = 'a[%s,%s]'%(v,gen))

def singleCommodityFlowVars(model):
    flowSC_vars = []
    flowSC_names = []
    for j in BSGenerators:
        for (u,v) in G.edges():
            flowSC_vars += [(u,v,j)]
            flowSC_names += ['f[%s,%s,%s]'%(u,v,j)]
            flow[u,v,j] = model.addVar(vtype = GRB.INTEGER, lb = -GRB.INFINITY, name = 'f[%s,%s,%s]'%(u,v,j))

def arcAssignmentVars(model):
    y_vars = []
    y_names = []
    for j in BSGenerators:
        for (u,v) in G.edges():
            y_vars += [(u,v,j)]
            y_names += ['y[%s,%s,%s]'%(u,v,j)]
            y[u,v,j] = model.addVar(vtype = GRB.BINARY, name = 'y[%s,%s,%s]'%(u,v,j))

def startVars(model):
    start_vars = []
    start_names = []
    for b in BSGenerators:
        for i in NBSForPowerConstraints:
            for t in range(1, timeHorizon + 1):
                if feasibleStartArray[(b, i, t)] == 1:
                    start_vars += [(b, i, t)]
                    start_names += ['start[%s,%s,%s]' % (b, i, t)]
                    start[b, i, t] = model.addVar(vtype=GRB.BINARY, name='w[%s,%s,%s]' % (b, i, t))

    for b in BSGenerators:
        for i in CLsForPowerConstraints:
            for t in range(LB, timeHorizon + 1):
                if feasibleStartArray[(b, i, t)] == 1:
                    start_vars += [(b, i, t)]
                    start_names += ['start[%s,%s,%s]' % (b, i, t)]
                    start[b, i, t] = model.addVar(vtype=GRB.BINARY, name='w[%s,%s,%s]' % (b, i, t))


def startVarsSingleRadiusHeuristic(model):
    start_vars = []
    start_names = []
    print('creating the start up variables')
    for b in BSGenerators:
        for i in NBSForPowerConstraints:
            for t in range(1, timeHorizon + 1):
                if feasibleStartArray[(b, i, t)] == 1:
                    start_vars += [(b, i, t)]
                    start_names += ['start[%s,%s,%s]' % (b, i, t)]
                    start[b, i, t] = model.addVar(vtype=GRB.BINARY, name='w[%s,%s,%s]' % (b, i, t))
