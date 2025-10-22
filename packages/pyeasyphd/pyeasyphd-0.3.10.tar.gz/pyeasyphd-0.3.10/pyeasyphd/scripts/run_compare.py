from pybibtexer.tools import compare_bibs_with_local, compare_bibs_with_zotero

from ._base import build_base_options, expand_paths


def run_compare_bib_with_local(
    options: dict,
    need_compare_bib: str,
    path_output: str,
    path_spidered_bibs: str,
    path_spidering_bibs: str,
    path_conferences_journals_json: str,
) -> None:
    # Expand and normalize file paths
    need_compare_bib, path_output, path_spidered_bibs, path_spidering_bibs = expand_paths(
        need_compare_bib, path_output, path_spidered_bibs, path_spidering_bibs
    )

    # Update options
    options_ = build_base_options([], [], ["arXiv"], [], path_conferences_journals_json)
    options_["include_early_access"] = True
    options_.update(options)

    # Compare
    compare_bibs_with_local(need_compare_bib, path_spidered_bibs, path_spidering_bibs, path_output, options_)


def run_compare_bib_with_zotero(
    options: dict,
    need_compare_bib: str,
    zotero_bib: str,
    path_output: str,
    path_conferences_journals_json: str,
) -> None:
    # Expand and normalize file paths
    need_compare_bib, zotero_bib, path_output = expand_paths(
        need_compare_bib, zotero_bib, path_output
    )

    # Update options
    options_ = build_base_options([], [], ["arXiv"], [], path_conferences_journals_json)
    options_.update(options)

    # Compare
    compare_bibs_with_zotero(zotero_bib, need_compare_bib, path_output, options_)
