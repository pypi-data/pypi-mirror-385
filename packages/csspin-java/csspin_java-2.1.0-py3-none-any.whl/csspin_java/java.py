# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2021 CONTACT Software GmbH
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


"""Implementation of the java plugin for csspin"""

import os
import shutil

from csspin import config, die, echo, interpolate1, mv, setenv
from path import Path

defaults = config(install_dir="{spin.data}/java")


def set_environment(cfg):
    """Set the environment variables needed for java"""
    java_bin_dir = cfg.java.java_home / "bin"
    setenv(
        JAVA_HOME=cfg.java.java_home,
        PATH=os.pathsep.join((java_bin_dir, "{PATH}")),
    )


def configure(cfg):
    """Configure the java plugin"""
    if cfg.java.use:
        if java_path := shutil.which(interpolate1(cfg.java.use)):
            # assuming java to be $JAVA_HOME/bin/java
            cfg.java.java_home = Path(java_path).realpath().dirname().dirname()
        else:
            die(f"Could not find java executable '{cfg.java.use}'")
    elif cfg.java.version:
        cfg.java.java_home = Path(interpolate1(cfg.java.install_dir)) / str(
            cfg.java.version
        )
    else:
        die(
            "'csspin_java.java' does not set a default version for java. "
            "Set either 'java.version' or 'java.use'."
        )


def provision(cfg):
    """Install java if it does not exist"""
    if cfg.java.version and not (cfg.java.use or cfg.java.java_home.exists()):
        from tempfile import TemporaryDirectory

        import jdk

        with TemporaryDirectory() as tmp_dir:
            echo(f"Downloading JDK from {jdk.get_download_url(cfg.java.version)}")
            jdk_path = jdk.install(cfg.java.version, path=Path(tmp_dir))
            mv(jdk_path, cfg.java.java_home)

    set_environment(cfg)


def init(cfg):
    """Initialize the environment"""
    set_environment(cfg)
