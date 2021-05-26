## Getting Started
---
In order to get started, you will first need to install the dependencies for this project.
This can be done by `pip install`ing the libraries in `requirements.txt`, as shown below:
```bash
pip3 install -r requirements.txt
```
Note: I would recommend creating a virtual environment for these installs

## Running the simulations
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