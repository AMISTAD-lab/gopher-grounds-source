## Original Source Code:
The source code for this project is based off of the Gopher's Gambit source code, commit 0d53c9a. That code can be found here:
[Gopher's Gambit Source](https://github.com/amanirmk/AMISTAD-intention-exp3/tree/0d53c9acc48591a7ace67b6032ca5edc54665a7a)

## Getting Started
In order to get started, you will first need to install the dependencies for this project.
This can be done by `pip install`ing the libraries in `requirements.txt`, as shown below:
```
pip3 install -r requirements.txt
```
Note: I would recommend creating a virtual environment for these installs

## Project Structure
Please refer to the following for the project structure. Most of the important files have been added, as well.
```
.
+-- gopher-cli.py
+-- README.md
+-- requirements.txt
+-- animation/
+-- classes/
|   +-- Board.py
|   +-- Cell.py
|   +-- Door.py
|   +-- Encoding.py
|   +-- Gopher.py
|   +-- Projectile.py
|   +-- Trap.py
|   +-- Wire.py
+-- database/
|   +-- client.py
|   +-- constants.py
|   +-- library.py
|   +-- plot.py
|   +-- setup.py
+-- enums/
+-- experiments/
|   +-- new_encoding/
|   |   +-- functional/
|   |   +-- multiobjective/
|   |   +-- coherence/
|   |   ...
|   +-- old_encoding/
|   |   ...
+-- frequencies/
|   +-- new_encoding/
|   |   +-- functional/
|   |   +-- multiobjective/
|   |   +-- coherence/
|   |   ...
|   +-- old_encoding/
|   |   ...
+-- geneticAlgorithm/
|   +-- analytical.py
|   +-- cellarray.py
|   +-- constants.py
|   +-- experiment.py
|   +-- fitnessFunctions.py
|   +-- library.py
|   +-- main.py
|   +-- utils.py
+-- images/
+-- legacy/
+-- libs/
+-- misc/
|   +-- visualization.py
|   +-- visualizationHelpers.py
+-- sc/
|   +-- goodTuring.py
|   +-- realExperiment.py
|   +-- scExperiment.py
```

## Interacting with the CLI
We have provided a command line interface (CLI) interface to allow users to more easily interact with the code without having to dig through files. To access the CLI, simple execute the command
```
./gopher-cli.py -h
```
If this doesn't work, then try adding executable permissions to the file via `chmod u+x gopher-cli.py`.
Finally, if that fails, we can also interact with the CLI using
```
python3 gopher-cli.py -h
```

## Defining an encoding
For most of the subparsers in the CLI, the encoding of a trap can be specified.
By default, the encoding of the list is [0..11].
To set the permutation, use the `--permutation (-p)` flag as follows:
`--permutation <string_encoding>`, (i.e. `--permutation '[0, 1, 2, ...]'`)

For our convenience, we have provided the hot key `-p 1` to set the permutation to the default permutation used in the code base:
<center><code>[9, 6, 3, 0, 1, 2, 5, 8, 11, 10, 7, 4]</code></center>

## Simulating a trap
We have provided a CLI command to simulate an arbitrary encoded trap. To use this command, simply call
```
./gopher-cli.py genetic-algorithm simulate '<trap_encoding> -h HUNGER -in?'
```
where <trap_string> is a string of the encoded trap (or the encoded trap surrounded by ''s). This should open your browser and play a simulation of the encoded trap. An example to trap is:
```
./gopher-cli.py genetic-algorithm simulate '[ 43, 7, 8, 72, 1, 23, 38, 2, 26, 8, 0, 25 ]'
```
Additionally, we can user the `--hunger` (`-h`) and `--intention` (`-in`) flags to set the gopher's hunger (in the interval (0, 1)) or simulate the gopher with intention, respectively.

We have also implemented a camera-ready functionality, which allows the user to open a static image of the board in the browser.
This option takes in the following arguments:
```
./gopher-cli.py genetic-algorithm simulate '<trap_encoding>' -na -g '<state_encoding> -f FRAME_NUM'
```
The `--no-animation` (`-na`) flag tells the compiler to turn off animation, and the `--gopher-state` (`-g`) flag tells the compiler to put a gopher on the board with state `<state_encoding>.`
The `<state_encoding>` is formatted as `[x, y, rotation, state],` where (`x`, `y`) is the gopher's 0-indexed position from the top left, `rotation` is the gopher's rotation in degrees, and `state` is the index of the gopher's health state, in the order `[dead, alive, hit].`
The default state is `[1, 4, 0, 1].`
Finally, we have the `--frame` (`-f`) flag that determines what frame of the trap the board should display

## Showing a trap as a PDF
The CLI has also been equipped to take in a trap string and generate a PDF of the given trap.
The command is as follows:
```
usage: gopher-cli.py genetic-algorithm show-trap [-h] [--save] [--output OUTPUT] [--no-pdf] [--no-gopher] trap

positional arguments:
  trap                  the encoded trap as a string (surrounded by ''s)

optional arguments:
  -h, --help            show this help message and exit
  --save, -s            whether or not to save the trap created
  --output OUTPUT, -o OUTPUT
                        the name of the file (no extensions) to be saved
  --no-pdf, -np         do not show PDF
  --no-gopher, -ng      do not show the gopher
```
The flags are as follows:
| Flag | Abbrev. | Default | Description |
| :--: | :----------: | :-----: | :---------: |
| --help | -h | N/A | help for any given parser|
| --save | -s | False | whether or not to save the PDF |
| --output | -o | 'generatedTrap' | the file name to save the trap to |
| --no-pdf | -np | False | will not show a PDF after the code executes |
| --no-gopher | -ng | False | will remove the gopher from the PDF |

All traps can be found in the `images/traps/` folder. If this folder does not exist, it must first be made.

## Getting the Fitness of a Gopher
To find the fitness of an arbitrary list encoding, we can use the CLI command:
```
./gopher-cli.py genetic-algorithm check-fitnesses '<trap_encoding>'
```

## Using the CLI to interact with the Genetic Algorithm
The genetic algorithm source code is found in the `geneticAlgorithm/` folder.
To learn about these commands, simply run
```
python3 cli.py genetic-algorithm -h
```
which tells us:
```
usage: gopher-cli.py genetic-algorithm [-h] {generate,runExperiment} ...

positional arguments:
  {generate,runExperiment}
                        genetic algorithm subparsers
    generate            generates a trap
    runExperiment       runs an experiment
```
We use the `generate` parser to generate trap using the genetic algorithm, and we use the `runExperiment` parser to generate a trap and then run an experiment.

For both the parsers, the fitness function will have to be given as input. The choices of fitness functions are:
- random: randomly generates a fitness for each member in a population
- coherence: assigns the fitness for each member in a population based on the coherence of that trap
- functional: assigns the fitness of each member in a population based on the function of that trap
- multiobjective: assigned the fitness of each member in a population based on both the coherence and function of that trap

Now, we can provide a table of the common flags that are shown in the help menu:

| Flag | Abbrev. | Default | Description |
| :--: | :----------: | :-----: | :---------: |
| --help | -h | N/A | help for any given parser|
| --max-generations | -g | 10,000 | maximum number of generations the algorithm runs |
| --no-logs | -nl | False | turns off logging during the genetic algorithm |
| --export | -e | False | exports outputs to a separate file (`-o` flag)| |
| --ouput-file | -o | x<sup>1</sup> | output file name (must include `.txt` extension) |
| --show | -s | False | simulates the trap in a browser (only for `generate` parser) |

These flags are just for the `genetic-algorithm runExperiment` parser:
| Flag | Abbrev. | Default | Description |
| :--: | :----------: | :-----: | :---------: |
| --num-simulations | -s | 10,000 | number of simulations to run on a trap |
| --no-print-stats | -np | False | turns off printing of simulation statistics |

These flags are for the `genetic-algorithm runBatchExperiments` parser:
| Flag | Abbrev. | Default | Description |
| :--: | :----------: | :-----: | :---------: |
| --num-experiments | -e | 10 | number of experiements to run |
| --max-generations | -g | 10,000 | maximum number of generations the algorithm runs |
| --ouput-suffix | -o | x<sup>1</sup> | the suffix to append to the end of the file name |
| --overwrite | -w | False | overwrites the experiment CSV file created with a new one |

<sup>1</sup> The default output file is 'geneticAlgorithm.txt' for the `generate` subparser and 'experiment.csv' for the `runExperiment` and `runBatchExperiments` subparsers. The file extension must be added.

Finally, we have added support for running batch experiments to the CLI. The command is
`./gopher-cli.py genetic-algorithm runBatchExperiments -h`.
Many of the flags can be found above, but one notable difference is the `--num-experiments` flag; this flag allows the user to determine how many experiments they want to run, and it defaults at 10 experiments. All outputs are generated in the `experiment.txt` file.

## Running legacy simulations
To run legacy simulations (from the Gopher's Gambit), we can simply use the legacy parser and follow the help command:
```
./gopher-cli.py legacy -h
```
Thereby giving us:
```
usage: gopher-cli.py legacy [-h] {runExperiment,simulate} ...

positional arguments:
  {runExperiment,simulate}
                        legacy parsers
    runExperiment       runs experiment
    simulate            simulates experiment

optional arguments:
  -h, --help            show this help message and exit
```

To run a legacy experiment, we can use 
```
./gopher-cli.py runExperiment <output file> <inputToVary> <numSimulations>
```

To simulate an experiment, we can use 
```
./gopher-cli.py simulate
```
with optional arguments
```
usage: cli.py simulate [-h] [--intention] \
                            [--cautious] \
                            [--defaultProbEnter DEFAULTPROBENTER] \
                            [--probReal PROBREAL] \
                            [--nTrapsWithoutFood NTRAPSWITHOUTFOOD] \
                            [--maxProjectileStrength MAXPROJECTILESTRENGTH]

optional arguments:
  -h, --help            show this help message and exit
  --intention, -i       turns on intention gopher
  --cautious, -c        if gopher is cautious
  --defaultProbEnter DEFAULTPROBENTER, -d DEFAULTPROBENTER
                        probability of gopher entering trap (not for intention)
  --probReal PROBREAL, -p PROBREAL
                        percentage of traps that are designed as opposed to random
  --nTrapsWithoutFood NTRAPSWITHOUTFOOD, -n NTRAPSWITHOUTFOOD
                        the amount of traps a gopher can survive without entering (due to starvation)
  --maxProjectileStrength MAXPROJECTILESTRENGTH, -m MAXPROJECTILESTRENGTH
                        the maximum projectile strength (thickWire strength)
```

Finally, we can run the whole simulation and open it in the web browser using the command
```
python3 run.py
```

## Help
If there are any questions or help is needed, you may email anshulkam@gmail.com.
