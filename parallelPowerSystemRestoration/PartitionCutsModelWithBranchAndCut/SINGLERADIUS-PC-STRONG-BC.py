# This file implements the Branch-and-Cut algorithm to solve the partition-cut formulation for a single radius.
# The radius value and other parameters are imported from parameterAndSetCreation.py.
# Unlike the other files, it defines all sub-methods/functions for constraints and cuts in itself (self contained).
# Note that the assignment and start variables define the index orders differently from those for the SCF variables.
# As usual, the network reduction rules can be imported before building the formulation.

from gurobipy import *
import pandas as pd
import networkx as nx
import time, datetime
import matplotlib.pyplot as plt

from parallelPowerSystemRestoration.NetworkReductionRules import *
from parallelPowerSystemRestoration.parameterAndSetCreation import *
from parallelPowerSystemRestoration.decisionVariables import *


time0 = time.time()

numberOfThreads = 8
# activate or deactivate the fractional cuts below
addFractionalCutsOption = True

initialize()
if LB != timeHorizon:
    raise ValueError("!!!!!!!!!! This is a single radius model: LB and timeHorizon must be identical!")

computeDegreesOf(GForPowerConstraints, degreeOfGForPower)
computeDegreesOf(G, degreeOfG)

networkReduction()

UB = timeHorizon
print("Radius value = ", LB)

# create a directed graph
GDirected = nx.DiGraph()
for v in G.nodes():
    GDirected.add_node(v)
for (u,v) in G.edges():
    # if v not in BSGenerators:
    GDirected.add_edge(u,v)
    # if u not in BSGenerators:
    GDirected.add_edge(v,u)


def printProblemParameters():
    print('BS generators:', BSGenerators)
    print('NBS generators:', NBSGenerators)
    print('CLs:', criticalNodes)
    print('components:', allComponents)
    print('TR nodes:', transNodes)
    print('# NBS generators:', len(NBSGenerators))
    print('# CLs:', len(criticalNodes))
    print('# components:', len(allComponents))
    print('# edges', len(GDirected.edges))
    print('# nodes', len(GDirected.nodes))
    print('radius set=', radiusSet)
    print('period set =', periodSet)

printProblemParameters()


time1 = time.time()

# ILP Model
model = Model('PARTITIONCUT_BC_STRONGCUTS_FRACTIONALCUTS')

# define the decision variables
singleRadiusStartVars(model)
assignmentVariables(model)

# Feasibility problem, no objective function is needed

