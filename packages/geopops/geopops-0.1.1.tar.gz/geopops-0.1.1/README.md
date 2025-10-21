# GeoPops
**Full documentation and tutorials coming soon!**

GeoPops is a package for generating geographically and demographically realistic synthetic populations for any US Census location using publically available data. Population generation includes three steps:
1. Generate individuals within households using combinatorial optimization (CO)
2. Assign individuals to schools and workplace locations using enrollment data and commute flows
3. Connect individuals within locations using graph algorithms

Resulting files include a list of agents with attributes (e.g., age, gender, income) and networks detailing their connections within home, school, workplace, and group quarters (e.g., correctional facilities, nursing homes) locations. GeoPops builds on a previous package, [GREASYPOP-CO](https://github.com/CDDEP-DC/GREASYPOP-CO/tree/main), and incorporates the following changes:
- All code wrapped in convenient python package that can be pip installed
- Compatibility with Census data beyond 2019
- Fully automated data downloading
- Users can adjust all config parameters from the front-end
- Class for exporting files compatible with the agent-based modeling software [Starsim](https://starsim.org/)


## How to use
First, obtain a Census API key [here](https://api.census.gov/data/key_signup.html).
Then, Install GeoPops from [PyPI](https://pypi.org/project/geopops/).
```
pip install geopops
```

Next, create environment in our output directory folder. While called with Python commands, combinatorial optimization, school and workplace assignment, and network generation steps occur in Julia to decrease run time. Try running the following in the terminal.
```
curl -fsSL https://install.julialang.org | sh
juliaup add 1.9.0        # install Julia 1.9.0
juliaup default 1.9.0    # make 1.9.0 the default (optional)
julia +1.9.0 --version   # run that version once
juliaup update           # update installed versions
julia                    # launch Julia and see version
]                        # enter package mode. prompt changes to "(@v1.9) pkg>"
add CSV@0.10.15          # add required package versions
add DataFrames@1.7.0
add Graphs@1.8.0 
add InlineStrings@1.4.0 
add JSON@0.21
status                   # view list of packages
```


You'll also need a Python environment with the dependencies listed in `pyproject.toml`. Now in a Python or Notebook script, create a dictionary of parameters. Default parameters are stored in a package file called `config.json`. Pass your dictionary into `WriteConfig()` to overwrite config.json with the parameters for your population of interest. Here's an example to for Howard County, MD.
```
pars_geopops = {'path': 'YOUR_OUTPUT_DIR', # designate folder for output files
                'census_api_key': "YOUR_CENSUS_API_KEY", 
                'main_year': 2019, # year of data
                'geos': ["24027"], # state or county fips code of main geographical area
                'commute_states': ["24"], # fips of commute states to use
                'use_pums': ["24"]} # Same as commute_states
geopops.WriteConfig(**pars_geopops) # Overwrite config.json with your parameters
```
The following commands will create your popoulation and store files in the output directory defined above. Downloaded raw data files are stored in the subfolders census, geo, pums, school, and work. Files created in the preprocessing step are stored in the subfolder called processed. The population in jlse format is stored in the subfolder jlse. `Export()` outputs csv versions into the subfolder pop_export. `ForStarsim()` outputs files formated for use with Starsim into the subfolder pop_export/starsim.
```
geopops.DownloadData()  # Download all Census and other data sources
geopops.ProcessData()   # Preprocessing for next steps
geopops.RunJulia()      # Run Julia scripts (much faster than Python)
geopops.ForStarsim()    # Format people and networks for Starsim
```
## Tutorials
For more detailed descriptions of each step, see the tutorials folder.

