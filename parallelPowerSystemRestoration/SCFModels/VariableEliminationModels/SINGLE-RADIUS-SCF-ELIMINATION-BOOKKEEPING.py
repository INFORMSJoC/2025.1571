import matplotlib.pyplot as plt
import networkx as nx
from parallelPowerSystemRestoration.SCFModels.VariableEliminationModels.NetworkReductionRulesAfterElimination import *
from parallelPowerSystemRestoration.SCFModels.VariableEliminationModels.constraintsWithElimination import *
from parallelPowerSystemRestoration.SCFModels.VariableEliminationModels.decisionVariablesWithElimination import *
from parallelPowerSystemRestoration.SCFModels.VariableEliminationModels.parameterAndSetCreationForElimination import *

startingTime = time.time()

initialize()

if LB != timeHorizon:
    raise ValueError("!!!!!!!!!! This is a single radius model: LB and timeHorizon must be identical!")
computeDegreesOf(GForPowerConstraints, degreeOfGForPower)
computeDegreesOf(G, degreeOfG)

GOriginal = nx.Graph()
for i in G.nodes:
    GOriginal.add_node(i)
# to draw the network, choose a layout
# positions = nx.spring_layout(GOriginal, seed=3)  # positions for all nodes - seed for reproducibility
positions = nx.random_layout(GOriginal, seed=16)  # positions for all nodes - seed for reproducibility
# positions = nx.spiral_layout(GOriginal, scale=1, center=None, dim=2, resolution=1011, equidistant=False)  # positions for all nodes - seed for reproducibility
# positions = nx.planar_layout(GOriginal)
# layers = {'A':bsGenerators, 'B':nbsGenerators, 'C':transNodes, 'D':criticalNodes}
# positions = nx.multipartite_layout(GOriginal, subset_key = layers, align='horizontal', scale=0.01, center=(0,0))
def drawNetwork(graph, positions):
    Gname = 'G' + str(len(GOriginal.nodes)) + '-' + str(len(graph.nodes)) + '-' + str(
        datetime.datetime.now()) + '-sol.png'
    fig, ax = plt.subplots()
    GN = nx.Graph()
    for (i, j) in graph.edges:
        GN.add_edge(i, j)
    color_map = []
    n_shape = []
    labeldict = {}
    layers = []
    for node in GN:
        if node in BSGenerators:
            color_map.append('tab:green')
            n_shape.append("d")
            labeldict[node] = '{:.0f}'.format(node)
        if node in NBSGenerators:
            color_map.append('tab:blue')
            n_shape.append("s")
            labeldict[node] = '{:.0f}'.format(node)
        if node in criticalNodes:
            color_map.append('tab:pink')
            n_shape.append("s")
            labeldict[node] = '{:.0f}'.format(node)
        if node in transNodes:
            color_map.append('tab:orange')
            n_shape.append("o")
            labeldict[node] = '{:.0f}'.format(node)
    nx.draw(GN, node_color=color_map, pos=positions, labels=labeldict, node_shape='s', with_labels=True,
            node_size=80, font_size=8, width=0.2, style="solid")
    plt.savefig(OUTPUT_DIR/'solutionFigures'/Gname, dpi=1000)
    # nx.draw(GN, node_color=color_map, pos=positions, labels=labeldict, node_shape='s', with_labels=False,
    #         node_size=10, font_size=5, width=0.1, style="solid")
    # Gname2= 'GNoLabel' + str(len(graph.nodes)) + '-' + str(datetime.datetime.now()) + '-sol.png'
    # plt.savefig(Gname2, dpi=1000)
    plt.show()

drawNetwork(G, positions)
preReductionTime = time.time()
preEliminationTime = time.time()
eliminationInitialize()
postEliminationTime = time.time()
#  network reduction
# networkReduction()

# networkReductionTROnly()
networkReductionBookkeeping()

postReductionTime = time.time()

drawNetwork(G, positions)

preModelTime = time.time()
model = Model('SINGLE-RADIUS-SCF-HEURISTIC-BOOKKEEPING')  # create the model

defineSingleRadiusVariables(model)  # pick variables

# defineObjective(model) #  pick objective

