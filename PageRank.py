#!/usr/bin/python

from collections import namedtuple
import time
import sys
import math
import numpy as np
import argparse

class Edge:
    def __init__ (self, origin=None):
        self.origin = origin
        self.weight = 1

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)
        
    ## write rest of code that you need for this class

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        # self.routes = [] # vector of edges of incoming routes
        self.routeHash = dict()     # dictionary of edges of incoming routes, indexed by the origin airport code
        self.outweight =  0  # sum of all routes in which the airport is origin
        self.pageIndex = 0

    def __repr__(self):
        return f"{self.code}\t{self.pageIndex}\t{self.name}"

parser = argparse.ArgumentParser()
parser.add_argument("--f", help="If set, writes the output into a file named output_methodX, where X is the chosen method.", action="store_true")
parser.add_argument("--method", help="The method to be used.", default=1, choices=[1,2,3], type=int)
args=parser.parse_args()

method = int(args.method)

# edgeList = [] # list of Edge
# edgeHash = dict() # hash of edge to ease the match
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport
numberOfRoutes = 0

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r");
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            if not(airportHash.get(a.code)):
                cont += 1
                airportList.append(a)
                airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")


def readRoutes(fd):
    print("Reading Routes file from {fd}")
    global numberOfRoutes
    with open(fd, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if not parts[2] or not parts[4]:
                continue  # Skip invalid or incomplete lines
            originCode = parts[2].strip()
            destinationCode = parts[4].strip()
            if originCode in airportHash and destinationCode in airportHash:
                numberOfRoutes += 1
                originAirport = airportHash[originCode]
                destinationAirport = airportHash[destinationCode]
                # There's already an edge, just increase its weight
                if destinationAirport.routeHash.get(originCode):
                    destinationAirport.routeHash[originCode].weight += 1
                    originAirport.outweight += 1
                else:
                    edge = Edge(origin = originAirport)
                    # edgeList.append(edge)
                    # edgeHash[(origin, destination)] = edge
                    destinationAirport.routeHash[originCode] = edge
                    originAirport.outweight += 1

def method1(L):
    # Adding self-loops of weight = 1 to every node
    n = len(airportList)

    equal = False
    iterations = 0
    while(not equal):
        iterations += 1
        Q = [0 for i in range(n)]
        equal = True
        for i in range(n):
            currentAirport = airportList[i]
            for route in currentAirport.routeHash.values():
                Q[i] = Q[i] + route.origin.pageIndex * route.weight / (route.origin.outweight + 1)      # +1 to consider also the self-loop
            Q[i] = Q[i] + currentAirport.pageIndex * 1 / (currentAirport.outweight + 1)         # Adding the term related to the self-loop
            Q[i] = L * Q[i] + (1-L)/n     
            if(equal and not(math.isclose(currentAirport.pageIndex, Q[i], rel_tol=1e-6))):
                equal = False
            currentAirport.pageIndex = Q[i]

        # Uncomment this to check that the norm remains 1 at each iteration
        # print(np.linalg.norm(Q,1))
    return iterations

def method2(L):
    # Letting the vector p have norm_1 = 1 by "filling" the gap between the real norm and 1 (after the application of the standard formula)
    # The remaining portion to arrive to 1 is divided through all the nodes, based on their incoming edges
    # The more a node has an incoming weight (i.e., the sum of the weights of its incoming edges), the more it will receive a fraction of this portion
    n = len(airportList)
    
    equal = False
    iterations = 0
    while(not equal):
        iterations += 1
        Q = [0 for i in range(n)]
        noOutAirports = False
        overallSum = 0
        incomingWeights = dict()        # a dictionary with the sum of the incoming weights for each node
        equal = True
        for i in range(n):
            currentAirport = airportList[i]
            incomingWeights[i] = 0
            for route in currentAirport.routeHash.values():
                Q[i] = Q[i] + route.origin.pageIndex * route.weight / route.origin.outweight
                incomingWeights[i] += route.weight
            Q[i] = L * Q[i] + (1-L)/n
            overallSum += Q[i]
            if currentAirport.outweight == 0:
                noOutAirports = True
            
        if (noOutAirports):
            overallSum = (1-overallSum) / numberOfRoutes # since #routes = sum of all the weights of all the edges
            for i in range(n):
                Q[i] += overallSum * incomingWeights[i]
                if(equal and not(math.isclose(airportList[i].pageIndex, Q[i], rel_tol=1e-6))):
                    equal = False
                airportList[i].pageIndex = Q[i]
        
        # Uncomment this to check that the norm remains 1 at each iteration
        # print(np.linalg.norm(Q,1))

    return iterations

def method3(L):
    # For the nodes with no incoming and no outgoing edges, the ranking is 0
    # For the problematic nodes without outgoing edges (but with some incoming), an outgoing edge is added for each incoming one, back to its origin, with the same weight
    n = len(airportList)
    global numberOfRoutes

    for airport in airportList:
        if airport.outweight == 0:
            # No incoming and no outcoming
            if len(airport.routeHash) == 0:
                del airportHash[airport.code]
            else:
                for route in airport.routeHash.values():
                    route.origin.routeHash[airport.code] = Edge(origin=airport)
                    numberOfRoutes += 1     # just for coherence
                    airport.outweight += route.weight

    n2 = len(airportHash)
    # Initialization
    for airport in airportHash.values():
        airport.pageIndex = 1/n2
                
    equal = False
    iterations = 0
    while(not equal):
        iterations += 1
        Q = [0 for i in range(n)]
        equal = True
        for i in range(n):
            currentAirport = airportList[i]
            for route in currentAirport.routeHash.values():
                Q[i] = Q[i] + route.origin.pageIndex * route.weight / (route.origin.outweight)      
            if Q[i] != 0:           
                Q[i] = L * Q[i] + (1-L)/n2
            if(equal and not(math.isclose(currentAirport.pageIndex, Q[i], rel_tol=1e-6))):
                equal = False
            currentAirport.pageIndex = Q[i]

        # Uncomment this to check that the norm remains 1 at each iteration
        # print(np.linalg.norm(Q,1))
    return iterations


def computePageRanks():
    # write your code
    L = 0.85
    if method != 3:     # method 3 has a different initialization
        for airport in airportList:
            airport.pageIndex = 1/len(airportList)
    if method == 2:
        return method2(L)
    if method == 3:
        return method3(L)
    return method1(L)           # default


def outputPageRanks():
    # write your code
    rank = 1
    if args.f:
        file = open("output_method" + str(method) + ".txt", "w")
    else:
        file = open(1, "w")      # stdout
    for index in np.argsort([airport.pageIndex for airport in airportList])[::-1]:
        file.write(str(rank) + " - " + str(airportList[index]) + "\n")
        rank += 1

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2-time1)


if __name__ == "__main__":
    sys.exit(main())
