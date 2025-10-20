from setuptools import setup, find_packages

setup(
    name='resumecompiler',
    version='0.8',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['preamble.tex']},
    install_requires=[
        'markdown',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            # 'resume-compiler=resumecompiler.resumecompiler:main',  # if applicable
        ],
    },
    author='Raphael Li',
    description='A compiler that compiles Markdown files into a resume PDF file, formatted in LaTeX.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)