def defineConstraints(model):

    def assignEachComponentToABS(model):
        # assign each node to a BS island
        for i in allComponents:
            # if i not in BSGenerators:
            cluster = LinExpr()
            for b in BSGenerators:
                cluster.addTerms(1, assign[i, b])
            model.addConstr(cluster.__eq__(1), name='oneCluster(%g)' % i)
            model.update()
            # print("one BS per node", cluster.__eq__(1))
        # print("one BS per node")
    def assignEachTransToAtMostOneBS(model):
        # assign each node to a BS island
        for i in transNodes:
            cluster = LinExpr()
            for b in BSGenerators:
                cluster.addTerms(1, assign[i, b])
            model.addConstr(cluster.__le__(1), name='oneCluster(%g)' % i)
            model.update()
            # print("one BS per node", cluster.__le__(1))
        # print("one BS per node")
    def assignEachBSToSelf(model):
        # assign BSs to their own islands
        for b in BSGenerators:
            clusterB = LinExpr()
            clusterB.addTerms(1, assign[b, b])
            model.addConstr(clusterB.__eq__(1), name='oneClusterSelf(%s)' % b)
            model.update()
            # print("self assinment BS",clusterB.__eq__(1))
        # print("self assinment BS")
        for b in BSGenerators:
            for b2 in BSGenerators:
                if b2 != b:
                    clusterBNot = LinExpr()
                    clusterBNot.addTerms(1, assign[b, b2])
                    model.addConstr(clusterBNot.__eq__(0), name='BSNotAllocatedToOthers(%s)' % b)
                    model.update()
                    # print("BS not allocated to others", clusterBNot.__eq__(0))
        # print("BS not allocated to others")
    def noIsolatedComponent(model):
        # one preceding node should be in the same island (or one preceding or succeeding node)
        for i in GDirected.nodes:
            if i not in BSGenerators:
                for b in BSGenerators:
                    noIsolatedNode = LinExpr()
                    noIsolatedNode.addTerms(-1, assign[i, b])
                    for j in GDirected.predecessors(i):
                        noIsolatedNode.addTerms(1, assign[j, b])
                    model.addConstr(noIsolatedNode.__ge__(0))
    def startInTheAssignedClusterSingleRadius(model):
        # connect the island assignment and start time variables
        for i in NBSForPowerConstraints:
            for b in BSGenerators:
                oneStart = LinExpr()
                oneStart.addTerms(-1, assign[i, b])
                for t in range(1, timeHorizon + 1):
                    oneStart.addTerms(1, start[b, i, t])
                model.addConstr(oneStart.__eq__(0), name='atMostOneStart(%g,%g)' % (i, b))
        # print("one start at assigned")
    def startBeforeTheSelectedRadiusSingleRadius(model):
        # at least one start before the selected radius
        for i in NBSForPowerConstraints:
            atLeastOneStartBeforeRadius = LinExpr()
            for b in BSGenerators:
                for t in range(1, timeHorizon + 1):
                    atLeastOneStartBeforeRadius.addTerms(1, start[b, i, t])
            model.addConstr(atLeastOneStartBeforeRadius.__eq__(1), name='atLeastOneStart(%g)' % (i))
        # print("at least one start before the radius")
    def startEachComponentSingleRadius(model):
        # one start for each NBS
        for i in NBSForPowerConstraints:
            oneStartPerComponent = LinExpr()
            for b in BSGenerators:
                for t in range(1, timeHorizon + 1):
                    oneStartPerComponent.addTerms(1, start[b, i, t])
            model.addConstr(oneStartPerComponent.__eq__(1), name='atMostOneStart(%g)' % i)
        # print("one start and one island per NBS")

    def netPowerSingleRadius(model):
        # Net Power Constraints
        for b in BSGenerators:
            for t in range(1, timeHorizon + 1):
                netPower = LinExpr()
                netPower.addConstant(powerOutputFromBS[b, t] + demandFrom[b,t])
                for i in NBSForPowerConstraints:
                    for startPeriod in range(1, t + 1):
                        timeSinceTheStart = t - startPeriod + 1
                        netPower.addTerms(powerOf[i, timeSinceTheStart], start[b, i, startPeriod])
                        if t == timeHorizon:
                            netPower.addTerms(demandFrom[i, timeHorizon], start[b, i, startPeriod])
                if t == timeHorizon:
                    for i in CLsForPowerConstraints: # all CLs start the last period
                        netPower.addTerms(powerOf[i, timeHorizon], assign[i, b])
                model.addConstr(netPower.__ge__(0), name='Eq(powerAgg)(%g, %g)' % (b, t))
        print("Net power output per island, last period and earlier periods")


    assignEachComponentToABS(model)
    assignEachTransToAtMostOneBS(model)
    assignEachBSToSelf(model)
    # noIsolatedComponent(model)
    startInTheAssignedClusterSingleRadius(model)
    startBeforeTheSelectedRadiusSingleRadius(model)
    startEachComponentSingleRadius(model)
    netPowerSingleRadius(model)


defineConstraints(model)


def setGurobiOptions(model):
    model.setParam('Threads', numberOfThreads)
    model.setParam(GRB.param.TimeLimit, 3600)
    model.setParam('MIPFocus', 1)
    model.Params.LazyConstraints = 1
    model.setParam(GRB.param.PreCrush, 1)
    model.setParam(GRB.param.SolutionLimit, 1) # activate for the single radius formulations which seek feasibility rather than optimality

    # variable branch priorities
    for i in GDirected.nodes:
        for b in BSGenerators:
            assign[i, b].BranchPriority = degreeOfG[i]

    # for log and solution outputs, uncomment below
    # timestamp = datetime.datetime.now()
    #
    # log_file = OUTPUT_DIR / 'LogFiles' / (
    #     f"Logfile-SINGLE-RADIUS-PC-BC-min-frac-{len(nodes)}-RADIUS={LB}-{timestamp}.txt"
    # )
    #
    # sol_file = OUTPUT_DIR / 'solFiles' / (
    #     f"Sol-SINGLE-RADIUS-PC-BC-min-frac-{len(nodes)}-RADIUS={LB}-{timestamp}.txt"
    # )
    #
    # model.setParam('LogFile', str(log_file))
    # model.setParam('SolFiles', str(sol_file))

