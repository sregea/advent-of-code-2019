import sys
sys.path.append('../')
import computer
import pdb
import math

# Define the different types of locations inside the grid.
LOCATION_TYPE_WALL = 0
LOCATION_TYPE_EMPTY = 1
LOCATION_TYPE_TANK = 2

# Define the four directions of movement for the robot.
MOVE_NORTH = 1
MOVE_SOUTH = 2
MOVE_WEST = 3
MOVE_EAST = 4
movements = [MOVE_NORTH, MOVE_SOUTH, MOVE_WEST, MOVE_EAST]

class Grid():
    def __init__(self):
        # Initialize the locations inside the grid.
        self.locations = {}

        # Keep track of the position of the oxygen tank.
        self.tankx = None
        self.tanky = None

        # Keep track of the extreme values of the grid.
        self.miny = 0
        self.maxy = 0
        self.minx = 0
        self.maxx = 0

        # Define some symbols to print the grid.
        self.symbols = {
            LOCATION_TYPE_EMPTY: ' ',
            LOCATION_TYPE_WALL: '#',
            LOCATION_TYPE_TANK: 'O'
        }
    
    # Updates the extreme values of the grid whenever they are inserted.
    def updateMaximalValues(self, value, coordinate):
        if coordinate == 'x':
            if value > self.maxx:
                self.maxx = value
            if value < self.minx:
                self.minx = value
        elif coordinate == 'y':
            if value > self.maxy:
                self.maxy = value
            if value < self.miny:
                self.miny = value

# This object represents the position of the robot.
class Location():
    def __init__(self, x, y, locationType=LOCATION_TYPE_EMPTY):
        self.x = x
        self.y = y
        self.type = locationType
    
    # Receives a movement and returns a new location moved.
    def move(self, movement):
        if movement == MOVE_EAST:
            return Location(self.x + 1, self.y)
        elif movement == MOVE_SOUTH:
            return Location(self.x, self.y - 1)
        elif movement == MOVE_WEST:
            return Location(self.x - 1, self.y)
        elif movement == MOVE_NORTH:
            return Location(self.x, self.y + 1)
        else:
            return None
    
    # Returns the movement needed to reach the specified location.
    def movementToReach(self, location):
        if self.x < location.x:
            return MOVE_EAST
        elif location.x < self.x:
            return MOVE_WEST
        elif location.y < self.y:
            return MOVE_SOUTH
        elif self.y < location.y:
            return MOVE_NORTH

# An object ready for Dijkstra.
class Node():
    def __init__(self, x, y, nodeType):
        self.x = x
        self.y = y
        self.type = nodeType
        self.visited = False
        self.distance = math.inf

def main(filename):

    # Explore the area.
    grid = exploreGrid(filename)

    # Print the area explored.
    print('State of the room (oxygen tank marked O):')
    for y in range(grid.miny, grid.maxy + 1):
        for x in range(grid.minx, grid.maxx + 1):
            if y in grid.locations and x in grid.locations[y]:
                print(grid.symbols[grid.locations[y][x]], end='')
            else:
                print(grid.symbols[LOCATION_TYPE_EMPTY], end='')
        print()

    # Calculate the shortest path between the robot and the oxygen tank.
    steps = solvePartOne(grid)
    print('\nSmallest number of steps from the robot to the tank: {}'.format(steps))

    # Find the number of minutes it takes to fill the room with oxygen.
    minutes = solvePartTwo(grid)
    print('Minutes until the room is filled with oxygen: {}'.format(minutes))

# Receives the filename for the controller software and returns the explored grid.
def exploreGrid(filename):
    # Load the controller software.
    controller = computer.readProgramFromFile(filename)
    controller.printOutputs(False)

    # Define the starting position of the robot.
    startLocation = Location(0, 0, LOCATION_TYPE_EMPTY)

    # Explore the area around the robot.
    grid = Grid()
    floodFill(startLocation, grid, controller)

    return grid

# Solves part one of the problem. Receives the grid and returns the minimal
# distance from the robot (0,0) to the oxygen tank.
def solvePartOne(grid):

    # Prepare a dictionary of nodes for Dijkstra algorithm.
    nodes = parseGrid(grid)

    # Calculate the number of steps to reach the tank.
    return dijkstra(nodes, 0, 0, LOCATION_TYPE_TANK)


# Receives the grid and applies Dijkstra from the oxygen tank.
# Returns the maximal distance to the oxygen tank.
def solvePartTwo(grid):

    # Parse the empty nodes and apply Dijkstra to all the empty locations.
    nodes = parseGrid(grid)
    dijkstra(nodes, grid.tankx, grid.tanky)
    
    # Find the location with the maximal distance value.
    maxDistance = - math.inf
    for y in nodes:
        for x in nodes[y]:
            if nodes[y][x].distance > maxDistance:
                maxDistance = nodes[y][x].distance
    
    return maxDistance

