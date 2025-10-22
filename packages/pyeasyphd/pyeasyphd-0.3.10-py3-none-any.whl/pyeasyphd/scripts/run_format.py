from pathlib import Path

from pybibtexer.tools import format_bib_to_abbr_zotero_save_modes, format_bib_to_save_mode_by_entry_type

from ._base import build_base_options, expand_paths


def run_format_bib_to_save_by_entry_type(
    options: dict,
    need_format_bib: str,
    path_output: str,
    path_conferences_journals_json: str,
) -> None:
    # Expand and normalize file paths
    need_format_bib, path_output = expand_paths(need_format_bib, path_output)

    # Update options
    options_ = build_base_options([], [], [], [], path_conferences_journals_json)
    options_.update(options)

    format_bib_to_save_mode_by_entry_type(Path(need_format_bib).stem, path_output, need_format_bib, options=options_)


def run_format_bib_to_abbr_zotero_save(
    options: dict,
    need_format_bib: str,
    path_output: str,
    path_conferences_journals_json: str,
) -> None:
    # Expand and normalize file paths
    need_format_bib, path_output = expand_paths(need_format_bib, path_output)

    # Update options
    options_ = build_base_options([], [], [], [], path_conferences_journals_json)
    options_.update(options)

    format_bib_to_abbr_zotero_save_modes(need_format_bib, path_output, options=options_)