# pick constraints
startTimeSelectionSingleRadiusHeuristic(model)
netPowerSingleRadiusHeuristic(model)
# assignment
assignments(model)
forcedAssignmentForEliminatedComponents(model)  # must be used for the reduced network
# connectivity
outgoingFlow(model)
flowAtTrans(model)
incomingFlow(model)
flowCapacity(model)
linkingXY(model)
# additional cuts
# startEachComponent(model)
noIsolatedComponent(model)


# fixAssignments(model)
# triangleSubClusters(model)
def setOptions(model):
    #  set running options
    model.setParam('Threads', 8)
    model.setParam(GRB.param.TimeLimit, 3600)
    model.setParam(GRB.param.SolutionLimit, 1)
    model.setParam('MIPFocus', 1)

    # for log and solution outputs, uncomment below
    # timestamp = datetime.datetime.now()
    #
    # log_file = OUTPUT_DIR / 'LogFiles' / (
    #     f"SINGLE-RADIUS-SCF-LOG-ELIMINATION-BOOKKEEPING-{len(nodes)}-RADIUS={LB}-{timestamp}.txt"
    # )
    #
    # sol_file = OUTPUT_DIR / 'solFiles' / (
    #     f"Sol-SINGLE-RADIUS-SCF-ELIMINATION-BOOKKEEPING-{len(nodes)}-RADIUS={LB}-{timestamp}.txt"
    # )
    #
    # model.setParam('LogFile', str(log_file))
    # model.setParam('SolFiles', str(sol_file))

    # variable priorities
    for i in G.nodes:
        for b in BSGenerators:
            assign[i, b].BranchPriority = degreeOfG[i]


setOptions(model)
# update and solve the model
model.update()
model.optimize()

timeAfterOptimization = time.time()
print('Elimination Time=' + str(postEliminationTime - preEliminationTime))
print('Reduction Time=' + str(postReductionTime - preReductionTime))
print('Elimination + Reduction Time=' + str(
    (postEliminationTime - preEliminationTime) + (postReductionTime - preReductionTime)))
print('Model Time=' + str(timeAfterOptimization - preModelTime))
print('Total Time=' + str(timeAfterOptimization - startingTime))

totalCLpow = 0
totalNBSpow15 = 0
for b in BSForPowerConstraints:
    powInOne = 0
    powIn15 = 0
    for i in NBSForPowerConstraints:
        for t in range(1, timeHorizon + 1):
            if feasibleStartArray[(b, i, t)] == 1:
                if start[b, i, t].x > 0.99:
                    # print(b, i, t, powerOf[i, 1])
                    if t == 1:
                        powInOne += powerOf[i, 1]
                    if t == 15:
                        powIn15 += powerOf[i, 1]
    print(b, 1, 15, powInOne, powIn15)
    totalCLPower = 0
    for j in criticalNodes:
        if assign[j, b].x > 0.99:
            # print(b, j, powerOf[j,timeHorizon])
            totalCLPower += powerOf[j, timeHorizon]
    # print(b, totalCLPower)
    totalCLpow += totalCLPower
    totalNBSpow15 += powIn15
    totalPow = totalCLPower + powIn15
    # print(b, totalPow)

print(totalCLpow, totalNBSpow15)


