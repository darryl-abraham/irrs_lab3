#!/usr/bin/python

from collections import namedtuple
import time
import sys
import math
import numpy as np

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
            origin = parts[2].strip()
            destination = parts[4].strip()
            if origin in airportHash and destination in airportHash:
                numberOfRoutes += 1
                originAirport = airportHash[origin]
                destinationAirport = airportHash[destination]
                # There's already an edge, just increase its weight
                if destinationAirport.routeHash.get(origin):
                    destinationAirport.routeHash[origin].weight += 1
                    originAirport.outweight += 1
                else:
                    edge = Edge(origin = originAirport)
                    # edgeList.append(edge)
                    # edgeHash[(origin, destination)] = edge
                    destinationAirport.routeHash[origin] = edge
                    originAirport.outweight += 1

def method1(L):
    n = len(airportList)

    iterations = 0
    while(True):
        iterations += 1
        Q = [0 for i in range(n)]
        for i in range(n):
            currentAirport = airportList[i]
            for route in currentAirport.routeHash.values():
                Q[i] = Q[i] + route.origin.pageIndex * route.weight / (route.origin.outweight + 1)      # +1 to consider also the self-loop
            Q[i] = L * (Q[i] + currentAirport.pageIndex * 1 / (currentAirport.outweight + 1)) + (1-L)/n
        # print(Q)
        # print(np.linalg.norm(Q,1))

        equal = True
        for i in range(n):
            if(not(math.isclose(airportList[i].pageIndex, Q[i], rel_tol=1e-6))):
                equal = False
                break
        if equal:
            break
        for i in range(len(airportList)):
            airportList[i].pageIndex = Q[i]

    return iterations

def method2(L):
    n = len(airportList)
    
    iterations = 0
    while(True):
        iterations += 1
        Q = [0 for i in range(n)]
        noOutAirports = False
        overallSum = 0
        incomingWeights = dict()        # a dictionary with the sum of the incoming weights for each node
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
        # print(Q)
        # print(np.linalg.norm(Q,1))

        equal = True
        for i in range(n):
            if(not(math.isclose(airportList[i].pageIndex, Q[i], rel_tol=1e-6))):
                equal = False
                break
        if (equal):
            break
        for i in range(len(airportList)):
            airportList[i].pageIndex = Q[i]
    return iterations

def computePageRanks():
    # write your code
    L = 0.85
    for airport in airportList:
        airport.pageIndex = 1/len(airportList)
    #return method1(L)
    return method2(L)


def outputPageRanks():
    # write your code
    rank = 1
    file = open("output1", "w")
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
