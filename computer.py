# computer.py is the module for executing Intcode programs.
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
OPCODE_RELBASE_OFFSET = 9
OPCODE_HALT = 99

# Define the parameter modes.
PARAM_MODE_POSITION = 0
PARAM_MODE_VALUE = 1
PARAM_MODE_RELATIVE = 2

# Different ways a program can finish its execution.
FINISH_HALT = 0
FINISH_FIRST_OUTPUT = 1
FINISH_ERROR = 10

# This class defines a program that can be executed by the Intcode computer.
class Program():
    # If no instructions are given, set them to an empty list.
    def __init__(self, instructions=[]):
        # Get a copy of the instructions.
        self.instructions = copyList(instructions)
        self.length = len(self.instructions)
        self.opcode = None

        # Set the default execution variables.
        self.position = 0
        self.inputs = []
        self.outputs = []
        self.relativeBase = 0

        # Set the default config variables.
        self.terminal = True
        self.returnOnOutput = False
    
    # The program receives a new set of instructions.
    def setInstructions(self, instructions):
        self.instructions = copyList(instructions)
        self.length = len(self.instructions)
    
    # Returns a copy of the current instructions.
    def getInstructions(self):
        return copyList(self.instructions)
    
    # Resets all the relevant variables for the execution.
    def resetExecutionState(self):
        self.position = 0
        self.inputs = []
        self.outputs = []
        self.relativeBase = 0
    
    # Reset the instruction position to the beginning.
    def resetPosition(self):
        self.position = 0
    
    # Resets all the config variables.
    def resetConfigState(self):
        self.terminal = True
        self.returnOnOutput = False
    
    # Decide if you want the outputs printed to the terminal.
    def printOutputs(self, decision):
        self.terminal = decision
    
    # Requests that the program returns on the first output.
    def returnOnFirstOutput(self, decision):
        self.returnOnOutput = decision
    
    # Receives a list of integer inputs and stores them for later use
    # on input instructions.
    def setInputs(self, input):
        self.inputs = copyList(input)
    
    # Adds to the existing inputs. values parameter has to be a list.
    def appendToInputs(self, values):
        for value in values:
            self.inputs.append(value)
    
    # Returns a copy of the outputs generated by the program.
    def getOutputs(self):
        return copyList(self.outputs)
    
    def emptyOutputs(self):
        self.outputs = []
    
    # Receives a number that represents an address. If there is no memory yet at
    # that address, fill the existing instructions until that address with zeros.
    def check(self, number):
        if number >= len(self.instructions):
            for i in range(number - len(self.instructions) + 1):
                self.instructions.append(0)
        
        self.length = len(self.instructions)
        return number
    
    # The place to store a value depends if the address is given in positional
    # or relative mode.
    def storeAt(self, address, modeIndex, value):
        # First decide if we have to store the value in position or relative mode.
        mode = self.opcode.modes[modeIndex] if len(self.opcode.modes) >= modeIndex + 1 else PARAM_MODE_POSITION

        # Store the value according to the mode.
        if mode == PARAM_MODE_POSITION:
            self.instructions[self.check(address)] = value
        elif mode == PARAM_MODE_RELATIVE:
            self.instructions[self.check(address + self.relativeBase)] = value
    
    # Receives a starting position in memory and a number of parameters, and returns a list
    # with the values of those parameters.
    def parseParameters(self, start, number):
        values = []

        # Try to give a value to all parameters requested.
        for i in range(number):
            if i < len(self.opcode.modes):
                # This parameter has a mode associated with it.
                if self.opcode.modes[i] == PARAM_MODE_POSITION:
                    value = self.instructions[self.check(self.instructions[self.check(start + i)])]
                elif self.opcode.modes[i] == PARAM_MODE_VALUE:
                    value = self.instructions[start + i]
                elif self.opcode.modes[i] == PARAM_MODE_RELATIVE:
                    value = self.instructions[self.check(self.instructions[self.check(start + i)]  + self.relativeBase)]
            else:
                # No mode has been supplied, the default is position mode.
                value = self.instructions[self.check(self.instructions[self.check(start + i)])]
            values.append(value)

        return values
    
    # Executes the instructions of this program with the current settings.
    def execute(self):
        while self.position < self.length:

            # Parse the next opcode.
            self.opcode = Opcode(self.instructions[self.check(self.position)])

            # Execute the appropriate operation.
            if self.opcode.opcode == OPCODE_SUM:
                self.executeSum()
            elif self.opcode.opcode == OPCODE_MULTIPLY:
                self.executeMultiplication()
            elif self.opcode.opcode == OPCODE_INPUT:
                self.executeInput()
            elif self.opcode.opcode == OPCODE_OUTPUT:
                self.executeOutput()
                if self.returnOnOutput:
                    return FINISH_FIRST_OUTPUT
            elif self.opcode.opcode == OPCODE_JUMP_IF_TRUE:
                self.executeJumpIfTrue()
            elif self.opcode.opcode == OPCODE_JUMP_IF_FALSE:
                self.executeJumpIfFalse()
            elif self.opcode.opcode == OPCODE_LESS_THAN:
                self.executeLessThan()
            elif self.opcode.opcode == OPCODE_EQUALS:
                self.executeEquals()
            elif self.opcode.opcode == OPCODE_RELBASE_OFFSET:
                self.executeRelativeBaseOffset()
            elif self.opcode.opcode == OPCODE_HALT:
                return FINISH_HALT
            else:
                print('ERROR: opcode {} not recognised by the computer'.format(self.instructions[self.position]))
                return FINISH_ERROR
    
        return FINISH_ERROR
    
    def executeSum(self):
        # Parse the two parameters needed.
        values = self.parseParameters(self.position + 1, 2)

        # Store the result at the appropriate address.
        self.storeAt(self.instructions[self.check(self.position + 3)], 2, values[0] + values[1])

        # Update the position of the next instruction.
        self.position += 4
    
    def executeMultiplication(self):
        # Parse the parameters to know the values.
        values = self.parseParameters(self.position + 1, 2)

        # Store the result at the appropriate address.
        self.storeAt(self.instructions[self.check(self.position + 3)], 2, values[0] * values[1])

        # Jump four positions.
        self.position += 4

    def executeInput(self):
        # Decide if the input was given, else ask for it from the command line.
        if self.inputs != None and len(self.inputs) >= 1:
            number = self.inputs[0]
            del self.inputs[0]
        else:
            number = input('Input: ')

        # Store it at the selected position.
        self.storeAt(self.instructions[self.check(self.position + 1)], 0, int(number))

        # Update position.
        self.position += 2
    
    def executeOutput(self):
        # Find the value to output.
        values = self.parseParameters(self.position + 1, 1)

        # Store the value in the output list.
        self.outputs.append(values[0])

        # Print to the terminal if requested.
        if self.terminal:
            print('Output: {}'.format(values[0]))

        # Update the position.
        self.position += 2

    def executeJumpIfTrue(self):
        values = self.parseParameters(self.position + 1, 2)

        self.position = values[1] if values[0] != 0 else self.position + 3
    
    def executeJumpIfFalse(self):
        values = self.parseParameters(self.position + 1, 2)

        self.position = values[1] if values[0] == 0 else self.position + 3
    
    def executeLessThan(self):
        values = self.parseParameters(self.position + 1, 2)

        # Store a 1 if less than, else store a 0.
        self.storeAt(self.instructions[self.check(self.position + 3)], 2, 1 if values[0] < values[1] else 0)

        self.position += 4
    
    def executeEquals(self):
        values = self.parseParameters(self.position + 1, 2)

        # Store a 1 if equals, else store a 0.
        self.storeAt(self.instructions[self.check(self.position + 3)], 2, 1 if values[0] == values[1] else 0)

        self.position += 4
    
    def executeRelativeBaseOffset(self):
        values = self.parseParameters(self.position + 1, 1)

        # Adjust the relative base by the value of the only parameter.
        self.relativeBase += values[0]

        # Jump two positions.
        self.position += 2

# Stores information about an opcode.
class Opcode():
    def __init__(self, opcode):
        # Get the opcode itself.
        self.opcode = opcode % 100

        # Get the modes of the parameters specified.
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
