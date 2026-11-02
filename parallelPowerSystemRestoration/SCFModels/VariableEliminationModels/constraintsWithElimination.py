from parallelPowerSystemRestoration.SCFModels.VariableEliminationModels.decisionVariablesWithElimination import *

# objective functions
def defineObjective(model):
    ## Objective: minimize the latest starting time=radius
    obj = LinExpr()
    for r in radius_set:
        obj.addTerms(r, radius[r])
    model.setObjective(obj, GRB.MINIMIZE)
    print("objective: minimize the latest starting time=radius")

def pickOneRadius(model):
    ### Pick one radius
    oneRadius = LinExpr()
    for r in radius_set:
        oneRadius.addTerms(1, radius[r])
    model.addConstr(oneRadius.__eq__(1), name='oneRadius')
    print("radius constraints")

def startBeforeTheSelectedRadiusHeuristic(model):
    ### at least one start before the selected radius
    for i in NBSForPowerConstraints:
        for r in radius_set:
            atLeastOneStartBeforeRadius = LinExpr()
            for b in BSForPowerConstraints:
                for t in range(1, r + 1):
                    if feasibleStartArray[b, i, t]:
                        atLeastOneStartBeforeRadius.addTerms(1, start[b, i, t])
            for m in radius_set:
                if m <= r:
                    atLeastOneStartBeforeRadius.addTerms(-1, radius[m])
            model.addConstr(atLeastOneStartBeforeRadius.__ge__(0), name='atLeastOneStart(%g.%g)' % (i, r))
    # for c in criticalNodesForPower:
    #     for r in radius_set:
    #         atLeastOneStartBeforeRadius = LinExpr()
    #         for b in bsForPower:
    #             for t in range(LB, r + 1):
    #                 if feasibleStartArray[b, c, t]:
    #                     atLeastOneStartBeforeRadius.addTerms(1, start[b, c, t])
    #         for m in radius_set:
    #             if m <= r:
    #                 atLeastOneStartBeforeRadius.addTerms(-1, radius[m])
    #         model.addConstr(atLeastOneStartBeforeRadius.__ge__(0), name='atLeastOneStart(%g.%g)' % (c, r))
    print("at least one start")

def forcedAssignmentForEliminatedComponents(model):
    singleDegreeNum = 0
    ### if a single degree component, they go together
    # for i in GForPower.nodes:
    # if degreeOfGForPower[i] == 1:
    for i in componentsForPowerConstraints:
        if forcedConnectionOfG[i] != -1:
            singleDegreeNum = singleDegreeNum + 1
            j = forcedConnectionOfG[i]
            for b in BSForPowerConstraints:
                singleCon = LinExpr()
                singleCon.addTerms(1,assign[i,b])
                singleCon.addTerms(-1, assign[j, b])
                model.addConstr(singleCon.__eq__(0), name='singleDegree(%s,%s)' %(i,j))
    for i in transNodes:
        if forcedConnectionOfG[i] != -1:
            singleDegreeNum = singleDegreeNum + 1
            j = forcedConnectionOfG[i]
            for b in BSForPowerConstraints:
                singleCon = LinExpr()
                singleCon.addTerms(1, assign[i, b])
                singleCon.addTerms(-1, assign[j, b])
                model.addConstr(singleCon.__eq__(0), name='singleDegree(%s,%s)' % (i, j))
    for i in transI:
        if forcedConnectionOfG[i] != -1:
            singleDegreeNum = singleDegreeNum + 1
            j = forcedConnectionOfG[i]
            for b in BSForPowerConstraints:
                singleCon = LinExpr()
                singleCon.addTerms(1, assign[i, b])
                singleCon.addTerms(-1, assign[j, b])
                model.addConstr(singleCon.__eq__(0), name='singleDegree(%s,%s)' % (i, j))

    print("number of single degree nodes in the power graph:", singleDegreeNum)

