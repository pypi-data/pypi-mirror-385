from pathlib import Path

from pybibtexer.tools import format_bib_to_abbr_zotero_save_modes, format_bib_to_save_mode_by_entry_type

from ._base import build_options, expand_path


def run_format_single_file_to_save(
    options: dict,
    need_format_bib: str,
    path_output: str,
    path_conferences_journals_json: str,
):
    # Expand and normalize file paths
    path_output = expand_path(path_output)

    need_format_bib = expand_path(need_format_bib)

    _, _, _, _, _, _, options_ = (
        build_options(options, "", "", path_conferences_journals_json)
    )

    format_bib_to_save_mode_by_entry_type(Path(need_format_bib).stem, path_output, need_format_bib, options=options_)


def run_format_single_file_to_abbr_zotero_save(
    options: dict,
    need_format_bib: str,
    path_output: str,
    path_conferences_journals_json: str,
):
    # Expand and normalize file paths
    path_output = expand_path(path_output)

    need_format_bib = expand_path(need_format_bib)

    _, _, _, _, _, _, options_ = (
        build_options(options, "", "", path_conferences_journals_json)
    )

    format_bib_to_abbr_zotero_save_modes(need_format_bib, path_output, options=options_)
