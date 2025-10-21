"""dlthub is a plugin to OSS `dlt` adding projects, packages a runner and new cli commands."""

from dlt import hub as _hub

from dlthub.version import __version__
from dlthub._runner import PipelineRunner as _PipelineRunner
from dlthub import destinations, sources, current
from dlthub.transformations import transformation
from dlthub.common.license import self_issue_trial_license

runner = _PipelineRunner

# dlt.hub is causing circular dependency if dlthub is imported first. reload


if not _hub.__found__:
    from importlib import reload as _reload

    _reload(_hub)

__all__ = [
    "__version__",
    "current",
    "runner",
    "destinations",
    "sources",
    "transformation",
    "self_issue_trial_license",
]