setGurobiOptions(model)
def isConnected(givenGraph) -> bool:
    # The given graph is not connected if there exists a node that cannot be reached from a subset of the nodes in the graph.
    clusterConnected = False
    # connectivity check with an algorithm
    explored = set()
    unexplored = set()
    visited = set()
    isVisited = dict.fromkeys(givenGraph.nodes, 0)
    isExplored = dict.fromkeys(givenGraph.nodes, 0)
    isUnexplored = dict.fromkeys(givenGraph.nodes, 1)

    for i in givenGraph.nodes:
        unexplored.add(i)
    randomNode = unexplored.pop()
    explored.add(randomNode)
    isExplored[randomNode] = 1

    exploredEmpty = 1
    while len(unexplored) >= 1 and exploredEmpty == 1:
        # as long as there are unexplored nodes or disconnectivity detected
        for j in givenGraph.nodes:
            if isExplored[j] == 1 and j not in visited:
                for v in givenGraph.successors(j):
                    if v in unexplored:
                        explored.add(v)
                        unexplored.remove(v)
                        isExplored[v] = 1
                        isUnexplored[v] = 0
                visited.add(j)
                isVisited[j] = 1
                explored.remove(j)
                isExplored[j] = 0
                if len(explored) == 0:
                    exploredEmpty = 0
                    break
    if len(unexplored) == 0:
        clusterConnected = True
    else:
        if len(explored) == 0 and len(unexplored) >= 1:  # disconnected
            # print("**************** Disconnected cluster ID, edges", b, myGraph.edges)
            clusterConnected = False
    return clusterConnected
def isReachable(givenGraph, origin, destination) -> bool:
    # To check if the destination is reachable from the origin on the given graph.
    # Starting from the origin, check the successors of all reachable nodes from the origin.
    # If the destination is not a successor of any reachable node, then it is not reachable.
    reachable = False
    # create a copy of the given graph
    workingGraph = givenGraph.copy()
    for i in workingGraph.nodes:
        for j in workingGraph.nodes:
            if (i,j) in GDirected.edges():
                workingGraph.add_edge(i,j)
            if (j,i) in GDirected.edges():
                workingGraph.add_edge(j,i)

    zExplored = set()
    zUnexplored = set()
    zVisited = set()
    isZVisited = dict.fromkeys(workingGraph.nodes, 0)
    isZExplored = dict.fromkeys(workingGraph.nodes, 0)
    isZUnexplored = dict.fromkeys(workingGraph.nodes, 1)

    zExplored.add(origin)
    isZExplored[origin] = 1
    for i in workingGraph.nodes:
        if i not in zExplored:
            zUnexplored.add(i)
    Ucopy = zUnexplored.copy()
    Ucopy.add(origin)
    zExploredEmpty = 1
    while zExploredEmpty != 0:
        for j in Ucopy:
            if isZExplored[j] == 1 and j not in zVisited:
                for next in workingGraph.successors(j):
                    if next == destination:
                        reachable = True
                        break
                    else:
                        if next in zUnexplored:
                            zExplored.add(next)
                            zUnexplored.remove(next)
                            isZExplored[next] = 1
                            isZUnexplored[next] = 0
                zVisited.add(j)
                isZVisited[j] = 1
                zExplored.remove(j)
                isZExplored[j] = 0
                if len(zExplored) == 0:
                    zExploredEmpty = 0
                    break
        if reachable:
            break
    return reachable

def findTheMinimalZGraph(ZGraph, clusterGraph, b, u):
    # find the minimal cut
    updatedCluster = nx.DiGraph()
    copyCluster = nx.DiGraph()
    ZGraphCopy = nx.DiGraph()
    updatedCluster = clusterGraph.copy()
    copyCluster = updatedCluster.copy()
    ZGraphCopy = ZGraph.copy()
    # print('Z and cluster ', ZGraph, clusterGraph.nodes())
    for nodeToRemove in ZGraphCopy:
        # print("nodeToRemove=", nodeToRemove)
        updatedCluster.add_node(nodeToRemove)
        edgesToAdd = []
        for node in copyCluster.nodes:
            if (nodeToRemove, node) in GDirected.edges:
                updatedCluster.add_edge(node, nodeToRemove)
                updatedCluster.add_edge(nodeToRemove, node)
                edgesToAdd.append((nodeToRemove, node))
                edgesToAdd.append((node, nodeToRemove))
        if isReachable(updatedCluster, b, u):
            # print("pair ", u, v, "is reachable")
            for node in copyCluster.nodes:
                if (nodeToRemove, node) in updatedCluster.edges:
                    updatedCluster.remove_edge(nodeToRemove, node)
                if (node, nodeToRemove) in updatedCluster.edges:
                    updatedCluster.remove_edge(node, nodeToRemove)
            updatedCluster.remove_node(nodeToRemove)
        else:
            # print("pair ", u, v, "is NOT reachable")
            ZGraph.remove(nodeToRemove)


