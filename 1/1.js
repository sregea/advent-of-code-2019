// Import module to read data from files.
const fs = require('fs');

// Input filename.
const FILENAME = '1.dat';

// Solve the problem.
solveProblem(FILENAME);

function solveProblem(fileName)
{
    // Read asynchronously from the file.
    fs.readFile(fileName, (error, data) => {
        if (error) {
            throw error;
        }
        else {
            // Calculate the result.
            let result = processData(data.toString());
            console.log('Result: ' + result);
        }
    });
}

function processData(stringData)
{
    // Convert the string data into an array of numbers.
    let numbers = stringData.split('\n');

    let sum = 0;
    for (let i = 0; i < numbers.length; i++)
    {
        // Check that the string is valid.
        if (numbers[i])
        {
            console.log('Current number: ' + numbers[i]);
            sum += ((Math.floor(parseInt(numbers[i], 10) / 3)) - 2);
            console.log('Current sum: ' + sum);
        }
    }

    return sum;
}