import os
from typing import Any, Dict, List

from pyeasyphd.tools import Searchkeywords


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
    path_spidered_bibs = _expand_path(path_spidered_bibs)
    path_spidering_bibs = _expand_path(path_spidering_bibs)
    path_conferences_journals_json = _expand_path(path_conferences_journals_json)

    # Configure search options
    options = _build_search_options(
        print_on_screen=True,
        search_year_list=[str(year)],
        include_publisher_list=[],
        include_abbr_list=[acronym],
        exclude_publisher_list=["arXiv"],
        exclude_abbr_list=[],
        keywords_type="Temp",
        keywords_list_list=[[title]],
        path_conferences_journals_json=path_conferences_journals_json,
    )

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
    path_main_output = _expand_path(path_main_output)
    path_spidered_bibs = _expand_path(path_spidered_bibs)
    path_spidering_bibs = _expand_path(path_spidering_bibs)
    path_conferences_journals_json = _expand_path(path_conferences_journals_json)

    # Configure search options
    options = _build_search_options(
        print_on_screen=False,
        search_year_list=[],
        include_publisher_list=[],
        include_abbr_list=[],
        exclude_publisher_list=["arXiv"],
        exclude_abbr_list=[],
        keywords_type=keywords_type,
        keywords_list_list=keywords_list_list,
        path_conferences_journals_json=path_conferences_journals_json,
    )

    # Execute searches across different bibliography sources
    _execute_searches(options, path_main_output, path_spidered_bibs, path_spidering_bibs)


def _expand_path(path: str) -> str:
    """Expand user home directory and environment variables in path."""
    return os.path.expandvars(os.path.expanduser(path))


def _build_search_options(
    print_on_screen: bool,
    search_year_list: List[str],
    include_publisher_list: List[str],
    include_abbr_list: List[str],
    exclude_publisher_list: List[str],
    exclude_abbr_list: List[str],
    keywords_type: str,
    keywords_list_list: List[List[str]],
    path_conferences_journals_json: str,
) -> Dict[str, Any]:
    """
    Build search options dictionary with common configuration.

    Args:
        print_on_screen: Whether to display results on screen
        search_year_list: List of years to filter search results
        include_publisher_list: List of publishers to include
        include_abbr_list: List of conference/journal abbreviations to include
        exclude_publisher_list: List of publishers to exclude from search
        exclude_abbr_list: List of conference/journal abbreviations to exclude from search
        keywords_type: Category name for search keywords
        keywords_list_list: Nested list of search keywords
        path_conferences_journals_json: Base path for conferences/journals JSON files

    Returns:
        Dictionary containing configured search options
    """
    return {
        "print_on_screen": print_on_screen,
        "search_year_list": search_year_list,
        "include_publisher_list": include_publisher_list,
        "include_abbr_list": include_abbr_list,
        "exclude_publisher_list": exclude_publisher_list,
        "exclude_abbr_list": exclude_abbr_list,
        "keywords_dict": {keywords_type: keywords_list_list},
        "keywords_type_list": [keywords_type],
        "full_json_c": os.path.join(path_conferences_journals_json, "conferences.json"),
        "full_json_j": os.path.join(path_conferences_journals_json, "journals.json"),
    }


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
