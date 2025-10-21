from pybibtexer.tools import compare_bibs_with_local, compare_bibs_with_zotero

from ._base import build_options, expand_path


def run_compare_bib_with_local(
    options: dict,
    need_compare_bib: str,
    path_output: str,
    path_spidered_bibs: str,
    path_spidering_bibs: str,
    path_conferences_journals_json: str,
):
    # Expand and normalize file paths
    path_output = expand_path(path_output)

    need_compare_bib = expand_path(need_compare_bib)

    path_spidered_bibs, path_spidering_bibs, _, _, _, _, options_ = (
        build_options(options, path_spidered_bibs, path_spidering_bibs, path_conferences_journals_json)
    )
    options_["include_early_access"] = True

    compare_bibs_with_local(need_compare_bib, path_spidered_bibs, path_spidering_bibs, path_output, options_)


def run_compare_bib_with_zotero(
    options: dict,
    need_compare_bib: str,
    zotero_bib: str,
    path_output: str,
    path_conferences_journals_json: str,
):
    # Expand and normalize file paths
    path_output = expand_path(path_output)

    zotero_bib = expand_path(zotero_bib)
    need_compare_bib = expand_path(need_compare_bib)

    _, _, _, _, _, _, options_ = (
        build_options(options, "", "", path_conferences_journals_json)
    )

    compare_bibs_with_zotero(zotero_bib, need_compare_bib, path_output, options_)
