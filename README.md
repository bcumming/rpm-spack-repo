## Plan

The first step is to split the `cray-mpich` Spack package that bundled `cray-mpich`, `cray-pmi` and `cray-mpich-gtl` into a single tar ball into individual spack packages that correspond 1-1 with the RPMs distributed by HPE.
- because existing processes
- because chain of trust

We targetted the following versions, only for gcc, in the following order:
- cray-pmi@6.1.10
    - `cray-pmi-6.1.10-0-12.sles15sp3.x86_64.rpm`
- cray-gtl@8.1.25
    - `cray-mpich-8.1.25-gtl-0-17.sles15sp3.x86_64.rpm`
- cray-mpich@8.1.25
    - `cray-mpich-8.1.25-gnu91-0-17.sles15sp3.x86_64.rpm`

The basic dependency tree between the packages is:

```
libfabric           cuda
    \                 |
     \  cray-pmi    cray-gtl
      \     |      /
       \    |     /
        cray-mpich
```

Where `cray-gtl` is an optional dependency, used if the `cray-mpich` package requests the `+cuda` variant.

This was relatively straightfoward, with the following issues hit:
- if a tar ball contains a single sub-directory (`/lib` in our case), the contents of that sub-directory are placed directly in the installatin prefix.
- because we are installing `cray-gtl` in its own prefix (as opposed to the `cray-mpich` prefix), the MPI wrappers `mpicc` etc. have to be patched to include `-L{self.spec['cray-gtl'].prefix.lib}`.

With this approach, we were able to build and run `osu-micro-benchmarks` Spack package using cray-mpich on the CSCS *hohgant* system.

See the stackinator tool for the Spack repo with the three configurations:
https://github.com/eth-cscs/stackinator/tree/523aa8edcb986dea3f62f7f53c168008466f234e/stackinator/repo

**concretisation when cray-mpich is configured by default (no cuda/rocm)**
```
==> Concretized osu-micro-benchmarks@5.9
 -   w6hnwwt  osu-micro-benchmarks@5.9%gcc@11.3.0~cuda~graphing~papi~rocm build_system=autotools arch=linux-sles15-zen2
 -   qlruoqw      ^cray-mpich@8.1.25%gcc@11.3.0~cuda~rocm build_system=generic arch=linux-sles15-zen2
 -   k5yopnf          ^cray-pmi@6.1.10%gcc@11.3.0 build_system=generic arch=linux-sles15-zen2
 -   5dkqgq3          ^libfabric@1.15.2.0%gcc@11.3.0~debug~kdreg build_system=autotools fabrics=sockets,tcp,udp arch=linux-sles15-zen2
 -   gpd5wtx          ^patchelf@0.17.2%gcc@11.3.0 build_system=autotools arch=linux-sles15-zen2
```

**concretisation for `cray-mpich +cuda`**
```
==> Concretized osu-micro-benchmarks@5.9
 -   smjat45  osu-micro-benchmarks@5.9%gcc@11.3.0~cuda~graphing~papi~rocm build_system=autotools arch=linux-sles15-zen2
 -   gcroh6n      ^cray-mpich@8.1.25%gcc@11.3.0+cuda~rocm build_system=generic arch=linux-sles15-zen2
 -   gvjlsiw          ^cray-gtl@8.1.25%gcc@11.3.0+cuda~rocm build_system=generic arch=linux-sles15-zen2
 -   oa5ctke              ^cuda@11.8.0%gcc@11.3.0~allow-unsupported-compilers~dev build_system=generic arch=linux-sles15-zen2
 -   n3z2rcw                  ^libxml2@2.10.3%gcc@11.3.0~python build_system=autotools arch=linux-sles15-zen2
[+]  ux66oco                      ^libiconv@1.17%gcc@11.3.0 build_system=autotools libs=shared,static arch=linux-sles15-zen2
 -   2cxf6rn                      ^pkgconf@1.9.5%gcc@11.3.0 build_system=autotools arch=linux-sles15-zen2
 -   rywasrf                      ^xz@5.4.1%gcc@11.3.0~pic build_system=autotools libs=shared,static arch=linux-sles15-zen2
 -   lmzqmzl                      ^zlib@1.2.13%gcc@11.3.0+optimize+pic+shared build_system=makefile arch=linux-sles15-zen2
 -   k5yopnf          ^cray-pmi@6.1.10%gcc@11.3.0 build_system=generic arch=linux-sles15-zen2
 -   5dkqgq3          ^libfabric@1.15.2.0%gcc@11.3.0~debug~kdreg build_system=autotools fabrics=sockets,tcp,udp arch=linux-sles15-zen2
 -   gpd5wtx          ^patchelf@0.17.2%gcc@11.3.0 build_system=autotools arch=linux-sles15-zen2
```

