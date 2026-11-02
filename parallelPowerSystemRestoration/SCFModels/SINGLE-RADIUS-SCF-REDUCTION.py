# This is the implementation of the single-radius SCF model SCF(r).
# To deactivate reduction rules, it is sufficient to comment the corresponding line for networkReduction()  # network reduction
# To active bookkeeping reductions as well, choose networkReductionBookkeeping() instead. Note that this requires activation of forcedAssignment constraints
# For the single-radius formulation with variable elimination, use the files from the VariableEliminationModels directory.
import matplotlib.pyplot as plt

from parallelPowerSystemRestoration.NetworkReductionRules import *
from parallelPowerSystemRestoration.constraints import *
from parallelPowerSystemRestoration.decisionVariables import *
from parallelPowerSystemRestoration.parameterAndSetCreation import *

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
# positions = nx.spiral_layout(GOriginal)  # positions for all nodes - seed for reproducibility
# positions = nx.planar_layout(GOriginal)
# positions = nx.spiral_layout(GOriginal, scale=1, center=None, dim=2, resolution=210, equidistant=False)  # positions for all nodes - seed for reproducibility

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
            node_size=40, font_size=5, width=0.2, style="solid")
    plt.savefig(OUTPUT_DIR/'solutionFigures' /Gname, dpi=1000)
    plt.show()


# drawNetwork(G, positions) # uncomment to draw the initial network
timePreReduction = time.time()

# apply the network reduction rules, choose among the different enhancement combinations
networkReduction()  # network reduction

timeAfterReduction = time.time()
print('reduction time = ', (timeAfterReduction - timePreReduction))

# drawNetwork(G, positions) # draw the network after applying the network reductions
preModelTime = time.time()
model = Model('SINGLE-RADIUS-SCF')  # create the model

defineSingleRadiusVariables(model)  # pick variables

# defineObjective(model) #  pick objective, not essential for feasibility problems

# ~~~~~~~~~~~~ pick constraints ~~~~~~~~~~~~~~~
startTimeSelectionSingleRadius(model)
netPowerSingleRadius(model)
# ~~~~~~~~~~~~~~ assignment ~~~~~~~~~~~~~~~~
assignments(model)
# forcedAssignmentForEliminatedComponents(model) # must be used for the reduced network with bookkeeping
# ~~~~~~~~~~~~~~ connectivity ~~~~~~~~~~~~~~
outgoingFlow(model)
flowAtTrans(model)
incomingFlow(model)
flowCapacity(model)
linkingXY(model)
# ~~~~~~~~~~~~~~~~ additional cuts ~~~~~~~~~~~~~~~
# startEachComponent(model) # identical to startTimeSelectionSingleRadius if radius variables are not used
noIsolatedComponent(model)


def setOptions(model):
    #  set running options
    # model.setParam('Threads', 8)
    model.setParam(GRB.param.TimeLimit, 3600)
    model.setParam(GRB.param.SolutionLimit, 1)
    model.setParam('MIPFocus', 1)

    # to create log files and solve files, uncomment below
    # timestamp = datetime.datetime.now()
    #
    # log_file = OUTPUT_DIR / 'LogFiles' / (
    #     f"SINGLE-RADIUS-SCF-LOG-{len(nodes)}-RADIUS={LB}-{timestamp}.txt"
    # )
    #
    # sol_file = OUTPUT_DIR / 'solFiles' / (
    #     f"Sol-SINGLE-RADIUS-SCF-{len(nodes)}-RADIUS={LB}-{timestamp}.txt"
    # )
    #
    # model.setParam('LogFile', str(log_file))
    # model.setParam('SolFiles', str(sol_file))

    # set branch priorities for the assignment variables
    for i in G.nodes:
        for b in BSGenerators:
            assign[i, b].BranchPriority = degreeOfG[i]


setOptions(model)
# update and solve the model
model.update()
model.optimize()
modelStatus = model.Status

if modelStatus == 2:
    print("Model status is 'Optimal' for radius ", LB)
else:
    if modelStatus == 3:
        print("Model status is 'Infeasible' for radius ", LB)

timeAfterOptimization = time.time()
print('Pre -reduction processing time = ', (timePreReduction - startingTime))
print('Model Time=' + str(timeAfterOptimization - preModelTime))
print('Model+reduction Time=' + str((timeAfterOptimization - preModelTime) + (timeAfterReduction - timePreReduction)))
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

    optSolution = pd.DataFrame(list(zip(variableName, variableValue)), columns=['varName', 'varVal'])
    # optSolution.to_csv(OUTPUT_DIR/'solFiles' /'optSol-SINGLE-RADIUS-REDUCTION.csv', index=False)  # Check

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
def drawSolution(positions):
    # print and draw each island network
    GSol = nx.Graph()
    GSolName = 'G' + str(len(GOriginal.nodes)) + 'Sol-RADIUS='+str(LB) +'-' + str(datetime.datetime.now()) + '-sol.png'
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

        GnameB = 'G' + str(len(GOriginal.nodes)) + '-' + str(b) + '-RADIUS='+str(LB) +'-' + str(datetime.datetime.now()) + '-sol.png'

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
                node_size=250, font_size=10, width=0.4, style="solid")
        plt.savefig(OUTPUT_DIR / 'solutionFigures' /GnameB, dpi=100)
        plt.show()

    nx.draw(GSol, node_color=color_mapSol, pos=positions, labels=labeldictSol, node_shape='s', with_labels=True,
            node_size=80, font_size=5, width=0.2, style="solid")
    plt.savefig(OUTPUT_DIR / 'solutionFigures' / GSolName, dpi=1000)
    plt.show()


# drawSolution(positions)
print('reduction time = ', (timeAfterReduction - timePreReduction))