def solutionValidation(model):
    # read the optimal solution
    variableName = []
    variableValue = []
    for v in model.getVars():
        if v.x > 0:
            variableName += [v.varname]
            variableValue += [v.x]

    optSolution = pd.DataFrame(list(zip(variableName, variableValue)), columns=['varName', 'varVal'])
    # optSolution.to_csv('optSol-SCF-SINGLE-RADIUS-ELIMINATION-BOOKKEEPING.csv', index=False)  # Check

    def checkPower():
        powerOK = True
        for b in BSForPowerConstraints:
            for t in range(1, timeHorizon + 1):
                periodNameBS = "period%s" % t
                [powerOutput_j_t] = nodes.loc[nodes['Bus'] == b, periodNameBS]
                lhs = 0
                for i in NBSForPowerConstraints:
                    for earlierT in range(1, t + 1):
                        if feasibleStartArray[(b, i, earlierT)] == 1:
                            relationT = t - earlierT + 1
                            lhs += (powerOf[i, relationT] * start[b, i, earlierT].x)
                for i in CLsForPowerConstraints:
                    for earlierT in range(LB, t + 1):
                        relationT = t - earlierT + 1
                        if feasibleStartArray[(b, i, t)] == 1:
                            lhs += (powerOf[i, relationT] * assign[i, b].x)
                if lhs < -powerOutput_j_t:
                    powerOK = False
                    print("violation power BS period ", b, t)
                    break
        if powerOK == True:
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
        if assignmentOK == True:
            print("assignment constraints OK ")

    def checkConnectivity():
        connectivityOK = True
        for b in BSForPowerConstraints:
            clusterGraph = nx.Graph()
            clusterGraph.add_node(b)
            for i in G:
                if assign[i, b].x > 0.99:
                    clusterGraph.add_node(i)
            for i in clusterGraph.nodes:
                for j in clusterGraph.nodes:
                    if (i, j) in G.edges:
                        clusterGraph.add_edge(i, j)
                    if (j, i) in G.edges:
                        clusterGraph.add_edge(j, i)

            if not areComponentsConnected(clusterGraph):
                connectivityOK = False
                print("cluster not connected ", clusterGraph.edges)
                print("cluster nodes ", clusterGraph.nodes)
                # break
        if connectivityOK == True:
            print("connectivity OK ")

    def checkStartTimes():
        startTimesOK = True
        for b in BSForPowerConstraints:
            for i in NBSForPowerConstraints:
                atLeastOneStartBeforeRadius = - assign[i, b].x
                for t in range(1, timeHorizon + 1):
                    if feasibleStartArray[b, i, t]:
                        atLeastOneStartBeforeRadius += start[b, i, t].x
                if atLeastOneStartBeforeRadius < 0:
                    startTimesOK = False
                    print("nbs not started ", i)
                    break
        if startTimesOK == True:
            print("startTimesOK ")

    checkPower()
    checkAssignemnts()
    checkConnectivity()
    checkStartTimes()


def drawSolution(positions):
    # print and draw each cluster network
    GSol = nx.Graph()
    GSolName = 'G' + str(len(GOriginal.nodes)) + 'Sol-' + str(datetime.datetime.now()) + '-sol.png'
    color_mapSol = []
    n_shapeSol = []
    labeldictSol = {}
    for b in BSForPowerConstraints:
        GB = nx.Graph()
        for k in G.nodes:
            if assign[k, b].x > 0.9:
                for j in G.neighbors(k):
                    if assign[j, b].x > 0.9:
                        GB.add_edge(j, k, weight=100)
                        GSol.add_edge(j, k, weight=100)

        GnameB = 'G' + str(len(GOriginal.nodes)) + '-' + str(b) + '-' + str(datetime.datetime.now()) + '-sol.png'

        color_map = []
        n_shape = []
        labeldict = {}
        counter = 1
        # positions = nx.spring_layout(GN, seed=3)  # positions for all nodes - seed for reproducibility
        for node in GB:
            # positions[node] = (counter % 20, counter*2)
            counter += 1
            if node in BSGenerators:
                color_map.append('tab:green')
                color_mapSol.append('tab:green')
                n_shape.append("d")
                labeldict[node] = '{:.0f}'.format(node)
                labeldictSol[node] = '{:.0f}'.format(node)
            if node in NBSGenerators:
                color_map.append('tab:blue')
                color_mapSol.append('tab:blue')
                n_shape.append("s")
                labeldict[node] = '{:.0f}'.format(node)
                labeldictSol[node] = '{:.0f}'.format(node)
            if node in criticalNodes:
                color_map.append('tab:pink')
                color_mapSol.append('tab:pink')
                n_shape.append("s")
                labeldict[node] = '{:.0f}'.format(node)
                labeldictSol[node] = '{:.0f}'.format(node)
            if node in transNodes:
                color_map.append('tab:orange')
                color_mapSol.append('tab:orange')
                n_shape.append("o")
                labeldict[node] = '{:.0f}'.format(node)
                labeldictSol[node] = '{:.0f}'.format(node)
        nx.draw(GB, node_color=color_map, pos=positions, labels=labeldict, node_shape='s', with_labels=True,
                node_size=200, font_size=10, width=0.4, style="solid")
        plt.savefig(OUTPUT_DIR/'solutionFigures'/ GnameB, dpi=100)
        plt.show()

    nx.draw(GSol, node_color=color_mapSol, pos=positions, labels=labeldictSol, node_shape='s', with_labels=True,
            node_size=80, font_size=8, width=0.2, style="solid")
    plt.savefig(OUTPUT_DIR/'solutionFigures'/ GSolName, dpi=1000)

    plt.show()


drawSolution(positions)

solutionValidation(model)
