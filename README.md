## Getting Started
---
In order to get started, you will first need to install the dependencies for this project.
This can be done by `pip install`ing the libraries in `requirements.txt`, as shown below:
```bash
pip3 install -r requirements.txt
```
Note: I would recommend creating a virtual environment for these installs

## Running simulations
---
Once the requirements have been run, there are several command-line parsers that have been added to help run the most important simulations.
These command-line arguments can be displayed as follows:
```bash
python3 experiment.py -h
```
Thereby giving us:
```bash
usage: experiment.py [-h] {runExperiment,simulate} ...

Commands to run the experiment

positional arguments:
  {runExperiment,simulate}
                        sub-command help
    runExperiment       runs experiment
    simulate            simulates experiment
```

To run an experiment, we can use 
```bash
python3 experiment.py runExperiment <output file> <inputToVary> <numSimulations>
```

To simulate an experiment, we can use 
```bash
python3 experiment.py simulate
```
with optional arguments
```bash
optional arguments:
  -h, --help            show this help message and exit
  --intention INTENTION, -i INTENTION
                        if gopher has intention (default true)
  --cautious CAUTIOUS, -c CAUTIOUS
                        if gopher is cautious (default false)
  --defaultProbEnter DEFAULTPROBENTER, -d DEFAULTPROBENTER
                        probability of gopher entering trap (not for intention, default 0.8)
  --probReal PROBREAL, -p PROBREAL
                        percentage of traps that are designed as opposed to random (default 0.2)
  --nTrapsWithoutFood NTRAPSWITHOUTFOOD, -n NTRAPSWITHOUTFOOD
                        the amount of traps a gopher can survive without entering (due to starvation, default 4)
  --maxProjectileStrength MAXPROJECTILESTRENGTH, -m MAXPROJECTILESTRENGTH
                        the maximum projectile strength (thickWire strength, default 0.45)
```

Finally, we can run the whole simulation and open it in the web browser using the command
```bash
python3 run.py
```

## Generating traps using the Genetic Algorithm
The genetic algorithm source code is found in the `geneticAlgorithm/` folder.
We have provided a CLI interface to allow a user to run the genetic algorithm from the command line.
To learn about these commands, simply run
```bash
python3 cli.py genetic-algorithm -h
```
which tells us:
```bash
usage: cli.py genetic-algorithm [-h] [--measure MEASURE] \
                                      [--threshold THRESHOLD] \
                                      [--maxIterations MAXITERATIONS] \
                                      [--log LOG] \
                                      [--improvedCallback IMPROVEDCALLBACK] \
                                      [--export EXPORT] \
                                      [--outputFile OUTPUTFILE] \
                                      [--show SHOW] \
                                      function

positional arguments:
  function              a choice of {random, coherence, functional}

optional arguments:
  -h, --help            'show this help message and exit'
  --measure MEASURE, -m MEASURE
                        'the measure for the threshold (max, mean, median, all)'
  --threshold THRESHOLD, -t THRESHOLD
                        'the threshold to use for termination in [0, 1]'
  --maxIterations MAXITERATIONS, -i MAXITERATIONS
                        'the maximum number of iterations to run'
  --log LOG, -l LOG     'whether or not to print the logs as generations increase'
  --improvedCallback IMPROVEDCALLBACK, -c IMPROVEDCALLBACK
                        'whether or not to use improved callback'
  --export EXPORT, -e EXPORT
                        'whether or not to export data to file (changed with -o flag)'
  --outputFile OUTPUTFILE, -o OUTPUTFILE
                        'the output file to which we write'
  --show SHOW, -s SHOW  'show output in browser'
```

Thus, to run a default simulation, we can run
```bash
python3 cli.py genetic-algorithm coherence
```

Some other notable flags are `--export` and `--show.` In this case, `--export` will create a file with name `--outputFile.` Additionally, if we pass the `--show` flag, then a simulation of the optimal trap will be opened in your browser.