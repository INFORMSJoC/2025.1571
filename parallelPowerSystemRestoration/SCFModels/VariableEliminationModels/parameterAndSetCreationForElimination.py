# This is where all input files are read,
# most global parameters and variables are created,
# and variable elimination is performed
# Any additional preprocessing procedure can be included here
import networkx as nx
import pandas as pd
import time
import datetime
from pathlib import Path

# Go from the current file to the project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]

NODES_DIR = PROJECT_ROOT / "input"/ "nodes"
LINES_DIR = PROJECT_ROOT / "input"/ "lines"
OUTPUT_DIR = PROJECT_ROOT / "output"

# the number of periods available in the input files determine 'timeHorizon'.
# This can be different for different files.
timeHorizon = 20
# lower bound LB and upper bound UB on the optimal value. LB, UB and timeHorizon must be identical for single radius formulations
LB = 20
UB = timeHorizon

# to load the input files for a network, uncomment a 'lines' and a 'nodes' file

# lines = pd.read_csv(LINES_DIR/'lines_30.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_30.csv')
# lines = pd.read_csv(LINES_DIR/'lines_57.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_57.csv')
lines = pd.read_csv(LINES_DIR/'lines_118.csv')
nodes = pd.read_csv(NODES_DIR/'nodes_118_sorted.csv')
# lines = pd.read_csv(LINES_DIR/'lines_200.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_200.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_300_indexed.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_300_indexed_cap48point49.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_300_nonidenticalpower.csv')
# lines = pd.read_csv(LINES_DIR/'lines_300.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_500_sorted.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_500_nonidenticalpower.csv')
# lines = pd.read_csv(LINES_DIR/'lines_500.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_1354_sorted_indexed.csv')
# lines = pd.read_csv(LINES_DIR/'lines_1354.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_1888_sorted.csv')
# lines = pd.read_csv(LINES_DIR/'lines_1888.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_1951_sorted.csv')
# lines = pd.read_csv(LINES_DIR/'lines_1951.csv')
# nodes = pd.read_csv(NODES_DIR/'nodes_2383_sorted.csv')
# lines = pd.read_csv(LINES_DIR/'lines_2383.csv')

#  define the sets and graphs to be used for the power constraints
BSForPowerConstraints = []
NBSForPowerConstraints = []
componentsForPowerConstraints = []
CLsForPowerConstraints = []


#  define the sets to be used for the reduced graphs
BSGenerators = []
NBSGenerators = []
allComponents = []
criticalNodes = []
nonBSNodes = []
transNodes = []
transI = []
radius_set = []
periodSet = []
tupleNodeTime = []

bsTime = []

primaryNBSsPerBS = [] # NBSs that can start with only one BS
secondaryNBSsPerBS = [] # NBSs that cannot be started with a single BS power hence needs another NBS to start first
nodeTuples = []


maxBSpower = 0
feasibleStartTimesPerBS = []

#  variables
radius = {}
assign = {}
flow = {}
y = {}
start = {}

GForPowerConstraints = nx.Graph()
GForPowerOriginal = nx.Graph()
G = nx.Graph()
initialValue = 0
initialValue2 = -1
powerOf = dict.fromkeys(tupleNodeTime, initialValue)  # power output components
demandFrom = dict.fromkeys(tupleNodeTime, initialValue)  # power output components
powerOutputBS = dict.fromkeys(bsTime, initialValue)  # power output BSs
degreeOfG = dict.fromkeys(G.nodes, initialValue)  # degree components
degreeOfGForPower = dict.fromkeys(GForPowerConstraints.nodes, initialValue)  # degree components
forcedConnectionOfG = dict.fromkeys(GForPowerConstraints.nodes, initialValue2)
# primaryNBS_BS = dict.fromkeys(nodeTuples, initialValue)  # degree components initialValue)  #
minCrankingTime_BS = dict.fromkeys(BSGenerators, initialValue2)
earliestCrankingNBS_BS = dict.fromkeys(BSGenerators, initialValue2)
feasibleStartArray = dict.fromkeys(nodeTuples, 0)  # degree components initialValue)  #

def initialize():
    fillSets(nodes, BSGenerators, BSForPowerConstraints, allComponents, componentsForPowerConstraints, nonBSNodes, NBSGenerators, NBSForPowerConstraints, criticalNodes,
             CLsForPowerConstraints, transNodes)
    fillNetwork(lines, G, GForPowerConstraints, BSGenerators)
    computeParameters(nodes, LB, UB, radius_set, timeHorizon, periodSet, componentsForPowerConstraints,
                      BSForPowerConstraints, powerOutputBS, powerOf, tupleNodeTime, bsTime)

