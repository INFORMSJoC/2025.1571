from parallelPowerSystemRestoration.NetworkReductionRules import *

from parallelPowerSystemRestoration.constraints import *
from parallelPowerSystemRestoration.decisionVariables import *
from parallelPowerSystemRestoration.parameterAndSetCreation import *



startingTime = time.time()

initialize()
computeDegreesOf(G, degreeOfG)
# networkReductionMultipleRadius()
# networkReductionMultipleRadiusBookkeeping()

preModelTime = time.time()
model = Model('SCF-ALLRADIUS')  # create the model

defineVariables(model)  # pick variables

defineObjective(model)  # pick objective

# pick constraints
pickOneRadius(model)
startBeforeTheSelectedRadius(model)
startTimeSelection(model)
startCLsLastPeriod(model)
netPower(model)
# assignment
assignments(model)
# forcedAssignmentForEliminatedComponents(model) # must be used for the bookkeeping reductions
# connectivity
outgoingFlow(model)
flowAtTrans(model)
incomingFlow(model)
flowCapacity(model)
linkingXY(model)
# additional cuts
# startEachComponent(model)
noIsolatedComponent(model)


def setOptions(model):
    #  set running options
    # model.setParam('Threads', 8)
    model.setParam(GRB.param.TimeLimit, 3600)
    model.setParam('MIPFocus', 1)

    # model.setParam(OUTPUT_DIR/'LogFile', 'SCF-LOG-REDUCED-' + str(len(nodes)) + "-LB=" + str(LB) + "-UB=" + str(UB) + "-" + str(
    #     datetime.datetime.now()) + '.txt')
    # model.setParam(OUTPUT_DIR/'SolFiles', 'Sol-SCF-REDUCED-' + str(len(nodes)) + "-LB=" + str(LB) + "-UB=" + str(UB) + "-" + str(
    #     datetime.datetime.now()) + '.txt')

    # variable BRANCHING priorities
    for i in G.nodes:
        for b in BSGenerators:
            assign[i, b].BranchPriority = degreeOfG[i]


setOptions(model)
# update and solve the model
model.update()
model.optimize()

timeAfterOptimization = time.time()
print('Model Time=' + str(timeAfterOptimization - preModelTime))
print('Total Time=' + str(timeAfterOptimization - startingTime))


def solutionValidation(model):
    # this method is created for solution validation purposes
    # read the optimal solution
    variableName = []
    variableValue = []
    for v in model.getVars():
        if v.x > 0:
            variableName += [v.varname]
            variableValue += [v.x]

    # optSolution = pd.DataFrame(list(zip(variableName, variableValue)), columns=['varName', 'varVal'])
    # optSolution.to_csv(OUTPUT_DIR/'optSol-SINGLE-RADIUS-REDUCTION.csv', index=False)  # Check

    def checkPower():
        powerOK = True
        for b in BSForPowerConstraints:
            for t in range(1, timeHorizon + 1):
                periodNameBS = "period%s" % t
                [powerOutput_j_t] = nodes.loc[nodes['Bus'] == b, periodNameBS]
                lhs = 0
                for i in NBSForPowerConstraints:
                    for startPeriod in range(1, t + 1):
                        timeSinceTheStart = t - startPeriod + 1
                        lhs += (powerOf[i, timeSinceTheStart] * start[b, i, startPeriod].x)
                for i in CLsForPowerConstraints:
                    for startPeriod in range(LB, t + 1):
                        timeSinceTheStart = t - startPeriod + 1
                        lhs += (powerOf[i, timeSinceTheStart] * start[b, i, startPeriod].x)
                if lhs < -powerOutput_j_t:
                    powerOK = False
                    print("violation power BS period ", b, t)
                    break
        if powerOK:
            print("power constraints OK ")

    def checkAssignemnts():
        assignmentOK = True
        for b in BSForPowerConstraints:
            if assign[b, b].x <= 0.99:
                assignmentOK = False
                break
        for b1 in BSForPowerConstraints:
            for b in BSForPowerConstraints:
                if b != b1:
                    if assign[b1, b].x > 0.99:
                        assignmentOK = False
                        break

        for i in componentsForPowerConstraints:
            totalAssignment = 0
            for b in BSForPowerConstraints:
                totalAssignment += assign[i, b].x
            if totalAssignment >= 1.01:
                assignmentOK = False
                break
            if totalAssignment <= 0.99:
                assignmentOK = False
                break

        for i in transNodes:
            totalAssignment = 0
            for b in BSForPowerConstraints:
                totalAssignment += assign[i, b].x
            if totalAssignment >= 1.01:
                assignmentOK = False
                break
            if totalAssignment <= 0.99:
                assignmentOK = False
                break
        if assignmentOK:
            print("assignment constraints OK ")

    def checkConnectivity():
        connectivityOK = True
        for b in BSForPowerConstraints:
            clusterGraph = nx.Graph()
            clusterGraph.add_node(b)
            for i in GForPowerConstraints:
                if assign[i, b].x > 0.99:
                    clusterGraph.add_node(i)
            for i in clusterGraph.nodes:
                for j in clusterGraph.nodes:
                    if (i, j) in GForPowerConstraints.edges:
                        clusterGraph.add_edge(i, j)
                    if (j, i) in GForPowerConstraints.edges:
                        clusterGraph.add_edge(j, i)

            if not areComponentsConnected(clusterGraph):
                connectivityOK = False
                print("cluster not connected ", clusterGraph.edges)
                print("cluster nodes ", clusterGraph.nodes)
                # break
        if connectivityOK:
            print("connectivity OK ")

    def checkStartTimes():
        startTimesOK = True
        for i in NBSForPowerConstraints:
            for r in radiusSet:
                atLeastOneStartBeforeRadius = 0
                for b in BSForPowerConstraints:
                    for t in range(1, r + 1):
                        atLeastOneStartBeforeRadius += start[b, i, t].x
                for m in radiusSet:
                    if m <= r:
                        atLeastOneStartBeforeRadius -= radius[m].x
                if atLeastOneStartBeforeRadius < 0:
                    startTimesOK = False
                    print("nbs not started ", i)
                    break
        if startTimesOK:
            print("startTimesOK ")

    checkPower()
    checkAssignemnts()
    checkConnectivity()
    checkStartTimes()

# solutionValidation(model)
