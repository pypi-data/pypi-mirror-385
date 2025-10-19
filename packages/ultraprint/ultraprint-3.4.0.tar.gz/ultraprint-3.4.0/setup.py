from setuptools import setup, find_packages

setup(
    name='ultraprint',
    version='3.4.0',
    license="MIT License with attribution requirement",
    author="Ranit Bhowmick",
    author_email='bhowmickranitking@duck.com',
    description='''Ultraprint is a versatile Python library that enhances your command-line output with colorful text, styled formatting, and easy-to-use logging utilities. Perfect for creating visually appealing console applications.''',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/Kawai-Senpai/UltraPrint',
    download_url='https://github.com/Kawai-Senpai/UltraPrint',
    keywords=["Printing", "Console", "Formatting", "Logging", "Colored Output", "Styled Text"],
    install_requires=[],
)
