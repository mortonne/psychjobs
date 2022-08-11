"""Scrape information from the psychjobswiki."""

from urllib import request
import dateutil.parser as dparser
from dateutil.parser import ParserError
import re
import argparse
from bs4 import BeautifulSoup
import pandas as pd


def parse(soup, p):
    """Parse a job entry."""
    links = [a['href'] for a in p.find_all('a') if a.has_attr('href')]
    if not links:
        raise ValueError('No link found.')

    if '#' in links[0]:
        # if first link is within page, follow it
        a_linked = soup.find('a', attrs={'name': links[0][1:]})
        if a_linked is not None:
            return parse(soup, a_linked.parent)

    if len(p.contents) < 4:
        return None

    bold = p.find_all('strong')
    institute = bold[0].contents[0] if bold else None
    status = bold[1].contents[0] if len(bold) > 1 else None

    contents = [c for c in p.contents if isinstance(c, str) and c.strip()]
    description = m.group(0) if (m := re.search(r'\w.*\w', contents[0])) else None

    s_date = m.group(0) if (m := re.search(r'\w.*\w', contents[1])) else None
    if s_date is not None:
        try:
            date, text = dparser.parse(s_date, fuzzy_with_tokens=True)
        except ParserError:
            date = None
        if date is not None:
            due = text[0].strip()
        else:
            due = s_date
    else:
        date = None
        due = None

    job = pd.Series(
        {
            'area': '',
            'institute': institute,
            'date': date,
            'due': due,
            'status': status,
            'description': description,
            'link': ','.join([l for l in links if not l.startswith('#')]),
        }
    )
    return job


def find_area_jobs(soup, area):
    """Find all jobs within an area."""
    target = soup.find('h3', text=area)
    if target is None:
        return None

    job_list = []
    for sib in target.find_next_siblings():
        if sib.name == "h3":
            break
        else:
            try:
                job = parse(soup, sib)
            except ValueError:
                print(f'Problem parsing entry: {sib.text}')
                continue
            if job is None:
                continue
            if job['institute'] is None or job['description'] is None:
                continue
            job['area'] = area
            job_list.append(job)
    jobs = pd.DataFrame(job_list)
    return jobs


def find_jobs(soup, areas):
    """Find all jobs in a list of areas."""
    area_list = []
    for area in areas:
        area_jobs = find_area_jobs(soup, area)
        area_list.append(area_jobs)
    jobs = pd.concat(area_list, axis=0, ignore_index=True)
    return jobs


def scrape_areas(areas):
    """Scrape the psych jobs wiki."""
    page = request.urlopen('http://psychjobsearch.wikidot.com')
    soup = BeautifulSoup(page, 'html.parser')
    jobs = find_jobs(soup, areas).sort_values(['area', 'date', 'institute'])
    return jobs


def scrape():
    """Scrape all areas and write to a spreadsheet."""
    doc = """
        Scrape job information and write to a spreadsheet.
    
        Areas codes are:
        
        cog: Cognitive
        neuro: Neuroscience & Biopsychology
        quant: Quantitative
        open: Open Area
        clinic: Clinical & Counseling
        comm: Community
        dev: Developmental
        ed: Educational
        health: Health
        eng: Human Factors & Engineering Psychology
        io: Industrial-Organizational (I-O)
        school: School
        social: Social & Personality
        other: Other
    """
    parser = argparse.ArgumentParser(
        description=doc, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('spreadsheet', help='path to csv file')
    parser.add_argument(
        '--areas', '-a', help='comma-separated list of areas to include'
    )
    args = parser.parse_args()

    areas = {
        'cog': 'Cognitive',
        'neuro': 'Neuroscience & Biopsychology',
        'quant': 'Quantitative',
        'open': 'Open Area',
        'clinic': 'Clinical & Counseling',
        'comm': 'Community',
        'dev': 'Developmental',
        'ed': 'Educational',
        'health': 'Health',
        'eng': 'Human Factors & Engineering Psychology',
        'io': 'Industrial-Organizational (I-O)',
        'school': 'School',
        'social': 'Social & Personality',
        'other': 'Other',
    }
    if args.areas is None:
        area_codes = list(areas.keys())
    else:
        area_codes = args.areas.split(',')
    areas_included = [areas[code] for code in area_codes]
    jobs = scrape_areas(areas_included)

    # split links
    split = jobs['link'].str.split(',', expand=True)
    split.columns = [f'link{i+1}' for i in split.columns]
    jobs = pd.concat([jobs.drop('link', axis=1), split], axis=1)

    jobs.to_csv(args.spreadsheet, index=False)
