import os
from typing import Any, Dict, List

from pyadvtools import transform_to_data_list
from pybibtexer.tools import compare_bibs_with_zotero

from pyeasyphd.tools import Searchkeywords

from ._base import build_base_options, build_search_options, expand_path, expand_paths


def run_search_for_screen(
    acronym: str,
    year: int,
    title: str,
    path_spidered_bibs: str,
    path_spidering_bibs: str,
    path_conferences_journals_json: str,
) -> None:
    """
    Run search for screen display with specific conference/journal parameters.

    Args:
        acronym: Conference/journal acronym to search for
        year: Publication year to filter by
        title: Paper title used as search keyword
        path_spidered_bibs: Path to spidered bibliography files
        path_spidering_bibs: Path to spidering bibliography files
        path_conferences_journals_json: Path to conferences/journals JSON files
    """
    # Expand and normalize file paths
    path_spidered_bibs, path_spidering_bibs, path_conferences_journals_json = expand_paths(
        path_spidered_bibs, path_spidering_bibs, path_conferences_journals_json
    )

    # Configure search options
    options = {
        **build_base_options(
            include_publisher_list=[],
            include_abbr_list=[acronym],
            exclude_publisher_list=["arXiv"],
            exclude_abbr_list=[],
            path_conferences_journals_json=path_conferences_journals_json,
        ),
        **build_search_options(
            print_on_screen=True, search_year_list=[str(year)], keywords_type="Temp", keywords_list_list=[[title]]
        ),
    }

    # Execute searches across different bibliography sources
    _execute_searches(options, "", path_spidered_bibs, path_spidering_bibs)


def run_search_for_files(
    keywords_type: str,
    keywords_list_list: List[List[str]],
    path_main_output: str,
    path_spidered_bibs: str,
    path_spidering_bibs: str,
    path_conferences_journals_json: str,
) -> None:
    """
    Run search and save results to files with custom keywords.

    Args:
        keywords_type: Category name for the search keywords
        keywords_list_list: Nested list of keywords to search for
        path_main_output: Main output directory for search results
        path_spidered_bibs: Path to spidered bibliography files
        path_spidering_bibs: Path to spidering bibliography files
        path_conferences_journals_json: Path to conferences/journals JSON files
    """
    # Expand and normalize file paths
    path_main_output = expand_path(path_main_output)
    path_spidered_bibs, path_spidering_bibs, path_conferences_journals_json = expand_paths(
        path_spidered_bibs, path_spidering_bibs, path_conferences_journals_json
    )

    # Configure search options
    options = {
        **build_base_options(
            include_publisher_list=[],
            include_abbr_list=[],
            exclude_publisher_list=["arXiv"],
            exclude_abbr_list=[],
            path_conferences_journals_json=path_conferences_journals_json,
        ),
        **build_search_options(
            print_on_screen=False,
            search_year_list=[],
            keywords_type=keywords_type,
            keywords_list_list=keywords_list_list,
        ),
    }
    # Execute searches across different bibliography sources
    _execute_searches(options, path_main_output, path_spidered_bibs, path_spidering_bibs)


def _execute_searches(
    options: Dict[str, Any], path_main_output: str, path_spidered_bibs: str, path_spidering_bibs: str
) -> None:
    """
    Execute searches across different bibliography sources.

    Args:
        options: Search configuration options
        path_main_output: Base path for search results output
        path_spidered_bibs: Path to spidered bibliography files
        path_spidering_bibs: Path to spidering bibliography files
    """
    # Search in spidered bibliographies (Conferences and Journals)
    for cj in ["Conferences", "Journals"]:
        path_storage = os.path.join(path_spidered_bibs, cj)
        path_output = os.path.join(path_main_output, "Search_spidered_bib", cj)
        Searchkeywords(path_storage, path_output, options).run()

    # Search in spidering bibliographies (Journals and Journals Early Access)
    for je in ["spider_j", "spider_j_e"]:
        path_storage = os.path.join(path_spidering_bibs, je)
        path_output = os.path.join(path_main_output, "Search_spidering_bib", je)
        Searchkeywords(path_storage, path_output, options).run()


def run_compare_after_search(
    zotero_bib: str, keywords_type: str, path_main_output: str, path_conferences_journals_json: str
):
    """
    Compare search results with Zotero bibliography and generate comparison report.

    Args:
        zotero_bib: Path to Zotero bibliography file
        keywords_type: Category name for the search keywords used
        path_main_output: Main output directory for search results and comparison
        path_conferences_journals_json: Path to conferences/journals JSON files
    """
    # Expand and normalize file paths
    zotero_bib = expand_path(zotero_bib)
    path_main_output = expand_path(path_main_output)
    path_conferences_journals_json = expand_path(path_conferences_journals_json)

    # Configure search options
    options = {
        **build_base_options(
            include_publisher_list=[],
            include_abbr_list=[],
            exclude_publisher_list=["arXiv"],
            exclude_abbr_list=[],
            path_conferences_journals_json=path_conferences_journals_json,
        ),
        **build_search_options(
            print_on_screen=False, search_year_list=[], keywords_type=keywords_type, keywords_list_list=[]
        ),
    }

    # Download bibliography files from local search results
    download_bib = _download_bib_from_local(path_main_output, keywords_type)

    # Generate comparison output path and run comparison
    path_output = os.path.join(path_main_output, "comparison_new")
    compare_bibs_with_zotero(zotero_bib, download_bib, path_output, options)

    return None


def _generate_data_list(path_output: str, folder_name: str, keywords_type: str) -> list[str]:
    """
    Extract bibliography data content from files in specified folder structure.

    Args:
        path_output: Base output path for search results
        folder_name: Specific folder name within the output structure
        keywords_type: Category name for the search keywords used

    Returns:
        List of bibliography data content extracted from .bib files in the specified folders
    """
    data_list = []

    # Extract data from both title and abstract bibliography folders
    for bib_type in ["title-bib-zotero", "abstract-bib-zotero"]:
        folder_path = os.path.join(path_output, f"{folder_name}-Separate", "article", keywords_type, bib_type)

        # Extract bibliography data content if folder exists
        if os.path.exists(folder_path):
            data_list.extend(transform_to_data_list(folder_path, ".bib"))

    return data_list


def _download_bib_from_local(path_output: str, keywords_type: str) -> list[str]:
    """
    Collect bibliography data content from all local search result directories.

    Args:
        path_output: Base output path containing search results
        keywords_type: Category name for the search keywords used

    Returns:
        Combined list of bibliography data content from all .bib files in search results
    """
    data_list = []

    # Collect data from spidered bibliographies (Conferences and Journals)
    for cj in ["Conferences", "Journals"]:
        folder_name = os.path.join("Search_spidered_bib", cj)
        data_list.extend(_generate_data_list(path_output, folder_name, keywords_type))

    # Collect data from spidering bibliographies (journal sources)
    for je in ["spider_j", "spider_j_e"]:
        folder_name = os.path.join("Search_spidering_bib", je)
        data_list.extend(_generate_data_list(path_output, folder_name, keywords_type))

    return data_list
