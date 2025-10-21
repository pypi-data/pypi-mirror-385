
# FredCollect

A modern Python wrapper for the Federal Reserve Economic Database (FRED) API.

## Installation

### From PyPI (recommended)
```bash
pip install fredcollect
```

### From source
1. Clone this repository:
```bash
git clone https://github.com/versaucc/fredcollect.git
cd fredcollect
```

2. Install the package:
```bash
pip install -e .
```

## Quick Start

1. Set up your FRED API key:
```bash
cp .env.example .env
# Edit .env and add your FRED API key
```

2. Verify the installation:
```python
from fredcollect import run
```

## Usage

Run a simple test:
```python
from fredcollect import run  
print(run.run_series_updates())
```

This will print the first and last 5 rows of the most recently updated series. 
This doesn't however, retrieve the observed values that were updated to the series. 

To do this we can take note of the id (series_id) and date: 
```python
from fredcollect import run
df = run.run_series_updates()
for row in df.loc[:,['id', 'title', 'last_updated']].itertuples(index=False):
    print(f"{row.title}:\n{run.run_series_observations(series_id=row.id, observation_start=row.last_updated)}") 
```
        
Will effortlessly fetch and print the series title and observations from that series. (I recommend adding a delay.)  
Likely you will find it easier to create a batch file to collect data from instead of the CLI.   
Take a look at `tests/test.py` to see usage examples of every possible FRED endpoint.   
Following this, you'll want to peek at `fredcollect/parameters.py` to see what types of arguments can be made for each endpoint.  


## In progress 
Currently, all endpoints make successful requests with required only parameters.   
Except for series/observations - which cleans datetime objects  
All functions can and will break when passed:   
    -Obscure arguments: like an extremely unpopular category id, discontinued series id, search text with certain symbols   

Issues with string formatting are next up on the boilerplate.  

Automated filesave:   
    -In /data_pipeline (currently obsolete) DataFrames and parameters passed here to automate the organization, naming, and saving of datasets.   
    -Maybe xlsx, likely csv.   

MatplotLib:   
    -Graphing, matching, statarb, etc.   


## License

Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0
