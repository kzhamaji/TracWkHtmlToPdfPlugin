from setuptools import setup

extra = {}

setup(
    name='TracWkHtmlToPdfPlugin',
    #description='',
    #keywords='',
    #url='',
    version='0.1',
    #license='',
    #author='',
    #author_email='',
    #long_description="",
    packages=['tracwkhtmltopdf'],
    package_data={
        'tracwkhtmltopdf': []
    },
    entry_points={
        'trac.plugins': [
            'tracwkhtmltopdf.api = tracwkhtmltopdf.api',
        ]
    },
    **extra
)