def assignments(model):
    #  network partition assignments
    for gen in BSForPowerConstraints:
        bsAssignment = LinExpr()
        bsAssignment.addTerms(1, assign[gen, gen])
        model.addConstr(bsAssignment.__eq__(1), name='BSAssignment(%s)' % gen)

    for gen in BSForPowerConstraints:
        for gen2 in BSForPowerConstraints:
            if gen2 != gen:
                bsAssignment2 = LinExpr()
                bsAssignment2.addTerms(1, assign[gen2, gen])
                model.addConstr(bsAssignment2.__eq__(0), name='BSAssignment2(%s,%s)' % (gen2, gen))
    print("Assignment of BSs")

    for v in componentsForPowerConstraints:
        componentAssigment = LinExpr()
        for gen in BSForPowerConstraints:
            componentAssigment.addTerms(1, assign[v,gen])
        model.addConstr(componentAssigment.__eq__(1), name='componentAssignment(%s)' % v)
    print("Assignment of components")

    for v in transI:
        componentAssigment = LinExpr()
        for gen in BSForPowerConstraints:
            componentAssigment.addTerms(1, assign[v,gen])
        model.addConstr(componentAssigment.__eq__(1), name='transIAssignment(%s)' % v)
    print("TransI assignment")

    for v in transNodes:
        transAssignment = LinExpr()
        for gen in BSForPowerConstraints:
            transAssignment.addTerms(1, assign[v,gen])
        model.addConstr(transAssignment.__eq__(1), name='transAssignment(%s)' % v)
    print("Assignment of transshipment nodes")

def outgoingFlow(model):
    ### Flow from i = X
    for b in BSGenerators:
        for i in allComponents:
            outgoing = LinExpr()
            outgoing.addTerms(-1, assign[i, b])
            for (u, v) in G.edges():
                if u == i:
                    outgoing.addTerms(1, flow[u, v, b])
                if v == i:
                    outgoing.addTerms(-1, flow[u, v, b])
            model.addConstr(outgoing.__eq__(0), name='outgoingFLowI(%s,%s)' % (i, b))

    for b in BSGenerators:
        for i in transI:
            outgoing = LinExpr()
            outgoing.addTerms(-1, assign[i, b])
            for (u, v) in G.edges():
                if u == i:
                    outgoing.addTerms(1, flow[u, v, b])
                if v == i:
                    outgoing.addTerms(-1, flow[u, v, b])
            model.addConstr(outgoing.__eq__(0), name='outgoingFLowTransI(%s,%s)' % (i, b))

def flowAtTrans(model):
    ### Flow conservative at transshipment nodes
    for j in BSGenerators:
        for i in transNodes:
            if i not in transI:
                conservation = LinExpr()
                for (u, v) in G.edges():
                    if u == i:
                        conservation.addTerms(1, flow[u, v, j])
                    if v == i:
                        conservation.addTerms(-1, flow[u, v, j])
                model.addConstr(conservation.__eq__(0), name='intermediateFlow(%s,%s)' % (i, j))

def incomingFlow(model):
    ### Flow Value into j = sum of X
    for b in BSGenerators:
        incoming = LinExpr()
        for i in allComponents:
            incoming.addTerms(-1, assign[i, b])
        for i in transI:
            incoming.addTerms(-1, assign[i, b])
        for (u, v) in G.edges():
            if u == b:
                incoming.addTerms(-1, flow[u, v, b])
            if v == b:
                incoming.addTerms(1, flow[u, v, b])
        model.addConstr(incoming.__eq__(0), name='incomingFlow(%s)' % b)

def flowCapacity(model):
    ### Flow Capacity on Edge
    numberDemandPoint = len(allComponents) + len(transI)
    for j in BSGenerators:
        for (u,v) in G.edges():
            edgeCap = LinExpr()
            edgeCap.addTerms(1,flow[u,v,j])
            edgeCap.addTerms(-numberDemandPoint,y[u,v,j])
            model.addConstr(edgeCap.__le__(0), name='flowCapUB(%s,%s,%s)'%(u,v,j))

    for j in BSGenerators:
        for (u, v) in G.edges():
            edgeCap = LinExpr()
            edgeCap.addTerms(1, flow[u, v, j])
            edgeCap.addTerms(numberDemandPoint, y[u, v, j])
            model.addConstr(edgeCap.__ge__(0), name='flowCapLB(%s,%s,%s)' % (u, v, j))

def linkingXY(model):
    ### Node Capacity on Edge
    for b in BSGenerators:
        for (u, v) in G.edges():
            linking1 = LinExpr()
            linking1.addTerms(1, y[u, v, b])
            linking1.addTerms(-1,assign[u, b])
            model.addConstr(linking1.__le__(0), name='linkingXY1(%s,%s,%s)' % (u, v, b))

    for b in BSGenerators:
        for (u, v) in G.edges():
            linking2 = LinExpr()
            linking2.addTerms(1, y[u, v, b])
            linking2.addTerms(-1,assign[v, b])
            model.addConstr(linking2.__le__(0), name='linkingXY2(%s,%s,%s)' % (u, v, b))

