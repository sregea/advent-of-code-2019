// Import module to load info from files.
const fs = require('fs');

// Import module to execute the commands of the computer.
const computer = require('./computer.js');

// Final result we are looking for.
const SOLUTION = 19690720;

// File with the initial memory for all the tries.
const FILENAME = 'initialMemory.dat';

// Find the solution to the problem.
solveProblem(FILENAME);

function solveProblem(fileName)
{
    fs.readFile(fileName, (error, data) => {
        if (error)
        {
            throw error;
        }
        else
        {
            // Convert to a string.
            let parsedData = data.toString();
            console.log('Initial memory for the program: ');
            console.log(parsedData);

            // Transform into an array separating by commas.
            let board = parsedData.split(',');

            // Remove any unwanted elements in the array.
            for (let i = board.length - 1; i >= 0; i--)
            {
                if (!board[i])
                {
                    // Remove this element from the array.
                    board.splice(i, 1);
                }
                else
                {
                    // Transform it into an integer.
                    board[i] = parseInt(board[i], 10);
                }
            }

            // Pass this initial memory.
            let results = findValues(board);
            if (results != undefined)
            {
                let value = 100 * results.noun + results.verb;
                console.log('Noun: ' + results.noun);
                console.log('Verb: ' + results.verb);
                console.log('100 * noun + verb: ' + value);
            }
            else
            {
                console.log('No solution could be found...');
            }
            
        }
    });
}

// Receives a reference to the initial memory and tries to find the solution.
function findValues(initialMemory)
{
    let currentMemory = [];
    for (let noun = 0; noun < 100; noun++)
    {
        for (let verb = 0; verb < 100; verb++)
        {
            // Copy the initial memory into the current one.
            currentMemory = [];
            for (let k = 0; k < initialMemory.length; k++)
            {
                currentMemory.push(initialMemory[k]);
            }

            // Substitute the current noun and verb.
            currentMemory[1] = noun;
            currentMemory[2] = verb;

            // Find the solution.
            solution = computer.execute(currentMemory);

            if (solution == SOLUTION)
            {
                return {
                    noun: noun,
                    verb: verb
                };
            }
        }
    }

    // No solution was found.
    return undefined;
}