# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2020 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module implementing the mvn plugin for csspin"""

import os
import sys
import tarfile
import urllib
from shutil import which

from csspin import (
    Verbosity,
    config,
    debug,
    die,
    download,
    exists,
    option,
    setenv,
    sh,
    task,
    warn,
)
from path import Path

defaults = config(
    exe="mvn",
    version="3.9.10",
    pom_file="pom.xml",
    mirrors=[
        "https://downloads.apache.org",
        "https://archive.apache.org/dist/",
    ],
    url="maven/maven-3/{mvn.version}/binaries/apache-maven-{mvn.version}-bin.tar.gz",
    install_dir="{spin.data}/apache-maven-{mvn.version}",
    requires=config(spin=["csspin_java.java"]),
)


def _get_mvn_use_exe(use: str) -> str:  # pylint: disable=inconsistent-return-statements
    """Get the absolute path of the Apache Maven executable to use."""
    if exec_path := which(use):
        debug(f"Using Apache Maven executable '{use}' found at '{exec_path}'.")
        return exec_path

    abs_path = os.path.abspath(use)
    if exec_path is None and os.path.exists(abs_path):
        debug(f"Using Apache Maven executable '{use}' found at '{abs_path}'.")
        return abs_path
    die(f"Could not find Apache Maven executable '{use}'.")


def provision(cfg):
    """Provision the mvn plugin"""

    if cfg.mvn.use:
        _get_mvn_use_exe(cfg.mvn.use)  # Ensure the executable is available

    elif not exists(cfg.mvn.install_dir):
        zipfile = cfg.mvn.install_dir / Path(cfg.mvn.url).basename()

        for mirror in cfg.mvn.mirrors:
            if mirror[-1] == "/":
                url = f"{mirror}{cfg.mvn.url}"
            else:
                url = f"{mirror}/{cfg.mvn.url}"
            try:
                download(url, zipfile)
                break
            except urllib.error.HTTPError:
                warn(f"Maven {cfg.mvn.version} not found at {url}")
                continue
            except urllib.error.URLError:
                warn(f"Mirror {mirror} currently not reachable")
                continue
        else:
            die(  # pylint: disable=broad-exception-raised
                "Could not download Apache Maven from any of the mirrors."
            )
        with tarfile.open(zipfile, "r:gz") as tar:
            tar.extractall(cfg.mvn.install_dir.dirname())  # nosec: B202
        zipfile.unlink()
    else:
        debug(f"Using cached Apache Maven: {cfg.mvn.install_dir}.")


def init(cfg):
    """Initialize the mvn plugin"""

    if cfg.mvn.use:
        if which(cfg.mvn.use) is None:
            setenv(PATH=os.pathsep.join((f"{_get_mvn_use_exe(cfg.mvn.use)}", "{PATH}")))
    else:
        setenv(
            PATH=os.pathsep.join(
                (f"{(cfg.mvn.install_dir / 'bin').normpath()}", "{PATH}")
            )
        )


@task(when="build")
def mvn(
    cfg,
    pom_file: option(
        "-f",  # noqa: F821
        "--file",  # noqa: F821
        "pom_file",  # noqa: F821
        show_default=(
            "Force the use of an alternate POM file "  # noqa: F722
            "(or directory with pom.xml)"
        ),
    ),
    defines: option(
        "-D",  # noqa: F821
        "--define",  # noqa: F821
        "defines",  # noqa: F821
        multiple=True,
        show_default="Define a system property",  # noqa
    ),
    args,
):
    """Run maven command"""
    cmd = "{mvn.exe}"
    if sys.platform.startswith("win32"):
        cmd += ".cmd"
    opts = cfg.mvn.opts
    if cfg.verbosity == Verbosity.QUIET:
        opts.append("-q")
    # add pom file
    opts.append("-f")
    opts.append(pom_file or cfg.mvn.pom_file)

    # add defines
    cfg_defines = cfg.mvn.defines
    for d in defines:
        name, val = d.split("=")
        cfg_defines[name] = val

    for d in cfg_defines.items():
        opts.append(f"-D{d[0]}={d[1]}")

    # do not use goals when some extra args are used
    if not args:
        opts.extend(cfg.mvn.goals)
    sh(cmd, *opts, *args)
