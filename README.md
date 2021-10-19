# psychjobs
Tools for scraping psychology faculty position information from the internet.

## Installation

You must have Python (3.8 or greater) installed. Then run:
```bash
pip install git+git://github.com/mortonne/psychjobs
```

## Usage

To scrape http://psychjobsearch.wikidot.com/ for 
jobs listed under Cognitive or Neuroscience & 
Biopsychology and save to a CSV file:
```bash
psychjobs jobs.csv --areas cog,neuro
```

To see the codes for the different areas:
```bash
psychjobs -h
```
