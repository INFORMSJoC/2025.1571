# define the objective function and the constraints for the PPSR formulations
# first select and define the variables needed and/or desired for the constraints and objective functions
from parallelPowerSystemRestoration.decisionVariables import *


# objective functions
def defineObjective(model):
    # Objective: minimize the latest starting time=radius
    obj = LinExpr()
    for r in radiusSet:
        obj.addTerms(r, radius[r])
    model.setObjective(obj, GRB.MINIMIZE)
    print("objective: minimize the latest starting time=radius")


#   constraints, valid inequalities and optimality cuts
def pickOneRadius(model):
    # Pick one radius
    oneRadius = LinExpr()
    for r in radiusSet:
        oneRadius.addTerms(1, radius[r])
    model.addConstr(oneRadius.__eq__(1), name='oneRadius')
    print("pick one radius")


def startBeforeTheSelectedRadius(model):
    # at least one start before the selected radius
    for i in NBSForPowerConstraints:
        for r in radiusSet:
            atLeastOneStartBeforeRadius = LinExpr()
            for b in BSForPowerConstraints:
                for t in range(1, r + 1):
                    atLeastOneStartBeforeRadius.addTerms(1, start[b, i, t])
            for m in radiusSet:
                if m <= r:
                    atLeastOneStartBeforeRadius.addTerms(-1, radius[m])
            model.addConstr(atLeastOneStartBeforeRadius.__ge__(0), name='atLeastOneStart(%g.%g)' % (i, r))
    for c in CLsForPowerConstraints:
        for r in radiusSet:
            atLeastOneStartBeforeRadius = LinExpr()
            for b in BSForPowerConstraints:
                for t in range(LB, r + 1):
                    atLeastOneStartBeforeRadius.addTerms(1, start[b, c, t])
            for m in radiusSet:
                if m <= r:
                    atLeastOneStartBeforeRadius.addTerms(-1, radius[m])
            model.addConstr(atLeastOneStartBeforeRadius.__ge__(0), name='atLeastOneStart(%g.%g)' % (c, r))
    print("at least one start")


def forcedAssignmentForEliminatedComponents(model):
    singleDegreeNum = 0
    # if a single degree component, they go together
    # for i in GForPower.nodes:
    # if degreeOfGForPower[i] == 1:
    for i in componentsForPowerConstraints:
        if forcedConnectionOfG[i] != -1:
            singleDegreeNum = singleDegreeNum + 1
            j = forcedConnectionOfG[i]
            for b in BSForPowerConstraints:
                singleCon = LinExpr()
                singleCon.addTerms(1, assign[i, b])
                singleCon.addTerms(-1, assign[j, b])
                model.addConstr(singleCon.__eq__(0), name='singleDegree(%s,%s)' % (i, j))
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
            componentAssigment.addTerms(1, assign[v, gen])
        model.addConstr(componentAssigment.__eq__(1), name='componentAssignment(%s)' % v)
    print("Assignment of components")

    for v in transI:
        componentAssigment = LinExpr()
        for gen in BSForPowerConstraints:
            componentAssigment.addTerms(1, assign[v, gen])
        model.addConstr(componentAssigment.__eq__(1), name='transIAssignment(%s)' % v)
    print("TransI assignment")

    for v in transNodes:
        transAssignment = LinExpr()
        for gen in BSForPowerConstraints:
            transAssignment.addTerms(1, assign[v, gen])
        model.addConstr(transAssignment.__eq__(1), name='transAssignment(%s)' % v)
    print("Assignment of transshipment nodes")


def outgoingFlow(model):
    # Flow from i = X
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
    # Flow conservative at transshipment nodes
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
    # Flow Value into j = sum of X
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
    # Flow Capacity on Edge
    numberDemandPoint = len(allComponents) + len(transI)
    for j in BSGenerators:
        for (u, v) in G.edges():
            edgeCap = LinExpr()
            edgeCap.addTerms(1, flow[u, v, j])
            edgeCap.addTerms(-numberDemandPoint, arc[u, v, j])
            model.addConstr(edgeCap.__le__(0), name='flowCapUB(%s,%s,%s)' % (u, v, j))

    for j in BSGenerators:
        for (u, v) in G.edges():
            edgeCap = LinExpr()
            edgeCap.addTerms(1, flow[u, v, j])
            edgeCap.addTerms(numberDemandPoint, arc[u, v, j])
            model.addConstr(edgeCap.__ge__(0), name='flowCapLB(%s,%s,%s)' % (u, v, j))


def linkingXY(model):
    # Node Capacity on Edge
    for b in BSGenerators:
        for (u, v) in G.edges():
            linking1 = LinExpr()
            linking1.addTerms(1, arc[u, v, b])
            linking1.addTerms(-1, assign[u, b])
            model.addConstr(linking1.__le__(0), name='linkingXY1(%s,%s,%s)' % (u, v, b))

    for b in BSGenerators:
        for (u, v) in G.edges():
            linking2 = LinExpr()
            linking2.addTerms(1, arc[u, v, b])
            linking2.addTerms(-1, assign[v, b])
            model.addConstr(linking2.__le__(0), name='linkingXY2(%s,%s,%s)' % (u, v, b))


