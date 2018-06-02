rustenv
==========

[![Build Status](https://travis-ci.org/chriskuehl/rustenv.svg?branch=master)](https://travis-ci.org/chriskuehl/rustenv)
[![Coverage Status](https://coveralls.io/repos/github/chriskuehl/rustenv/badge.svg?branch=master)](https://coveralls.io/github/chriskuehl/rustenv?branch=master)
[![PyPI version](https://badge.fury.io/py/rustenv.svg)](https://pypi.org/project/rustenv/)

Create virtual, activate-able environments for Rust, similar to `virtualenv`
for Python.

A virtual environment is a self-contained installation of Rust, Cargo, etc.,
which is completely isolated from any user-level installations you may have.

For example:

```bash
# Create a new rustenv
$ rustenv renv

# Run a command in it
$ renv/bin/rustc --version
rustc 1.26.1 (827013a31 2018-05-25)
$ renv/bin/cargo --version
cargo 1.26.0 (0e7c5a931 2018-04-06)

# Activate it to avoid having to prefix your commands
$ . renv/bin/activate
(renv) $ rustc --version
rustc 1.26.1 (827013a31 2018-05-25)

# Install hello-cli: https://crates.io/crates/hello-cli
(renv) $ cargo install hello-cli
(renv) $ hello
Hello World!

# Deactivate it to restore your PATH and PS1
(renv) $ deactivate_rustenv
$ rustc --version
command not found: rustc
```


## Installation

rustenv is [available via PyPI](https://pypi.org/project/rustenv/) and can be
installed using `pip`:

```bash
$ pip install rustenv
```


## Project status
### What works right now

* Everything in the example above.


### Remaining work

* Provide some additional options when creating the rustenv:
  * Allow specifying rustc / cargo version
  * Allow disabling PS1 modification, similar to virtualenv
* ...and more? (file an issue! :))