Example output:
```
└── srun -n2 -N2 --partition=cpu osu_bw
# OSU MPI Bandwidth Test v5.9
# Size      Bandwidth (MB/s)
1                       2.05
2                       4.07
4                       8.60
8                      17.15
16                     34.65
32                     69.44
64                    139.06
128                   263.36
256                   493.64
512                  1051.25
1024                 2097.47
2048                 4196.75
4096                 8326.25
8192                16320.55
16384               19975.33
32768               19271.78
65536               21507.91
131072              22239.16
262144              22489.53
524288              22707.80
1048576             22771.54
2097152             22803.64
4194304             23286.54
```

## Direct From RPM

In step 1 we manually repackaged the contents of the RPMs as tar balls.

We then investigated using the RPM directly for the `cray-pmi` package.

After some trial and error we arrived at the following in our `package.py`:
see https://github.com/eth-cscs/stackinator/blob/stackify-cray/stackinator/repo/packages/cray-pmi/package.py for the full package.

```python
    def install(self, spec, prefix):
        rpm_path = self.stage.archive_file
        tmp_path = self.stage.source_path

        args = [
            "rpm",
            "-ivh",
            "--relocate",
            f"/opt/cray/pe={prefix}",
            "--relocate",
            f"/opt/cray/pe/pmi/6.1.10={prefix}",
            "--nodeps",
            "--badreloc",
            "--dbpath",
            f"{tmp_path}",
            f"{rpm_path}"
        ]

        subprocess.run(args)
```

The stack was rebuilt and validated with the OSU benchmark.

We stopped here, because we had the proof of concept, and doing the same for the other two packages would be an exercise in box ticking.

### todo and thoughts

The RPM installer can be modified to make installation of just the components that we care about

The following information should be provided to the RPM installer:

**for compiler wrappers**
- prefix of C, C++ and Fortran compilers
- whether GTL is required, which flavour (CUDA or HSA) and the `prefix.lib` path where the library is located.

**for rpaths**
- a list of rpaths to patch
- optionally, we could leave rpath patching to the spack package - more thought is needed to find the best approach there.

One option that we floated was creating a Spack package type for CrayRPM, similar to CMake, Meson and Python package types. This could automatically perform the rpath conversion, and the interface with the RPM installation.

**SUMMARY FINISHES HERE**

## NOTES

Running libtree on the generated binaries shows that dependencies like hwloc and curl are pulled in from the system, i.e. locations like `/usr/lib64`.
This is expected because these are not explicit dependencies of the spack packages that we have created for `cray-pmi`, `cray-gtl` and `cray-mpich`.
We could explicitly add these as requirements, and have.

### cray-mpich-gtl

the cray-mpich-gtl rpm contains only `lib` path with the gtl libraries, and a `lib/pkgconfig` path with `cray-gtl-cuda.pc`  and `cray-gtl-hsa.pc`.
These contain:
```
prefix=/opt/cray/pe/mpich/8.1.25/gtl
includedir=${prefix}/include
libdir=${prefix}/lib
```

However, there is no `includedir`, and no headers, so this configuration isn't useful.
Though this probably isn't important, because the package is only intended to provide the libraries used by cray-mpich, which has already been compiled, so we don't include or patch the pkgconfig files.
