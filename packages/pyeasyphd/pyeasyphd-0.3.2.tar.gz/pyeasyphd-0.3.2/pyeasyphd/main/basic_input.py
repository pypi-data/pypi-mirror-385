import os
from typing import Any, Dict

from pyadvtools import read_list
from pybibtexer.main import BasicInput as BasicInputInPyBibtexer


class BasicInput(BasicInputInPyBibtexer):
    """Basic input class for handling bibliography and template configurations.

    Args:
        options (Dict[str, Any]): Configuration options.

    Attributes:
        full_json_c (str): Full path to conferences JSON file.
        full_json_j (str): Full path to journals JSON file.
        full_csl_style_pandoc (str): Full path to CSL style for pandoc.
        full_tex_article_template_pandoc (str): Full path to tex article template for pandoc.
        full_tex_beamer_template_pandoc (str): Full path to tex beamer template for pandoc.
        article_template_tex (List[str]): Article template for LaTeX.
        article_template_header_tex (List[str]): Article template header for LaTeX.
        article_template_tail_tex (List[str]): Article template tail for LaTeX.
        beamer_template_header_tex (List[str]): Beamer template header for LaTeX.
        beamer_template_tail_tex (List[str]): Beamer template tail for LaTeX.
        math_commands_tex (List[str]): LaTeX math commands.
        usepackages_tex (List[str]): LaTeX usepackages.
        handly_preamble (bool): Whether to handle preamble manually.
        options (Dict[str, Any]): Configuration options.
    """

    def __init__(self, options: Dict[str, Any]) -> None:
        """Initialize BasicInput with configuration options.

        Args:
            options (Dict[str, Any]): Configuration options dictionary.
        """
        super().__init__(options)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self._path_templates = os.path.join(os.path.dirname(current_dir), "data", "Templates")

        # main
        self._initialize_pandoc_md_to(options)
        self._initialize_python_run_tex(options)

        self.options = options

    def _initialize_pandoc_md_to(self, options: Dict[str, Any]) -> None:
        """Initialize pandoc markdown to other formats configuration.

        Args:
            options (Dict[str, Any]): Configuration options.
        """
        csl_name = options.get("csl_name", "apa-no-ampersand")
        if not isinstance(csl_name, str):
            csl_name = "apa-no-ampersand"
        self.full_csl_style_pandoc = os.path.join(self._path_templates, "CSL", f"{csl_name}.csl")
        if not os.path.exists(self.full_csl_style_pandoc):
            self.full_csl_style_pandoc = os.path.join(self._path_templates, "CSL", "apa-no-ampersand.csl")

        self.full_tex_article_template_pandoc = os.path.join(self._path_templates, "TEX", "eisvogel.latex")
        self.full_tex_beamer_template_pandoc = os.path.join(self._path_templates, "TEX", "eisvogel.beamer")

        self.article_template_tex = self._try_read_list("TEX", "Article.tex")

    def _initialize_python_run_tex(self, options: Dict[str, Any]) -> None:
        """Initialize Python LaTeX processing configuration.

        Args:
            options (Dict[str, Any]): Configuration options.
        """
        self.article_template_header_tex = self._try_read_list("TEX", "Article_Header.tex")
        self.article_template_tail_tex = self._try_read_list("TEX", "Article_Tail.tex")
        self.beamer_template_header_tex = self._try_read_list("TEX", "Beamer_Header.tex")
        self.beamer_template_tail_tex = self._try_read_list("TEX", "Beamer_Tail.tex")
        self.math_commands_tex = self._try_read_list("TEX", "math_commands.tex")
        self.usepackages_tex = self._try_read_list("TEX", "Style.tex")

        # handly preamble
        self.handly_preamble = options.get("handly_preamble", False)
        if self.handly_preamble:
            self.article_template_header_tex, self.article_template_tail_tex = [], []
            self.beamer_template_header_tex, self.beamer_template_tail_tex = [], []
            self.math_commands_tex, self.usepackages_tex = [], []

    def _try_read_list(self, folder_name: str, file_name: str):
        """Try to read a list from a file in the templates directory.

        Args:
            folder_name (str): Name of the folder in templates directory.
            file_name (str): Name of the file to read.

        Returns:
            List[str]: List of lines from the file, or empty list if file cannot be read.
        """
        path_file = os.path.join(self._path_templates, folder_name, file_name)

        try:
            data_list = read_list(path_file)
        except Exception as e:
            print(e)
            data_list = []
        return data_list
