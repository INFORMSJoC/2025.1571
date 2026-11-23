from parallelPowerSystemRestoration.GSSModels.singleRadiusGSSModel import *
from parallelPowerSystemRestoration.parameterAndSetCreation import *
# from parallelPowerSystemRestoration.GSSModels.timeDependentInput import *

BSstartingTime = time.time()
# LB = 1
tLB = LB
tUB = timeHorizon
optimalValue = timeHorizon

initialize()
exploredRadius = []

timeInputFilled = time.time()

# Binary search
while tUB > tLB + 1:
    time2 = time.time()
    currentRadius = int(tLB + tUB) // 2
    statusModel = 'unknown'
    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~ radius ', currentRadius, '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ')

    # LB = tLB
    # UB = tUB
    timeHorizon = currentRadius
    # initializeTimeDependentInput(tLB, tUB, currentRadius)

    model = Model('RELAXED-RADIUS-GSS')  # create the model
    buildSingleRelaxedRadiusGSSModel(model, tLB, tUB, currentRadius)

    if solveSingleRadiusGSSModel(model, tLB, tUB, currentRadius):
        model2 = Model('ALL-RADIUS-GSS')  # create the model
        buildSingleRadiusGSSModel(model2, tLB, tUB, currentRadius)
        if solveSingleRadiusGSSModel(model2, tLB, tUB, currentRadius):
            tUB = currentRadius
            UB = currentRadius
            optimalValue = UB
            # print('**************** the integer model is FEASIBLE tLB tUB currentRadius', tLB, tUB, currentRadius )
        else:
            tLB = currentRadius + 1
            # print('!!!!!!!!!!!!! the integer model is INFEASIBLE tLB tUB currentRadius', tLB, tUB, currentRadius)
    else:
        tLB = currentRadius + 1
        # print('!!!!!!!!!!!!! the continuous model is INFEASIBLE tLB tUB currentRadius', tLB, tUB, currentRadius)

    exploredRadius.append(currentRadius)

if tUB == tLB + 1:
    time2 = time.time()
    if tUB not in exploredRadius:
        currentRadius = tUB
        statusModel = 'unknown'
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~ radius ', currentRadius, '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ')
        # initializeTimeDependentInput(tLB, tUB, currentRadius)

        model = Model('ALL-RADIUS-GSS')  # create the model
        buildSingleRadiusGSSModel(model, tLB, tUB, currentRadius)

        if solveSingleRadiusGSSModel(model, tLB, tUB, currentRadius):
            model2 = Model('ALL-RADIUS-GSS')  # create the model
            buildSingleRadiusGSSModel(model2, tLB, tUB, currentRadius)
            if solveSingleRadiusGSSModel(model2, tLB, tUB, currentRadius):
                tUB = currentRadius
                UB = currentRadius
                optimalValue = UB
                # print('**************** the integer model is FEASIBLE tLB tUB currentRadius', tLB, tUB, currentRadius )
            else:
                tLB = currentRadius + 1
                # print('!!!!!!!!!!!!! the integer model is INFEASIBLE tLB tUB currentRadius', tLB, tUB, currentRadius)
    else:
        if tLB not in exploredRadius:
            currentRadius = tLB
            statusModel = 'unknown'
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~ radius ', currentRadius, '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ')
            # initializeTimeDependentInput(tLB, tUB, currentRadius)

            model = Model('ALL-RADIUS-GSS')  # create the model
            buildSingleRadiusGSSModel(model, tLB, tUB, currentRadius)

            if solveSingleRadiusGSSModel(model, tLB, tUB, currentRadius):
                if solveSingleRadiusGSSModel(model, tLB, tUB, currentRadius):
                    tUB = currentRadius
                    UB = currentRadius
                    optimalValue = UB
                    # print('***************** the model is FEASIBLE tLB tUB currentRadius', tLB, tUB, currentRadius)
            else:
                tLB = currentRadius + 1
                # print('!!!!!!!!!!!!! the model is INFEASIBLE tLB tUB currentRadius', tLB, tUB, currentRadius)

afterBSTime = time.time()
print('Time for input process is ', timeInputFilled - BSstartingTime)
print('Optimal value is ', optimalValue)
print('Total Binary Search with RFGSS_STAR time is ', afterBSTime - timeInputFilled)