def startTimeSelection(model):
    # Start Time Selection Constraints
    for b in BSForPowerConstraints:
        for i in NBSForPowerConstraints:
            NBSstartInTheAssignedIsland = LinExpr()
            NBSstartInTheAssignedIsland.addTerms(-1, assign[i, b])
            for t in range(1, timeHorizon + 1):
                NBSstartInTheAssignedIsland.addTerms(1, start[b, i, t])
            model.addConstr(NBSstartInTheAssignedIsland.__eq__(0), name='startTimeSelection(%s,%s)' % (b, i))
    for b in BSForPowerConstraints:
        for c in CLsForPowerConstraints:
            CLstartInTheAssignedIsland = LinExpr()
            CLstartInTheAssignedIsland.addTerms(-1, assign[c, b])
            for t in range(LB, timeHorizon + 1):
                CLstartInTheAssignedIsland.addTerms(1, start[b, c, t])
            model.addConstr(CLstartInTheAssignedIsland.__eq__(0), name='startTimeSelection(%s,%s)' % (b, c))


def netPower(model):
    # Net power constraints
    for b in BSForPowerConstraints:
        for t in range(1, timeHorizon + 1):
            rhs = -(powerOutputFromBS[b, t] + demandFrom[b, t])  # if any CL or NBS is merged to b
            netPower = LinExpr()
            for i in NBSForPowerConstraints:
                for startPeriod in range(1, t + 1):
                    timeSinceTheStart = t - startPeriod + 1
                    netPower.addTerms(powerOf[i, timeSinceTheStart], start[b, i, startPeriod])
                    if t == timeHorizon:
                        netPower.addTerms(demandFrom[i, timeHorizon], start[b, i, startPeriod])
            if t >= LB:
                for i in CLsForPowerConstraints:
                    for startPeriod in range(LB, t + 1):
                        timeSinceTheStart = t - startPeriod + 1
                        netPower.addTerms(powerOf[i, timeSinceTheStart] + demandFrom[i, t], start[b, i, startPeriod])
            model.addConstr(netPower.__ge__(rhs), name='netPower(%s,%s)' % (b, t))


def startTimeSelectionSingleRadius(model):
    # Select a start time for each NBS
    for b in BSForPowerConstraints:
        for i in NBSForPowerConstraints:
            startInTheAssignedNBS = LinExpr()
            startInTheAssignedNBS.addTerms(-1, assign[i, b])
            for t in range(1, timeHorizon + 1):
                startInTheAssignedNBS.addTerms(1, start[b, i, t])
            model.addConstr(startInTheAssignedNBS.__eq__(0), name='startTimeSelection(%s,%s)' % (b, i))
            model.update()


def netPowerSingleRadius(model):
    # Net power constraints
    for b in BSForPowerConstraints:
        for t in range(1, timeHorizon + 1):
            rhs = -(powerOutputFromBS[b, t] + demandFrom[b, t])
            netPower = LinExpr()
            for i in NBSForPowerConstraints:
                for startPeriod in range(1, t + 1):
                    timeSinceTheStart = t - startPeriod + 1
                    netPower.addTerms(powerOf[i, timeSinceTheStart], start[b, i, startPeriod])
                    if t == timeHorizon:
                        netPower.addTerms(demandFrom[i, timeHorizon], start[b, i, startPeriod])
            if t == timeHorizon:
                for i in CLsForPowerConstraints:
                    netPower.addTerms(powerOf[i, timeHorizon], assign[i, b])
            model.addConstr(netPower.__ge__(rhs), name='netPower(%s,%s)' % (b, t))


def startCLsLastPeriod(model):
    # start CLs in the last period
    for i in CLsForPowerConstraints:
        for k in radiusSet:
            startLate = LinExpr()
            startLate.addTerms(-1, radius[k])
            for b in BSForPowerConstraints:
                startLate.addTerms(1, start[b, i, k])
            model.addConstr(startLate.__eq__(0), name='startLate(%g,%g)' % (i, k))
    print("start CLs late")


#  implied or valid inequalities
def startEachComponent(model):
    # one start for each NBS
    for i in NBSForPowerConstraints:
        oneStartPerComponent = LinExpr()
        for b in BSForPowerConstraints:
            for t in range(1, timeHorizon + 1):
                oneStartPerComponent.addTerms(1, start[b, i, t])
        model.addConstr(oneStartPerComponent.__eq__(1), name='atMostOneStart(%g)' % i)
    print("one start and one island per I")


# valid inequalities
def noIsolatedComponent(model):
    # one preceding node should be in the same island (or one preceding or succeeding node)
    for i in componentsForPowerConstraints:
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


def defineObjectiveLatest(model):
    # Objective: maximize suprlus capacity
    obj = LinExpr()
    for b in BSForPowerConstraints:
        for i in allComponents:
            obj.addTerms(powerOf[i, 1], assign[i, b])
        for t in range(1, timeHorizon + 1):
            for v in NBSForPowerConstraints:
                obj.addTerms(t * (-1 * powerOf[v, 1]), start[b, v, t])
    model.setObjective(obj, GRB.MAXIMIZE)
