
from parallelPowerSystemRestoration.GSSModels.constraintsGSS import *
from parallelPowerSystemRestoration.GSSModels.decisionVariablesGSS import *


def buildSingleRadiusGSSModel(model, tLB, tUB, currentRadius):
    # pick variables
    defineSingleRadiusVariablesGSS(model, currentRadius)

    #  pick objective: optional since no objective function is needed for the feasibility problem
    # defineObjective(model)

    # pick constraints
    startTimeSelectionSingleRadius(model, currentRadius)
    netPowerSingleRadius(model, currentRadius)
    # startEachComponent(model, tLB, tUB, currentRadius)  # this is optional


def buildSingleRelaxedRadiusGSSModel(model, tLB, tUB, currentRadius):
    # pick variables
    defineRelaxedSingleRadiusVariablesGSS(model, currentRadius)
    #  pick objective: optional since no objective function is needed for the feasibility problem
    # defineObjective(model)

    # pick constraints
    startTimeSelectionSingleRadius(model, currentRadius)
    netPowerSingleRadius(model, currentRadius)
    # startEachComponent(model, tLB, tUB, currentRadius) # this is optional


def solveSingleRadiusGSSModel(model, tLB, tUB, timeHorizon) -> bool:
    def setOptions(model):
        #  set the run options
        model.setParam('Threads', 8)
        model.setParam(GRB.param.TimeLimit, 3600)
        model.setParam(GRB.param.SolutionLimit, 1)
        model.setParam('MIPFocus', 1)
        # model.setParam(OUTPUT_DIR/'LogFile',
        #                'SINGLE-RADIUS--LOG-' + str(len(nodes)) + "-LB=" + str(tLB) + "-UB=" + str(tUB) + "-" + str(
        #                    datetime.datetime.now()) + '.txt')
        # model.setParam(OUTPUT_DIR/'SolFiles',
        #                'Solution-SINGLE-RADIUS-' + str(len(nodes)) + "-LB=" + str(tLB) + "-UB=" + str(tUB) + "-" + str(
        #                    datetime.datetime.now()) + '.txt')

    setOptions(model)
    # update and solve the model
    model.update()
    model.optimize()

    modelStatus = model.Status
    # print('model status is ', modelStatus)

    if modelStatus == 3:
        # print('returning false')
        return False
    if modelStatus == 9:
        return False
    if modelStatus == 10:
        # print('returning true')
        return True
    if modelStatus == 2:
        return True

    def solutionValidation(model):
        # read the optimal solution
        variableName = []
        variableValue = []
        for v in model.getVars():
            if v.x > 0:
                variableName += [v.varname]
                variableValue += [v.x]

        # optSolution = pd.DataFrame(list(zip(variableName, variableValue)), columns=['varName', 'varVal'])
        # optSolution.to_csv(OUTPUT_DIR/'optSol-SINGLE-RADIUS.csv', index=False)  # Check

        def checkPower():
            powerOK = True
            for t in range(1, timeHorizon + 1):
                rhs = 0
                for b in BSForPower:
                    rhs = rhs - powerOutputBS[b, t]
                lhs = 0
                for i in NBSForPower:
                    for startPeriod in range(1, t + 1):
                        timeSinceTheStart = t - startPeriod + 1
                        lhs += (powerOf[i, timeSinceTheStart] * start[i, startPeriod].x)
                if t == timeHorizon:
                    for i in criticalNodesForPower:
                        lhs += powerOf[i, t]
                if lhs < rhs:
                    powerOK = False
                    print("violation power BS period ", t)
                    break
            if powerOK == True:
                print("power constraints OK ")

        checkPower()

    solutionValidation(model)
    timeAfterOptimization = time.time()
    # print('Model Time=' + str(timeAfterOptimization - preModelTime))
    # print('Total Time=' + str(timeAfterOptimization - startingTime))


def solveSingleRadiusGSSModelWithAuxiliaries(model, tLB, tUB, timeHorizon) -> bool:
    def setOptions(model):
        #  set the run options
        model.setParam('Threads', 8)
        model.setParam(GRB.param.TimeLimit, 3600)
        # model.setParam(GRB.param.SolutionLimit, 1)
        model.setParam('MIPFocus', 1)
        # model.setParam(OUTPUT_DIR/'LogFile',
        #                'SINGLE-RADIUS--LOG-' + str(len(nodes)) + "-LB=" + str(tLB) + "-UB=" + str(tUB) + "-" + str(
        #                    datetime.datetime.now()) + '.txt')
        # model.setParam(OUTPUT_DIR/'SolFiles',
        #                'Sol-SINGLE-RADIUS-' + str(len(nodes)) + "-LB=" + str(tLB) + "-UB=" + str(tUB) + "-" + str(
        #                    datetime.datetime.now()) + '.txt')

    setOptions(model)
    # update and solve the model
    model.update()
    model.optimize()

    modelStatus = model.Status
    print('model status is ', modelStatus)
    objVal = model.objVal

    if objVal < 0.00001:
        return True
    if objVal > 0:
        return False


def buildSingleRadiusGSSModelWithAuxiliaryVariables(model, tLB, tUB, currentRadius):
    # pick variables
    defineSingleRadiusVariablesGSSWithAuxiliaryVariables(model, currentRadius)
    #  pick objective
    defineObjectiveWithAuxiliaries(model, currentRadius)

    # pick constraints
    startTimeSelectionSingleRadius(model, currentRadius)
    netPowerSingleRadiusWithAuxiliaries(model, currentRadius)
    # startEachComponent(model, tLB, tUB, currentRadius)
