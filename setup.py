import setuptools


setuptools.setup(
    entry_points={
        'console_scripts': [
            'psychjobs = psychjobs.wiki:scrape',
        ],
    }
)
