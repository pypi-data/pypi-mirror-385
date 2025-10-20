# Resume Compiler

A compiler that compiles Markdown files into a resume PDF file, formatted in LaTeX.

Resumes outputted by this compiler will follow the structure given by the ["Jake's Resume" template](https://www.overleaf.com/latex/templates/jakes-resume/syzfjbzwjncs).


## Installation

The compiler is available as a [Python package on PyPI](https://pypi.org/project/resumecompiler/). To install the compiler through ```pip```, simply run the following terminal command.

```aiignore
pip install resumecompiler
```


## Terminology

This section introduces several terms (in bold) used throughout this project and its documentation. The ["Jake's Resume" template](https://www.overleaf.com/latex/templates/jakes-resume/syzfjbzwjncs) will be used as an example.

- **Title.** The candidate's first and last name, as displayed at the top of the resume, e.g. ```Jake Ryan```.
- **Contact information.** A list of the candidate's contact details, e.g. ```123-456-7890 | jake@su.edu | ... | github.com/jake```.
- **Section.** In the resume, all achievements, experiences and projects (resume items) are classified into several categories. Each of these categories constitutes a section of the resultant document, such as ```Education```, ```Experience```, ```Projects``` or ```Technical Skills```. As explained below, a section can be any one of the following:
  - a toolset section,
  - an organisational section, or
  - a catalogue section.
- **Heading.** The text that marks the start of each section.
- **Resume item.** An achievement, experiences or project as listed in a toolset or organisational section. (A catalogue section cannot contain any resume items.) A resume item contains:
  - A subheading that describes the achievement, e.g. ```Undergraduate Research Assistant```.
  - A description list that offers brief details thereof, e.g. ```• Developed a REST API using...```.
  - Other auxiliary information detailing the relevant time, organisation and location, if needed.
- **Subheading.** The text that marks the start of each resume item.
- **Description list.** Each resume item ends with an optional list of sentences providing details to the achievement, experience or project. This is called the description list.
- **Toolset section.** In some sections, resume items are formatted as follows, with the subheading and auxiliary information packed into one row. These resume items usually include information such as tools and skills relevant to the achievement, experience or project. These sections are called toolset sections.

```aiignore
Gitlytics | Python, Flask, React...     June 2020 – Present

• Description list item #1
• Description list item #2
```

- **Organisational section.** In some sections, resume items are formatted like so, with the subheading and auxiliary information placed in a 2x2 grid. These sections are called organisational sections.

```aiignore
Undergraduate Research Assistant     June 2020 – Present
Texas A&M University                 College Station, TX

• Description list item #1
• Description list item #2
```

- **Catalogue section.** A type of section that contains a simple unordered list, e.g. ```Technical skills```. Each item in the unordered list may optionally begin with a label (e.g. ```Languages```).


## Syntax

### Add a title

A title can be added using an H1 line.

```aiignore
# Jake Ryan
```

The title must precede the first section.


### Add a contact list

A contact list can be added using an unordered list. The list may contain hyperlinks. If a contact list item contains both a hyperlink(s) and plain text, only the first hyperlink will be displayed.

```aiignore
# Jake Ryan
- 123-456-7890
- jake@su.edu
- [resume-compiler.com](resume-compiler.com)
```

A contact list must precede the first section.


### Add an organisational section

Create a new section by adding an H2 heading.

```aiignore
## Education
```

For each resume item, create an H3 subheading. This is followed by an indented preformatted code block containing three lines of auxiliary information. These will appear from left to right and from top to bottom in the compiled document.

```aiignore
### Undergraduate Research Assistant 
    June 2020 - Present
    Texas A&M University
    College Station, TX
```

Add a description list by adding an unordered list afterwards.

```aiignore
### Undergraduate Research Assistant 
    June 2020 - Present
    Texas A&M University
    College Station, TX

- Description list item #1
- Description list item #2
```


### Add a toolset section

Create a new section by adding an H2 heading. To indicate that this is a toolset section, prefix the heading with an exclamation mark.

```aiignore
## !Projects
```

For each resume item, create an H3 subheading. This is followed by an indented preformatted code block containing two lines of auxiliary information. These will appear from left to right in the compiled document.

```aiignore
### Gitlytics
    Python, Flask, React, PostgreSQL, Docker
    June 2020 - Present
```

Add a description list by adding an unordered list afterwards.

```aiignore
### Gitlytics
    Python, Flask, React, PostgreSQL, Docker
    June 2020 - Present

- Description list item #1
- Description list item #2
```


### Add a catalogue section

Create a new section by adding an H2 heading. A catalogue section contains no resume items, so do not add any H3 subheadings here.

```aiignore
## Technical Skills
```

Complete the catalogue section by adding an unordered list. Each item in the unordered list may optionally begin with a label (e.g. Languages), like so:

```aiignore
## Technical Skills

- Languages: Java, Python, ...
- Another label: Something else, ...
```


### Add comments

Any text that is not part of a title, contact list, heading, subheading or resume item (i.e. that when translated to HTML does not belong to a tag) will be ignored and treated as a comment.


### Hide resume items

To hide a resume item in an organisational or toolset section, prefix its subheading with a caret (```^```).

For example, including the following resume item in a toolset section will have no effect on the final compiled PDF document.

```aiignore
### ^Gitlytics
    Python, Flask, React, PostgreSQL, Docker
    June 2020 - Present

- Description list item #1
- Description list item #2
```


### Escape characters

Some characters have special meaning in LaTeX and should be escaped using backslashes (```\```) when writing Markdown source code.



| Character |                Escape sequence in Markdown                 |
|:---------:|:----------------------------------------------------------:|
|  ```&```  |                          ```\&```                          |
|  ```%```  |                          ```\%```                          |
|  ```$```  |                          ```\$```                          |
|  ```#```  | ```\#``` in preformatted code blocks, ```\\\#``` otherwise |
|  ```_```  | ```\_``` in preformatted code blocks, ```\\\_``` otherwise |
|  ```{```  | ```\{``` in preformatted code blocks, ```\\\{``` otherwise |
|  ```}```  | ```\}``` in preformatted code blocks, ```\\\}``` otherwise |
|  ```~```  |                   ```\textasciitilde```                    |
|  ```^```  |                   ```\textasciicircum```                   |
|  ```\```  |                    ```\textbackslash```                    |



### LaTeX injections

When necessary, it is possible to inject LaTeX code into Markdown source code (especially in preformatted code blocks). Note, however, that precautions should be taken and escape sequences should be used.


## Compilation

To compile a markdown file in the source directory into a LaTeX file in the destination directory, install the ```resumecompiler``` package via ```pip``` (see the "Installation" section above) and import the class ```ResumeCompiler``` in a Python file.

```aiignore
from resumecompiler import ResumeCompiler
```

Create a ```ResumeCompiler``` instance with the source and destination directory paths as arguments. To execute the compilation process, run any one of the methods on the ```ResumeCompiler``` object:
- ```ResumeCompiler.compile(src_file_path, font)``` compiles the file specified by the inputted path.
- ```ResumeCompiler.run(font)``` compiles all Markdown files in the source directory and saves the results in the destination directory, with each LaTeX file in a different subdirectory.
- ```ResumeCompiler.run_with_live_reload(font)``` runs a loop to continuously detect when a Markdown file in the source directory is created or saved. Whenever this happens, that file is compiled with outputs saved in the destination directory.

```aiignore
from resumecompiler import ResumeCompiler

compiler = ResumeCompiler("src", "dist")
compiler.run_with_live_reload()
```

Each of these methods includes an optional ```font``` parameter that determines the typeface used to create the PDF document. This parameter takes an instance of the enum class ```Font```, which can be any of the following.

- ```Font.COMPUTER_MODERN```
- ```Font.TIMES_NEW_ROMAN```
- ```Font.FIRA_SANS```
- ```Font.ROBOTO```
- ```Font.NOTO_SANS```
- ```Font.SOURCE_SANS_PRO```
- ```Font.CORMORANT_GARAMOND```
- ```Font.CHARTER```

The argument defaults to Times New Roman (```Font.TIMES_NEW_ROMAN```). See an example code snippet below.

```
from resumecompiler.Enums.Font import Font
from resumecompiler import ResumeCompiler

compiler = ResumeCompiler("example-src", "example-dist")
compiler.run_with_live_reload(font=Font.TIMES_NEW_ROMAN)
```


### Accessing the Resume object

The compiler works by reading the contents of the input Markdown file and then creating a corresponding ```Resume``` object. To access this internal ```Resume``` object, use the function ```get_resume_object_from_markdown```. The function takes the path to the Markdown source file as input.

```aiignore
resume = get_resume_object_from_markdown('example-src/example.md')
```


## Future improvements

Future improvements with regard to more robust parsing and compilation:

- More user-friendly error handling
- More mature handling of escape characters and LaTeX injection
- UML visualisation of classes