def addViolatedZcbCut(model, ZGraph, b, u):
    cutBU = LinExpr()
    rhs = 0
    cutBU.addTerms(1, assign[u, b])
    for z in ZGraph:
        cutBU.addTerms(-1, assign[z, b])
    model.cbCut(cutBU.__le__(rhs))
    cutAdded = True
    # print('a new fractional cut for', b, u, cutBU)

def addViolatedZcbLazyCut(model, ZGraph, b, u):
    cutBU = LinExpr()
    rhs = 0
    cutBU.addTerms(1, assign[u, b])
    for z in ZGraph:
        cutBU.addTerms(-1, assign[z, b])
    model.cbLazy(cutBU.__le__(rhs), 2)
    cutAdded = True
    # print('a new integer cut for', b, u, cutBU)


def fractionalCuts(model):
    for b in BSGenerators:
        aVals = dict.fromkeys(GDirected.nodes, 0)
        cutAdded = False
        clusterGraph = nx.DiGraph()
        clusterGraph.add_node(b)
        aVals[b] = 1
        for i in GDirected.nodes:
           if i not in BSGenerators:
                val = model.cbGetNodeRel(assign[i, b])
                if val > 0:
                    clusterGraph.add_node(i)
                    aVals[i] = val
        if len(clusterGraph.nodes) > 1:
            for i in clusterGraph.nodes:
                for j in clusterGraph.nodes:
                    if (i, j) in GDirected.edges:
                        clusterGraph.add_edge(i, j)
                    if (j, i) in GDirected.edges:
                        clusterGraph.add_edge(j, i)
            clusterConnected = isConnected(clusterGraph)
            if clusterConnected:
                # print('CONNECTED FRACTIONAL partition')
                flowGraphForSTCut = nx.DiGraph()
                flowGraphForSTCut.add_node(b)
                flowGraphForSTCut.add_edge(b, str(b)+'prime', capacity=aVals[b])
                for i in GDirected.nodes:
                    if i not in BSGenerators:
                        flowGraphForSTCut.add_node(i)
                        copyI = str(i) + 'prime'
                        flowGraphForSTCut.add_node(copyI)
                        flowGraphForSTCut.add_edge(i,copyI,capacity=aVals[i])
                for (i, j) in clusterGraph.edges:
                    flowGraphForSTCut.add_edge(str(i) + 'prime', j)

                # print('flowGraphForSTCut', flowGraphForSTCut.edges())
                for sink in clusterGraph.nodes:
                    if sink != b and (b, sink) not in clusterGraph.edges:
                        ZSet = set()
                        # solve the min-cut problem to obtain a partition
                        cut_value, partition = nx.minimum_cut(flowGraphForSTCut, b, sink)
                        reachable, non_reachable = partition
                        # print("S reachable", reachable)
                        for node in reachable:
                            # if node in clusterGraph and node != b:
                            if node != b and node in GDirected.nodes:
                                ZSet.add(node)
                        # findTheMinimalZGraph(ZSet, clusterGraph, b, sink) # activate if you prefer to go for the minimal Z, might be expensive
                        addViolatedZcbCut(model, ZSet, b, sink)
                        cutAdded = True
                        if cutAdded:
                            break
            else:
                for u in clusterGraph.nodes:
                    if u != b and (u, b) not in clusterGraph.edges and (b, u) not in clusterGraph.edges:
                        if not isReachable(clusterGraph, u, b):
                            ZGraph = set()
                            for n in GDirected.nodes:
                                if n != u and n != b and n not in clusterGraph.nodes and n not in BSGenerators:
                                    ZGraph.add(n)
                            # print('Z before minimal',ZGraph)
                            # findTheMinimalZGraph(ZGraph, clusterGraph, b, u) # activate if you prefer to go for the minimal Z, might be expensive
                            # print('Z  minimal', ZGraph)
                            addViolatedZcbCut(model, ZGraph, b, u)
                            cutAdded = True
                        if cutAdded:
                            break

