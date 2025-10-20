# Suzuki-Trotter-Evolver

A C++ header-only library for evolving states under the Schrödinger equation using first-order Suzuki-Trotter and computing switching functions.

[![Build and Test Ubuntu-latest](https://github.com/Christopher-K-Long/Suzuki-Trotter-Evolver/actions/workflows/ubuntu_latest.yml/badge.svg)](https://github.com/Christopher-K-Long/Suzuki-Trotter-Evolver/actions/workflows/ubuntu_latest.yml) [![Build and Test macOS-latest](https://github.com/Christopher-K-Long/Suzuki-Trotter-Evolver/actions/workflows/macos-latest.yml/badge.svg)](https://github.com/Christopher-K-Long/Suzuki-Trotter-Evolver/actions/workflows/macos-latest.yml) [![Build and Test Windows-latest](https://github.com/Christopher-K-Long/Suzuki-Trotter-Evolver/actions/workflows/windows-latest.yml/badge.svg)](https://github.com/Christopher-K-Long/Suzuki-Trotter-Evolver/actions/workflows/windows-latest.yml)

## Installation

Suzuki-Trotter-Evolver can be installed as follows:

```bash
git clone https://github.com/Christopher-K-Long/Suzuki-Trotter-Evolver
cd Suzuki-Trotter-Evolver
cmake -S . -B build # set optional flags here
sudo cmake --build build --config Release --target install -j $(nproc)
```

There are several optional flags that can be set:
- ``-DSuzuki-Trotter-Evolver_INSTALL_LIBRARY=ON/OFF``(Suzuki-Trotter-Evolver is installed if set to ``ON``)
- ``-DSuzuki-Trotter-Evolver_BUILD_TESTING=ON/OFF`` (The unit tests and examples are build and run if set to ``ON``)
- ``-DSuzuki-Trotter-Evolver_BUILD_DOCS=ON/OFF`` (The documentation is build if set to ``ON``)

These optional flags should be appended to ``cmake -S ../.. -B build``. All three default to ``ON`` if the project is top level (i.e. if the project is not being build as a dependency of another project).

### Requirements

Runs on Linux, macOS, and Windows. Requires:

- [Eigen3](https://eigen.tuxfamily.org/)

#### Additional requirements for testing

- [Catch2](https://github.com/catchorg/Catch2)

#### Additional requirements for building documentation

- [doxygen](https://doxygen.nl/)
- [Sphinx](https://www.sphinx-doc.org/)
- [Furo](https://github.com/pradyunsg/furo)
- [Exhale](https://exhale.readthedocs.io)
- [Breathe](https://breathe.readthedocs.io)
- [MyST-Parser](https://myst-parser.readthedocs.io/)

## Documentation

Documentation including worked examples can be found at: [https://Suzuki-Trotter-Evolver.readthedocs.io](https://Suzuki-Trotter-Evolver.readthedocs.io)

## Source Code

Source code can be found at: [https://github.com/Christopher-K-Long/Suzuki-Trotter-Evolver](https://github.com/Christopher-K-Long/Suzuki-Trotter-Evolver)

## Version and Changes

The current version is [`1.1.0`](ChangeLog.md#release-110). Please see the [Change Log](ChangeLog.md) for more details. Suzuki-Trotter-Evolver uses [semantic versioning](https://semver.org/).