def startTimeSelectionHeuristic(model):
    ## Start Time Selection Constraints
    for b in BSForPowerConstraints:
        for i in NBSForPowerConstraints:
            startInTheAssignedNBS = LinExpr()
            startInTheAssignedNBS.addTerms(-1, assign[i, b])
            for t in range(1,timeHorizon + 1):
                if feasibleStartArray[b, i, t]:
                    startInTheAssignedNBS.addTerms(1,start[b, i, t])
            model.addConstr(startInTheAssignedNBS.__eq__(0), name='Eq.startTimeSelection(%s,%s)'%(b, i))
    for b in BSForPowerConstraints:
        for c in CLsForPowerConstraints:
            startInTheAssignedCL = LinExpr()
            startInTheAssignedCL.addTerms(-1, assign[c, b])
            for t in range(LB,timeHorizon + 1):
                if feasibleStartArray[b, c, t]:
                    startInTheAssignedCL.addTerms(1, start[b, c, t])
            model.addConstr(startInTheAssignedCL.__eq__(0), name='Eq.startTimeSelection(%s,%s)'%(b, c))



def netPowerHeuristic(model):
    ## Power Aggregation Constraints
    for b in BSForPowerConstraints:
        for t in range(1,timeHorizon + 1):
            rhs =  -(powerOutputBS[b,t] + demandFrom[b,t])
            netPower = LinExpr()
            for i in NBSForPowerConstraints:
                for earlierT in range(1,t+1):
                    relationT = t - earlierT + 1
                    if feasibleStartArray[(b, i, earlierT)] == 1:
                        netPower.addTerms(powerOf[i, relationT], start[b, i, earlierT])
                        netPower.addTerms(demandFrom[i, timeHorizon], start[b, i, earlierT])

            if t >= LB:
                for i in CLsForPowerConstraints:
                    for earlierT in range(LB,t+1):
                        relationT = t - earlierT + 1
                        if feasibleStartArray[(b, i, earlierT)] == 1:
                            netPower.addTerms(powerOf[i, relationT], start[b, i, earlierT])
            # if t >= LB:
            #     for i in criticalNodesForPower:
            #         for earlierT in range(LB, t + 1):
            #             if feasibleStartArray[(b, i, earlierT)] == 1:
            #                 relationT = t - earlierT + 1
            #                 netPower.addTerms(powerOf[i,relationT] + demandFrom[i,t],start[b, i, earlierT])
            model.addConstr(netPower.__ge__(rhs), name='Eq(netPower)(%s,%s)'%(b,t))

def startTimeSelectionSingleRadiusHeuristic(model):
    ## Start Time Selection Constraints
    for b in BSForPowerConstraints:
        for i in NBSForPowerConstraints:
            startInTheAssignedNBS = LinExpr()
            startInTheAssignedNBS.addTerms(-1, assign[i, b])
            for t in range(1,timeHorizon + 1):
                if feasibleStartArray[b, i, t]:
                    startInTheAssignedNBS.addTerms(1,start[b, i, t])
            model.addConstr(startInTheAssignedNBS.__eq__(0), name='Eq.startTimeSelection(%s,%s)'%(b, i))
            model.update()
            # print(startInTheAssignedNBS.__eq__(0))

def netPowerSingleRadiusHeuristic(model):
    ## Power Aggregation Constraints
    for b in BSForPowerConstraints:
        for t in range(1,timeHorizon + 1):
            rhs = -(powerOutputBS[b,t] + demandFrom[b,t])
            netPower = LinExpr()
            for i in NBSForPowerConstraints:
                for earlierT in range(1,t+1):
                    if feasibleStartArray[(b, i, earlierT)] == 1:
                        relationT = t - earlierT + 1
                        netPower.addTerms(powerOf[i, relationT], start[b, i, earlierT])
                        if t == timeHorizon:
                            netPower.addTerms(demandFrom[i, timeHorizon], start[b, i, earlierT])
            if t == timeHorizon:
                for i in CLsForPowerConstraints:
                    if feasibleStartArray[(b, i, t)] == 1:
                        netPower.addTerms(powerOf[i,timeHorizon],assign[i, b])
            model.addConstr(netPower.__ge__(rhs), name='Eq(netPower)(%s,%s)'%(b,t))

def startCLsLastPeriodHeuristic(model):
    ### one start for each component
    for i in CLsForPowerConstraints:
        for k in radius_set:
            startLate = LinExpr()
            startLate.addTerms(-1,radius[k])
            for b in BSForPowerConstraints:
                if feasibleStartArray[b, i, k]:
                    startLate.addTerms(1, start[b, i, k])
            model.addConstr(startLate.__eq__(0), name='startLate(%g,%g)' % (i, k))
            model.update()
            # print("CL", i, "radius",k, startLate)
        # for t in range(1, LB):
        #     startCL = LinExpr()
        #     for b in bsGenerators:
        #         startCL.addTerms(1, start[b, i, t])
        #     model.addConstr(startCL.__eq__(0), name='startLate(%g,%g)' % (i, t))
    print("start CLs late")

