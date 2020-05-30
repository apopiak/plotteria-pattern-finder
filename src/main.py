#!/usr/bin/python3
import glob
import json
import operator
import os
import sys
import time
from collections import deque
from random import choice
import itertools
import functools
import sys

def generateGraph(dimension, depth):
    assert dimension > 1 # tuple cardinality like 3 = (1,1,1)
    assert depth > 1 # range of values eg 1..3
    graph = {}
    for (i,j,k) in itertools.product(range(depth), repeat=dimension):
        graph[(i,j,k)] = { 
            'out': [(j,k,n) for n in range(depth) if not (i == j and j == k and n == i)],
            'in' : [(n,i,j) for n in range(depth) if not (i == j and j == k and n == k)],
        }
    return graph

global solutionCount
global prettySolutionCount
global printCount
solutionCount = 0
prettySolutionCount = 0
printCount = 0

def solutionToStr(solution):
    res = "".join([str(x) for x in solution[0]]) 
    for step in solution[1:]:
        res += str(step[2])
    return res

def indexDefault(list, value, default):
    try:
        return list.index(value)
    except Exception:
        return default

def isSolutionValid(solution, depth, dimension):
    #check whether 000 111 222 333 is equally spaced
    #solutionStr = solutionToStr(solution)
    findings = [0] + [indexDefault(solution[2:], triple, -1) for triple in [(x,x,x) for x in range(1, depth)]]
    index = 0
    for i, val in enumerate(reversed(findings)):
        if val < 0: continue
        index = i
        break
    positions = findings[:-index] if index > 0 else findings
        
    chunkSize = (depth**dimension) // depth
    pattern = [x * chunkSize for x in range(depth)]
    for a,b in zip(positions, pattern):
        if a != b:
            return 0
    if len(pattern) > len(positions):
        return 0 if len(solution)+(dimension-1) > pattern[len(positions)]+4 else -1
    else:
        return 1


def findHamiltonBF(visited, graph, isValid):
    global solutionCount
    global prettySolutionCount
    global printCount
    printCount += 1
    if printCount % 100_000 == 0:
        print(solutionToStr(visited), end='\r')
        printCount = 0
    if len(visited) >= len(graph.values()):
        solutionCount +=1
        #print(f"Solutions {prettySolutionCount}/{solutionCount}", end='\r')
        if isValid(visited):
            prettySolutionCount += 1
            print(solutionToStr(visited))
            #print(f"Solutions {prettySolutionCount}/{solutionCount}", end='\r')
            return [visited]
    elif not isValid(visited):
        return []
    
    solutions = []
    current = visited[-1]
    for next in graph[current]['out']:
        if not next in visited:
            solutions += findHamiltonBF(visited + [next], graph, isValid)
    
    return solutions

def main():
    dimension = 3
    depth = 3
    graph = generateGraph(dimension, depth)
    visited = [(0,0,0)]
    solutions = findHamiltonBF(visited, graph, lambda x : isSolutionValid(x, depth, dimension))
    print(f"Solutions found: {len(solutions)}")

    with open('solutions.txt','w') as file:
        file.writelines([solutionToStr(sol)+'\n' for sol in solutions])

def isValidPattern(pattern):
    pattern = ''.join(pattern)
    tuples = dict()
    for i in range(1, len(pattern)-2):
        x = pattern[i:i+3]
        if (x not in tuples):
            tuples.setdefault(x, None)
        else:
            return False
    return True

import re

def traversePatternState(depth, pattern):
    try:
        xpos = next(i for i,x in enumerate(pattern) if x=='x')
    except StopIteration:
        if isValidPattern(pattern):
            print(''.join(pattern))
            return
    else:
        for x in range(0, depth):
            next_pattern = list(pattern)
            next_pattern[xpos] = str(x)
            traversePatternState(depth, next_pattern)

def main2():
    print('Start searching')
    dimension = 3
    depth = 3
    pattern_str = "000xxxxxxx111xxxxxxx222xxxxxx"
    pattern = list(pattern_str)
    assert len(pattern) == (depth**dimension)+2
    traversePatternState(depth, pattern)
    
if __name__ == "__main__":
    main()
