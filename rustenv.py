"""Create Rust virtual environments.

A virtual environment is a self-contained Rust installation, holding all the
binaries and other dependencies necesary to build Rust projects (rustc, cargo,
etc.).

For example:

    # Create a new environment
    $ rustenv renv
    $ renv/bin/rustc --version
    rustc 1.28.0-nightly (c2d46037f 2018-05-24)

    # Request a specific version of Rust
    [TODO: unimplemented]
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
import urllib.request
from typing import Sequence


ACTIVATE = '''\
_RUSTENV_BIN_PATH='{RUSTENV_BIN_PATH}'
_RUSTENV_NAME='{RUSTENV_NAME}'

# TODO: it might be nice to intelligently add/remove from PATH/PS1 instead of
# just restoring the old one
_RUSTENV_OLD_PS1="$PS1"
_RUSTENV_OLD_PATH="$PATH"

export PATH="$_RUSTENV_BIN_PATH:$PATH"
export PS1="($_RUSTENV_NAME) $PS1"
hash -r 2>/dev/null

deactivate_rustenv() {{
    export PS1="$_RUSTENV_OLD_PS1"
    export PATH="$_RUSTENV_OLD_PATH"
    hash -r 2>/dev/null

    unset _RUSTENV_NAME
    unset _RUSTENV_BIN_PATH
    unset _RUSTENV_OLD_PS1
    unset _RUSTENV_OLD_PATH
}}
'''

RUSTENV_PROXY = '''\
#!/bin/sh
set -eu
rustinstall="$(dirname "$(cd -L "$(dirname "$0")" && pwd)")/rust"
export CARGO_HOME="$rustinstall"
export RUSTUP_HOME="$rustinstall"
exec "${rustinstall}/bin/$(basename "$0")" "$@"
'''


def _rustup(rustup_home: str, cargo_home: str) -> None:
    with tempfile.NamedTemporaryFile() as tf:
        shutil.copyfileobj(urllib.request.urlopen('https://sh.rustup.rs'), tf)
        tf.flush()

        subprocess.check_call(
            ('sh', tf.name, '-y', '--no-modify-path'),
            env=dict(
                os.environ,
                RUSTUP_HOME=rustup_home,
                CARGO_HOME=cargo_home,
            ),
        )


def create_rustenv(destination: str) -> None:
    rust_root = os.path.join(destination, 'rust')
    bin_root = os.path.join(destination, 'bin')
    for path in (destination, rust_root, bin_root):
        os.mkdir(path)

    _rustup(rust_root, rust_root)

    # Rust binaries require RUSTUP_HOME and CARGO_HOME to be set at all times,
    # since they're really just shims themselves.
    #
    # I'm a little conflicted between the two options:
    #
    #   (a) Require activating the rustenv before use, and have the activate
    #       script set these. This is what nodeenv does.
    #
    #   (b) Add our own shims that set these environment variables, which
    #       allows doing stuff like `rustenv/bin/rustc --version` without first
    #       activating.
    #
    # For now we're doing (b), but this might change in the future if we find a
    # reason it doesn't work well.
    #
    # TODO: look into what rustup is actually getting us -- maybe we should
    # just avoid it and install rustc and cargo ourselves?
    proxy = os.path.join(bin_root, 'rustenv-proxy')
    with open(proxy, 'w') as f:
        f.write(RUSTENV_PROXY)
    os.chmod(proxy, os.stat(proxy).st_mode | 0o111)

    rust_bins = os.path.join(rust_root, 'bin')
    for binname in os.listdir(rust_bins):
        os.symlink(proxy, os.path.join(bin_root, binname))

    with open(os.path.join(bin_root, 'activate'), 'w') as f:
        f.write(
            ACTIVATE.format(
                RUSTENV_BIN_PATH=f'{bin_root}:{rust_bins}',
                RUSTENV_NAME=os.path.basename(destination),
            ),
        )

    with open(os.path.join(destination, '.gitignore'), 'w') as f:
        f.write('# created by rustenv automatically\n*\n')


def _new_directory_type(path: str) -> str:
    path = os.path.abspath(path)
    if not os.path.isdir(os.path.dirname(path)):
        raise argparse.ArgumentTypeError(
            f'Parent directory of {path} does not exist.',
        )
    elif os.path.exists(path):
        raise argparse.ArgumentTypeError(
            f'Directory {path} already exists.',
        )
    else:
        return path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        'destination',
        type=_new_directory_type,
        help='directory in which to create rustenv',
    )
    args = parser.parse_args(argv)
    create_rustenv(args.destination)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
