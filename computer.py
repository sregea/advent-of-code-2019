# computer.py is the module for executing intcode programs.
import pdb

# Define the opcodes.
OPCODE_SUM = 1
OPCODE_MULTIPLY = 2
OPCODE_INPUT = 3
OPCODE_OUTPUT = 4
OPCODE_JUMP_IF_TRUE = 5
OPCODE_JUMP_IF_FALSE = 6
OPCODE_LESS_THAN = 7
OPCODE_EQUALS = 8
OPCODE_HALT = 99

# Define the parameter modes.
PARAMETER_POSITION = 0
PARAMETER_VALUE = 1


# A class that defines a program.
class Program():
    def __init__(self, instructions=[]):
        # Copy the instructions.
        self.instructions = copyList(instructions)
        self.length = len(self.instructions)
        self.position = 0
        self.terminal = True
        self.inputs = []
        self.outputs = []
    
    # The program receives a new set of instructions.
    def setInstructions(self, instructions):
        self.instructions = copyList(instructions)
        self.length = len(self.instructions)
    
    # Returns a copy of the current instructions.
    def getInstructions(self):
        return copyList(self.instructions)
    
    # Decide if you want the outputs printed to the terminal.
    def printOutputs(self, decision):
        self.terminal = decision
    
    # Reset the instruction position to the beginning.
    def resetPosition(self):
        self.position = 0
    
    # Requests that the program returns on the first output.
    def returnOnOutput(self):
        self.returnOnOutput = True
    
    # Receives a list of integer inputs and stores them for later use
    # on input instructions.
    def setInputs(self, input):
        self.inputs = copyList(input)
    
    # Returns a copy of the outputs generated by the program.
    def getOutputs(self):
        return copyList(self.outputs)
    
    # Executes the instructions of this program with the current settings.
    def execute(self):
        while self.position < self.length:

            # Parse the next opcode.
            opcode = Opcode(self.instructions[self.position])

            # Execute the appropriate operation.
            if opcode.opcode == OPCODE_SUM:
                self.position = executeSum(self.instructions, self.position, opcode.modes)
            elif opcode.opcode == OPCODE_MULTIPLY:
                self.position = executeMultiplication(self.instructions, self.position, opcode.modes)
            elif opcode.opcode == OPCODE_INPUT:
                self.position = executeInput(self.instructions, self.position, self.inputs)
            elif opcode.opcode == OPCODE_OUTPUT:
                self.position = executeOutput(self.instructions, self.position, opcode.modes, self.outputs, self.terminal)
            elif opcode.opcode == OPCODE_JUMP_IF_TRUE:
                self.position = executeJumpIfTrue(self.instructions, self.position, opcode.modes)
            elif opcode.opcode == OPCODE_JUMP_IF_FALSE:
                self.position = executeJumpIfFalse(self.instructions, self.position, opcode.modes)
            elif opcode.opcode == OPCODE_LESS_THAN:
                self.position = executeLessThan(self.instructions, self.position, opcode.modes)
            elif opcode.opcode == OPCODE_EQUALS:
                self.position = executeEquals(self.instructions, self.position, opcode.modes)
            elif opcode.opcode == OPCODE_HALT:
                return
            else:
                print('ERROR: opcode {} not recognised by the computer'.format(self.instructions[self.position]))
                return
    
        return

# Stores information about an opcode.
class Opcode():
    def __init__(self, opcode):
        # Get the opcode itself.
        self.opcode = opcode % 100

        # Get the parameters modes.
        self.modes = []
        value = int(opcode / 100)
        while value >= 1:
            self.modes.append(value % 10)
            value = int(value / 10)

# Creates a copy of the list provided as a parameter.
def copyList(givenList):
    result = []
    for element in givenList:
        result.append(element)
    
    return result

# Receives a filename and returns a program with the instructions set to the
# values inside the file.
def readProgramFromFile(filename):
    return Program(readInstructionsFromFile(filename))

# Reads instructions from a file and returns them.
def readInstructionsFromFile(filename):
    with open(filename, 'r') as inputFile:
        instructions = [int(element) for element in inputFile.read().rstrip('\n').replace(' ', '').split(',')]
    
    return instructions

def copyProgram(initialProgram):
    return Program(initialProgram.instructions)    

# Receives a starting position and a set of instructions, and returns the values for the parameters.
# If in positional mode, it accessess the address, else it returns the value itself.
def parseParameters(instructions, position, modes, totalParameters):
    values = []
    for i in range(totalParameters):
        if i < len(modes):
            # We have a code for the parameters's mode.
            value = instructions[instructions[position + i]] if modes[i] == PARAMETER_POSITION else instructions[position + i]
        else:
            # The default mode is positional.
            value = instructions[instructions[position + i]]
        values.append(value)

    return values


def executeSum(instructions, position, modes):
    # Parse the parameters to know the values.
    values = parseParameters(instructions, position + 1, modes, 2)

    # Store the result at the appropriate address.
    instructions[instructions[position + 3]] = values[0] + values[1]

    return position + 4

def executeMultiplication(instructions, position, modes):
    # Parse the parameters to know the values.
    values = parseParameters(instructions, position + 1, modes, 2)

    # Store the result at the appropriate address.
    instructions[instructions[position + 3]] = values[0] * values[1]

    return position + 4

def executeInput(instructions, position, inputs):
    # Decide if the input was given, else ask for it from the command line.
    if inputs != None and len(inputs) >= 1:
        number = inputs[0]
        del inputs[0]
    else:
        number = input('Input: ')

    # Store it at the selected position.
    instructions[instructions[position + 1]] = int(number)

    return position + 2

def executeOutput(instructions, position, modes, outputs, terminal):
    # Find the value to output.
    values = parseParameters(instructions, position + 1, modes, 1)

    # Store the value in the output list.
    outputs.append(values[0])

    # Print to the terminal if requested.
    if terminal:
        print('Output: {}'.format(values[0]))

    return position + 2

def executeJumpIfTrue(instructions, position, modes):
    values = parseParameters(instructions, position + 1, modes, 2)

    return values[1] if values[0] != 0 else position + 3

def executeJumpIfFalse(instructions, position, modes):
    values = parseParameters(instructions, position + 1, modes, 2)

    return values[1] if values[0] == 0 else position + 3

def executeLessThan(instructions, position, modes):
    values = parseParameters(instructions, position + 1, modes, 2)

    instructions[instructions[position + 3]] = 1 if values[0] < values[1] else 0

    return position + 4

def executeEquals(instructions, position, modes):
    values = parseParameters(instructions, position + 1, modes, 2)

    instructions[instructions[position + 3]] = 1 if values[0] == values[1] else 0

    return position + 4