def eliminationInitialize():
    variableElimination(primaryNBSsPerBS, secondaryNBSsPerBS, minCrankingTime_BS, earliestCrankingNBS_BS, feasibleStartTimesPerBS, nodeTuples, feasibleStartArray)


def fillSets(nodes, BSGenerators, BSForPower, components, componentsForPower, nonBSNodes, NBSGenerators, NBSForPower, criticalNodes, CLsForPowerConstraints, transNodes):
    for v in nodes['Bus']:
        [busType] = nodes.loc[nodes['Bus'] == v, 'Type']
        if busType == 'BS':
            BSGenerators += [v]
            BSForPower += [v]
        if busType == 'NBS':
            components += [v]
            componentsForPower += [v]
            nonBSNodes += [v]
            NBSGenerators += [v]
            NBSForPower += [v]
        if busType == 'CL':
            components += [v]
            componentsForPower += [v]
            nonBSNodes += [v]
            criticalNodes += [v]
            CLsForPowerConstraints += [v]
        if busType == 'Trans':
            transNodes += [v]
            nonBSNodes += [v]

def fillNetwork(lines, G, GForPower, bsGenerators):
    for l in lines['Line']:
        [Source] = lines.loc[lines['Line'] == l, 'Source']
        [Target] = lines.loc[lines['Line'] == l, 'Target']
        GForPowerOriginal.add_edge(Source, Target)
        interBSLink = False
        if Source in bsGenerators and Target in bsGenerators:
            interBSLink = True
        if not interBSLink:
            G.add_edge(Source, Target)
            GForPower.add_edge(Source, Target)
    print('Number of nodes in the original power, reduced power and reduced design graphs:', GForPowerOriginal.number_of_nodes(), GForPower.number_of_nodes(), G.number_of_nodes())

def computeParameters(nodes, LB, UB, radius_set, timeHorizon, periodSet, componentsForPower, BSForPower, powerOutputBS,
                      powerOf, tupleNodeTime, bsTime):
    for r in range(LB, UB + 1):
        radius_set += [r]
    for t in range(1, timeHorizon + 1):
        periodSet += [t]
    for i in componentsForPower:
        for t in range(1, timeHorizon + 1):
            tupleNodeTime += [i, t]
    for b in BSForPower:
        for t in range(1, timeHorizon + 1):
            bsTime += [b, t]
        # for j in nbsForPower:
        #     nodeTuples.append(b, j)
    maxBSpower = 0
    for b in BSForPower:
        for t in range(1, timeHorizon + 1):
            periodName = "period%s" % t
            [value] = nodes.loc[nodes['Bus'] == b, periodName]
            powerOutputBS[b, t] = value
            if value > maxBSpower:
                maxBSpower = value
            demandFrom[b, t] = 0
    for i in componentsForPower:
        for t in range(1, timeHorizon + 1):
            periodName = "period%s" % t
            [value] = nodes.loc[nodes['Bus'] == i, periodName]
            powerOf[i, t] = value
            demandFrom[i, t] = 0
            # print('demand from i at period ', i, t)
            # print("power of %s at %s" % (i, t), powerOf[i, t])
    for v in GForPowerConstraints.nodes:
        forcedConnectionOfG[v] = -1

