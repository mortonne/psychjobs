import setuptools


setuptools.setup(
    entry_points={
        'console_scripts': [
            'scrape = psychjobs.wiki:scrape',
        ],
    }
)
