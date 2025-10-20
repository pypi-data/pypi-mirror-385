
.. image:: https://readthedocs.org/projects/esc-mini-tools-lib/badge/?version=latest
    :target: https://esc-mini-tools-lib.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/easyscalecloud/esc_mini_tools_lib-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/easyscalecloud/esc_mini_tools_lib-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/easyscalecloud/esc_mini_tools_lib-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/easyscalecloud/esc_mini_tools_lib-project

.. image:: https://img.shields.io/pypi/v/esc-mini-tools-lib.svg
    :target: https://pypi.python.org/pypi/esc-mini-tools-lib

.. image:: https://img.shields.io/pypi/l/esc-mini-tools-lib.svg
    :target: https://pypi.python.org/pypi/esc-mini-tools-lib

.. image:: https://img.shields.io/pypi/pyversions/esc-mini-tools-lib.svg
    :target: https://pypi.python.org/pypi/esc-mini-tools-lib

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/easyscalecloud/esc_mini_tools_lib-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/easyscalecloud/esc_mini_tools_lib-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://esc-mini-tools-lib.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/easyscalecloud/esc_mini_tools_lib-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/easyscalecloud/esc_mini_tools_lib-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/easyscalecloud/esc_mini_tools_lib-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/esc-mini-tools-lib#files


Welcome to ``esc_mini_tools_lib`` Documentation
==============================================================================
.. image:: https://esc-mini-tools-lib.readthedocs.io/en/latest/_static/esc_mini_tools_lib-logo.png
    :target: https://esc-mini-tools-lib.readthedocs.io/en/latest/

``esc_mini_tools_lib`` is a collection of reusable mini-tools that provides core business logic for multi-platform deployment scenarios. Each tool implements the Command Pattern using Pydantic models, enabling built-in validation, type safety, and easy OpenAPI specification generation. The library is designed to be pip-installed and seamlessly integrated into various applications: as web app endpoints, as AWS Lambda functions for remote capabilities, or as MCP (Model Context Protocol) servers for AI assistants. By extracting core logic into this standalone library, you can deploy the same validated functionality across different platforms without code duplication.


.. _install:

Install
------------------------------------------------------------------------------

``esc_mini_tools_lib`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install esc-mini-tools-lib

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade esc-mini-tools-lib