#  implied or valid inequalities
def startEachComponentHeuristic(model):
    ### one start for each component
    for i in NBSForPowerConstraints:
        oneStartPerComponent = LinExpr()
        for b in BSForPowerConstraints:
            for t in range(1, timeHorizon + 1):
                oneStartPerComponent.addTerms(1, start[b, i, t])
        model.addConstr(oneStartPerComponent.__eq__(1), name='atMostOneStart(%g)' % i)
    print("one start and one island per I")

# valid inequalities
def noIsolatedComponent(model):
    ### one preceding node should be in the same island (or one preceding or succeeding node)
    for i in componentsForPowerConstraints:
        for b in BSForPowerConstraints:
            if (b, i) not in GForPowerConstraints.edges:
                noIsolatedNode = LinExpr()
                noIsolatedNode.addTerms(1, assign[i, b])
                for (u,v) in GForPowerConstraints.edges:
                    if u == i:
                        noIsolatedNode.addTerms(-1, assign[v, b])
                    if v == i and u not in BSForPowerConstraints:
                        noIsolatedNode.addTerms(-1, assign[u, b])
                model.addConstr(noIsolatedNode.__le__(0))
    for i in transNodes:
        for b in BSForPowerConstraints:
            if (b, i) not in GForPowerConstraints.edges:
                noIsolatedNode = LinExpr()
                noIsolatedNode.addTerms(1, assign[i, b])
                for (u, v) in GForPowerConstraints.edges:
                    if u == i:
                        noIsolatedNode.addTerms(-1, assign[v, b])
                    if v == i and u not in BSForPowerConstraints:
                        noIsolatedNode.addTerms(-1, assign[u, b])
                model.addConstr(noIsolatedNode.__le__(0))
    print("no isolated component")

def noIsolatedComponentWithPowerNodesOnly(model):
    ### one preceding node should be in the same island (or one preceding or succeeding node)
    for i in componentsForPowerConstraints:
        for b in BSForPowerConstraints:
            if (b, i) not in GForPowerConstraints.edges:
                noIsolatedNode = LinExpr()
                noIsolatedNode.addTerms(1, assign[i, b])
                for (u,v) in GForPowerConstraints.edges:
                    if u == i:
                        noIsolatedNode.addTerms(-1, assign[v, b])
                    if v == i and u not in BSForPowerConstraints:
                        noIsolatedNode.addTerms(-1, assign[u, b])
                model.addConstr(noIsolatedNode.__le__(0))
    for i in transNodes:
        for b in BSForPowerConstraints:
            if (b, i) not in GForPowerConstraints.edges:
                noIsolatedNode = LinExpr()
                noIsolatedNode.addTerms(1, assign[i, b])
                for (u, v) in GForPowerConstraints.edges:
                    if u == i:
                        noIsolatedNode.addTerms(-1, assign[v, b])
                    if v == i and u not in BSForPowerConstraints:
                        noIsolatedNode.addTerms(-1, assign[u, b])
                model.addConstr(noIsolatedNode.__le__(0))
    print("no isolated component")



