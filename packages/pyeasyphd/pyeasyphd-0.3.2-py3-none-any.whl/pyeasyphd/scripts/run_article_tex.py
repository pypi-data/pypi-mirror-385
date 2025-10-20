import os

from pyadvtools import GitAutoCommitter

from pyeasyphd.tools import PyRunBibMdTex


def run_article_tex_submit(
    path_input_file: str,
    input_file_names: list[str],
    path_output_file: str,
    bib_path_or_file: str,
    path_conferences_journals_json: str,
    options: dict
) -> None:
    """
    Process academic article files (TeX, and bibliography) with automated Git version control.

    This function handles the conversion and processing of academic article files including TeX documents, and
    bibliography management with automatic Git commit and push capabilities.

    Note: The raw figures and TeX source files must be located in the data/raw subdirectory of the input path.

    Args:
        path_input_file (str): Path to input files directory
        input_file_names (list[str]): List of input file names
        path_output_file (str): Path to output directory
        bib_path_or_file (str): Path to bibliography file or directory
        path_conferences_journals_json (str): Path to conferences and journals JSON files directory
        options (dict): Additional options to override default settings

    Returns:
        None
    """
    path_input_file = os.path.expandvars(os.path.expanduser(path_input_file))
    path_output_file = os.path.expandvars(os.path.expanduser(path_output_file))

    # Initialize default options with detailed descriptions
    _options = {
        "full_json_c": os.path.expanduser(os.path.join(path_conferences_journals_json, "conferences.json")),
        "full_json_j": os.path.expanduser(os.path.join(path_conferences_journals_json, "journals.json")),

        # figure options
        "includegraphics_figs_directory": os.path.join(path_input_file, "data", "raw"),
        "shutil_includegraphics_figs": True,
        "includegraphics_figs_in_relative_path": True,
        "figure_folder_name": "figs",  # "" or "figs" or "main"

        # bib options
        "abbr_index_article_for_abbr": 1,  # 0, 1, 2
        "abbr_index_inproceedings_for_abbr": 0,  # 0, 1, 2
        "add_link_to_fields_for_abbr": None,  # None, or ["title", "journal", "booktitle"]
        "maximum_authors_for_abbr": 0,  # 0, 1, 2, ...
        "add_index_to_entries": False,
        "bib_for_abbr_name": "abbr.bib",
        "bib_for_zotero_name": "zotero.bib",
        "bib_for_save_name": "save.bib",
        "display_google_connected_scite": ["google", "connected", "scite"],

        "bib_folder_name": "bibs",  # "" or "bib" or "bibs" or "main"
        "delete_original_bib_in_output_folder": False,
        "bib_path_or_file": os.path.expanduser(bib_path_or_file),

        # tex options
        "handly_preamble": True,
        "final_output_main_tex_name": "main.tex",
        "run_latex": False,
        "delete_run_latex_cache": False,

        "input_texs_directory": os.path.join(path_input_file, "data", "raw"),
        "shutil_input_texs": True,
        "input_texs_in_relative_path": True,
        "tex_folder_name": "texs",  # "" or "tex" or "texs" or "main"
        "delete_original_tex_in_output_folder": True,
        "generate_tex": True,

        # md options
        "add_url_for_basic_dict": True,  # default is True
        "add_anchor_for_basic_dict": False,  # default is False
        "add_anchor_for_beauty_dict": False,  # default is False
        "add_anchor_for_complex_dict": False,  # default is False

        "final_output_main_md_name": "main.md",
        "delete_temp_generate_md": True,
        "add_reference_in_md": True,
        "add_bib_in_md": False,
        "replace_cite_to_fullcite_in_md": True,
        "replace_by_basic_beauty_complex_in_md": "basic",
        "display_basic_beauty_complex_references_in_md": "beauty",
        "add_anchor_in_md": False,  # default is False

        "md_folder_name": "mds",  # "" or "md" or "main"
        "delete_original_md_in_output_folder": False,  # default is False

        # html options
        "generate_html": False,
    }

    # Update with user-provided options
    _options.update(options)

    committer = GitAutoCommitter(path_output_file)

    if not committer.auto_check(remote="origin", branch="master"):
        print("Remote != Local, please manually pull")

    else:
        # Create full file paths from input file names
        file_list = [os.path.join(path_input_file, f) for f in input_file_names]

        PyRunBibMdTex(path_output_file, ".tex", "paper", _options).run_files(file_list, "", "current")

        if committer.has_changes():
            # Auto commit
            committer.auto_commit()
            # Auto push
            committer.auto_push(remote="origin", branch="master")

    return None
