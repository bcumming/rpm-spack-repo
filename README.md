CSCS artifactory: https://nexus.cmn.alps.cscs.ch/service/rest/repository/browse/cpe-23.03-sles15-sp3/

Use the following RPMs:
- `cray-mpich-8.1.25-gtl-0-17.sles15sp3.x86_64.rpm`
- `cray-mpich-8.1.25-gnu91-0-17.sles15sp3.x86_64.rpm`
- `cray-pmi-6.1.10-0-12.sles15sp3.x86_64.rpm`


## Plan

Target the following versions, only for gcc, in the following order
- cray-pmi@6.1.10
- cray-gtl@8.1.25
- cray-mpich@8.1.25

```
libfabric           cuda
    \                 |
     \  cray-pmi    cray-gtl
      \     |      /
       \    |     /
        cray-mpich
```

## NOTES

Running libtree on the generated binaries shows that dependencies like numactl and curl are pulled in from the system, i.e. locations like `/usr/lib64`.
This is expected because these are not explicit dependencies of the spack packages that we have created for `cray-pmi`, `cray-gtl` and `cray-mpich`.
We could explicitly add these as requirements, and have.

### RPMs

From the interwebs:
```
# nodep
rpm -ivh --nodeps foo.rpm

# in a different prefix
rpm -ivh --prefix=/opt foo.rpm
```

in Spack, the prefix is: `self.spec.prefix`

### cray-mpich-gtl

the cray-mpich-gtl rpm contains only `lib` path with the gtl libraries, and a `lib/pkgconfig` path with `cray-gtl-cuda.pc`  and `cray-gtl-hsa.pc`.
These contain:
```
prefix=/opt/cray/pe/mpich/8.1.25/gtl
includedir=${prefix}/include
libdir=${prefix}/lib
```

However, there is no `includedir`, and no headers, so this configuration isn't useful.
Though this probably isn't important, because the package is only intended to provide the libraries used by cray-mpich, which has alreadybeen compiled, so we don't include or patch the pkgconfig files.

```
==> Concretized osu-micro-benchmarks@5.9
 -   w6hnwwt  osu-micro-benchmarks@5.9%gcc@11.3.0~cuda~graphing~papi~rocm build_system=autotools arch=linux-sles15-zen2
 -   qlruoqw      ^cray-mpich@8.1.25%gcc@11.3.0~cuda~rocm build_system=generic arch=linux-sles15-zen2
 -   k5yopnf          ^cray-pmi@6.1.10%gcc@11.3.0 build_system=generic arch=linux-sles15-zen2
 -   5dkqgq3          ^libfabric@1.15.2.0%gcc@11.3.0~debug~kdreg build_system=autotools fabrics=sockets,tcp,udp arch=linux-sles15-zen2
 -   gpd5wtx          ^patchelf@0.17.2%gcc@11.3.0 build_system=autotools arch=linux-sles15-zen2

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

## Test program for PMI

Not needed if we demonstrate.
```
#include <pmi.h>

int main() {
    int flags;
    int result = 0;
    result += PMI_Init(&flags);
    result += PMI_Finalize();
    return result;
}
```
