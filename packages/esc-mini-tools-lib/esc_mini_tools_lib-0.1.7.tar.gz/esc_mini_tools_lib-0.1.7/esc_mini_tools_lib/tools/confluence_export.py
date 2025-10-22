# -*- coding: utf-8 -*-

"""
Confluence Export Tool - URL Transformation Module

This module provides functionality to convert various Confluence page URL formats
to the REST API format for exporting page content.
"""

import typing as T
import re
import json
from enum import Enum
from functools import cached_property
from urllib.parse import urlparse, parse_qs

from pydantic import BaseModel, Field
from docpack.api import ConfluencePage


# ------------------------------------------------------------------------------
# URL converter
# ------------------------------------------------------------------------------
class ConfluenceUrlPattern(str, Enum):
    """Enum representing different Confluence URL patterns."""

    STANDARD_PAGE = "standard_page"  # /spaces/{space}/pages/{id}/{title}
    PAGE_WITH_QUERY = (
        "page_with_query"  # /spaces/{space}/pages/{id}/{title}?param=value
    )
    EDIT_PAGE = "edit_page"  # /spaces/{space}/pages/edit-v2/{id}
    DRAFT_PAGE = "draft_page"  # /pages/resumedraft.action?draftId={id}
    UNKNOWN = "unknown"


def identify_url_pattern(url: str) -> ConfluenceUrlPattern:
    """
    Identify which Confluence URL pattern the given URL matches.

    :param url: The Confluence page URL to identify
    :return: The pattern type as a ConfluenceUrlPattern enum value

    Examples:
        >>> identify_url_pattern("https://domain.atlassian.net/wiki/spaces/SPACE/pages/123/Title")
        ConfluenceUrlPattern.STANDARD_PAGE

        >>> identify_url_pattern("https://domain.atlassian.net/wiki/spaces/SPACE/pages/123/Title?atlOrigin=xyz")
        ConfluenceUrlPattern.PAGE_WITH_QUERY

        >>> identify_url_pattern("https://domain.atlassian.net/wiki/spaces/SPACE/pages/edit-v2/123")
        ConfluenceUrlPattern.EDIT_PAGE

        >>> identify_url_pattern("https://domain.atlassian.net/wiki/pages/resumedraft.action?draftId=123")
        ConfluenceUrlPattern.DRAFT_PAGE
    """
    try:
        parsed = urlparse(url)
        path = parsed.path
        query = parsed.query

        # Pattern 4: Draft page - /pages/resumedraft.action?draftId={id}
        if "/pages/resumedraft.action" in path and "draftId=" in query:
            return ConfluenceUrlPattern.DRAFT_PAGE

        # Pattern 3: Edit page - /spaces/{space}/pages/edit-v2/{id}
        if "/pages/edit-v2/" in path:
            return ConfluenceUrlPattern.EDIT_PAGE

        # Pattern 1 & 2: Standard page - /spaces/{space}/pages/{id}/{title}
        # Use regex to match the pattern
        standard_pattern = r"/spaces/[^/]+/pages/\d+"
        if re.search(standard_pattern, path):
            if query:
                return ConfluenceUrlPattern.PAGE_WITH_QUERY
            else:
                return ConfluenceUrlPattern.STANDARD_PAGE

        return ConfluenceUrlPattern.UNKNOWN

    except Exception:
        return ConfluenceUrlPattern.UNKNOWN


def extract_page_id_from_standard_url(url: str) -> str | None:
    """
    Extract page ID from standard Confluence page URL.

    Pattern: https://{domain}/wiki/spaces/{space}/pages/{pageId}/{title}

    :param url: Standard Confluence page URL
    :return: Page ID as string, or None if extraction fails
    """
    pattern = r"/spaces/[^/]+/pages/(\d+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def extract_page_id_from_page_with_query_url(url: str) -> str | None:
    """
    Extract page ID from Confluence page URL with query parameters.

    Pattern: https://{domain}/wiki/spaces/{space}/pages/{pageId}/{title}?param=value

    :param url: Confluence page URL with query parameters
    :return: Page ID as string, or None if extraction fails
    """
    # Same logic as standard URL since query params don't affect the path
    return extract_page_id_from_standard_url(url)


