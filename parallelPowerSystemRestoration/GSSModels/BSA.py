# The binary search algorithm for solving the generator startup sequencing problem (GSS)
# It works on the single radius formulation
# removing print lines may increase speed

from parallelPowerSystemRestoration.GSSModels.singleRadiusGSSModel import *
from parallelPowerSystemRestoration.parameterAndSetCreation import *
# from parallelPowerSystemRestoration.GSSModels.timeDependentInput import *

BSAStartingTime = time.time()
# LB = 1
# tempLB = initialLB
# tempUB = maxTimeHorizon
# optimalValue = maxTimeHorizon

tempLB = LB
tempUB = timeHorizon
optimalValue = timeHorizon


initialize()

timeInputFilled = time.time()

# Binary search
while tempUB > tempLB + 1:
    time2 = time.time()
    currentRadius = int(tempLB + tempUB) // 2
    modelStatus = 'unknown'
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~ radius ', currentRadius, '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ')

    timeHorizon = currentRadius
    # initializeTimeDependentInput(tempLB, tempUB, currentRadius)

    print("radius set:", radiusSet)
    print("period set:", periodSet)
    model = Model('SingleRadius-GSS')  # create the model
    buildSingleRadiusGSSModel(model, tempLB, tempUB, currentRadius)

    if solveSingleRadiusGSSModel(model, tempLB, tempUB, currentRadius):
        tempUB = currentRadius
        optimalValue = currentRadius
        print('**************** the model is FEASIBLE tempLB tempUB currentRadius', tempLB, tempUB, currentRadius)
    else:
        tempLB = currentRadius + 1
        print('!!!!!!!!!!!!! the model is INFEASIBLE tempLB tempUB currentRadius', tempLB, tempUB, currentRadius)

if tempUB == tempLB + 1:
    time2 = time.time()

    currentRadius = tempLB
    modelStatus = 'unknown'
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~ radius ', currentRadius, '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ')
    # initializeTimeDependentInput(tempLB, tempUB, currentRadius)

    model = Model('SingleRadius-GSS')  # create the model
    buildSingleRadiusGSSModel(model, tempLB, tempUB, currentRadius)

    if solveSingleRadiusGSSModel(model, tempLB, tempUB, currentRadius):
        tempUB = currentRadius
        optimalValue = currentRadius
        print('***************** the model is FEASIBLE tempLB tempUB currentRadius', tempLB, tempUB, currentRadius)
    else:
        tempLB = currentRadius + 1
        print('!!!!!!!!!!!!! the model is INFEASIBLE tempLB tempUB currentRadius', tempLB, tempUB, currentRadius)

afterBSATime = time.time()
print('Time for input process is ', timeInputFilled - BSAStartingTime)
print('Optimal value is ', optimalValue)
print('Total Binary Search time is ', afterBSATime - timeInputFilled)
