import os
import re
from functools import cached_property

import requests
import tomli

from osa_tool.analytics.metadata import RepositoryMetadata
from osa_tool.analytics.sourcerank import SourceRank
from osa_tool.config.settings import ConfigLoader
from osa_tool.readmegen.generator.header import HeaderBuilder
from osa_tool.readmegen.generator.installation import InstallationSectionBuilder
from osa_tool.readmegen.models.llm_service import LLMClient
from osa_tool.readmegen.utils import find_in_repo_tree
from osa_tool.utils import osa_project_root


class MarkdownBuilderBase:
    def __init__(self, config_loader: ConfigLoader, metadata: RepositoryMetadata, overview=None, getting_started=None):
        self.config_loader = config_loader
        self.config = self.config_loader.config
        self.sourcerank = SourceRank(self.config_loader)
        self.repo_url = self.config.git.repository
        self.metadata = metadata
        self.url_path = f"https://{self.config.git.host_domain}/{self.config.git.full_name}/"
        self.branch_path = f"tree/{self.metadata.default_branch}/"

        self._overview = overview
        self._getting_started = getting_started

        self.header = HeaderBuilder(self.config_loader, self.metadata).build_header()
        self.installation = InstallationSectionBuilder(self.config_loader, self.metadata).build_installation()

        self.template_path = os.path.join(osa_project_root(), "config", "templates", "template.toml")
        self._template = self.load_template()

    def load_template(self) -> dict:
        """
        Loads a TOML template file and returns its sections as a dictionary.
        """
        with open(self.template_path, "rb") as file:
            return tomli.load(file)

    @staticmethod
    def _check_url(url):
        response = requests.get(url)
        return response.status_code == 200

    @property
    def overview(self) -> str:
        """Generates the README Overview section"""
        if not self._overview:
            return ""
        return self._template["overview"].format(self._overview)

    @property
    def getting_started(self) -> str:
        """Generates the README Getting Started section"""
        if not self._getting_started:
            return ""
        return self._template["getting_started"].format(self._getting_started)

    @property
    def examples(self) -> str:
        """Generates the README Examples section"""
        if not self.sourcerank.examples_presence():
            return ""

        pattern = r"\b(tutorials?|examples|notebooks?)\b"
        path = self.url_path + self.branch_path + f"{find_in_repo_tree(self.sourcerank.tree, pattern)}"
        return self._template["examples"].format(path=path)

    @property
    def documentation(self) -> str:
        """Generates the README Documentation section"""
        if not self.metadata.homepage_url:
            if self.sourcerank.docs_presence():
                pattern = r"\b(docs?|documentation|wiki|manuals?)\b"
                path = self.url_path + self.branch_path + f"{find_in_repo_tree(self.sourcerank.tree, pattern)}"
            else:
                return ""
        else:
            path = self.metadata.homepage_url
        return self._template["documentation"].format(repo_name=self.metadata.name, path=path)

    @property
    def license(self) -> str:
        """Generates the README License section"""
        if not self.metadata.license_name:
            return ""

        pattern = r"\bLICEN[SC]E(\.\w+)?\b"
        help_var = find_in_repo_tree(self.sourcerank.tree, pattern)
        path = self.url_path + self.branch_path + help_var if help_var else self.metadata.license_url
        return self._template["license"].format(license_name=self.metadata.license_name, path=path)

    @cached_property
    def citation(self) -> str:
        """Generates the README Citation section"""
        if self.sourcerank.citation_presence():
            pattern = r"\bCITATION(\.\w+)?\b"
            path = self.url_path + self.branch_path + find_in_repo_tree(self.sourcerank.tree, pattern)
            return self._template["citation"] + self._template["citation_v1"].format(path=path)

        llm_client = LLMClient(self.config_loader, self.metadata)
        citation_from_readme = llm_client.get_citation_from_readme()

        if citation_from_readme:
            return self._template["citation"] + citation_from_readme

        return self._template["citation"] + self._template["citation_v2"].format(
            owner=self.metadata.owner,
            year=self.metadata.created_at.split("-")[0],
            repo_name=self.config.git.name,
            publisher=self.config.git.host_domain,
            repository_url=self.config.git.repository,
        )

    @staticmethod
    def table_of_contents(sections: dict) -> str:
        """Generates an adaptive Table of Contents based on provided sections."""
        toc = ["## Table of Contents\n"]

        for section_name, section_content in sections.items():
            if section_content:
                toc.append("- [{}]({})".format(section_name, "#" + re.sub(r"\s+", "-", section_name.lower())))

        toc.append("\n---")
        return "\n".join(toc)
