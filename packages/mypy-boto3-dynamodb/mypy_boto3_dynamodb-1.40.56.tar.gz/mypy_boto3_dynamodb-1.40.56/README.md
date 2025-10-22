<a id="mypy-boto3-dynamodb"></a>

# mypy-boto3-dynamodb

[![PyPI - mypy-boto3-dynamodb](https://img.shields.io/pypi/v/mypy-boto3-dynamodb.svg?color=blue)](https://pypi.org/project/mypy-boto3-dynamodb/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mypy-boto3-dynamodb.svg?color=blue)](https://pypi.org/project/mypy-boto3-dynamodb/)
[![Docs](https://img.shields.io/readthedocs/boto3-stubs.svg?color=blue)](https://youtype.github.io/boto3_stubs_docs/)
[![PyPI - Downloads](https://static.pepy.tech/badge/mypy-boto3-dynamodb)](https://pypistats.org/packages/mypy-boto3-dynamodb)

![boto3.typed](https://github.com/youtype/mypy_boto3_builder/raw/main/logo.png)

Type annotations for [boto3 DynamoDB 1.40.56](https://pypi.org/project/boto3/)
compatible with [VSCode](https://code.visualstudio.com/),
[PyCharm](https://www.jetbrains.com/pycharm/),
[Emacs](https://www.gnu.org/software/emacs/),
[Sublime Text](https://www.sublimetext.com/),
[mypy](https://github.com/python/mypy),
[pyright](https://github.com/microsoft/pyright) and other tools.

Generated with
[mypy-boto3-builder 8.11.0](https://github.com/youtype/mypy_boto3_builder).

More information can be found on
[boto3-stubs](https://pypi.org/project/boto3-stubs/) page and in
[mypy-boto3-dynamodb docs](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_dynamodb/).

See how it helps you find and fix potential bugs:

![types-boto3 demo](https://github.com/youtype/mypy_boto3_builder/raw/main/demo.gif)

- [mypy-boto3-dynamodb](#mypy-boto3-dynamodb)
  - [How to install](#how-to-install)
    - [Generate locally (recommended)](<#generate-locally-(recommended)>)
    - [VSCode extension](#vscode-extension)
    - [From PyPI with pip](#from-pypi-with-pip)
    - [From conda-forge](#from-conda-forge)
  - [How to uninstall](#how-to-uninstall)
  - [Usage](#usage)
    - [VSCode](#vscode)
    - [PyCharm](#pycharm)
    - [Emacs](#emacs)
    - [Sublime Text](#sublime-text)
    - [Other IDEs](#other-ides)
    - [mypy](#mypy)
    - [pyright](#pyright)
    - [Pylint compatibility](#pylint-compatibility)
  - [Explicit type annotations](#explicit-type-annotations)
    - [Client annotations](#client-annotations)
    - [Paginators annotations](#paginators-annotations)
    - [Waiters annotations](#waiters-annotations)
    - [Service Resource annotations](#service-resource-annotations)
    - [Other resources annotations](#other-resources-annotations)
    - [Collections annotations](#collections-annotations)
    - [Literals](#literals)
    - [Type definitions](#type-definitions)
  - [How it works](#how-it-works)
  - [What's new](#what's-new)
    - [Implemented features](#implemented-features)
    - [Latest changes](#latest-changes)
  - [Versioning](#versioning)
  - [Thank you](#thank-you)
  - [Documentation](#documentation)
  - [Support and contributing](#support-and-contributing)

<a id="how-to-install"></a>

## How to install

<a id="generate-locally-(recommended)"></a>

### Generate locally (recommended)

You can generate type annotations for `boto3` package locally with
`mypy-boto3-builder`. Use
[uv](https://docs.astral.sh/uv/getting-started/installation/) for build
isolation.

1. Run mypy-boto3-builder in your package root directory:
   `uvx --with 'boto3==1.40.56' mypy-boto3-builder`
2. Select `boto3-stubs` AWS SDK.
3. Add `DynamoDB` service.
4. Use provided commands to install generated packages.

<a id="vscode-extension"></a>

### VSCode extension

Add
[AWS Boto3](https://marketplace.visualstudio.com/items?itemName=Boto3typed.boto3-ide)
extension to your VSCode and run `AWS boto3: Quick Start` command.

Click `Modify` and select `boto3 common` and `DynamoDB`.

<a id="from-pypi-with-pip"></a>

### From PyPI with pip

Install `boto3-stubs` for `DynamoDB` service.

```bash
# install with boto3 type annotations
python -m pip install 'boto3-stubs[dynamodb]'

# Lite version does not provide session.client/resource overloads
# it is more RAM-friendly, but requires explicit type annotations
python -m pip install 'boto3-stubs-lite[dynamodb]'

# standalone installation
python -m pip install mypy-boto3-dynamodb
```

<a id="from-conda-forge"></a>

### From conda-forge

Add `conda-forge` to your channels with:

```bash
conda config --add channels conda-forge
conda config --set channel_priority strict
```

Once the `conda-forge` channel has been enabled, `mypy-boto3-dynamodb` can be
installed with:

```bash
conda install mypy-boto3-dynamodb
```

List all available versions of `mypy-boto3-dynamodb` available on your platform
with:

```bash
conda search mypy-boto3-dynamodb --channel conda-forge
```

<a id="how-to-uninstall"></a>

## How to uninstall

```bash
python -m pip uninstall -y mypy-boto3-dynamodb
```

<a id="usage"></a>

## Usage

<a id="vscode"></a>

### VSCode

- Install
  [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- Install
  [Pylance extension](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- Set `Pylance` as your Python Language Server
- Install `boto3-stubs[dynamodb]` in your environment:

```bash
python -m pip install 'boto3-stubs[dynamodb]'
```

Both type checking and code completion should now work. No explicit type
annotations required, write your `boto3` code as usual.

<a id="pycharm"></a>

### PyCharm

> ⚠️ Due to slow PyCharm performance on `Literal` overloads (issue
> [PY-40997](https://youtrack.jetbrains.com/issue/PY-40997)), it is recommended
> to use [boto3-stubs-lite](https://pypi.org/project/boto3-stubs-lite/) until
> the issue is resolved.

> ⚠️ If you experience slow performance and high CPU usage, try to disable
> `PyCharm` type checker and use [mypy](https://github.com/python/mypy) or
> [pyright](https://github.com/microsoft/pyright) instead.

> ⚠️ To continue using `PyCharm` type checker, you can try to replace
> `boto3-stubs` with
> [boto3-stubs-lite](https://pypi.org/project/boto3-stubs-lite/):

```bash
pip uninstall boto3-stubs
pip install boto3-stubs-lite
```

Install `boto3-stubs[dynamodb]` in your environment:

```bash
python -m pip install 'boto3-stubs[dynamodb]'
```

Both type checking and code completion should now work.

<a id="emacs"></a>

### Emacs

- Install `boto3-stubs` with services you use in your environment:

```bash
python -m pip install 'boto3-stubs[dynamodb]'
```

- Install [use-package](https://github.com/jwiegley/use-package),
  [lsp](https://github.com/emacs-lsp/lsp-mode/),
  [company](https://github.com/company-mode/company-mode) and
  [flycheck](https://github.com/flycheck/flycheck) packages
- Install [lsp-pyright](https://github.com/emacs-lsp/lsp-pyright) package

```elisp
(use-package lsp-pyright
  :ensure t
  :hook (python-mode . (lambda ()
                          (require 'lsp-pyright)
                          (lsp)))  ; or lsp-deferred
  :init (when (executable-find "python3")
          (setq lsp-pyright-python-executable-cmd "python3"))
  )
```

- Make sure emacs uses the environment where you have installed `boto3-stubs`

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="sublime-text"></a>

### Sublime Text

- Install `boto3-stubs[dynamodb]` with services you use in your environment:

```bash
python -m pip install 'boto3-stubs[dynamodb]'
```

- Install [LSP-pyright](https://github.com/sublimelsp/LSP-pyright) package

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="other-ides"></a>

### Other IDEs

Not tested, but as long as your IDE supports `mypy` or `pyright`, everything
should work.

<a id="mypy"></a>

### mypy

- Install `mypy`: `python -m pip install mypy`
- Install `boto3-stubs[dynamodb]` in your environment:

```bash
python -m pip install 'boto3-stubs[dynamodb]'
```

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="pyright"></a>

### pyright

- Install `pyright`: `npm i -g pyright`
- Install `boto3-stubs[dynamodb]` in your environment:

```bash
python -m pip install 'boto3-stubs[dynamodb]'
```

Optionally, you can install `boto3-stubs` to `typings` directory.

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="pylint-compatibility"></a>

### Pylint compatibility

It is totally safe to use `TYPE_CHECKING` flag in order to avoid
`mypy-boto3-dynamodb` dependency in production. However, there is an issue in
`pylint` that it complains about undefined variables. To fix it, set all types
to `object` in non-`TYPE_CHECKING` mode.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_ec2 import EC2Client, EC2ServiceResource
    from mypy_boto3_ec2.waiters import BundleTaskCompleteWaiter
    from mypy_boto3_ec2.paginators import DescribeVolumesPaginator
else:
    EC2Client = object
    EC2ServiceResource = object
    BundleTaskCompleteWaiter = object
    DescribeVolumesPaginator = object

...
```

<a id="explicit-type-annotations"></a>

## Explicit type annotations

<a id="client-annotations"></a>

### Client annotations

`DynamoDBClient` provides annotations for `boto3.client("dynamodb")`.

```python
from boto3.session import Session

from mypy_boto3_dynamodb import DynamoDBClient

client: DynamoDBClient = Session().client("dynamodb")

# now client usage is checked by mypy and IDE should provide code completion
```

<a id="paginators-annotations"></a>

### Paginators annotations

`mypy_boto3_dynamodb.paginator` module contains type annotations for all
paginators.

```python
from boto3.session import Session

from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_dynamodb.paginator import (
    ListBackupsPaginator,
    ListTablesPaginator,
    ListTagsOfResourcePaginator,
    QueryPaginator,
    ScanPaginator,
)

client: DynamoDBClient = Session().client("dynamodb")

# Explicit type annotations are optional here
# Types should be correctly discovered by mypy and IDEs
list_backups_paginator: ListBackupsPaginator = client.get_paginator("list_backups")
list_tables_paginator: ListTablesPaginator = client.get_paginator("list_tables")
list_tags_of_resource_paginator: ListTagsOfResourcePaginator = client.get_paginator(
    "list_tags_of_resource"
)
query_paginator: QueryPaginator = client.get_paginator("query")
scan_paginator: ScanPaginator = client.get_paginator("scan")
```

<a id="waiters-annotations"></a>

### Waiters annotations

`mypy_boto3_dynamodb.waiter` module contains type annotations for all waiters.

```python
from boto3.session import Session

from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_dynamodb.waiter import TableExistsWaiter, TableNotExistsWaiter

client: DynamoDBClient = Session().client("dynamodb")

# Explicit type annotations are optional here
# Types should be correctly discovered by mypy and IDEs
table_exists_waiter: TableExistsWaiter = client.get_waiter("table_exists")
table_not_exists_waiter: TableNotExistsWaiter = client.get_waiter("table_not_exists")
```

<a id="service-resource-annotations"></a>

### Service Resource annotations

`DynamoDBServiceResource` provides annotations for
`boto3.resource("dynamodb")`.

```python
from boto3.session import Session

from mypy_boto3_dynamodb import DynamoDBServiceResource

resource: DynamoDBServiceResource = Session().resource("dynamodb")

# now resource usage is checked by mypy and IDE should provide code completion
```

<a id="other-resources-annotations"></a>

### Other resources annotations

`mypy_boto3_dynamodb.service_resource` module contains type annotations for all
resources.

```python
from boto3.session import Session

from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table

resource: DynamoDBServiceResource = Session().resource("dynamodb")

# Explicit type annotations are optional here
# Type should be correctly discovered by mypy and IDEs
my_table: Table = resource.Table(...)
```

<a id="collections-annotations"></a>

### Collections annotations

`mypy_boto3_dynamodb.service_resource` module contains type annotations for all
`DynamoDBServiceResource` collections.

```python
from boto3.session import Session

from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import ServiceResourceTablesCollection

resource: DynamoDBServiceResource = Session().resource("dynamodb")

# Explicit type annotations are optional here
# Type should be correctly discovered by mypy and IDEs
tables: dynamodb_resources.ServiceResourceTablesCollection = resource.tables
```

<a id="literals"></a>

### Literals

`mypy_boto3_dynamodb.literals` module contains literals extracted from shapes
that can be used in user code for type checking.

Full list of `DynamoDB` Literals can be found in
[docs](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_dynamodb/literals/).

```python
from mypy_boto3_dynamodb.literals import ApproximateCreationDateTimePrecisionType


def check_value(value: ApproximateCreationDateTimePrecisionType) -> bool: ...
```

<a id="type-definitions"></a>

### Type definitions

`mypy_boto3_dynamodb.type_defs` module contains structures and shapes assembled
to typed dictionaries and unions for additional type checking.

Full list of `DynamoDB` TypeDefs can be found in
[docs](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_dynamodb/type_defs/).

```python
# TypedDict usage example
from mypy_boto3_dynamodb.type_defs import ArchivalSummaryTypeDef


def get_value() -> ArchivalSummaryTypeDef:
    return {
        "ArchivalDateTime": ...,
    }
```

<a id="how-it-works"></a>

## How it works

Fully automated
[mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder) carefully
generates type annotations for each service, patiently waiting for `boto3`
updates. It delivers drop-in type annotations for you and makes sure that:

- All available `boto3` services are covered.
- Each public class and method of every `boto3` service gets valid type
  annotations extracted from `botocore` schemas.
- Type annotations include up-to-date documentation.
- Link to documentation is provided for every method.
- Code is processed by [ruff](https://docs.astral.sh/ruff/) for readability.

<a id="what's-new"></a>

## What's new

<a id="implemented-features"></a>

### Implemented features

- Fully type annotated `boto3`, `botocore`, `aiobotocore` and `aioboto3`
  libraries
- `mypy`, `pyright`, `VSCode`, `PyCharm`, `Sublime Text` and `Emacs`
  compatibility
- `Client`, `ServiceResource`, `Resource`, `Waiter` `Paginator` type
  annotations for each service
- Generated `TypeDefs` for each service
- Generated `Literals` for each service
- Auto discovery of types for `boto3.client` and `boto3.resource` calls
- Auto discovery of types for `session.client` and `session.resource` calls
- Auto discovery of types for `client.get_waiter` and `client.get_paginator`
  calls
- Auto discovery of types for `ServiceResource` and `Resource` collections
- Auto discovery of types for `aiobotocore.Session.create_client` calls

<a id="latest-changes"></a>

### Latest changes

Builder changelog can be found in
[Releases](https://github.com/youtype/mypy_boto3_builder/releases).

<a id="versioning"></a>

## Versioning

`mypy-boto3-dynamodb` version is the same as related `boto3` version and
follows
[Python Packaging version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/).

<a id="thank-you"></a>

## Thank you

- [Allie Fitter](https://github.com/alliefitter) for
  [boto3-type-annotations](https://pypi.org/project/boto3-type-annotations/),
  this package is based on top of his work
- [black](https://github.com/psf/black) developers for an awesome formatting
  tool
- [Timothy Edmund Crosley](https://github.com/timothycrosley) for
  [isort](https://github.com/PyCQA/isort) and how flexible it is
- [mypy](https://github.com/python/mypy) developers for doing all dirty work
  for us
- [pyright](https://github.com/microsoft/pyright) team for the new era of typed
  Python

<a id="documentation"></a>

## Documentation

All services type annotations can be found in
[boto3 docs](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_dynamodb/)

<a id="support-and-contributing"></a>

## Support and contributing

This package is auto-generated. Please reports any bugs or request new features
in [mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder/issues/)
repository.
