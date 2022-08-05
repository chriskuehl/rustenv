from __future__ import annotations

import collections
import re
import subprocess

import pytest

import rustenv


TEST_SCRIPT = '''\
set -eu
RUSTENV='{RUSTENV}'

PATH=/bin:/usr/bin
PS1=$

report() {{
    echo "[[$1-PATH:$PATH]]"
    echo "[[$1-PS1:$PS1]]"
    echo "[[$1-rustc:$(rustc --version 2>&1)]]"
    echo "[[$1-cargo:$(cargo --version 2>&1)]]"
    echo "[[$1-hello:$(hello 2>&1)]]"
}}

report start

. "$RUSTENV/bin/activate"
report activated

cargo install hello-cli
report installed

cargo uninstall hello-cli
report uninstalled

deactivate_rustenv
report deactivated
'''


@pytest.fixture(scope='module')
def built_rustenv(tmpdir_factory):
    destination = tmpdir_factory.mktemp('built_rustenv').join('rustenv')
    rustenv.main((destination.strpath,))
    return destination


def test_rustenv_looks_sane(built_rustenv):
    assert built_rustenv.join('bin', 'activate').check(file=True)
    assert built_rustenv.join('bin', 'cargo').check(link=True)
    assert built_rustenv.join('bin', 'rustc').check(link=True)
    assert built_rustenv.join('rust').check(dir=True)


@pytest.mark.parametrize(
    ('shell', 'not_found_message'),
    (
        (
            'bash',
            '{}: command not found',
        ),
        (
            'zsh',
            'command not found: {}',
        ),
    ),
)
def test_runenv_shell(shell, not_found_message, built_rustenv, tmpdir):
    test_script = tmpdir.join('test.sh')
    test_script.write(
        TEST_SCRIPT.format(
            SHELL='bash',
            RUSTENV=built_rustenv.strpath,
        ),
    )
    output = subprocess.check_output((shell, test_script.strpath))

    stages: dict[str, dict[str, str]] = collections.defaultdict(dict)
    for stage, key, value in re.findall(
            r'\[\[([^-]+)-([^:]+):(.*?)\]\]', output.decode('utf8'),
    ):
        stages[stage][key] = value

    assert stages['start'] == stages['deactivated']

    assert stages['start']['PS1'] == '$'
    assert stages['start']['PATH'] == '/bin:/usr/bin'
    assert not_found_message.format('cargo') in stages['start']['cargo']
    assert not_found_message.format('rustc') in stages['start']['rustc']
    assert not_found_message.format('hello') in stages['start']['hello']

    assert stages['activated']['PS1'] == '(rustenv) $'
    assert stages['activated']['PATH'] == '{0}/bin:{0}/rust/bin:/bin:/usr/bin'.format(
        built_rustenv.strpath,
    )
    assert stages['activated']['cargo'].startswith('cargo ')
    assert stages['activated']['rustc'].startswith('rustc ')
    assert stages['activated']['hello'] == stages['start']['hello']

    assert stages['installed']['hello'] == 'Hello World!'
    assert stages['uninstalled'] == stages['activated']
