import time
import datetime
from parallelPowerSystemRestoration.GSSModels.constraintsGSS import *
from parallelPowerSystemRestoration.GSSModels.decisionVariablesGSS import *
from gurobipy import *
from parallelPowerSystemRestoration.parameterAndSetCreation import *
# from parallelPowerSystemRestoration.GSSModels.timeDependentInput import *

startingTime = time.time()

initialize()
# initializeTimeDependentInput(LB,timeHorizon,timeHorizon)
preModelTime = time.time()
model = Model('ALL-RADIUS-GSS')  # create the model

defineVariablesGSS(model,LB,timeHorizon)  # pick variables

defineObjective(model)  # pick objective

# pick constraints
pickOneRadius(model)
startBeforeTheSelectedRadius(model,LB)
startTimeSelection(model,LB,timeHorizon)
netPower(model,timeHorizon)


# startCLsLastPeriod(model)
# startEachComponent(model)
def setOptions(model):
    #  set the run options
    model.setParam('Threads', 8)
    model.setParam(GRB.param.TimeLimit, 3600)
    model.setParam('MIPFocus', 1)

setOptions(model)
# update and solve the model
model.update()
model.optimize()

timeAfterOptimization = time.time()
print('Model Time=' + str(timeAfterOptimization - preModelTime))
print('Total Time=' + str(timeAfterOptimization - startingTime))
