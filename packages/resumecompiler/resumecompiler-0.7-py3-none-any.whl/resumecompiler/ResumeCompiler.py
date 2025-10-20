import os
from os.path import join, splitext, getmtime, basename
from pathlib import Path
import subprocess

from .ResumeComponents.Resume import Resume
from .Enums.Font import Font
from .Funcs.Funcs import create_and_write_file


class ResumeCompiler:
    def __init__(self, src_dir_path, dist_dir_path):
        """
        :param src_dir_path: The source directory path.
        :param dist_dir_path: The destination directory path.
        """
        self.src_dir = src_dir_path
        self.dist_dir = dist_dir_path

        # Last time files are saved
        # Key: Source file path
        # Value: Last modification time since the epoch (rounded)
        self.last_modification_timestamps: dict[str, int] = dict()

    def get_paths_to_markdown_files_in_src_dir(self):
        """
        :return: A list of paths to markdown files in the source directory.
        """
        result = []

        for directory_item in os.listdir(self.src_dir):
            # Ignore non-markdown files
            src_file_extension = splitext(directory_item)[1]

            if src_file_extension == ".md":
                src_file_path = join(self.src_dir, directory_item)
                result.append(src_file_path)

        return result

    def compile(self, src_file_path, font: Font = Font.TIMES_NEW_ROMAN):
        """
        :param src_file_path: The path to the source markdown file to be compiled.
        :param font: The font to use for the compiled resume.
        :return:
        """
        src_file_name = splitext(basename(src_file_path))[0]

        resume = get_resume_object_from_markdown(src_file_path)

        # Try to compile the markdown file to LaTeX
        try:
            latex_result = "\n".join(resume.to_latex_lines(font))
        except (Exception, IndexError) as e:
            print("MARKDOWN TO LATEX COMPILATION FAILED. ERROR:", e)
            return

        # Create and write to a destination file located in a subdirectory of the same name
        dest_file_path = Path(self.dist_dir, src_file_name, src_file_name + ".tex")
        create_and_write_file(dest_file_path, latex_result)

        # Compile latex to pdf
        compile_latex_file_to_pdf(dest_file_path)


    def run(self, font: Font = Font.TIMES_NEW_ROMAN):
        """
        :return: Compiles all markdown files in the source directory and saves the outputs in the destination directory.
        """
        for src_file_path in self.get_paths_to_markdown_files_in_src_dir():
            self.compile(src_file_path, font)

    def run_with_live_reload(self, font: Font = Font.TIMES_NEW_ROMAN):
        """
        :return: Runs a loop so that whenever a markdown file in the source directory is created or saved, it is compiled with the outputs saved in the destination directory.
        """
        while True:
            for src_file_path in self.get_paths_to_markdown_files_in_src_dir():
                last_mod_timestamp_recorded = self.last_modification_timestamps.get(src_file_path, -1)
                last_mod_timestamp_of_file = round(getmtime(src_file_path))

                if last_mod_timestamp_of_file == last_mod_timestamp_recorded:
                    continue

                self.last_modification_timestamps[src_file_path] = last_mod_timestamp_of_file
                self.compile(src_file_path, font)



def get_resume_object_from_markdown(src_file_path) -> Resume:
    """
    :param src_file_path: The path to the source markdown file from which the Resume object is to be read.
    :return: A Resume object.
    """
    with open(src_file_path, "r", encoding="utf-8") as markdown_file:
        return Resume(markdown_file.read())


def compile_latex_file_to_pdf(latex_file_path: Path, print_stdout_and_stderr: bool = True):
    """
    :param latex_file_path: The path to the LaTeX file.
    :param print_stdout_and_stderr: Whether to print the stdout and stderr messages to the console.
    :return: Compiles the specified LaTeX file to PDF, optionally printing stdout and stderr messages to the console.
    """
    # Change our working directory to where the destination tex file was created, then compile it to pdf
    parent_directory_of_latex_file = latex_file_path.parent.as_posix()

    process = subprocess.Popen(
        ['pdflatex', latex_file_path.name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        text=True,
        cwd=parent_directory_of_latex_file
    )

    if print_stdout_and_stderr:
        # Capture and print the output
        stdout, stderr = process.communicate()

        # Print the output for debugging
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)
