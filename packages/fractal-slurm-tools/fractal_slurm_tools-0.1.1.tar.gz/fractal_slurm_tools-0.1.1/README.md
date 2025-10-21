# fractal-slurm-tools

[![PyPI version](https://img.shields.io/pypi/v/fractal-slurm-tools?color=gree)](https://pypi.org/project/fractal-slurm-tools/)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)


You can run a version of this tool from PyPI or GitHub, either via
[pipx](https://pipx.pypa.io/stable/examples/#pipx-run-examples) or
[uvx](https://docs.astral.sh/uv/guides/tools).

Examples (the CLI entrypoint <entrypoint> must be one of `fractal-slurm-aggregate` `fractal-slurm-parse-bulk` or `fractal-slurm-parse-single-job`):
```console
# Latest PyPI release
$ pipx run --spec fractal-slurm-tools <entrypoint>
$ uvx --from fractal-slurm-tools <entrypoint>

# Specific PyPI release
$ pipx run --spec fractal-slurm-tools==0.1.0 <entrypoint>
$ uvx --from fractal-slurm-tools==0.1.0 <entrypoint>

# Latest git commit on the default branch
$ pipx run --spec git+https://github.com/fractal-analytics-platform/fractal-slurm-tools.git <entrypoint>
$ uvx --from git+https://github.com/fractal-analytics-platform/fractal-slurm-tools.git <entrypoint>

# Specific git commit
$ pipx run --spec git+https://github.com/fractal-analytics-platform/fractal-slurm-tools.git@3faeefd0eac0f53c6c73d2e3179b10ff2a111793 <entrypoint>
$ uvx --from git+https://github.com/fractal-analytics-platform/fractal-slurm-tools.git@3faeefd0eac0f53c6c73d2e3179b10ff2a111793 <entrypoint>

# Specific git branch
$ pipx run --spec git+https://github.com/fractal-analytics-platform/fractal-slurm-tools.git@main <entrypoint>
$ uvx --from git+https://github.com/fractal-analytics-platform/fractal-slurm-tools.git@main <entrypoint>
```

# A useful `sacct` command
```console
sacct --format='JobID%18,JobName%18,State,ReqMem,MaxRSS,AveRSS,Elapsed,NCPUS,CPUTimeRaw,MaxDiskRead,MaxDiskWrite' -j XXXX
```

# Development

```console
$ python -m venv venv
$ source venv/bin/activate
$ python -m pip install -e .[dev]
[...]
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit

# Run mypi
$ python -m mypy ./src

# Make a release
$ bumpver update --patch --dry
```


## Contributors and license

Fractal was conceived in the Liberali Lab at the Friedrich Miescher Institute for Biomedical Research and in the Pelkmans Lab at the University of Zurich by [@jluethi](https://github.com/jluethi) and [@gusqgm](https://github.com/gusqgm). The Fractal project is now developed at the [BioVisionCenter](https://www.biovisioncenter.uzh.ch/en.html) at the University of Zurich and the project lead is with [@jluethi](https://github.com/jluethi). The core development is done under contract by [eXact lab S.r.l.](https://www.exact-lab.it).

Unless otherwise specified, Fractal components are released under the BSD 3-Clause License, and copyright is with the BioVisionCenter at the University of Zurich.