def variableElimination(primaryNBSsPerBS, secondaryNBSsPerBS, minCrankingTimePerBS, earliestCrankingNBSPerBS, feasibleStartTimesPerBS, nodeTuples, feasibleStartArray):
    for b in BSForPowerConstraints:
        for i in NBSForPowerConstraints:
            for t in range(1, timeHorizon + 1):
                nodeTuples += [b, i, t]
                feasibleStartArray[(b, i, t)] = 0
        for i in CLsForPowerConstraints:
            for t in range(1, timeHorizon):
                nodeTuples += [b, i, t]
                if LB == timeHorizon:
                    feasibleStartArray[(b, i, t)] = 0
                if LB < timeHorizon:
                    feasibleStartArray[(b, i, t)] = 1
            nodeTuples += [b, i, timeHorizon]
            feasibleStartArray[(b, i, timeHorizon)] = 1

    candidateNBSsToBeCL = []
    notCL = []
    for b in BSForPowerConstraints:
        minCrankTime = timeHorizon
        minCrankNBS = -1
        for j in NBSForPowerConstraints:
            if abs(powerOf[j, 1]) > powerOutputBS[b, timeHorizon]:
                secondaryNBSsPerBS += [(b, j)]
                # print('secondary NBS for BS', b, j)
            else:
                primaryNBSsPerBS += [(b, j)]
                # print('primary NBS for BS', b, j)
                [cTime] = nodes.loc[nodes['Bus'] == j, 'Cranking Time (5 min)']
                for t in range(1, timeHorizon + 1):
                    if abs(powerOf[j, 1]) <= powerOutputBS[b, t]:
                        # feasibleStartArray[(b, j, t)] = 1
                        cTime = cTime + t
                        break
                if cTime < minCrankTime:
                    minCrankTime = cTime
                    minCrankNBS = j
                    # print('crank time for BS', b, j, cTime, minCrankTime)
        minCrankingTimePerBS[b] = minCrankTime
        earliestCrankingNBSPerBS[b] = minCrankNBS
        # print('min crank time for BS', b, minCrankTime)
        # print('earlies cranking NBS for BS', b, minCrankNBS)

        for j in NBSForPowerConstraints:
            if (b, j) in primaryNBSsPerBS:
                [cTime] = nodes.loc[nodes['Bus'] == j, 'Cranking Time (5 min)']
                timeUntilGeneration = cTime + 1
                if timeUntilGeneration > timeHorizon:
                    print('NBS', j, 'does not generate early enough in BS', b,
                          'since its  cranking time is', cTime)
                    for t in range(1, timeHorizon + 1):
                        if abs(powerOf[j, 1]) <= powerOutputBS[b, t]:
                            feasibleStartArray[(b, j, t)] = 1

                    if j not in candidateNBSsToBeCL:
                        candidateNBSsToBeCL.append(j)

                else:
                    if j not in notCL:
                        notCL.append(j)
                    for t in range(1, timeHorizon + 1):
                        if abs(powerOf[j, 1]) <= powerOutputBS[b, t]:
                            feasibleStartTimesPerBS += [(b, j, t)]
                            feasibleStartArray[(b, j, t)] = 1



            else:
                if (b, j) in secondaryNBSsPerBS:
                    [cTime] = nodes.loc[nodes['Bus'] == j, 'Cranking Time (5 min)']
                    timeUntilGeneration = cTime + minCrankingTimePerBS[b] + 2
                    if timeUntilGeneration > timeHorizon:
                        print('NBS', j, 'is secondary and does not generate early enough in BS', b,
                              'since its earliest cranking is', minCrankingTimePerBS[b], 'and cranking time is', cTime)
                        # feasibleStartTimes_BS += [(b, j, timeHorizon)]
                        # feasibleStartArray [(b, j, timeHorizon)] = 1
                        for t in range(minCrankTime + 1, timeHorizon + 1):
                            feasibleStartTimesPerBS += [(b, j, t)]
                            feasibleStartArray[(b, j, t)] = 1

                        if j not in candidateNBSsToBeCL:
                            candidateNBSsToBeCL.append(j)

                    else:
                        if j not in notCL:
                            notCL.append(j)
                        for t in range(minCrankTime, timeHorizon + 1):
                            feasibleStartTimesPerBS += [(b, j, t)]
                            feasibleStartArray[(b, j, t)] = 1

    tmpNBS = NBSForPowerConstraints.copy()
    print("candidate NBSs to be CL", candidateNBSsToBeCL)
    for j in candidateNBSsToBeCL:
        if j not in notCL:
            NBSGenerators.remove(j)
            NBSForPowerConstraints.remove(j)
            criticalNodes.append(j)
            CLsForPowerConstraints.append(j)
            print(criticalNodes)
            print(NBSForPowerConstraints)
            for t in range(1, timeHorizon + 1):
                powerOf[j, t] = powerOf[j, 1]
            print('NBS', j, 'becomes a CL')
            if LB == timeHorizon:
                for b in BSForPowerConstraints:
                    for t in range(1, timeHorizon):
                        feasibleStartArray[(b, j, t)] = 0
    # for j in criticalNodesForPower:
    #     for b in bsForPower:
    #         for t in range(1, timeHorizon+1):
    #             print("feasibleStartArray", b, j, t, '=', feasibleStartArray[(b, j, t)])







