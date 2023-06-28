# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

import spack.compilers
from spack.package import *


class CrayPmi(Package):
    """Install cray-pmi"""

    """Intended to override the main cray-pmi"""

    homepage = "https://www.hpe.com/us/en/compute/hpc/hpc-software.html"
    url = "file:///scratch/e1000/bcumming/hpe-hackathon/cray-pmi-6.1.10.tar.gz"
    maintainers = ["bcumming"]

    version(
        "6.1.10",
        sha256="537e0b924423b9a217ff260a2ba3f3446d696aacb605a7c2f30d0defcbc0ed9f",
        url="file:///scratch/e1000/bcumming/hpe-hackathon/cray-pmi-6.1.10.tar.gz",
    )

    # Fix up binaries with patchelf.
    depends_on("patchelf", type="build")

    def get_rpaths(self):
        # Those rpaths are already set in the build environment, so
        # let's just retrieve them.
        pkgs = os.getenv("SPACK_RPATH_DIRS", "").split(":")
        compilers = os.getenv("SPACK_COMPILER_IMPLICIT_RPATHS", "").split(":")
        return ":".join([p for p in pkgs + compilers if p])

    def should_patch(self, file):
        # Returns true if non-symlink ELF file.
        if os.path.islink(file):
            return False
        try:
            with open(file, "rb") as f:
                return f.read(4) == b"\x7fELF"
        except OSError:
            return False

    def install(self, spec, prefix):
        install_tree(".", prefix)

    @run_after("install")
    def fixup_binaries(self):
        patchelf = which("patchelf")
        rpath = self.get_rpaths()
        for root, _, files in os.walk(self.prefix):
            for name in files:
                f = os.path.join(root, name)
                if not self.should_patch(f):
                    continue
                patchelf("--force-rpath", "--set-rpath", rpath, f, fail_on_error=False)

