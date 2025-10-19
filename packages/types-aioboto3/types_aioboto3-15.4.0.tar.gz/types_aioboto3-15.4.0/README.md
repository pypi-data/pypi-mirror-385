<a id="types-aioboto3"></a>

# types-aioboto3

[![PyPI - types-aioboto3](https://img.shields.io/pypi/v/types-aioboto3.svg?color=blue)](https://pypi.org/project/types-aioboto3/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/types-aioboto3.svg?color=blue)](https://pypi.org/project/types-aioboto3/)
[![Docs](https://img.shields.io/readthedocs/boto3-stubs.svg?color=blue)](https://youtype.github.io/types_aioboto3_docs/)
[![PyPI - Downloads](https://static.pepy.tech/badge/types-aioboto3)](https://pypistats.org/packages/types-aioboto3)

![boto3.typed](https://github.com/youtype/mypy_boto3_builder/raw/main/logo.png)

Type annotations for [aioboto3 15.4.0](https://pypi.org/project/aioboto3/)
compatible with [VSCode](https://code.visualstudio.com/),
[PyCharm](https://www.jetbrains.com/pycharm/),
[Emacs](https://www.gnu.org/software/emacs/),
[Sublime Text](https://www.sublimetext.com/),
[mypy](https://github.com/python/mypy),
[pyright](https://github.com/microsoft/pyright) and other tools.

Generated with
[mypy-boto3-builder 8.11.0](https://github.com/youtype/mypy_boto3_builder).

More information can be found in
[types-aioboto3 docs](https://youtype.github.io/types_aioboto3_docs/).

See how it helps you find and fix potential bugs:

![types-boto3 demo](https://github.com/youtype/mypy_boto3_builder/raw/main/demo.gif)

- [types-aioboto3](#types-aioboto3)
  - [How to install](#how-to-install)
    - [Generate locally (recommended)](<#generate-locally-(recommended)>)
    - [From PyPI with pip](#from-pypi-with-pip)
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
  - [How it works](#how-it-works)
  - [What's new](#what's-new)
    - [Implemented features](#implemented-features)
    - [Latest changes](#latest-changes)
  - [Versioning](#versioning)
  - [Thank you](#thank-you)
  - [Documentation](#documentation)
  - [Support and contributing](#support-and-contributing)
  - [Submodules](#submodules)

<a id="how-to-install"></a>

## How to install

<a id="generate-locally-(recommended)"></a>

### Generate locally (recommended)

You can generate type annotations for `aioboto3` package locally with
`mypy-boto3-builder`. Use
[uv](https://docs.astral.sh/uv/getting-started/installation/) for build
isolation.

1. Run mypy-boto3-builder in your package root directory:
   `uvx --with 'aioboto3==15.4.0' mypy-boto3-builder`
2. Select `aioboto3` AWS SDK.
3. Select services you use in the current project.
4. Use provided commands to install generated packages.

<a id="from-pypi-with-pip"></a>

### From PyPI with pip

Install `types-aioboto3` to add type checking for `aioboto3` package.

```bash
# install type annotations only for aioboto3
python -m pip install types-aioboto3

# install aioboto3 type annotations
# for cloudformation, dynamodb, ec2, lambda, rds, s3, sqs
python -m pip install 'types-aioboto3[essential]'

# or install annotations for services you use
python -m pip install 'types-aioboto3[acm,apigateway]'

# or install annotations in sync with aioboto3 version
python -m pip install 'types-aioboto3[aioboto3]'

# or install all-in-one annotations for all services
python -m pip install 'types-aioboto3[full]'

# Lite version does not provide session.client/resource overloads
# it is more RAM-friendly, but requires explicit type annotations
python -m pip install 'types-aioboto3-lite[essential]'
```

<a id="how-to-uninstall"></a>

## How to uninstall

```bash
# uninstall types-aioboto3
python -m pip uninstall -y types-aioboto3
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
- Install `types-aioboto3[essential]` in your environment:

```bash
python -m pip install 'types-aioboto3[essential]'
```

Both type checking and code completion should now work. No explicit type
annotations required, write your `aioboto3` code as usual.

<a id="pycharm"></a>

### PyCharm

> ⚠️ Due to slow PyCharm performance on `Literal` overloads (issue
> [PY-40997](https://youtrack.jetbrains.com/issue/PY-40997)), it is recommended
> to use [types-aioboto3-lite](https://pypi.org/project/types-aioboto3-lite/)
> until the issue is resolved.

> ⚠️ If you experience slow performance and high CPU usage, try to disable
> `PyCharm` type checker and use [mypy](https://github.com/python/mypy) or
> [pyright](https://github.com/microsoft/pyright) instead.

> ⚠️ To continue using `PyCharm` type checker, you can try to replace
> `types-aioboto3` with
> [types-aioboto3-lite](https://pypi.org/project/types-aioboto3-lite/):

```bash
pip uninstall types-aioboto3
pip install types-aioboto3-lite
```

Install `types-aioboto3[essential]` in your environment:

```bash
python -m pip install 'types-aioboto3[essential]'
```

Both type checking and code completion should now work.

<a id="emacs"></a>

### Emacs

- Install `types-aioboto3` with services you use in your environment:

```bash
python -m pip install 'types-aioboto3[essential]'
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

- Make sure emacs uses the environment where you have installed
  `types-aioboto3`

Type checking should now work. No explicit type annotations required, write
your `aioboto3` code as usual.

<a id="sublime-text"></a>

### Sublime Text

- Install `types-aioboto3[essential]` with services you use in your
  environment:

```bash
python -m pip install 'types-aioboto3[essential]'
```

- Install [LSP-pyright](https://github.com/sublimelsp/LSP-pyright) package

Type checking should now work. No explicit type annotations required, write
your `aioboto3` code as usual.

<a id="other-ides"></a>

### Other IDEs

Not tested, but as long as your IDE supports `mypy` or `pyright`, everything
should work.

<a id="mypy"></a>

### mypy

- Install `mypy`: `python -m pip install mypy`
- Install `types-aioboto3[essential]` in your environment:

```bash
python -m pip install 'types-aioboto3[essential]'
```

Type checking should now work. No explicit type annotations required, write
your `aioboto3` code as usual.

<a id="pyright"></a>

### pyright

- Install `pyright`: `npm i -g pyright`
- Install `types-aioboto3[essential]` in your environment:

```bash
python -m pip install 'types-aioboto3[essential]'
```

Optionally, you can install `types-aioboto3` to `typings` directory.

Type checking should now work. No explicit type annotations required, write
your `aioboto3` code as usual.

<a id="pylint-compatibility"></a>

### Pylint compatibility

It is totally safe to use `TYPE_CHECKING` flag in order to avoid
`types-aioboto3` dependency in production. However, there is an issue in
`pylint` that it complains about undefined variables. To fix it, set all types
to `object` in non-`TYPE_CHECKING` mode.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types_aiobotocore_ec2 import EC2Client, EC2ServiceResource
    from types_aiobotocore_ec2.waiters import BundleTaskCompleteWaiter
    from types_aiobotocore_ec2.paginators import DescribeVolumesPaginator
else:
    EC2Client = object
    EC2ServiceResource = object
    BundleTaskCompleteWaiter = object
    DescribeVolumesPaginator = object

...
```

<a id="how-it-works"></a>

## How it works

Fully automated
[mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder) carefully
generates type annotations for each service, patiently waiting for `aioboto3`
updates. It delivers drop-in type annotations for you and makes sure that:

- All available `aioboto3` services are covered.
- Each public class and method of every `aioboto3` service gets valid type
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

`types-aioboto3` version is the same as related `aioboto3` version and follows
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
[aioboto3 docs](https://youtype.github.io/types_aioboto3_docs/)

<a id="support-and-contributing"></a>

## Support and contributing

This package is auto-generated. Please reports any bugs or request new features
in [mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder/issues/)
repository.

<a id="submodules"></a>

## Submodules

- `types-aioboto3[full]` - Type annotations for all 412 services in one package
  (recommended).
- `types-aioboto3[all]` - Type annotations for all 412 services in separate
  packages.
- `types-aioboto3[essential]` - Type annotations for
  [CloudFormation](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudformation/),
  [DynamoDB](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_dynamodb/),
  [EC2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ec2/),
  [Lambda](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_lambda/),
  [RDS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_rds/),
  [S3](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_s3/) and
  [SQS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sqs/)
  services.
- `types-aioboto3[aioboto3]` - Install annotations in sync with `aioboto3`
  version.
- `types-aioboto3[accessanalyzer]` - Type annotations for
  [AccessAnalyzer](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_accessanalyzer/)
  service.
- `types-aioboto3[account]` - Type annotations for
  [Account](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_account/)
  service.
- `types-aioboto3[acm]` - Type annotations for
  [ACM](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_acm/)
  service.
- `types-aioboto3[acm-pca]` - Type annotations for
  [ACMPCA](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_acm_pca/)
  service.
- `types-aioboto3[aiops]` - Type annotations for
  [AIOps](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_aiops/)
  service.
- `types-aioboto3[amp]` - Type annotations for
  [PrometheusService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_amp/)
  service.
- `types-aioboto3[amplify]` - Type annotations for
  [Amplify](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_amplify/)
  service.
- `types-aioboto3[amplifybackend]` - Type annotations for
  [AmplifyBackend](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_amplifybackend/)
  service.
- `types-aioboto3[amplifyuibuilder]` - Type annotations for
  [AmplifyUIBuilder](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_amplifyuibuilder/)
  service.
- `types-aioboto3[apigateway]` - Type annotations for
  [APIGateway](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_apigateway/)
  service.
- `types-aioboto3[apigatewaymanagementapi]` - Type annotations for
  [ApiGatewayManagementApi](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_apigatewaymanagementapi/)
  service.
- `types-aioboto3[apigatewayv2]` - Type annotations for
  [ApiGatewayV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_apigatewayv2/)
  service.
- `types-aioboto3[appconfig]` - Type annotations for
  [AppConfig](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_appconfig/)
  service.
- `types-aioboto3[appconfigdata]` - Type annotations for
  [AppConfigData](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_appconfigdata/)
  service.
- `types-aioboto3[appfabric]` - Type annotations for
  [AppFabric](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_appfabric/)
  service.
- `types-aioboto3[appflow]` - Type annotations for
  [Appflow](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_appflow/)
  service.
- `types-aioboto3[appintegrations]` - Type annotations for
  [AppIntegrationsService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_appintegrations/)
  service.
- `types-aioboto3[application-autoscaling]` - Type annotations for
  [ApplicationAutoScaling](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_application_autoscaling/)
  service.
- `types-aioboto3[application-insights]` - Type annotations for
  [ApplicationInsights](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_application_insights/)
  service.
- `types-aioboto3[application-signals]` - Type annotations for
  [CloudWatchApplicationSignals](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_application_signals/)
  service.
- `types-aioboto3[applicationcostprofiler]` - Type annotations for
  [ApplicationCostProfiler](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_applicationcostprofiler/)
  service.
- `types-aioboto3[appmesh]` - Type annotations for
  [AppMesh](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_appmesh/)
  service.
- `types-aioboto3[apprunner]` - Type annotations for
  [AppRunner](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_apprunner/)
  service.
- `types-aioboto3[appstream]` - Type annotations for
  [AppStream](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_appstream/)
  service.
- `types-aioboto3[appsync]` - Type annotations for
  [AppSync](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_appsync/)
  service.
- `types-aioboto3[apptest]` - Type annotations for
  [MainframeModernizationApplicationTesting](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_apptest/)
  service.
- `types-aioboto3[arc-region-switch]` - Type annotations for
  [ARCRegionswitch](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_arc_region_switch/)
  service.
- `types-aioboto3[arc-zonal-shift]` - Type annotations for
  [ARCZonalShift](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_arc_zonal_shift/)
  service.
- `types-aioboto3[artifact]` - Type annotations for
  [Artifact](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_artifact/)
  service.
- `types-aioboto3[athena]` - Type annotations for
  [Athena](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_athena/)
  service.
- `types-aioboto3[auditmanager]` - Type annotations for
  [AuditManager](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_auditmanager/)
  service.
- `types-aioboto3[autoscaling]` - Type annotations for
  [AutoScaling](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_autoscaling/)
  service.
- `types-aioboto3[autoscaling-plans]` - Type annotations for
  [AutoScalingPlans](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_autoscaling_plans/)
  service.
- `types-aioboto3[b2bi]` - Type annotations for
  [B2BI](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_b2bi/)
  service.
- `types-aioboto3[backup]` - Type annotations for
  [Backup](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_backup/)
  service.
- `types-aioboto3[backup-gateway]` - Type annotations for
  [BackupGateway](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_backup_gateway/)
  service.
- `types-aioboto3[backupsearch]` - Type annotations for
  [BackupSearch](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_backupsearch/)
  service.
- `types-aioboto3[batch]` - Type annotations for
  [Batch](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_batch/)
  service.
- `types-aioboto3[bcm-dashboards]` - Type annotations for
  [BillingandCostManagementDashboards](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bcm_dashboards/)
  service.
- `types-aioboto3[bcm-data-exports]` - Type annotations for
  [BillingandCostManagementDataExports](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bcm_data_exports/)
  service.
- `types-aioboto3[bcm-pricing-calculator]` - Type annotations for
  [BillingandCostManagementPricingCalculator](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bcm_pricing_calculator/)
  service.
- `types-aioboto3[bcm-recommended-actions]` - Type annotations for
  [BillingandCostManagementRecommendedActions](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bcm_recommended_actions/)
  service.
- `types-aioboto3[bedrock]` - Type annotations for
  [Bedrock](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bedrock/)
  service.
- `types-aioboto3[bedrock-agent]` - Type annotations for
  [AgentsforBedrock](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bedrock_agent/)
  service.
- `types-aioboto3[bedrock-agent-runtime]` - Type annotations for
  [AgentsforBedrockRuntime](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bedrock_agent_runtime/)
  service.
- `types-aioboto3[bedrock-agentcore]` - Type annotations for
  [BedrockAgentCoreDataPlaneFrontingLayer](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bedrock_agentcore/)
  service.
- `types-aioboto3[bedrock-agentcore-control]` - Type annotations for
  [BedrockAgentCoreControlPlaneFrontingLayer](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bedrock_agentcore_control/)
  service.
- `types-aioboto3[bedrock-data-automation]` - Type annotations for
  [DataAutomationforBedrock](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bedrock_data_automation/)
  service.
- `types-aioboto3[bedrock-data-automation-runtime]` - Type annotations for
  [RuntimeforBedrockDataAutomation](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bedrock_data_automation_runtime/)
  service.
- `types-aioboto3[bedrock-runtime]` - Type annotations for
  [BedrockRuntime](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_bedrock_runtime/)
  service.
- `types-aioboto3[billing]` - Type annotations for
  [Billing](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_billing/)
  service.
- `types-aioboto3[billingconductor]` - Type annotations for
  [BillingConductor](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_billingconductor/)
  service.
- `types-aioboto3[braket]` - Type annotations for
  [Braket](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_braket/)
  service.
- `types-aioboto3[budgets]` - Type annotations for
  [Budgets](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_budgets/)
  service.
- `types-aioboto3[ce]` - Type annotations for
  [CostExplorer](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ce/)
  service.
- `types-aioboto3[chatbot]` - Type annotations for
  [Chatbot](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_chatbot/)
  service.
- `types-aioboto3[chime]` - Type annotations for
  [Chime](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_chime/)
  service.
- `types-aioboto3[chime-sdk-identity]` - Type annotations for
  [ChimeSDKIdentity](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_chime_sdk_identity/)
  service.
- `types-aioboto3[chime-sdk-media-pipelines]` - Type annotations for
  [ChimeSDKMediaPipelines](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_chime_sdk_media_pipelines/)
  service.
- `types-aioboto3[chime-sdk-meetings]` - Type annotations for
  [ChimeSDKMeetings](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_chime_sdk_meetings/)
  service.
- `types-aioboto3[chime-sdk-messaging]` - Type annotations for
  [ChimeSDKMessaging](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_chime_sdk_messaging/)
  service.
- `types-aioboto3[chime-sdk-voice]` - Type annotations for
  [ChimeSDKVoice](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_chime_sdk_voice/)
  service.
- `types-aioboto3[cleanrooms]` - Type annotations for
  [CleanRoomsService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cleanrooms/)
  service.
- `types-aioboto3[cleanroomsml]` - Type annotations for
  [CleanRoomsML](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cleanroomsml/)
  service.
- `types-aioboto3[cloud9]` - Type annotations for
  [Cloud9](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloud9/)
  service.
- `types-aioboto3[cloudcontrol]` - Type annotations for
  [CloudControlApi](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudcontrol/)
  service.
- `types-aioboto3[clouddirectory]` - Type annotations for
  [CloudDirectory](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_clouddirectory/)
  service.
- `types-aioboto3[cloudformation]` - Type annotations for
  [CloudFormation](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudformation/)
  service.
- `types-aioboto3[cloudfront]` - Type annotations for
  [CloudFront](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudfront/)
  service.
- `types-aioboto3[cloudfront-keyvaluestore]` - Type annotations for
  [CloudFrontKeyValueStore](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudfront_keyvaluestore/)
  service.
- `types-aioboto3[cloudhsm]` - Type annotations for
  [CloudHSM](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudhsm/)
  service.
- `types-aioboto3[cloudhsmv2]` - Type annotations for
  [CloudHSMV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudhsmv2/)
  service.
- `types-aioboto3[cloudsearch]` - Type annotations for
  [CloudSearch](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudsearch/)
  service.
- `types-aioboto3[cloudsearchdomain]` - Type annotations for
  [CloudSearchDomain](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudsearchdomain/)
  service.
- `types-aioboto3[cloudtrail]` - Type annotations for
  [CloudTrail](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudtrail/)
  service.
- `types-aioboto3[cloudtrail-data]` - Type annotations for
  [CloudTrailDataService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudtrail_data/)
  service.
- `types-aioboto3[cloudwatch]` - Type annotations for
  [CloudWatch](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cloudwatch/)
  service.
- `types-aioboto3[codeartifact]` - Type annotations for
  [CodeArtifact](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codeartifact/)
  service.
- `types-aioboto3[codebuild]` - Type annotations for
  [CodeBuild](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codebuild/)
  service.
- `types-aioboto3[codecatalyst]` - Type annotations for
  [CodeCatalyst](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codecatalyst/)
  service.
- `types-aioboto3[codecommit]` - Type annotations for
  [CodeCommit](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codecommit/)
  service.
- `types-aioboto3[codeconnections]` - Type annotations for
  [CodeConnections](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codeconnections/)
  service.
- `types-aioboto3[codedeploy]` - Type annotations for
  [CodeDeploy](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codedeploy/)
  service.
- `types-aioboto3[codeguru-reviewer]` - Type annotations for
  [CodeGuruReviewer](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codeguru_reviewer/)
  service.
- `types-aioboto3[codeguru-security]` - Type annotations for
  [CodeGuruSecurity](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codeguru_security/)
  service.
- `types-aioboto3[codeguruprofiler]` - Type annotations for
  [CodeGuruProfiler](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codeguruprofiler/)
  service.
- `types-aioboto3[codepipeline]` - Type annotations for
  [CodePipeline](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codepipeline/)
  service.
- `types-aioboto3[codestar-connections]` - Type annotations for
  [CodeStarconnections](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codestar_connections/)
  service.
- `types-aioboto3[codestar-notifications]` - Type annotations for
  [CodeStarNotifications](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_codestar_notifications/)
  service.
- `types-aioboto3[cognito-identity]` - Type annotations for
  [CognitoIdentity](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cognito_identity/)
  service.
- `types-aioboto3[cognito-idp]` - Type annotations for
  [CognitoIdentityProvider](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cognito_idp/)
  service.
- `types-aioboto3[cognito-sync]` - Type annotations for
  [CognitoSync](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cognito_sync/)
  service.
- `types-aioboto3[comprehend]` - Type annotations for
  [Comprehend](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_comprehend/)
  service.
- `types-aioboto3[comprehendmedical]` - Type annotations for
  [ComprehendMedical](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_comprehendmedical/)
  service.
- `types-aioboto3[compute-optimizer]` - Type annotations for
  [ComputeOptimizer](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_compute_optimizer/)
  service.
- `types-aioboto3[config]` - Type annotations for
  [ConfigService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_config/)
  service.
- `types-aioboto3[connect]` - Type annotations for
  [Connect](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_connect/)
  service.
- `types-aioboto3[connect-contact-lens]` - Type annotations for
  [ConnectContactLens](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_connect_contact_lens/)
  service.
- `types-aioboto3[connectcampaigns]` - Type annotations for
  [ConnectCampaignService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_connectcampaigns/)
  service.
- `types-aioboto3[connectcampaignsv2]` - Type annotations for
  [ConnectCampaignServiceV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_connectcampaignsv2/)
  service.
- `types-aioboto3[connectcases]` - Type annotations for
  [ConnectCases](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_connectcases/)
  service.
- `types-aioboto3[connectparticipant]` - Type annotations for
  [ConnectParticipant](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_connectparticipant/)
  service.
- `types-aioboto3[controlcatalog]` - Type annotations for
  [ControlCatalog](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_controlcatalog/)
  service.
- `types-aioboto3[controltower]` - Type annotations for
  [ControlTower](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_controltower/)
  service.
- `types-aioboto3[cost-optimization-hub]` - Type annotations for
  [CostOptimizationHub](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cost_optimization_hub/)
  service.
- `types-aioboto3[cur]` - Type annotations for
  [CostandUsageReportService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_cur/)
  service.
- `types-aioboto3[customer-profiles]` - Type annotations for
  [CustomerProfiles](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_customer_profiles/)
  service.
- `types-aioboto3[databrew]` - Type annotations for
  [GlueDataBrew](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_databrew/)
  service.
- `types-aioboto3[dataexchange]` - Type annotations for
  [DataExchange](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_dataexchange/)
  service.
- `types-aioboto3[datapipeline]` - Type annotations for
  [DataPipeline](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_datapipeline/)
  service.
- `types-aioboto3[datasync]` - Type annotations for
  [DataSync](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_datasync/)
  service.
- `types-aioboto3[datazone]` - Type annotations for
  [DataZone](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_datazone/)
  service.
- `types-aioboto3[dax]` - Type annotations for
  [DAX](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_dax/)
  service.
- `types-aioboto3[deadline]` - Type annotations for
  [DeadlineCloud](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_deadline/)
  service.
- `types-aioboto3[detective]` - Type annotations for
  [Detective](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_detective/)
  service.
- `types-aioboto3[devicefarm]` - Type annotations for
  [DeviceFarm](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_devicefarm/)
  service.
- `types-aioboto3[devops-guru]` - Type annotations for
  [DevOpsGuru](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_devops_guru/)
  service.
- `types-aioboto3[directconnect]` - Type annotations for
  [DirectConnect](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_directconnect/)
  service.
- `types-aioboto3[discovery]` - Type annotations for
  [ApplicationDiscoveryService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_discovery/)
  service.
- `types-aioboto3[dlm]` - Type annotations for
  [DLM](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_dlm/)
  service.
- `types-aioboto3[dms]` - Type annotations for
  [DatabaseMigrationService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_dms/)
  service.
- `types-aioboto3[docdb]` - Type annotations for
  [DocDB](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_docdb/)
  service.
- `types-aioboto3[docdb-elastic]` - Type annotations for
  [DocDBElastic](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_docdb_elastic/)
  service.
- `types-aioboto3[drs]` - Type annotations for
  [Drs](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_drs/)
  service.
- `types-aioboto3[ds]` - Type annotations for
  [DirectoryService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ds/)
  service.
- `types-aioboto3[ds-data]` - Type annotations for
  [DirectoryServiceData](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ds_data/)
  service.
- `types-aioboto3[dsql]` - Type annotations for
  [AuroraDSQL](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_dsql/)
  service.
- `types-aioboto3[dynamodb]` - Type annotations for
  [DynamoDB](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_dynamodb/)
  service.
- `types-aioboto3[dynamodbstreams]` - Type annotations for
  [DynamoDBStreams](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_dynamodbstreams/)
  service.
- `types-aioboto3[ebs]` - Type annotations for
  [EBS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ebs/)
  service.
- `types-aioboto3[ec2]` - Type annotations for
  [EC2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ec2/)
  service.
- `types-aioboto3[ec2-instance-connect]` - Type annotations for
  [EC2InstanceConnect](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ec2_instance_connect/)
  service.
- `types-aioboto3[ecr]` - Type annotations for
  [ECR](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ecr/)
  service.
- `types-aioboto3[ecr-public]` - Type annotations for
  [ECRPublic](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ecr_public/)
  service.
- `types-aioboto3[ecs]` - Type annotations for
  [ECS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ecs/)
  service.
- `types-aioboto3[efs]` - Type annotations for
  [EFS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_efs/)
  service.
- `types-aioboto3[eks]` - Type annotations for
  [EKS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_eks/)
  service.
- `types-aioboto3[eks-auth]` - Type annotations for
  [EKSAuth](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_eks_auth/)
  service.
- `types-aioboto3[elasticache]` - Type annotations for
  [ElastiCache](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_elasticache/)
  service.
- `types-aioboto3[elasticbeanstalk]` - Type annotations for
  [ElasticBeanstalk](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_elasticbeanstalk/)
  service.
- `types-aioboto3[elastictranscoder]` - Type annotations for
  [ElasticTranscoder](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_elastictranscoder/)
  service.
- `types-aioboto3[elb]` - Type annotations for
  [ElasticLoadBalancing](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_elb/)
  service.
- `types-aioboto3[elbv2]` - Type annotations for
  [ElasticLoadBalancingv2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_elbv2/)
  service.
- `types-aioboto3[emr]` - Type annotations for
  [EMR](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_emr/)
  service.
- `types-aioboto3[emr-containers]` - Type annotations for
  [EMRContainers](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_emr_containers/)
  service.
- `types-aioboto3[emr-serverless]` - Type annotations for
  [EMRServerless](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_emr_serverless/)
  service.
- `types-aioboto3[entityresolution]` - Type annotations for
  [EntityResolution](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_entityresolution/)
  service.
- `types-aioboto3[es]` - Type annotations for
  [ElasticsearchService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_es/)
  service.
- `types-aioboto3[events]` - Type annotations for
  [EventBridge](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_events/)
  service.
- `types-aioboto3[evidently]` - Type annotations for
  [CloudWatchEvidently](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_evidently/)
  service.
- `types-aioboto3[evs]` - Type annotations for
  [EVS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_evs/)
  service.
- `types-aioboto3[finspace]` - Type annotations for
  [Finspace](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_finspace/)
  service.
- `types-aioboto3[finspace-data]` - Type annotations for
  [FinSpaceData](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_finspace_data/)
  service.
- `types-aioboto3[firehose]` - Type annotations for
  [Firehose](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_firehose/)
  service.
- `types-aioboto3[fis]` - Type annotations for
  [FIS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_fis/)
  service.
- `types-aioboto3[fms]` - Type annotations for
  [FMS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_fms/)
  service.
- `types-aioboto3[forecast]` - Type annotations for
  [ForecastService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_forecast/)
  service.
- `types-aioboto3[forecastquery]` - Type annotations for
  [ForecastQueryService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_forecastquery/)
  service.
- `types-aioboto3[frauddetector]` - Type annotations for
  [FraudDetector](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_frauddetector/)
  service.
- `types-aioboto3[freetier]` - Type annotations for
  [FreeTier](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_freetier/)
  service.
- `types-aioboto3[fsx]` - Type annotations for
  [FSx](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_fsx/)
  service.
- `types-aioboto3[gamelift]` - Type annotations for
  [GameLift](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_gamelift/)
  service.
- `types-aioboto3[gameliftstreams]` - Type annotations for
  [GameLiftStreams](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_gameliftstreams/)
  service.
- `types-aioboto3[geo-maps]` - Type annotations for
  [LocationServiceMapsV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_geo_maps/)
  service.
- `types-aioboto3[geo-places]` - Type annotations for
  [LocationServicePlacesV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_geo_places/)
  service.
- `types-aioboto3[geo-routes]` - Type annotations for
  [LocationServiceRoutesV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_geo_routes/)
  service.
- `types-aioboto3[glacier]` - Type annotations for
  [Glacier](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_glacier/)
  service.
- `types-aioboto3[globalaccelerator]` - Type annotations for
  [GlobalAccelerator](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_globalaccelerator/)
  service.
- `types-aioboto3[glue]` - Type annotations for
  [Glue](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_glue/)
  service.
- `types-aioboto3[grafana]` - Type annotations for
  [ManagedGrafana](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_grafana/)
  service.
- `types-aioboto3[greengrass]` - Type annotations for
  [Greengrass](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_greengrass/)
  service.
- `types-aioboto3[greengrassv2]` - Type annotations for
  [GreengrassV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_greengrassv2/)
  service.
- `types-aioboto3[groundstation]` - Type annotations for
  [GroundStation](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_groundstation/)
  service.
- `types-aioboto3[guardduty]` - Type annotations for
  [GuardDuty](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_guardduty/)
  service.
- `types-aioboto3[health]` - Type annotations for
  [Health](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_health/)
  service.
- `types-aioboto3[healthlake]` - Type annotations for
  [HealthLake](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_healthlake/)
  service.
- `types-aioboto3[iam]` - Type annotations for
  [IAM](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iam/)
  service.
- `types-aioboto3[identitystore]` - Type annotations for
  [IdentityStore](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_identitystore/)
  service.
- `types-aioboto3[imagebuilder]` - Type annotations for
  [Imagebuilder](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_imagebuilder/)
  service.
- `types-aioboto3[importexport]` - Type annotations for
  [ImportExport](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_importexport/)
  service.
- `types-aioboto3[inspector]` - Type annotations for
  [Inspector](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_inspector/)
  service.
- `types-aioboto3[inspector-scan]` - Type annotations for
  [Inspectorscan](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_inspector_scan/)
  service.
- `types-aioboto3[inspector2]` - Type annotations for
  [Inspector2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_inspector2/)
  service.
- `types-aioboto3[internetmonitor]` - Type annotations for
  [CloudWatchInternetMonitor](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_internetmonitor/)
  service.
- `types-aioboto3[invoicing]` - Type annotations for
  [Invoicing](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_invoicing/)
  service.
- `types-aioboto3[iot]` - Type annotations for
  [IoT](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iot/)
  service.
- `types-aioboto3[iot-data]` - Type annotations for
  [IoTDataPlane](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iot_data/)
  service.
- `types-aioboto3[iot-jobs-data]` - Type annotations for
  [IoTJobsDataPlane](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iot_jobs_data/)
  service.
- `types-aioboto3[iot-managed-integrations]` - Type annotations for
  [ManagedintegrationsforIoTDeviceManagement](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iot_managed_integrations/)
  service.
- `types-aioboto3[iotanalytics]` - Type annotations for
  [IoTAnalytics](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iotanalytics/)
  service.
- `types-aioboto3[iotdeviceadvisor]` - Type annotations for
  [IoTDeviceAdvisor](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iotdeviceadvisor/)
  service.
- `types-aioboto3[iotevents]` - Type annotations for
  [IoTEvents](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iotevents/)
  service.
- `types-aioboto3[iotevents-data]` - Type annotations for
  [IoTEventsData](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iotevents_data/)
  service.
- `types-aioboto3[iotfleethub]` - Type annotations for
  [IoTFleetHub](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iotfleethub/)
  service.
- `types-aioboto3[iotfleetwise]` - Type annotations for
  [IoTFleetWise](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iotfleetwise/)
  service.
- `types-aioboto3[iotsecuretunneling]` - Type annotations for
  [IoTSecureTunneling](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iotsecuretunneling/)
  service.
- `types-aioboto3[iotsitewise]` - Type annotations for
  [IoTSiteWise](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iotsitewise/)
  service.
- `types-aioboto3[iotthingsgraph]` - Type annotations for
  [IoTThingsGraph](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iotthingsgraph/)
  service.
- `types-aioboto3[iottwinmaker]` - Type annotations for
  [IoTTwinMaker](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iottwinmaker/)
  service.
- `types-aioboto3[iotwireless]` - Type annotations for
  [IoTWireless](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_iotwireless/)
  service.
- `types-aioboto3[ivs]` - Type annotations for
  [IVS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ivs/)
  service.
- `types-aioboto3[ivs-realtime]` - Type annotations for
  [Ivsrealtime](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ivs_realtime/)
  service.
- `types-aioboto3[ivschat]` - Type annotations for
  [Ivschat](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ivschat/)
  service.
- `types-aioboto3[kafka]` - Type annotations for
  [Kafka](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kafka/)
  service.
- `types-aioboto3[kafkaconnect]` - Type annotations for
  [KafkaConnect](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kafkaconnect/)
  service.
- `types-aioboto3[kendra]` - Type annotations for
  [Kendra](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kendra/)
  service.
- `types-aioboto3[kendra-ranking]` - Type annotations for
  [KendraRanking](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kendra_ranking/)
  service.
- `types-aioboto3[keyspaces]` - Type annotations for
  [Keyspaces](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_keyspaces/)
  service.
- `types-aioboto3[keyspacesstreams]` - Type annotations for
  [KeyspacesStreams](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_keyspacesstreams/)
  service.
- `types-aioboto3[kinesis]` - Type annotations for
  [Kinesis](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kinesis/)
  service.
- `types-aioboto3[kinesis-video-archived-media]` - Type annotations for
  [KinesisVideoArchivedMedia](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kinesis_video_archived_media/)
  service.
- `types-aioboto3[kinesis-video-media]` - Type annotations for
  [KinesisVideoMedia](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kinesis_video_media/)
  service.
- `types-aioboto3[kinesis-video-signaling]` - Type annotations for
  [KinesisVideoSignalingChannels](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kinesis_video_signaling/)
  service.
- `types-aioboto3[kinesis-video-webrtc-storage]` - Type annotations for
  [KinesisVideoWebRTCStorage](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kinesis_video_webrtc_storage/)
  service.
- `types-aioboto3[kinesisanalytics]` - Type annotations for
  [KinesisAnalytics](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kinesisanalytics/)
  service.
- `types-aioboto3[kinesisanalyticsv2]` - Type annotations for
  [KinesisAnalyticsV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kinesisanalyticsv2/)
  service.
- `types-aioboto3[kinesisvideo]` - Type annotations for
  [KinesisVideo](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kinesisvideo/)
  service.
- `types-aioboto3[kms]` - Type annotations for
  [KMS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_kms/)
  service.
- `types-aioboto3[lakeformation]` - Type annotations for
  [LakeFormation](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_lakeformation/)
  service.
- `types-aioboto3[lambda]` - Type annotations for
  [Lambda](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_lambda/)
  service.
- `types-aioboto3[launch-wizard]` - Type annotations for
  [LaunchWizard](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_launch_wizard/)
  service.
- `types-aioboto3[lex-models]` - Type annotations for
  [LexModelBuildingService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_lex_models/)
  service.
- `types-aioboto3[lex-runtime]` - Type annotations for
  [LexRuntimeService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_lex_runtime/)
  service.
- `types-aioboto3[lexv2-models]` - Type annotations for
  [LexModelsV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_lexv2_models/)
  service.
- `types-aioboto3[lexv2-runtime]` - Type annotations for
  [LexRuntimeV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_lexv2_runtime/)
  service.
- `types-aioboto3[license-manager]` - Type annotations for
  [LicenseManager](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_license_manager/)
  service.
- `types-aioboto3[license-manager-linux-subscriptions]` - Type annotations for
  [LicenseManagerLinuxSubscriptions](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_license_manager_linux_subscriptions/)
  service.
- `types-aioboto3[license-manager-user-subscriptions]` - Type annotations for
  [LicenseManagerUserSubscriptions](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_license_manager_user_subscriptions/)
  service.
- `types-aioboto3[lightsail]` - Type annotations for
  [Lightsail](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_lightsail/)
  service.
- `types-aioboto3[location]` - Type annotations for
  [LocationService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_location/)
  service.
- `types-aioboto3[logs]` - Type annotations for
  [CloudWatchLogs](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_logs/)
  service.
- `types-aioboto3[lookoutequipment]` - Type annotations for
  [LookoutEquipment](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_lookoutequipment/)
  service.
- `types-aioboto3[lookoutmetrics]` - Type annotations for
  [LookoutMetrics](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_lookoutmetrics/)
  service.
- `types-aioboto3[lookoutvision]` - Type annotations for
  [LookoutforVision](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_lookoutvision/)
  service.
- `types-aioboto3[m2]` - Type annotations for
  [MainframeModernization](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_m2/)
  service.
- `types-aioboto3[machinelearning]` - Type annotations for
  [MachineLearning](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_machinelearning/)
  service.
- `types-aioboto3[macie2]` - Type annotations for
  [Macie2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_macie2/)
  service.
- `types-aioboto3[mailmanager]` - Type annotations for
  [MailManager](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mailmanager/)
  service.
- `types-aioboto3[managedblockchain]` - Type annotations for
  [ManagedBlockchain](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_managedblockchain/)
  service.
- `types-aioboto3[managedblockchain-query]` - Type annotations for
  [ManagedBlockchainQuery](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_managedblockchain_query/)
  service.
- `types-aioboto3[marketplace-agreement]` - Type annotations for
  [AgreementService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_marketplace_agreement/)
  service.
- `types-aioboto3[marketplace-catalog]` - Type annotations for
  [MarketplaceCatalog](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_marketplace_catalog/)
  service.
- `types-aioboto3[marketplace-deployment]` - Type annotations for
  [MarketplaceDeploymentService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_marketplace_deployment/)
  service.
- `types-aioboto3[marketplace-entitlement]` - Type annotations for
  [MarketplaceEntitlementService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_marketplace_entitlement/)
  service.
- `types-aioboto3[marketplace-reporting]` - Type annotations for
  [MarketplaceReportingService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_marketplace_reporting/)
  service.
- `types-aioboto3[marketplacecommerceanalytics]` - Type annotations for
  [MarketplaceCommerceAnalytics](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_marketplacecommerceanalytics/)
  service.
- `types-aioboto3[mediaconnect]` - Type annotations for
  [MediaConnect](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mediaconnect/)
  service.
- `types-aioboto3[mediaconvert]` - Type annotations for
  [MediaConvert](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mediaconvert/)
  service.
- `types-aioboto3[medialive]` - Type annotations for
  [MediaLive](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_medialive/)
  service.
- `types-aioboto3[mediapackage]` - Type annotations for
  [MediaPackage](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mediapackage/)
  service.
- `types-aioboto3[mediapackage-vod]` - Type annotations for
  [MediaPackageVod](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mediapackage_vod/)
  service.
- `types-aioboto3[mediapackagev2]` - Type annotations for
  [Mediapackagev2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mediapackagev2/)
  service.
- `types-aioboto3[mediastore]` - Type annotations for
  [MediaStore](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mediastore/)
  service.
- `types-aioboto3[mediastore-data]` - Type annotations for
  [MediaStoreData](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mediastore_data/)
  service.
- `types-aioboto3[mediatailor]` - Type annotations for
  [MediaTailor](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mediatailor/)
  service.
- `types-aioboto3[medical-imaging]` - Type annotations for
  [HealthImaging](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_medical_imaging/)
  service.
- `types-aioboto3[memorydb]` - Type annotations for
  [MemoryDB](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_memorydb/)
  service.
- `types-aioboto3[meteringmarketplace]` - Type annotations for
  [MarketplaceMetering](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_meteringmarketplace/)
  service.
- `types-aioboto3[mgh]` - Type annotations for
  [MigrationHub](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mgh/)
  service.
- `types-aioboto3[mgn]` - Type annotations for
  [Mgn](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mgn/)
  service.
- `types-aioboto3[migration-hub-refactor-spaces]` - Type annotations for
  [MigrationHubRefactorSpaces](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_migration_hub_refactor_spaces/)
  service.
- `types-aioboto3[migrationhub-config]` - Type annotations for
  [MigrationHubConfig](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_migrationhub_config/)
  service.
- `types-aioboto3[migrationhuborchestrator]` - Type annotations for
  [MigrationHubOrchestrator](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_migrationhuborchestrator/)
  service.
- `types-aioboto3[migrationhubstrategy]` - Type annotations for
  [MigrationHubStrategyRecommendations](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_migrationhubstrategy/)
  service.
- `types-aioboto3[mpa]` - Type annotations for
  [MultipartyApproval](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mpa/)
  service.
- `types-aioboto3[mq]` - Type annotations for
  [MQ](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mq/)
  service.
- `types-aioboto3[mturk]` - Type annotations for
  [MTurk](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mturk/)
  service.
- `types-aioboto3[mwaa]` - Type annotations for
  [MWAA](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_mwaa/)
  service.
- `types-aioboto3[neptune]` - Type annotations for
  [Neptune](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_neptune/)
  service.
- `types-aioboto3[neptune-graph]` - Type annotations for
  [NeptuneGraph](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_neptune_graph/)
  service.
- `types-aioboto3[neptunedata]` - Type annotations for
  [NeptuneData](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_neptunedata/)
  service.
- `types-aioboto3[network-firewall]` - Type annotations for
  [NetworkFirewall](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_network_firewall/)
  service.
- `types-aioboto3[networkflowmonitor]` - Type annotations for
  [NetworkFlowMonitor](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_networkflowmonitor/)
  service.
- `types-aioboto3[networkmanager]` - Type annotations for
  [NetworkManager](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_networkmanager/)
  service.
- `types-aioboto3[networkmonitor]` - Type annotations for
  [CloudWatchNetworkMonitor](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_networkmonitor/)
  service.
- `types-aioboto3[notifications]` - Type annotations for
  [UserNotifications](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_notifications/)
  service.
- `types-aioboto3[notificationscontacts]` - Type annotations for
  [UserNotificationsContacts](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_notificationscontacts/)
  service.
- `types-aioboto3[oam]` - Type annotations for
  [CloudWatchObservabilityAccessManager](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_oam/)
  service.
- `types-aioboto3[observabilityadmin]` - Type annotations for
  [CloudWatchObservabilityAdminService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_observabilityadmin/)
  service.
- `types-aioboto3[odb]` - Type annotations for
  [Odb](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_odb/)
  service.
- `types-aioboto3[omics]` - Type annotations for
  [Omics](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_omics/)
  service.
- `types-aioboto3[opensearch]` - Type annotations for
  [OpenSearchService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_opensearch/)
  service.
- `types-aioboto3[opensearchserverless]` - Type annotations for
  [OpenSearchServiceServerless](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_opensearchserverless/)
  service.
- `types-aioboto3[organizations]` - Type annotations for
  [Organizations](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_organizations/)
  service.
- `types-aioboto3[osis]` - Type annotations for
  [OpenSearchIngestion](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_osis/)
  service.
- `types-aioboto3[outposts]` - Type annotations for
  [Outposts](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_outposts/)
  service.
- `types-aioboto3[panorama]` - Type annotations for
  [Panorama](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_panorama/)
  service.
- `types-aioboto3[partnercentral-selling]` - Type annotations for
  [PartnerCentralSellingAPI](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_partnercentral_selling/)
  service.
- `types-aioboto3[payment-cryptography]` - Type annotations for
  [PaymentCryptographyControlPlane](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_payment_cryptography/)
  service.
- `types-aioboto3[payment-cryptography-data]` - Type annotations for
  [PaymentCryptographyDataPlane](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_payment_cryptography_data/)
  service.
- `types-aioboto3[pca-connector-ad]` - Type annotations for
  [PcaConnectorAd](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_pca_connector_ad/)
  service.
- `types-aioboto3[pca-connector-scep]` - Type annotations for
  [PrivateCAConnectorforSCEP](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_pca_connector_scep/)
  service.
- `types-aioboto3[pcs]` - Type annotations for
  [ParallelComputingService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_pcs/)
  service.
- `types-aioboto3[personalize]` - Type annotations for
  [Personalize](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_personalize/)
  service.
- `types-aioboto3[personalize-events]` - Type annotations for
  [PersonalizeEvents](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_personalize_events/)
  service.
- `types-aioboto3[personalize-runtime]` - Type annotations for
  [PersonalizeRuntime](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_personalize_runtime/)
  service.
- `types-aioboto3[pi]` - Type annotations for
  [PI](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_pi/)
  service.
- `types-aioboto3[pinpoint]` - Type annotations for
  [Pinpoint](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_pinpoint/)
  service.
- `types-aioboto3[pinpoint-email]` - Type annotations for
  [PinpointEmail](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_pinpoint_email/)
  service.
- `types-aioboto3[pinpoint-sms-voice]` - Type annotations for
  [PinpointSMSVoice](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_pinpoint_sms_voice/)
  service.
- `types-aioboto3[pinpoint-sms-voice-v2]` - Type annotations for
  [PinpointSMSVoiceV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_pinpoint_sms_voice_v2/)
  service.
- `types-aioboto3[pipes]` - Type annotations for
  [EventBridgePipes](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_pipes/)
  service.
- `types-aioboto3[polly]` - Type annotations for
  [Polly](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_polly/)
  service.
- `types-aioboto3[pricing]` - Type annotations for
  [Pricing](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_pricing/)
  service.
- `types-aioboto3[proton]` - Type annotations for
  [Proton](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_proton/)
  service.
- `types-aioboto3[qapps]` - Type annotations for
  [QApps](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_qapps/)
  service.
- `types-aioboto3[qbusiness]` - Type annotations for
  [QBusiness](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_qbusiness/)
  service.
- `types-aioboto3[qconnect]` - Type annotations for
  [QConnect](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_qconnect/)
  service.
- `types-aioboto3[qldb]` - Type annotations for
  [QLDB](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_qldb/)
  service.
- `types-aioboto3[qldb-session]` - Type annotations for
  [QLDBSession](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_qldb_session/)
  service.
- `types-aioboto3[quicksight]` - Type annotations for
  [QuickSight](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_quicksight/)
  service.
- `types-aioboto3[ram]` - Type annotations for
  [RAM](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ram/)
  service.
- `types-aioboto3[rbin]` - Type annotations for
  [RecycleBin](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_rbin/)
  service.
- `types-aioboto3[rds]` - Type annotations for
  [RDS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_rds/)
  service.
- `types-aioboto3[rds-data]` - Type annotations for
  [RDSDataService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_rds_data/)
  service.
- `types-aioboto3[redshift]` - Type annotations for
  [Redshift](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_redshift/)
  service.
- `types-aioboto3[redshift-data]` - Type annotations for
  [RedshiftDataAPIService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_redshift_data/)
  service.
- `types-aioboto3[redshift-serverless]` - Type annotations for
  [RedshiftServerless](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_redshift_serverless/)
  service.
- `types-aioboto3[rekognition]` - Type annotations for
  [Rekognition](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_rekognition/)
  service.
- `types-aioboto3[repostspace]` - Type annotations for
  [RePostPrivate](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_repostspace/)
  service.
- `types-aioboto3[resiliencehub]` - Type annotations for
  [ResilienceHub](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_resiliencehub/)
  service.
- `types-aioboto3[resource-explorer-2]` - Type annotations for
  [ResourceExplorer](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_resource_explorer_2/)
  service.
- `types-aioboto3[resource-groups]` - Type annotations for
  [ResourceGroups](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_resource_groups/)
  service.
- `types-aioboto3[resourcegroupstaggingapi]` - Type annotations for
  [ResourceGroupsTaggingAPI](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_resourcegroupstaggingapi/)
  service.
- `types-aioboto3[robomaker]` - Type annotations for
  [RoboMaker](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_robomaker/)
  service.
- `types-aioboto3[rolesanywhere]` - Type annotations for
  [IAMRolesAnywhere](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_rolesanywhere/)
  service.
- `types-aioboto3[route53]` - Type annotations for
  [Route53](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_route53/)
  service.
- `types-aioboto3[route53-recovery-cluster]` - Type annotations for
  [Route53RecoveryCluster](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_route53_recovery_cluster/)
  service.
- `types-aioboto3[route53-recovery-control-config]` - Type annotations for
  [Route53RecoveryControlConfig](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_route53_recovery_control_config/)
  service.
- `types-aioboto3[route53-recovery-readiness]` - Type annotations for
  [Route53RecoveryReadiness](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_route53_recovery_readiness/)
  service.
- `types-aioboto3[route53domains]` - Type annotations for
  [Route53Domains](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_route53domains/)
  service.
- `types-aioboto3[route53profiles]` - Type annotations for
  [Route53Profiles](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_route53profiles/)
  service.
- `types-aioboto3[route53resolver]` - Type annotations for
  [Route53Resolver](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_route53resolver/)
  service.
- `types-aioboto3[rum]` - Type annotations for
  [CloudWatchRUM](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_rum/)
  service.
- `types-aioboto3[s3]` - Type annotations for
  [S3](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_s3/)
  service.
- `types-aioboto3[s3control]` - Type annotations for
  [S3Control](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_s3control/)
  service.
- `types-aioboto3[s3outposts]` - Type annotations for
  [S3Outposts](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_s3outposts/)
  service.
- `types-aioboto3[s3tables]` - Type annotations for
  [S3Tables](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_s3tables/)
  service.
- `types-aioboto3[s3vectors]` - Type annotations for
  [S3Vectors](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_s3vectors/)
  service.
- `types-aioboto3[sagemaker]` - Type annotations for
  [SageMaker](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sagemaker/)
  service.
- `types-aioboto3[sagemaker-a2i-runtime]` - Type annotations for
  [AugmentedAIRuntime](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sagemaker_a2i_runtime/)
  service.
- `types-aioboto3[sagemaker-edge]` - Type annotations for
  [SagemakerEdgeManager](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sagemaker_edge/)
  service.
- `types-aioboto3[sagemaker-featurestore-runtime]` - Type annotations for
  [SageMakerFeatureStoreRuntime](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sagemaker_featurestore_runtime/)
  service.
- `types-aioboto3[sagemaker-geospatial]` - Type annotations for
  [SageMakergeospatialcapabilities](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sagemaker_geospatial/)
  service.
- `types-aioboto3[sagemaker-metrics]` - Type annotations for
  [SageMakerMetrics](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sagemaker_metrics/)
  service.
- `types-aioboto3[sagemaker-runtime]` - Type annotations for
  [SageMakerRuntime](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sagemaker_runtime/)
  service.
- `types-aioboto3[savingsplans]` - Type annotations for
  [SavingsPlans](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_savingsplans/)
  service.
- `types-aioboto3[scheduler]` - Type annotations for
  [EventBridgeScheduler](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_scheduler/)
  service.
- `types-aioboto3[schemas]` - Type annotations for
  [Schemas](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_schemas/)
  service.
- `types-aioboto3[sdb]` - Type annotations for
  [SimpleDB](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sdb/)
  service.
- `types-aioboto3[secretsmanager]` - Type annotations for
  [SecretsManager](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_secretsmanager/)
  service.
- `types-aioboto3[security-ir]` - Type annotations for
  [SecurityIncidentResponse](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_security_ir/)
  service.
- `types-aioboto3[securityhub]` - Type annotations for
  [SecurityHub](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_securityhub/)
  service.
- `types-aioboto3[securitylake]` - Type annotations for
  [SecurityLake](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_securitylake/)
  service.
- `types-aioboto3[serverlessrepo]` - Type annotations for
  [ServerlessApplicationRepository](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_serverlessrepo/)
  service.
- `types-aioboto3[service-quotas]` - Type annotations for
  [ServiceQuotas](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_service_quotas/)
  service.
- `types-aioboto3[servicecatalog]` - Type annotations for
  [ServiceCatalog](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_servicecatalog/)
  service.
- `types-aioboto3[servicecatalog-appregistry]` - Type annotations for
  [AppRegistry](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_servicecatalog_appregistry/)
  service.
- `types-aioboto3[servicediscovery]` - Type annotations for
  [ServiceDiscovery](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_servicediscovery/)
  service.
- `types-aioboto3[ses]` - Type annotations for
  [SES](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ses/)
  service.
- `types-aioboto3[sesv2]` - Type annotations for
  [SESV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sesv2/)
  service.
- `types-aioboto3[shield]` - Type annotations for
  [Shield](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_shield/)
  service.
- `types-aioboto3[signer]` - Type annotations for
  [Signer](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_signer/)
  service.
- `types-aioboto3[simspaceweaver]` - Type annotations for
  [SimSpaceWeaver](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_simspaceweaver/)
  service.
- `types-aioboto3[snow-device-management]` - Type annotations for
  [SnowDeviceManagement](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_snow_device_management/)
  service.
- `types-aioboto3[snowball]` - Type annotations for
  [Snowball](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_snowball/)
  service.
- `types-aioboto3[sns]` - Type annotations for
  [SNS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sns/)
  service.
- `types-aioboto3[socialmessaging]` - Type annotations for
  [EndUserMessagingSocial](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_socialmessaging/)
  service.
- `types-aioboto3[sqs]` - Type annotations for
  [SQS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sqs/)
  service.
- `types-aioboto3[ssm]` - Type annotations for
  [SSM](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ssm/)
  service.
- `types-aioboto3[ssm-contacts]` - Type annotations for
  [SSMContacts](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ssm_contacts/)
  service.
- `types-aioboto3[ssm-guiconnect]` - Type annotations for
  [SSMGUIConnect](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ssm_guiconnect/)
  service.
- `types-aioboto3[ssm-incidents]` - Type annotations for
  [SSMIncidents](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ssm_incidents/)
  service.
- `types-aioboto3[ssm-quicksetup]` - Type annotations for
  [SystemsManagerQuickSetup](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ssm_quicksetup/)
  service.
- `types-aioboto3[ssm-sap]` - Type annotations for
  [SsmSap](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_ssm_sap/)
  service.
- `types-aioboto3[sso]` - Type annotations for
  [SSO](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sso/)
  service.
- `types-aioboto3[sso-admin]` - Type annotations for
  [SSOAdmin](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sso_admin/)
  service.
- `types-aioboto3[sso-oidc]` - Type annotations for
  [SSOOIDC](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sso_oidc/)
  service.
- `types-aioboto3[stepfunctions]` - Type annotations for
  [SFN](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_stepfunctions/)
  service.
- `types-aioboto3[storagegateway]` - Type annotations for
  [StorageGateway](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_storagegateway/)
  service.
- `types-aioboto3[sts]` - Type annotations for
  [STS](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_sts/)
  service.
- `types-aioboto3[supplychain]` - Type annotations for
  [SupplyChain](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_supplychain/)
  service.
- `types-aioboto3[support]` - Type annotations for
  [Support](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_support/)
  service.
- `types-aioboto3[support-app]` - Type annotations for
  [SupportApp](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_support_app/)
  service.
- `types-aioboto3[swf]` - Type annotations for
  [SWF](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_swf/)
  service.
- `types-aioboto3[synthetics]` - Type annotations for
  [Synthetics](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_synthetics/)
  service.
- `types-aioboto3[taxsettings]` - Type annotations for
  [TaxSettings](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_taxsettings/)
  service.
- `types-aioboto3[textract]` - Type annotations for
  [Textract](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_textract/)
  service.
- `types-aioboto3[timestream-influxdb]` - Type annotations for
  [TimestreamInfluxDB](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_timestream_influxdb/)
  service.
- `types-aioboto3[timestream-query]` - Type annotations for
  [TimestreamQuery](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_timestream_query/)
  service.
- `types-aioboto3[timestream-write]` - Type annotations for
  [TimestreamWrite](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_timestream_write/)
  service.
- `types-aioboto3[tnb]` - Type annotations for
  [TelcoNetworkBuilder](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_tnb/)
  service.
- `types-aioboto3[transcribe]` - Type annotations for
  [TranscribeService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_transcribe/)
  service.
- `types-aioboto3[transfer]` - Type annotations for
  [Transfer](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_transfer/)
  service.
- `types-aioboto3[translate]` - Type annotations for
  [Translate](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_translate/)
  service.
- `types-aioboto3[trustedadvisor]` - Type annotations for
  [TrustedAdvisorPublicAPI](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_trustedadvisor/)
  service.
- `types-aioboto3[verifiedpermissions]` - Type annotations for
  [VerifiedPermissions](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_verifiedpermissions/)
  service.
- `types-aioboto3[voice-id]` - Type annotations for
  [VoiceID](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_voice_id/)
  service.
- `types-aioboto3[vpc-lattice]` - Type annotations for
  [VPCLattice](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_vpc_lattice/)
  service.
- `types-aioboto3[waf]` - Type annotations for
  [WAF](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_waf/)
  service.
- `types-aioboto3[waf-regional]` - Type annotations for
  [WAFRegional](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_waf_regional/)
  service.
- `types-aioboto3[wafv2]` - Type annotations for
  [WAFV2](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_wafv2/)
  service.
- `types-aioboto3[wellarchitected]` - Type annotations for
  [WellArchitected](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_wellarchitected/)
  service.
- `types-aioboto3[wisdom]` - Type annotations for
  [ConnectWisdomService](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_wisdom/)
  service.
- `types-aioboto3[workdocs]` - Type annotations for
  [WorkDocs](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_workdocs/)
  service.
- `types-aioboto3[workmail]` - Type annotations for
  [WorkMail](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_workmail/)
  service.
- `types-aioboto3[workmailmessageflow]` - Type annotations for
  [WorkMailMessageFlow](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_workmailmessageflow/)
  service.
- `types-aioboto3[workspaces]` - Type annotations for
  [WorkSpaces](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_workspaces/)
  service.
- `types-aioboto3[workspaces-instances]` - Type annotations for
  [WorkspacesInstances](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_workspaces_instances/)
  service.
- `types-aioboto3[workspaces-thin-client]` - Type annotations for
  [WorkSpacesThinClient](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_workspaces_thin_client/)
  service.
- `types-aioboto3[workspaces-web]` - Type annotations for
  [WorkSpacesWeb](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_workspaces_web/)
  service.
- `types-aioboto3[xray]` - Type annotations for
  [XRay](https://youtype.github.io/types_aioboto3_docs/types_aiobotocore_xray/)
  service.