def addPartitionCuts(model, where):
    if addFractionalCutsOption == True:
        if where == GRB.Callback.MIPNODE:
            statusNode = model.cbGet(GRB.Callback.MIPNODE_STATUS)
            if statusNode == GRB.OPTIMAL:
                depth = model.cbGet(GRB.Callback.MIPNODE_NODCNT)
                if depth == 0: # only at the root node, otherwise might be expensive
                    fractionalCuts(model)

    if where == GRB.Callback.MIPSOL:
        for b in BSGenerators:
            cutAdded = False
            # construct the cluster of BS b
            clusterGraph = nx.DiGraph()
            clusterGraph.add_node(b)
            for i in GDirected.nodes:
                if i not in BSGenerators:
                    val = model.cbGetSolution(assign[i, b])
                    if val >= 0.999:
                        clusterGraph.add_node(i)
            if len(clusterGraph.nodes) > 1:
                for i in clusterGraph.nodes:
                    for j in clusterGraph.nodes:
                        if (i,j) in GDirected.edges:
                            clusterGraph.add_edge(i, j)
                        if (j,i) in GDirected.edges:
                            clusterGraph.add_edge(j, i)
                #  if the cluster is disconnected
                if not isConnected(clusterGraph):
                    for u in clusterGraph.nodes:
                        if u != b and (u, b) not in clusterGraph.edges and (b, u) not in clusterGraph.edges:
                            if not isReachable(clusterGraph, b, u):
                                ZGraph = set()
                                for n in GDirected.nodes:
                                    if n != u and n != b and n not in clusterGraph.nodes and n not in BSGenerators:
                                        ZGraph.add(n)
                                # print('Z before minimal', ZGraph)
                                findTheMinimalZGraph(ZGraph, clusterGraph, b, u)
                                # print('minimal Z', ZGraph)
                                addViolatedZcbLazyCut(model, ZGraph, b, u)
                                cutAdded = True
                            if cutAdded:
                                break
                        # if cutAdded:
                        #     break
            # if cutAdded:
            #     break

model.optimize(addPartitionCuts)


modelStatus = model.Status
timeFinal = time.time()
timeAlgo = timeFinal - time1
totalTime = timeFinal - time0
print("model status=", modelStatus)
print("solving time=", timeAlgo)
print('total time=', totalTime)

if modelStatus == GRB.INFEASIBLE or modelStatus == GRB.TIME_LIMIT:
    print('No solution found because the model is ', modelStatus)
else:
    UB = model.objVal
    def drawSolution():
        # print and draw each cluster network
        for b in BSGenerators:
            bCluster = set()
            bCluster.add(b)
            arcIn = []
            arcIn.clear()
            for i in GDirected.nodes:
                if i not in BSGenerators:
                    if assign[i,b].x > 0.5:
                        bCluster.add(i)
                        # print(i, b, assign[i,b].x)
            print(bCluster)
            for i in bCluster:
                for j in bCluster:
                    if (i,j) in GDirected.edges:
                        if not arcIn.__contains__((i, j)):
                            arcIn.append((i, j))
            Gname0 = 'G'
            Gname1 = str(len(GDirected.nodes))
            Gname2 = str(b)
            Gname3 = '-sol.png'
            Gname = Gname0 + Gname1 + Gname2 + Gname3
            print(Gname)
            GN = nx.DiGraph()
            print(arcIn)
            for (i, j) in GDirected.edges:
                if arcIn.__contains__((i, j)):
                    GN.add_edge(i, j, weight=100)
            color_map = []
            n_shape = []
            labeldict = {}
            counter = 1
            positions = nx.spring_layout(GN, seed=3)  # positions for all nodes - seed for reproducibility
            for node in GN:
                # positions[node] = (counter % 20, counter*2)
                counter += 1
                if node in BSGenerators:
                    color_map.append('green')
                    n_shape.append("d")
                    labeldict[node] = '{:.0f}'.format(node)
                if node in NBSGenerators:
                    color_map.append('blue')
                    n_shape.append("s")
                    labeldict[node] = '{:.0f}'.format(node)
                if node in criticalNodes:
                    color_map.append('red')
                    n_shape.append("s")
                    labeldict[node] = '{:.0f}'.format(node)
                if node in transNodes:
                    color_map.append('orange')
                    n_shape.append("o")
                    labeldict[node] = '{:.0f}'.format(node)
            nx.draw(GN, node_color=color_map, pos=positions, labels=labeldict, node_shape='o', with_labels=True,
                    node_size=20, font_size=5, width=0.1)
            plt.savefig(OUTPUT_DIR/'solutionFigures'/Gname, dpi=600)
            plt.show()
    # drawSolution()


    # print('algo time=', timeAlgo)
    print('objective value=', UB)
    print('total time=', totalTime)
    print('best proven LB=', LB)

