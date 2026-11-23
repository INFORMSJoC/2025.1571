# define the objective function and the constraints for the GSS formulations
# first select and define the variables needed and desired for the constraints and objective functions

from parallelPowerSystemRestoration.GSSModels.decisionVariablesGSS import *


# variable definitions
def defineVariablesGSS(model, LB, timeHorizon):
    # select the variables needed and desired
    radiusVars(model)
    startVarsGSS(model, LB, timeHorizon)


def defineSingleRadiusVariablesGSS(model, timeHorizon):
    # select the variables needed and desired here
    startVarsSingleRadiusGSS(model, timeHorizon)


def defineRelaxedSingleRadiusVariablesGSS(model, timeHorizon):
    # select the variables needed and desired here
    continuousStartVarsSingleRadiusGSS(model, timeHorizon)


def defineSingleRadiusVariablesGSSWithAuxiliaryVariables(model, timeHorizon):
    # select the variables needed and desired here
    startVarsSingleRadiusGSS(model, timeHorizon)
    auxiliaryVariablesGSS(model, timeHorizon)


# objective functions
def defineObjective(model):
    # Objective: minimize the latest starting time=radius
    obj = LinExpr()
    for r in radiusSet:
        obj.addTerms(r, radius[r])
    model.setObjective(obj, GRB.MINIMIZE)
    print("objective: minimize the latest starting time=radius")


def defineObjectiveWithAuxiliaries(model, timeHorizon):
    objAux = LinExpr()
    for t in range(1, timeHorizon + 1):
        objAux.addTerms(t, auxiliary[t])
    model.setObjective(objAux, GRB.MINIMIZE)
    print("objective: minimize the sum of auxiliary variables")


#   constraints, valid inequalities and optimality cuts
def pickOneRadius(model):
    # Pick one radius
    oneRadius = LinExpr()
    for r in radiusSet:
        oneRadius.addTerms(1, radius[r])
    model.addConstr(oneRadius.__eq__(1), name='oneRadius')
    print("radius constraints:", oneRadius)


def startBeforeTheSelectedRadius(model, LB):
    # at least one start before the selected radius
    for i in NBSForPowerConstraints:
        for r in radiusSet:
            atLeastOneStartBeforeRadius = LinExpr()
            for t in range(1, r + 1):
                atLeastOneStartBeforeRadius.addTerms(1, start[i, t])

            for m in radiusSet:
                if m <= r:
                    atLeastOneStartBeforeRadius.addTerms(-1, radius[m])
            model.addConstr(atLeastOneStartBeforeRadius.__ge__(0), name='atLeastOneStart(%g.%g)' % (i, r))
    for c in CLsForPowerConstraints:
        for r in radiusSet:
            atLeastOneStartBeforeRadius = LinExpr()
            for t in range(LB, r + 1):
                atLeastOneStartBeforeRadius.addTerms(1, start[c, t])

            for m in radiusSet:
                if m <= r:
                    atLeastOneStartBeforeRadius.addTerms(-1, radius[m])
            model.addConstr(atLeastOneStartBeforeRadius.__ge__(0), name='atLeastOneStart(%g.%g)' % (c, r))
    print("at least one start")


def startTimeSelection(model, LB, timeHorizon):
    # select a start time for each NBS
    for i in NBSForPowerConstraints:
        startTimeSelectionForNBS = LinExpr()
        for t in range(1, timeHorizon + 1):
            startTimeSelectionForNBS.addTerms(1, start[i, t])
        model.addConstr(startTimeSelectionForNBS.__eq__(1), name='startTimeSelectionNBS(%s)' % (i))
    # select a start time for each CL
    for c in CLsForPowerConstraints:
        startTimeSelectionForCL = LinExpr()
        for t in range(LB, timeHorizon + 1):
            startTimeSelectionForCL.addTerms(1, start[c, t])
        model.addConstr(startTimeSelectionForCL.__eq__(1), name='startTimeSelectionCL(%s)' % (c))


def netPower(model, timeHorizon):
    # net power
    for t in range(1, timeHorizon + 1):
        rhs = 0
        for b in BSForPowerConstraints:
            rhs = rhs - (powerOutputFromBS[b, t] + demandFrom[b, t])
        netPower = LinExpr()
        for i in NBSForPowerConstraints:
            for startPeriod in range(1, t + 1):
                timeSinceTheStart = t - startPeriod + 1
                netPower.addTerms(powerOf[i, timeSinceTheStart], start[i, startPeriod])

        for i in CLsForPowerConstraints:
            for r in radiusSet:
                if r <= t:
                    netPower.addTerms(powerOf[i, t], radius[r])
        model.addConstr(netPower.__ge__(rhs), name='netPower(%s)' % (t))


def startTimeSelectionSingleRadius(model, timeHorizon):
    # select a start time for each NBS
    for i in NBSForPowerConstraints:
        startTimeSelectionForNBS = LinExpr()
        for t in range(1, timeHorizon + 1):
            startTimeSelectionForNBS.addTerms(1, start[i, t])
        model.addConstr(startTimeSelectionForNBS.__eq__(1), name='startTimeSelectionNBS(%s)' % (i))


def netPowerSingleRadius(model, timeHorizon):
    # net power for the single radius model
    for t in range(1, timeHorizon + 1):
        rhs = 0
        for b in BSForPowerConstraints:
            rhs = rhs - powerOutputFromBS[b, t]
        netPower = LinExpr()
        for i in NBSForPowerConstraints:
            for startPeriod in range(1, t + 1):
                timeSinceTheStart = t - startPeriod + 1
                netPower.addTerms(powerOf[i, timeSinceTheStart], start[i, startPeriod])
        if t == timeHorizon:
            for i in CLsForPowerConstraints:
                rhs = rhs - powerOf[i, t]
        model.update()
        model.addConstr(netPower.__ge__(rhs), name='netPower(%s)' % (t))


def netPowerSingleRadiusWithAuxiliaries(model, timeHorizon):
    # net power for the single radius model with auxiliary variables
    for t in range(1, timeHorizon + 1):
        rhs = 0
        for b in BSForPowerConstraints:
            rhs = rhs - powerOutputFromBS[b, t]
        netPower = LinExpr()
        netPower.addTerms(1, auxiliary[t])
        for i in NBSForPowerConstraints:
            for startPeriod in range(1, t + 1):
                timeSinceTheStart = t - startPeriod + 1
                netPower.addTerms(powerOf[i, timeSinceTheStart], start[i, startPeriod])
        if t == timeHorizon:
            for i in CLsForPowerConstraints:
                rhs = rhs - powerOf[i, t]
        model.update()
        model.addConstr(netPower.__ge__(rhs), name='netPower(%s)' % (t))


def startCLsLastPeriod(model):
    # start CLs in the last period
    for i in CLsForPowerConstraints:
        for k in radiusSet:
            startLate = LinExpr()
            startLate.addTerms(-1, radius[k])
            startLate.addTerms(1, start[i, k])
            model.addConstr(startLate.__eq__(0), name='startLate(%g,%g)' % (i, k))
    print("start CLs late")


#  implied or valid inequalities
def startEachComponent(model, timeHorizon):
    # one start for each component
    for i in NBSForPowerConstraints:
        oneStartPerComponent = LinExpr()
        for t in range(1, timeHorizon + 1):
            oneStartPerComponent.addTerms(1, start[i, t])
        model.addConstr(oneStartPerComponent.__eq__(1), name='atMostOneStart(%g)' % i)
    print("start each NBS")