def triangleSubClusters(model):
    triangledNeighbors = []
    nodesToDeleteFromPower = []
    for v in G.nodes:
        if degreeOfG[v]==2:
            counter = 0
            nbd1 = -1
            nbd2 = -1
            for j in G.neighbors(v):
                # print('neighbor of ', v, 'is', j)
                if counter==0:
                    nbd1 = j
                if counter==1:
                    nbd2 = j
                if degreeOfG[j] == 2:
                    for u in G.neighbors(j):
                        if u != v:

                           if u == nbd1:
                               print('~~~~~~~~~~~~~~~ triangled neighbors ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                               print('neighbor of ', v, 'is', j, 'and neighbor of ', j, 'is', u, 'that is also neighbor of ', v)
                               triangle = []
                               triangle.append(v)
                               triangle.append(j)
                               triangle.append(u)
                               sortedTriangle = sorted(triangle)
                               if not triangledNeighbors.__contains__(sortedTriangle):
                                   triangledNeighbors.append(sortedTriangle)

                               if v not in nodesToDeleteFromPower:
                                   print('degree of ', v, 'is', degreeOfG[v], ' will be deleted')
                                   print('power graph degree of ', v, 'is', degreeOfGForPower[v], ' will be deleted')
                                   nodesToDeleteFromPower.append(v)
                               if j not in nodesToDeleteFromPower:
                                   print('power graph degree of ', j, 'is', degreeOfGForPower[j], ' will be deleted')
                                   nodesToDeleteFromPower.append(j)
                           if u == nbd2:
                                triangle = []
                                triangle.append(v)
                                triangle.append(j)
                                triangle.append(u)
                                sortedTriangle = sorted(triangle)
                                if not triangledNeighbors.__contains__(sortedTriangle):
                                    triangledNeighbors.append(sortedTriangle)
                                if v not in nodesToDeleteFromPower:
                                    nodesToDeleteFromPower.append(v)
                                if j not in nodesToDeleteFromPower:
                                    nodesToDeleteFromPower.append(j)
                                print(
                                    '~~~~~~~~~~~~~~~ triangled neighbors ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                                print('neighbor of ', v, 'is', j, 'and neighbor of ', j, 'is', u,
                                      'that is also neighbor of ', v)
                                print(
                                    '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                counter+=1

    print('size of the power network', len(GForPowerConstraints.nodes()), len(GForPowerConstraints.edges()))
    for v in nodesToDeleteFromPower:
        if v in BSForPowerConstraints:
            print('node ', v, 'is a BS')
        if v in NBSForPowerConstraints:
            NBSForPowerConstraints.remove(v)
            print('node ', v, 'is being deleted from nbsForPower')
        if v in CLsForPowerConstraints:
            CLsForPowerConstraints.remove(v)
            print('node ', v, 'is being deleted from criticalNodesForPower')

    print('size of the power network', len(GForPowerConstraints.nodes()), len(GForPowerConstraints.edges()))
    for triangle in triangledNeighbors:
        for b in BSGenerators:
            for u in triangle:
                for v in triangle:
                    if u < v:
                        sameIsland = LinExpr()
                        sameIsland.addTerms(1, assign[u, b])
                        sameIsland.addTerms(-1, assign[v, b])
                        model.addConstr(sameIsland.__eq__(0), name='sameIsland(%g)' % b)
                        model.update()
                        print(sameIsland)
    print("triangled islands")


def fixAssignments(model):

    # for b in bsForPower:
    #     for j in G.neighbors(b):
    #         if degreeOfG[j] > 2:
    #             assignFeasible = True
    #             for u in G.neighbors(j):
    #                 if u != b and u in bsForPower:
    #                     assignFeasible = False
    #             if assignFeasible:
    #                 assignJToB = LinExpr()
    #                 assignJToB.addTerms(1, assign[j, b])
    #                 model.addConstr(assignJToB.__eq__(1))
    #                 model.update()
    #                 print(assignJToB)
    cutAdded = 0
    for b in BSForPowerConstraints:
        if degreeOfG[b] == 1:
            for j in G.neighbors(b):
                assignJToB = LinExpr()
                assignJToB.addTerms(1, assign[j, b])
                model.addConstr(assignJToB.__eq__(1))
                model.update()
                print(assignJToB)
        if degreeOfG[b] >=2:
            for j in G.neighbors(b):
                if degreeOfG[j] >= 2:
                    assignFeasible = True
                    for u in G.neighbors(j):
                        if u != b and u in BSForPowerConstraints:
                            assignFeasible = False
                    if assignFeasible:
                        assignJToB = LinExpr()
                        assignJToB.addTerms(1, assign[j, b])
                        model.addConstr(assignJToB.__eq__(1))
                        model.update()
                        print(assignJToB)
                        cutAdded += 1
                        # break
        if cutAdded > len(BSForPowerConstraints):
            break
    # fix86 = LinExpr()
    # fix86.addTerms(1, assign[86, 31])
    # model.addConstr(fix86.__eq__(1))
    # model.update()
    # print(fix86)
    for b in BSForPowerConstraints:
        for j in G.neighbors(b):
            if degreeOfG[j] == 1:
                assignJToB = LinExpr()
                assignJToB.addTerms(1, assign[j, b])
                model.addConstr(assignJToB.__eq__(1))
                model.update()
                print(assignJToB)

    print("````~~~~~~~§§§§§§§§§§§§§ adding a heuristic cut to assign degree-2 neighbors of a BS to that BS no §§§§§§§§§§§§§§§§``````~~~")

def defineObjectiveLatest(model):
    ## Objective: maximize suprlus capacity
    obj = LinExpr()
    for b in BSForPowerConstraints:
        for i in allComponents:
            obj.addTerms(powerOf[i, 1], assign[i, b])
        for t in range(1, timeHorizon + 1):
            for v in NBSForPowerConstraints:
                obj.addTerms(t*(-1*powerOf[v,1]), start[b, v, t])
    model.setObjective(obj, GRB.MAXIMIZE)