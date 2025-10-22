import os
from typing import Any, Dict, List


def expand_path(path: str) -> str:
    """Expand user home directory and environment variables in path."""
    return os.path.expandvars(os.path.expanduser(path))


def expand_paths(*paths):
    # Expand and normalize file paths
    return [expand_path(path) for path in paths]


def build_base_options(
    include_publisher_list: List[str],
    include_abbr_list: List[str],
    exclude_publisher_list: List[str],
    exclude_abbr_list: List[str],
    path_conferences_journals_json: str,
) -> Dict[str, Any]:
    """
    Build options dictionary with common configuration.

    Args:
        include_publisher_list: List of publishers to include
        include_abbr_list: List of conference/journal abbreviations to include
        exclude_publisher_list: List of publishers to exclude
        exclude_abbr_list: List of conference/journal abbreviations to exclude
        path_conferences_journals_json: Base path for conferences/journals JSON files

    Returns:
        Dictionary containing configured options
    """
    path_conferences_journals_json = expand_path(path_conferences_journals_json)
    return {
        "include_publisher_list": include_publisher_list,
        "include_abbr_list": include_abbr_list,
        "exclude_publisher_list": exclude_publisher_list,
        "exclude_abbr_list": exclude_abbr_list,
        "full_json_c": os.path.join(path_conferences_journals_json, "conferences.json"),
        "full_json_j": os.path.join(path_conferences_journals_json, "journals.json"),
        "full_json_k": os.path.join(path_conferences_journals_json, "keywords.json"),
    }


def build_search_options(
    print_on_screen: bool, search_year_list: List[str], keywords_type: str, keywords_list_list: List[List[str]]
) -> Dict[str, Any]:
    """
    Build search options dictionary with common configuration.

    Args:
        print_on_screen: Whether to display results on screen
        search_year_list: List of years to filter search results
        keywords_type: Category name for search keywords
        keywords_list_list: Nested list of search keywords

    Returns:
        Dictionary containing configured search options
    """
    return {
        "print_on_screen": print_on_screen,
        "search_year_list": search_year_list,
        "keywords_dict": {keywords_type: keywords_list_list},
        "keywords_type_list": [keywords_type],
    }