# Explores a grid performing flood fill with the help
# of the robot controller.
def floodFill(currentLocation, grid, controller, lastLocation=None):
    
    # Get this location inside the grid and mark its type.
    if not currentLocation.y in grid.locations:
        grid.locations[currentLocation.y] = {}
        grid.updateMaximalValues(currentLocation.y, 'y')
    if not currentLocation.x in grid.locations[currentLocation.y]:
        grid.locations[currentLocation.y][currentLocation.x] = currentLocation.type
        grid.updateMaximalValues(currentLocation.x, 'x')
    
    # If this is a wall, do not continue with the algorithm.
    if currentLocation.type == LOCATION_TYPE_WALL:
        return
    
    # If this is the oxygen tank, store the value.
    if currentLocation.type == LOCATION_TYPE_TANK:
        grid.tankx = currentLocation.x
        grid.tanky = currentLocation.y
    
    # Perform flood fill in all four directions.
    for movement in movements:

        # Calculate the direction where the robot is moving next.
        newLocation = currentLocation.move(movement)
        
        # Check if it has already been visited and return if so.
        if newLocation.y in grid.locations:
            if newLocation.x in grid.locations[newLocation.y]:
                # Go explore the next direction.
                continue

        # Try to move the robot to the new location.
        controller.emptyOutputs()
        controller.setInputs([movement])
        controller.returnOnOutputNumber(1)
        controller.execute()
        newLocation.type = controller.getOutputs()[0]

        # Perform flood fill on this new location, recursively if needed.
        floodFill(newLocation, grid, controller, currentLocation)

    # If not the starting location, backtrack to the previous location.
    if lastLocation != None:
        controller.emptyOutputs()
        controller.setInputs([currentLocation.movementToReach(lastLocation)])
        controller.returnOnOutputNumber(1)
        controller.execute()

# Receives a grid from the flood fill algorithm and returns a dictionary with the nodes
# prepared for Dijkstra.
def parseGrid(grid):
    nodes = {}
    for y in grid.locations:
        for x in grid.locations[y]:
            if grid.locations[y][x] == LOCATION_TYPE_EMPTY or grid.locations[y][x] == LOCATION_TYPE_TANK:
                # Add it to the nodes for Dijkstra.
                if not y in nodes:
                    nodes[y] = {}
                nodes[y][x] = Node(x, y, grid.locations[y][x])

    return nodes

# Applies Dijkstra's algorithm. If targetLocation is specified, it returns the minimal number of steps
# to reach it. If not, it fills the grid with minimal distances from the starting position.
def dijkstra(nodes, startx, starty, targetLocation=None):

    # Set the distance to the initial node to zero.
    nodes[starty][startx].distance = 0

    # Set the initial node as the current.
    current = nodes[starty][startx]

    # Create a set of all the unvisited nodes.
    unvisited = {}
    for y in nodes:
        for x in nodes[y]:
            if not y in unvisited:
                unvisited[y] = {}
            unvisited[y][x] = nodes[y][x]

    # Loop until we find the destination node.
    while targetLocation and current.type != targetLocation or not targetLocation and unvisited:

        # Get a list of the unvisited neighbors of the current node.
        neighbors = getNeighbors(current, unvisited)

        # Evaluate all the neighbors and update the distances.
        for neighbor in neighbors:
            if current.distance + 1 < neighbor.distance:
                neighbor.distance = current.distance + 1
        
        # Mark the current node as visited.
        current.visited = True

        # Remove the current node from the unvisited set.
        del unvisited[current.y][current.x]
        if len(unvisited[current.y].keys()) == 0:
            del unvisited[current.y]

        # Among the neighbors, select the one with the smallest distance.
        smallestDistance = math.inf
        for y in unvisited:
            for x in unvisited[y]:
                if unvisited[y][x].distance < smallestDistance:
                    current = unvisited[y][x]
                    smallestDistance = unvisited[y][x].distance

    return current.distance if targetLocation else None

# Returns a list of the neighbors of the current nodes among the nodes provided.
def getNeighbors(current, nodes): 
    neighbors = []
    if current.x - 1 in nodes[current.y]:
        neighbors.append(nodes[current.y][current.x - 1])
    if current.x + 1 in nodes[current.y]:
        neighbors.append(nodes[current.y][current.x + 1])
    if current.y - 1 in nodes and current.x in nodes[current.y - 1]:
        neighbors.append(nodes[current.y - 1][current.x])
    if current.y + 1 in nodes and current.x in nodes[current.y + 1]:
        neighbors.append(nodes[current.y + 1][current.x])
    
    return neighbors

if __name__ == '__main__':
    main('controller.dat')