# This is where the network reduction rules are implemented.
# The default implementations are for single radius models. For multiple radius models, choose the multiple radius versions.
# For descriptions and further methodological details, refer to Calik et al. (2026)

from parallelPowerSystemRestoration.parameterAndSetCreation import *

def networkReduction():
    # only for single-radius methods. For multi-radius methods, use the multiRadius versions
    # computeDegreesOf(GForPower, degreeOfGForPower)  # compute the node degrees for GForPower
    computeDegreesOf(G, degreeOfG)  # compute the node degrees for G
    print('lengths of NBS, CL, components, TR, transI and componentsForPower before reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))

    d1num = 0
    d2num = 0
    for v in G.nodes():
        if degreeOfG[v] == 1:
            d1num += 1
        if degreeOfG[v] == 2:
            d2num += 1
    print('number of leaf nodes in G', d1num)
    print('number of deg-2 nodes in G', d2num)

    # Rule 1: all transshipment nodes with degree one can be removed
    print('eliminating single degree transshipment nodes')
    removeLeafTRNodes(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)
    d1num = 0
    d2num = 0
    for v in G.nodes():
        if degreeOfG[v] == 1:
            d1num += 1
        if degreeOfG[v] == 2:
            d2num += 1
    print('number of leaf nodes in G', d1num)
    print('number of deg-2 nodes in G', d2num)

    # Rule 2: all transshipment nodes with degree two can be removed
    print('eliminating double degree transshipment nodes')
    removeDegree2TRNodes(G, degreeOfG)
    # computeDegreesOf(G, degreeOfG) # not necessary after removing degree-2 nodes since the node degrees remain the same

    # Rules for leaf CLs
    rulesForLeafCLs(G, degreeOfG)

    rulesForLeafNBSs(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    deeperLeafNBSRules(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    if areComponentsConnected(G):
        print("Connected")
    else:
        print("Not Connected")
    print('********** BS generators ********************************', BSForPowerConstraints)
    print('componentsForPower', componentsForPowerConstraints)
    print('NBSForPower', NBSForPowerConstraints)
    print('CLs', CLsForPowerConstraints)
    print('radius set', radiusSet)
    print('transI', transI)
    print('total non transI TR nodes ', len(transNodes) - len(transI))
    print('Number of nodes and edges after network reduction:', G.number_of_nodes(), G.number_of_edges())
    print('lengths of NBS, CL, component, TR, transI and componentsForPower after reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def networkReductionMultipleRadius():
    computeDegreesOf(GForPowerConstraints, degreeOfGForPower)  # compute degrees for GForPower
    computeDegreesOf(G, degreeOfG)  # compute degrees for G
    print('lengths of NBS, CL, components, TR, transI and componentsForPower before reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))

    d1num = 0
    d2num = 0
    for v in G.nodes():
        if degreeOfG[v] == 1:
            d1num += 1
        if degreeOfG[v] == 2:
            d2num += 1
    print('number of leaf nodes in G', d1num)
    print('number of deg-2 nodes in G', d2num)

    # Rule 1: all transshipment nodes with degree one can be removed
    print('eliminating single degree transshipment nodes')
    removeLeafTRNodes(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)
    d1num = 0
    d2num = 0
    for v in G.nodes():
        if degreeOfG[v] == 1:
            d1num += 1
        if degreeOfG[v] == 2:
            d2num += 1
    print('number of leaf nodes in G', d1num)
    print('number of deg-2 nodes in G', d2num)

    # Rule 2: all transshipment nodes with degree two can be removed
    print('eliminating double degree transshipment nodes')
    removeDegree2TRNodes(G, degreeOfG)
    # computeDegreesOf(G, degreeOfG) # not necessary after removing degree-2 nodes since the node degrees remain the same

    # Rules for leaf CLs
    rulesForLeafCLsMultiRadius(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    rulesForLeafNBSsMultiRadius(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    if areComponentsConnected(G) == True:
        print("Connected")
    else:
        print("Not Connected")

    print('********** BS generators ********************************', BSForPowerConstraints)
    print('componentsForPower', componentsForPowerConstraints)
    print('NBSForPower', NBSForPowerConstraints)
    print('CLs', CLsForPowerConstraints)
    print('radius set', radiusSet)
    print('transI', transI)
    print('total non transI TR nodes ', len(transNodes) - len(transI))
    print('Number of nodes and edges after network reduction:', G.number_of_nodes(), G.number_of_edges())
    print('lengths of NBS, CL, component, TR, transI and componentsForPower after reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def networkReductionMultipleRadiusBookkeeping():
    computeDegreesOf(GForPowerConstraints, degreeOfGForPower)  # compute degrees for GForPower
    computeDegreesOf(G, degreeOfG)  # compute degrees for G
    print('lengths of NBS, CL, components, TR, transI and componentsForPower before reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))

    d1num = 0
    d2num = 0
    for v in G.nodes():
        if degreeOfG[v] == 1:
            d1num += 1
        if degreeOfG[v] == 2:
            d2num += 1
    print('number of leaf nodes in G', d1num)
    print('number of deg-2 nodes in G', d2num)

    # Rule 1: all transshipment nodes with degree one can be removed
    print('eliminating single degree transshipment nodes')
    removeLeafTRNodes(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)
    d1num = 0
    d2num = 0
    for v in G.nodes():
        if degreeOfG[v] == 1:
            d1num += 1
        if degreeOfG[v] == 2:
            d2num += 1
    print('number of leaf nodes in G', d1num)
    print('number of deg-2 nodes in G', d2num)

    # Rule 2: all transshipment nodes with degree two can be removed
    print('eliminating double degree transshipment nodes')
    removeDegree2TRNodes(G, degreeOfG)
    # computeDegreesOf(G, degreeOfG) # not necessary after removing degree-2 nodes since the node degrees remain the same

    # Rules for leaf CLs
    rulesForLeafCLsMultiRadius(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    rulesForLeafNBSsMultiRadius(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    bookkeeping(G, degreeOfG)

    if areComponentsConnected(G) == True:
        print("Connected")
    else:
        print("Not Connected")
    print('********** BS generators ********************************', BSForPowerConstraints)
    print('componentsForPower', componentsForPowerConstraints)
    print('nbsForPower', NBSForPowerConstraints)
    print('criticals', CLsForPowerConstraints)
    print('radius set', radiusSet)
    print('transI', transI)
    print('total non transI transnodes ', len(transNodes) - len(transI))
    print('Number of nodes and edges after network reduction:', G.number_of_nodes(), G.number_of_edges())
    print('lengths of NBS, CL, components, TR, transI and componentsForPower after reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def networkReductionBookkeeping():
    computeDegreesOf(GForPowerConstraints, degreeOfGForPower)  # compute degrees for GForPower
    computeDegreesOf(G, degreeOfG)  # compute degrees for G
    print('lengths of NBS, CL, components, TR, transI and componentsForPower before reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))

    d1num = 0
    d2num = 0
    for v in G.nodes():
        if degreeOfG[v] == 1:
            d1num += 1
        if degreeOfG[v] == 2:
            d2num += 1
    print('number of leaf nodes in G', d1num)
    print('number of deg-2 nodes in G', d2num)

    # Rule 1: all transshipment nodes with degree one can be removed
    print('eliminating single degree transshipment nodes')
    removeLeafTRNodes(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)
    d1num = 0
    d2num = 0
    for v in G.nodes():
        if degreeOfG[v] == 1:
            d1num += 1
        if degreeOfG[v] == 2:
            d2num += 1
    print('number of leaf nodes in G', d1num)
    print('number of deg-2 nodes in G', d2num)

    # Rule 2: all transshipment nodes with degree two can be removed
    print('eliminating double degree transshipment nodes')
    removeDegree2TRNodes(G, degreeOfG)
    # computeDegreesOf(G, degreeOfG) # not necessary after removing degree-2 nodes since the node degrees remain the same

    # Rules for leaf CLs
    rulesForLeafCLs(G, degreeOfG)

    rulesForLeafNBSs(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    deeperLeafNBSRules(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    bookkeeping(G, degreeOfG)

    if areComponentsConnected(G) == True:
        print("Connected")
    else:
        print("Not Connected")
    print('********** BS generators ********************************', BSForPowerConstraints)
    print('componentsForPower', componentsForPowerConstraints)
    print('nbsForPower', NBSForPowerConstraints)
    print('criticals', CLsForPowerConstraints)
    print('radius set', radiusSet)
    print('transI', transI)
    print('total non transI transnodes ', len(transNodes) - len(transI))
    print('Number of nodes and edges after network reduction:', G.number_of_nodes(), G.number_of_edges())
    print('lengths of NBS, CL, components, TR, transI and componentsForPower after reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def networkReductionTROnly():
    computeDegreesOf(GForPowerConstraints, degreeOfGForPower)  # compute degrees for GForPower
    computeDegreesOf(G, degreeOfG)  # compute degrees for G
    print('lengths of NBS, CL, components, TR, transI and componentsForPower before reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))

    # Rule 1: all transshipment nodes with degree one can be removed
    print('eliminating single degree transshipment nodes')
    removeLeafTRNodes(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    # Rule 2: all transshipment nodes with degree two can be removed
    print('eliminating double degree transshipment nodes')
    removeDegree2TRNodes(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)  # not necessary after removing degree-2 nodes since the node degrees remain the same

    if areComponentsConnected(G) == True:
        print("Connected")
    else:
        print("Not Connected")
    print('********** BS generators ********************************', BSForPowerConstraints)
    print('componentsForPower', componentsForPowerConstraints)
    print('nbsForPower', NBSForPowerConstraints)
    print('criticals', CLsForPowerConstraints)
    print('transI', transI)
    print('total non transI transnodes ', len(transNodes) - len(transI))
    print('Number of nodes and edges after network reduction:', G.number_of_nodes(), G.number_of_edges())
    print('lengths of NBS, CL, components, TR, transI and componentsForPower after reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def networkReductionTRCLOnly():
    computeDegreesOf(GForPowerConstraints, degreeOfGForPower)  # compute degrees for GForPower
    computeDegreesOf(G, degreeOfG)  # compute degrees for G
    print('lengths of NBS, CL, components, TR, transI and componentsForPower before reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))

    # Rule 1: all transshipment nodes with degree one can be removed
    print('eliminating single degree transshipment nodes')
    removeLeafTRNodes(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    # Rule 2: all transshipment nodes with degree two can be removed
    print('eliminating double degree transshipment nodes')
    removeDegree2TRNodes(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)  # not necessary after removing degree-2 nodes since the node degrees remain the same

    # Rules for leaf CLs
    rulesForLeafCLs(G, degreeOfG)


    if areComponentsConnected(G) == True:
        print("Connected")
    else:
        print("Not Connected")
    print('********** BS generators ********************************', BSForPowerConstraints)
    print('componentsForPower', componentsForPowerConstraints)
    print('nbsForPower', NBSForPowerConstraints)
    print('criticals', CLsForPowerConstraints)
    print('transI', transI)
    print('total non transI transnodes ', len(transNodes) - len(transI))
    print('Number of nodes and edges after network reduction:', G.number_of_nodes(), G.number_of_edges())
    print('lengths of NBS, CL, components, TR, transI and componentsForPower after reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def networkReductionNoDeepNBS():
    computeDegreesOf(GForPowerConstraints, degreeOfGForPower)  # compute degrees for GForPower
    computeDegreesOf(G, degreeOfG)  # compute degrees for G
    print('lengths of NBS, CL, components, TR, transI and componentsForPower before reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))

    # Rule 1: all transshipment nodes with degree one can be removed
    print('eliminating single degree transshipment nodes')
    removeLeafTRNodes(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    # Rule 2: all transshipment nodes with degree two can be removed
    print('eliminating double degree transshipment nodes')
    removeDegree2TRNodes(G, degreeOfG)
    # computeDegreesOf(G, degreeOfG) # not necessary after removing degree-2 nodes since the node degrees remain the same

    # Rules for leaf CLs
    rulesForLeafCLs(G, degreeOfG)

    # Rules for leaf NBSs
    rulesForLeafNBSs(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    if areComponentsConnected(G) == True:
        print("Connected")
    else:
        print("Not Connected")
    print('********** BS generators ********************************', BSForPowerConstraints)
    print('componentsForPower', componentsForPowerConstraints)
    print('nbsForPower', NBSForPowerConstraints)
    print('criticals', CLsForPowerConstraints)
    print('transI', transI)
    print('total non transI transnodes ', len(transNodes) - len(transI))
    print('Number of nodes and edges after network reduction:', G.number_of_nodes(), G.number_of_edges())
    print('lengths of NBS, CL, components, TR, transI and componentsForPower after reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def networkReductionNoNBS():
    computeDegreesOf(GForPowerConstraints, degreeOfGForPower)  # compute degrees for GForPower
    computeDegreesOf(G, degreeOfG)  # compute degrees for G
    print('lengths of NBS, CL, components, TR, transI and componentsForPower before reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))

    # Rule 1: all transshipment nodes with degree one can be removed
    print('eliminating single degree transshipment nodes')
    removeLeafTRNodes(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    # Rule 2: all transshipment nodes with degree two can be removed
    print('eliminating double degree transshipment nodes')
    removeDegree2TRNodes(G, degreeOfG)
    # computeDegreesOf(G, degreeOfG) # not necessary after removing degree-2 nodes since the node degrees remain the same

    # Rules for leaf CLs
    rulesForLeafCLs(G, degreeOfG)
    computeDegreesOf(G, degreeOfG)

    if areComponentsConnected(G) == True:
        print("Connected")
    else:
        print("Not Connected")
    print('********** BS generators ********************************', BSForPowerConstraints)
    print('componentsForPower', componentsForPowerConstraints)
    print('nbsForPower', NBSForPowerConstraints)
    print('criticals', CLsForPowerConstraints)
    print('transI', transI)
    print('total non transI transnodes ', len(transNodes) - len(transI))
    print('Number of nodes and edges after network reduction:', G.number_of_nodes(), G.number_of_edges())
    print('lengths of NBS, CL, components, TR, transI and componentsForPower after reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))

def computeDegreesOf(graph, degreeOfG):
    tmpGraph = graph.copy()
    for v in tmpGraph.nodes:
        # [busType] = nodes.loc[nodes['Bus'] == v, 'Type']
        degreeOfG[v] = 0
        for u in graph.neighbors(v):
            degreeOfG[v] = degreeOfG[v] + 1
        # print(v, degreeOfG[v], busType)


def removeLeafTRNodes(graph, degreeOfG):
    #  eliminate degree-1 transshipment nodes
    tmpGraph = graph.copy()
    degree1transSet = []
    for i in transNodes:
        if degreeOfG[i] == 1:
            degree1transSet.append(i)
    while len(degree1transSet) >= 1:
        print('eliminating single degree transshipment nodes')
        for v in degree1transSet:
            for j in tmpGraph.neighbors(v):
                if (v, j) in tmpGraph:
                    graph.remove_edge(v, j)
                    tmpGraph.remove_edge(v, j)
                if (j, v) in tmpGraph:
                    graph.remove_edge(j, v)
                    tmpGraph.remove_edge(j, v)
            graph.remove_node(v)
            transNodes.remove(v)
            print('Leaf TR removed', v)

        tmpGraph = graph.copy()
        computeDegreesOf(graph, degreeOfG)
        degree1transSet = []
        for i in transNodes:
            if degreeOfG[i] == 1:
                degree1transSet.append(i)
    print('lengths of NBS, CL, components, TR, transI and componentsForPower after leaf TR reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def removeDegree2TRNodes(graph, degreeOfG):
    #  eliminate degree-2 transshipment nodes
    tmpGraph = graph.copy()
    degree2transSet = []
    for i in transNodes:
        if degreeOfG[i] == 2:
            degree2transSet.append(i)

    for v in degree2transSet:
        # print('---------------------- transshipment node ', v)
        adj1 = -1
        adj2 = -1
        for j in tmpGraph.neighbors(v):
            # print('a neighbor of ', v, ' is ', j)
            if adj1 == -1:
                adj1 = j
            else:
                adj2 = j
        # print('adj1 ', adj1)
        # print('adj2 ', adj2)

        graph.remove_edge(v, adj1)
        graph.remove_edge(v, adj2)
        graph.add_edge(adj1, adj2)
        graph.remove_node(v)
        transNodes.remove(v)
        tmpGraph = graph.copy()
        print('Degree-2 TR removed', v)
        # break

    print('lengths of NBS, CL, components, TR, transI and componentsForPower after degree-2 TR reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def rulesForLeafCLs(graph, degreeOfG):
    tmpGraph = graph.copy()
    degree1CLs = []
    for i in criticalNodes:
        if degreeOfG[i] == 1:
            degree1CLs.append(i)
    while len(degree1CLs) > 0:
        for v in degree1CLs:
            for j in tmpGraph.neighbors(v):
                # if j is a CL
                if j in criticalNodes:
                    print('Leaf CL--- CL ', v, ' merged to CL', j)
                    for t in range(1, timeHorizon + 1):
                        powerOf[j, t] = powerOf[j, t] + powerOf[v, t]
                    graph.remove_edge(v, j)
                    graph.remove_node(v)
                    CLsForPowerConstraints.remove(v)
                    criticalNodes.remove(v)
                    componentsForPowerConstraints.remove(v)
                    allComponents.remove(v)

                # if j is a TR
                if j in transNodes:
                    print('Leaf CL--- TR ', j, ' replaced by CL ', v)
                    for u in tmpGraph.neighbors(j):
                        if u != v:
                            graph.add_edge(u, v)
                        graph.remove_edge(u, j)
                    graph.remove_node(j)
                    transNodes.remove(j)

                # if j is a BS
                if j in BSGenerators:
                    print('Leaf CL--- CL ', v, ' merged to BS  ', j)
                    demandFrom[j, timeHorizon] = demandFrom[j, timeHorizon] + powerOf[v, timeHorizon]
                    graph.remove_edge(v, j)
                    graph.remove_node(v)
                    CLsForPowerConstraints.remove(v)
                    criticalNodes.remove(v)
                    componentsForPowerConstraints.remove(v)
                    allComponents.remove(v)

                # if j is an NBS
                if j in NBSGenerators:
                    print('Leaf CL--- CL ', v, ' merged to NBS  ', j)
                    demandFrom[j, timeHorizon] = demandFrom[j, timeHorizon] + powerOf[v, timeHorizon]
                    graph.remove_edge(v, j)
                    graph.remove_node(v)
                    CLsForPowerConstraints.remove(v)
                    criticalNodes.remove(v)
                    componentsForPowerConstraints.remove(v)
                    allComponents.remove(v)

            tmpGraph = graph.copy()
            computeDegreesOf(graph, degreeOfG)

        degree1CLs = []
        for i in criticalNodes:
            if degreeOfG[i] == 1:
                degree1CLs.append(i)

    print('lengths of NBS, CL, components, TR, transI and componentsForPower after leaf CL reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def rulesForLeafNBSs(graph, degreeOfG):
    tmpGraph = graph.copy()
    leafNBSs = []
    for i in NBSGenerators:
        if degreeOfG[i] == 1:
            for j in tmpGraph.neighbors(i):
                if j not in BSGenerators and j not in NBSGenerators:
                    leafNBSs.append(i)
    while len(leafNBSs) > 0:
        for v in leafNBSs:
            for j in tmpGraph.neighbors(v):
                # if j is a CL
                if j in criticalNodes:
                    print('Leaf NBS ----- CL ', j, ' replaced through merging by NBS ', v)
                    for u in tmpGraph.neighbors(j):
                        if u != v:
                            graph.add_edge(u, v)
                            graph.remove_edge(u, j)
                    graph.remove_node(j)
                    CLsForPowerConstraints.remove(j)
                    criticalNodes.remove(j)
                    componentsForPowerConstraints.remove(j)
                    allComponents.remove(j)
                    demandFrom[v, timeHorizon] = demandFrom[v, timeHorizon] + powerOf[j, timeHorizon]

                # if j is a TR
                if j in transNodes:
                    print('Leaf NBS ----- TR node ', j, ' replaced by NBS ', v)
                    for u in tmpGraph.neighbors(j):
                        if u != v:
                            graph.add_edge(u, v)
                            graph.remove_edge(u, j)
                    graph.remove_node(j)
                    transNodes.remove(j)

            tmpGraph = graph.copy()
            computeDegreesOf(graph, degreeOfG)

        leafNBSs = []
        for i in NBSGenerators:
            if degreeOfG[i] == 1:
                for j in tmpGraph.neighbors(i):
                    if j not in BSGenerators and j not in NBSGenerators:
                        leafNBSs.append(i)

    print('lengths of NBS, CL, components, TR, transI and componentsForPower after leaf NBS reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def rulesForLeafCLsMultiRadius(graph, degreeOfG):
    tmpGraph = graph.copy()
    degree1CLs = []
    for i in criticalNodes:
        if degreeOfG[i] == 1:
            degree1CLs.append(i)
    stopCriterion = False
    while len(degree1CLs) > 0 and stopCriterion == False:
        for v in degree1CLs:
            for j in tmpGraph.neighbors(v):
                # if j is a CL
                if j in criticalNodes:
                    print('Leaf CL--- CL ', v, ' merged to CL', j)
                    for t in range(1, timeHorizon + 1):
                        powerOf[j, t] = powerOf[j, t] + powerOf[v, t]
                    graph.remove_edge(v, j)
                    graph.remove_node(v)
                    CLsForPowerConstraints.remove(v)
                    criticalNodes.remove(v)
                    componentsForPowerConstraints.remove(v)
                    allComponents.remove(v)
                    nonBSNodes.remove(v)

                # if j is a TR
                if j in transNodes:
                    print('Leaf CL--- TR ', j, ' replaced by CL ', v)
                    for u in tmpGraph.neighbors(j):
                        if u != v:
                            graph.add_edge(u, v)
                        graph.remove_edge(u, j)
                    graph.remove_node(j)
                    transNodes.remove(j)
                    nonBSNodes.remove(j)

                if j in BSGenerators or j in NBSGenerators:
                    stopCriterion = True

            tmpGraph = graph.copy()
            computeDegreesOf(graph, degreeOfG)

        degree1CLs = []
        for i in criticalNodes:
            if degreeOfG[i] == 1:
                degree1CLs.append(i)

    print('lengths of NBS, CL, components, TR, transI and componentsForPower after reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def rulesForLeafNBSsMultiRadius(graph, degreeOfG):
    tmpGraph = graph.copy()
    leafNBSs = []
    for i in NBSGenerators:
        if degreeOfG[i] == 1:
            for j in tmpGraph.neighbors(i):
                if j not in BSGenerators and j not in NBSGenerators:
                    leafNBSs.append(i)
    stopCriterion = False
    while len(leafNBSs) > 0 and stopCriterion == False:
        for v in leafNBSs:
            for j in tmpGraph.neighbors(v):
                # if j is a TR
                if j in transNodes:
                    print('Leaf NBS ----- TR node ', j, ' is replaced by NBS ', v)
                    for u in tmpGraph.neighbors(j):
                        if u != v:
                            graph.add_edge(u, v)
                            graph.remove_edge(u, j)
                    graph.remove_node(j)
                    transNodes.remove(j)
                else:
                    stopCriterion = True

            tmpGraph = graph.copy()
            computeDegreesOf(graph, degreeOfG)

        leafNBSs = []
        for i in NBSGenerators:
            if degreeOfG[i] == 1:
                for j in tmpGraph.neighbors(i):
                    if j not in BSGenerators and j not in NBSGenerators:
                        leafNBSs.append(i)

    print('lengths of NBS, CL, components, TR, transI and componentsForPower after reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def deeperLeafNBSRules(graph, degreeOfG):
    tmpGraph = graph.copy()
    stopCriterion = True
    leafNBSAdjacentNBSdeg2 = []
    for leafV in NBSGenerators:
        if degreeOfG[leafV] == 1:
            for neighborV in tmpGraph.neighbors(leafV):
                if neighborV in NBSGenerators and degreeOfG[neighborV] == 2:
                    leafNBSAdjacentNBSdeg2.append(leafV)
                    stopCriterion = False

    print(leafNBSAdjacentNBSdeg2)

    while stopCriterion is False:
        print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=- Deeper Leaf NBS Rules -=-=-=-=-=-=-=-=-=-=-=-=-=-=-')

        for leafV in leafNBSAdjacentNBSdeg2:
            exploredNodes = []
            exploredNodes.append(leafV)
            for neighborV in tmpGraph.neighbors(leafV):
                exploredNodes.append(neighborV)
                if degreeOfG[neighborV] == 2:
                    print('Leaf NBS ', leafV, ' is adjacent to', neighborV, 'with degree', degreeOfG[neighborV])
                    for neighborOfNeighborV in tmpGraph.neighbors(neighborV):
                        print('^', neighborV, ' is adjacent to', neighborOfNeighborV)
                        if neighborOfNeighborV in criticalNodes and neighborOfNeighborV not in exploredNodes:
                            print('^', neighborOfNeighborV, ' is a CL')
                            print('^-------------- CL ', neighborOfNeighborV, ' replaced by adjacent NBS ', neighborV,
                                  ' adjacent to leaf NBS ', leafV)
                            exploredNodes.append(neighborOfNeighborV)
                            for neighborOfNeighborOfNeighborV in tmpGraph.neighbors(neighborOfNeighborV):
                                if neighborOfNeighborOfNeighborV not in exploredNodes:
                                    print('^^', neighborOfNeighborV, ' is adjacent to ', neighborOfNeighborOfNeighborV)
                                    print('^^edge added ', neighborOfNeighborOfNeighborV, neighborV)
                                    graph.add_edge(neighborOfNeighborOfNeighborV, neighborV)
                                    print('^^edge removed ', neighborOfNeighborOfNeighborV, neighborOfNeighborV)
                                    graph.remove_edge(neighborOfNeighborOfNeighborV, neighborOfNeighborV)
                            graph.remove_edge(neighborV, neighborOfNeighborV)
                            print('^edge removed ', neighborV, neighborOfNeighborV)
                            graph.remove_node(neighborOfNeighborV)
                            print('^node removed ', neighborOfNeighborV)
                            CLsForPowerConstraints.remove(neighborOfNeighborV)
                            criticalNodes.remove(neighborOfNeighborV)
                            componentsForPowerConstraints.remove(neighborOfNeighborV)
                            allComponents.remove(neighborOfNeighborV)
                            demandFrom[neighborV, timeHorizon] = demandFrom[neighborV, timeHorizon] + powerOf[
                                neighborOfNeighborV, timeHorizon]

                            tmpGraph = graph.copy()
                            computeDegreesOf(graph, degreeOfG)

                        if neighborOfNeighborV in transNodes and neighborOfNeighborV not in exploredNodes:
                            print('^-------------- TR ', neighborOfNeighborV, ' replaced by adjacent NBS ',
                                  neighborV, ' adjacent to leaf NBS ', leafV)
                            for neighborOfNeighborOfNeighborV in tmpGraph.neighbors(neighborOfNeighborV):
                                if neighborOfNeighborOfNeighborV not in exploredNodes:
                                    print('^^nbd of ', neighborOfNeighborV, ' to process is ',
                                          neighborOfNeighborOfNeighborV)
                                    graph.add_edge(neighborOfNeighborOfNeighborV, neighborV)
                                    print('^^edge added ', neighborOfNeighborOfNeighborV, neighborV)
                                    graph.remove_edge(neighborOfNeighborOfNeighborV, neighborOfNeighborV)
                                    print('^^edge removed ', neighborOfNeighborOfNeighborV, neighborOfNeighborV)
                            graph.remove_edge(neighborV, neighborOfNeighborV)
                            print('^edge removed ', neighborV, neighborOfNeighborV)
                            graph.remove_node(neighborOfNeighborV)
                            print('^node removed ', neighborOfNeighborV)
                            transNodes.remove(neighborOfNeighborV)

                            tmpGraph = graph.copy()
                            computeDegreesOf(graph, degreeOfG)

                        if neighborOfNeighborV in NBSGenerators and neighborOfNeighborV not in exploredNodes:
                            print('^', neighborOfNeighborV, ' is an NBS')
                            print('^degree of ', neighborOfNeighborV, ' is ', degreeOfG[neighborOfNeighborV])
                            if degreeOfG[neighborOfNeighborV] == 2:
                                print('^--------------Deg 2 NBS ', neighborOfNeighborV, ' adjacent to NBS ', neighborV,
                                      ' adjacent to leaf NBS ', leafV)
                                for neighborOfNeighborOfNeighborV in tmpGraph.neighbors(neighborOfNeighborV):
                                    if neighborOfNeighborOfNeighborV not in exploredNodes:
                                        nbsToExplore = neighborOfNeighborV
                                        print('^^nbs to explore ', nbsToExplore)
                                        print('^^current neighbor of ', neighborOfNeighborV, ' is ',
                                              neighborOfNeighborOfNeighborV)
                                        stopcriterion2 = False
                                        while stopcriterion2 == False:
                                            if degreeOfG[neighborOfNeighborV] < 2:
                                                stopcriterion2 = True
                                            else:
                                                for neighborOfNeighborOfNeighborV in tmpGraph.neighbors(nbsToExplore):
                                                    if neighborOfNeighborOfNeighborV not in exploredNodes:
                                                        for u in tmpGraph.neighbors(neighborOfNeighborOfNeighborV):
                                                            print('^^^ neighbors of ', neighborOfNeighborOfNeighborV,
                                                                  ' are ', u)
                                                        print('^^^++++++++++ ', neighborOfNeighborOfNeighborV,
                                                              ' adjacent to nbs ',
                                                              nbsToExplore, ' adjacent to NBS ', neighborV,
                                                              ' adjacent to leaf NBS ', leafV)
                                                        if neighborOfNeighborOfNeighborV in transNodes:
                                                            if degreeOfG[neighborOfNeighborOfNeighborV] > 2:
                                                                stopcriterion2 = True
                                                            print('^^^Leaf NBS ', leafV, '------------------- TR ',
                                                                  neighborOfNeighborOfNeighborV, ' replaced by NBS ',
                                                                  nbsToExplore,
                                                                  ' adjacent to NBS ', neighborV,
                                                                  ' adjacent to leaf NBS ', leafV)
                                                            exploredNodes.append(neighborOfNeighborOfNeighborV)
                                                            for uNbd2 in tmpGraph.neighbors(
                                                                    neighborOfNeighborOfNeighborV):
                                                                print('^^^^nbd of ', neighborOfNeighborOfNeighborV,
                                                                      ' is ', uNbd2)
                                                                if uNbd2 not in exploredNodes:
                                                                    graph.add_edge(uNbd2, nbsToExplore)
                                                                    print('^^^^edge added ', uNbd2, nbsToExplore)
                                                                    graph.remove_edge(uNbd2,
                                                                                      neighborOfNeighborOfNeighborV)
                                                                    print('^^^^edge removed ', uNbd2,
                                                                          neighborOfNeighborOfNeighborV)
                                                            graph.remove_edge(nbsToExplore,
                                                                              neighborOfNeighborOfNeighborV)
                                                            print('^^^edge removed ', nbsToExplore,
                                                                  neighborOfNeighborOfNeighborV)
                                                            graph.remove_node(neighborOfNeighborOfNeighborV)
                                                            print('^^^node removed ', neighborOfNeighborOfNeighborV)
                                                            transNodes.remove(neighborOfNeighborOfNeighborV)

                                                            tmpGraph = graph.copy()
                                                            computeDegreesOf(graph, degreeOfG)

                                                        if neighborOfNeighborOfNeighborV in criticalNodes:
                                                            if degreeOfG[neighborOfNeighborOfNeighborV] > 2:
                                                                stopcriterion2 = True
                                                            print('^^^Leaf NBS ', leafV, '------------------- CL ',
                                                                  neighborOfNeighborOfNeighborV, ' replaced by NBS ',
                                                                  nbsToExplore,
                                                                  ' adjacent to NBS ', neighborV,
                                                                  ' adjacent to leaf NBS ', leafV)

                                                            demandFrom[nbsToExplore, timeHorizon] = demandFrom[
                                                                                                        nbsToExplore, timeHorizon] + \
                                                                                                    powerOf[
                                                                                                        neighborOfNeighborOfNeighborV, timeHorizon]
                                                            exploredNodes.append(neighborOfNeighborOfNeighborV)
                                                            for uNbd2 in tmpGraph.neighbors(
                                                                    neighborOfNeighborOfNeighborV):
                                                                print('^^^^nbd of ', neighborOfNeighborOfNeighborV,
                                                                      ' is ', uNbd2)
                                                                if uNbd2 not in exploredNodes:
                                                                    print('^^^^edge added ', uNbd2, nbsToExplore)
                                                                    graph.add_edge(uNbd2, nbsToExplore)
                                                                    print('^^^^edge removed ', uNbd2,
                                                                          neighborOfNeighborOfNeighborV)
                                                                    graph.remove_edge(uNbd2,
                                                                                      neighborOfNeighborOfNeighborV)
                                                            graph.remove_edge(nbsToExplore,
                                                                              neighborOfNeighborOfNeighborV)
                                                            print('^^^edge removed ', nbsToExplore,
                                                                  neighborOfNeighborOfNeighborV)
                                                            graph.remove_node(neighborOfNeighborOfNeighborV)
                                                            print('^^^node removed ', neighborOfNeighborOfNeighborV)
                                                            CLsForPowerConstraints.remove(neighborOfNeighborOfNeighborV)
                                                            criticalNodes.remove(neighborOfNeighborOfNeighborV)
                                                            componentsForPowerConstraints.remove(
                                                                neighborOfNeighborOfNeighborV)
                                                            allComponents.remove(neighborOfNeighborOfNeighborV)
                                                            print('^^^ nbsToExplore =', nbsToExplore)

                                                            tmpGraph = graph.copy()
                                                            computeDegreesOf(graph, degreeOfG)

                                                        if neighborOfNeighborOfNeighborV in NBSGenerators:
                                                            print('^^^next node', neighborOfNeighborOfNeighborV,
                                                                  'is an NBS with degree ',
                                                                  degreeOfG[neighborOfNeighborOfNeighborV])
                                                            if degreeOfG[neighborOfNeighborOfNeighborV] > 2:
                                                                stopcriterion2 = True
                                                            else:
                                                                nbsToExplore = neighborOfNeighborOfNeighborV
                                                                exploredNodes.append(neighborOfNeighborOfNeighborV)

                                                        if neighborOfNeighborOfNeighborV in BSGenerators:
                                                            stopcriterion2 = True
                                                            print(
                                                                '^^^ &&&&&&&&&&&&&&&&&&&&&&&&&&&.  bs generator reached &&&&&&&&&&&&&&&&&&&&&&&&&&&')

                        if neighborOfNeighborV in BSGenerators:
                            stopCriterion = True
                            print(' &&&&&&&&&&&&&&&&&&&&&&&&&&&.  bs generator reached &&&&&&&&&&&&&&&&&&&&&&&&&&&')
                            print('the following nodes ', exploredNodes, 'nust connect to BS', neighborOfNeighborV)

                else:
                    if neighborV in NBSGenerators:
                        print('degree of ', neighborV, 'is', degreeOfG[neighborV])
                        stopCriterion = True
                        break

        tmpGraph = graph.copy()
        computeDegreesOf(graph, degreeOfG)
        for i in NBSGenerators:
            if degreeOfG[i] == 1:
                deg2 = False
                for neighborV in tmpGraph.neighbors(i):
                    if neighborV in NBSGenerators and degreeOfG[neighborV] == 2:
                        for neighborOfNeighborV in tmpGraph.neighbors(neighborV):
                            if neighborOfNeighborV not in BSGenerators:
                                deg2 = True
                if deg2 and i not in leafNBSAdjacentNBSdeg2:
                    leafNBSAdjacentNBSdeg2.append(i)
        print(leafNBSAdjacentNBSdeg2)

    print('lengths of NBS, CL, components, TR, transI and componentsForPower after leaf TR reduction', len(NBSGenerators),
          len(criticalNodes), len(allComponents), len(transNodes), len(transI), len(componentsForPowerConstraints))


def bookkeeping(G, degreeOfG):
    setToCheck = allComponents.copy()
    tmpSetToCheck = setToCheck.copy()
    for v in tmpSetToCheck:
        if degreeOfG[v] == 1:
            [busType] = nodes.loc[nodes['Bus'] == v, 'Type']
            for (i, j) in G.edges:
                if j == v:
                    G.remove_edge(i, v)
                    if v in componentsForPowerConstraints:
                        forcedConnectionOfG[v] = i
                        if i in transNodes and i not in transI:
                            transI.append(i)
                    if v in transI:
                        forcedConnectionOfG[v] = i
                        if i in transNodes and i not in transI:
                            transI.append(i)
                    # if v in transNodes and v not in transI:
                    #     print('transshipment node not essential for any component')
                if i == v:
                    G.remove_edge(v, j)
                    if v in componentsForPowerConstraints:
                        forcedConnectionOfG[v] = j
                        if j in transNodes and j not in transI:
                            transI.append(j)
                    if v in transI:
                        forcedConnectionOfG[v] = j
                        if j in transNodes and j not in transI:
                            transI.append(j)
                    # if v in transNodes and v not in transI:
                    #     print('transshipment node not essential for any component')

            G.remove_node(v)
            if v in allComponents:
                allComponents.remove(v)
            if v in transNodes and v not in transI:
                transNodes.remove(v)
                GForPowerConstraints.remove_node(v)
            if v in NBSGenerators:
                NBSGenerators.remove(v)
            if v in criticalNodes:
                criticalNodes.remove(v)
            if v in transI:
                transI.remove(v)
            print("%%%%%%%%%% node ", v, busType, " has degree 1 only, hence removed: forcedConnection: ",
                  forcedConnectionOfG[v])
    print("%%%%%%%%%%%% transI size and elements", len(transI), transI)


def areComponentsConnected(graph) -> bool:
    copyThisGraph = nx.DiGraph()
    for node in graph.nodes():
        copyThisGraph.add_node(node)
    for (u, v) in graph.edges:
        copyThisGraph.add_edge(u, v)
        copyThisGraph.add_edge(v, u)
    clusterConnected = True
    # connectivity check with an algorithm
    explored = set()
    unexplored = set()
    visited = set()
    isVisited = dict.fromkeys(copyThisGraph.nodes, 0)
    isExplored = dict.fromkeys(copyThisGraph.nodes, 0)
    isUnexplored = dict.fromkeys(copyThisGraph.nodes, 1)

    for i in copyThisGraph.nodes:
        unexplored.add(i)
    randomNode = unexplored.pop()
    explored.add(randomNode)
    isExplored[randomNode] = 1

    exploredEmpty = 1
    while len(unexplored) >= 1 and exploredEmpty == 1:
        # as long as there are unexplored nodes or disconnectivity detected
        for j in copyThisGraph.nodes:
            if isExplored[j] == 1 and j not in visited:
                for v in copyThisGraph.successors(j):
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
            print("**************** Disconnected cluster ID, edges", copyThisGraph.edges)
            for v in unexplored:
                [busType] = nodes.loc[nodes['Bus'] == v, 'Type']
                print('unreachable node and its type:', v, busType)
                if busType == 'CL' or busType == 'NBS':
                    clusterConnected = False
                if busType == 'BS':
                    print("Isolated BS, the cluster is assumed connected")
                if busType == 'Trans':
                    print("Isolated Trans, the cluster is assumed connected")
    return clusterConnected