def extract_page_id_from_edit_url(url: str) -> str | None:
    """
    Extract page ID from Confluence edit page URL.

    Pattern: https://{domain}/wiki/spaces/{space}/pages/edit-v2/{pageId}

    :param url: Confluence edit page URL
    :return: Page ID as string, or None if extraction fails
    """
    pattern = r"/pages/edit-v2/(\d+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def extract_page_id_from_draft_url(url: str) -> str | None:
    """
    Extract page ID from Confluence draft page URL.

    Pattern: https://{domain}/wiki/pages/resumedraft.action?draftId={pageId}

    :param url: Confluence draft page URL
    :return: Page ID as string, or None if extraction fails
    """
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    draft_id = query_params.get("draftId", [None])[0]
    return draft_id


def convert_to_api_url(url: str) -> str | None:
    """
    Convert any supported Confluence page URL to REST API format.

    Target format: https://{domain}/wiki/rest/api/content/{pageId}?expand=body.atlas_doc_format

    :param url: Any supported Confluence page URL
    :return: REST API URL, or None if conversion fails

    Examples:
        >>> url = "https://sanhehu.atlassian.net/wiki/spaces/TECHGARDEN/pages/461242370/Title"
        >>> convert_to_api_url(url)
        'https://sanhehu.atlassian.net/wiki/rest/api/content/461242370?expand=body.atlas_doc_format'
    """
    # Identify the URL pattern
    pattern = identify_url_pattern(url)

    # Extract page ID based on pattern
    page_id = None
    if pattern == ConfluenceUrlPattern.STANDARD_PAGE:
        page_id = extract_page_id_from_standard_url(url)
    elif pattern == ConfluenceUrlPattern.PAGE_WITH_QUERY:
        page_id = extract_page_id_from_page_with_query_url(url)
    elif pattern == ConfluenceUrlPattern.EDIT_PAGE:
        page_id = extract_page_id_from_edit_url(url)
    elif pattern == ConfluenceUrlPattern.DRAFT_PAGE:
        page_id = extract_page_id_from_draft_url(url)

    if not page_id:
        return None

    # Extract base domain from original URL
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # Construct REST API URL
    api_url = f"{base_url}/wiki/rest/api/content/{page_id}?expand=body.atlas_doc_format"
    return api_url


class ConfluenceUrlTransformInput(BaseModel):
    """Input model for Confluence URL transformation."""

    url: str = Field(
        description="The Confluence page URL to transform to REST API format"
    )

    def main(self):
        """
        Transform the Confluence URL to REST API format.

        :return: ConfluenceUrlTransformOutput with the transformation result
        """
        pattern = identify_url_pattern(self.url)
        api_url = convert_to_api_url(self.url)

        return ConfluenceUrlTransformOutput(
            input=self,
            pattern=pattern,
            api_url=api_url,
            success=api_url is not None,
        )


class ConfluenceUrlTransformOutput(BaseModel):
    """Output model for Confluence URL transformation."""

    input: ConfluenceUrlTransformInput = Field(description="The original input")
    pattern: ConfluenceUrlPattern = Field(description="The identified URL pattern type")
    api_url: str | None = Field(
        description="The transformed REST API URL, or None if transformation failed"
    )
    success: bool = Field(description="Whether the transformation was successful")


# ------------------------------------------------------------------------------
# API response to markdown
# ------------------------------------------------------------------------------
def get_body_in_atlas_doc_format_from_page_data(
    page_data: dict[str, T.Any],
) -> dict[str, T.Any]:
    return json.loads(page_data["body"]["atlas_doc_format"]["value"])


class Record(BaseModel):
    url: str = Field()
    page_data: dict[str, T.Any] = Field()
    xml: str | None = Field(default=None)
    md: str | None = Field(default=None)
    success: bool = Field(default=False)

    @cached_property
    def conf_page(self) -> "ConfluencePage":
        return ConfluencePage(
            page_data=self.page_data,
            site_url="",
            id_path="",
            position_path="",
            breadcrumb_path="",
        )


class ConfluencePageExportInput(BaseModel):
    records: list[Record] = Field()
    wanted_fields: list[str] | None = Field(default=None)

    def main(self):
        docs = list()
        for record in self.records:
            try:
                xml = record.conf_page.to_xml()
                md = record.conf_page.markdown
                docs.append(xml)
                record.xml = xml
                record.md = md
                record.success = True
            except Exception as e:
                pass
        text = "\n".join(docs)
        return ConfluencePageExportOutput(
            input=self,
            text=text,
        )


class ConfluencePageExportOutput(BaseModel):
    input: ConfluencePageExportInput = Field()
    text: str = Field()
