# TubeCutterDXF

Programmatically create Spiral and Brickwork style patterns for rotary laser cutting tubing.

## Creating a Pattern
```python
from tubecutterdxf import CutPattern, CutBrick, CutSpiral, CutPartline, INCH

def newCutPattern():
    # Create the pattern container.  This stores the geometry and will help produce the DXF
    pattern = CutPattern()

    # Specify some general parameters
    OD = 1
    continuous = False # Change to True when ready to send to laser cutter

    # Define the cut pattern
    # Parting line at x = 0
    cutPartline = CutPartline(OD)
    # Spiral starting at x = 0.1in with 30deg cut followed by 10deg uncut repeating 5 times at a pitch of 0.1in with each cut increasing by 5deg and uncut portion decreasing by 5deg for each repetition.
    cutSpiral = CutSpiral(OD, 0.1 * INCH, 0, 30, 10, 0.1 * INCH, 5, variableCutLength=True, 5, -5, continuous=continuous)
    # Brick starting where cutSpiral left off with 3 90deg cuts equally spaced circumferentially and repeated 5 times with a pitch of 0.1in and each repetition offset by 45deg from the prior.  No variation in cut length.
    cutBrick = CutBrick(OD, cutSpiral.xNext, 0, 90, 3, 45, 0.1 * INCH, 5)
    
    # Add the cuts to the pattern container
    pattern.add(cutPartline)
    pattern.add(cutSpiral)
    pattern.add(cutBrick)

    # Preview the pattern in an interactive graph
    pattern.preview()

    # List the cuts added and remove any by their cut #
    pattern.printCutTable()
    pattern.remove(1)

    # Draw and Save the pattern to a file in the 'output' folder: this saves the .dxf and a .json config file
    pattern.draw()
    pattern.save("newCutPattern")
```
## Getting Started
Create a python virtual environment.  If you don't know what this is, Google "venv", it may change your life.

Install the required packages


    > pip install -r requirements.txt

Create a directory called "output" (I could do this for you in the code... but I don't want to)

    > mkdir ./output

Now you're ready to go back up to [Creating a Pattern](#creating-a-pattern)!

## Liability Release :)
This code has bugs, for one.  For another, be warned, if you are trying to make super small cuts you will run into floating point errors and anomalies due to the nature of how computers represent numbers.  This mainly affects non-continuous cut patterns due to the overflow calculation when a cut wraps beyond the circumference; most of these errors are avoided when you create a continuous cut pattern, which most rotary laser cutters prefer anyways!

Feel free to post any bugs or requests for improvements via [Issues](https://github.com/qwiebe/TubeCutterDXF/issues).