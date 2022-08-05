from __future__ import annotations

import urllib.request
from unittest import mock

import pytest

import rustenv


FAKE_RUSTUP = b'''\
mkdir $CARGO_HOME
mkdir $CARGO_HOME/bin
touch $CARGO_HOME/bin/cargo
touch $CARGO_HOME/bin/rustc
'''


@pytest.fixture
def fake_rustup():
    with mock.patch.object(
            urllib.request, 'urlopen', mock.mock_open(read_data=FAKE_RUSTUP),
    ):
        yield


@pytest.mark.parametrize('destination', ('/nonexist/foo', '/tmp'))
def test_run_with_bad_destination(destination, capsys):
    with pytest.raises(SystemExit):
        rustenv.main((destination,))
    assert 'error: argument destination' in capsys.readouterr().err


def test_creates_files(tmpdir, fake_rustup):
    dest = tmpdir.join('rustenv')
    rustenv.main((dest.strpath,))

    assert dest.join('bin', 'activate').check(file=True)
    assert dest.join('bin', 'rustenv-proxy').check(file=True)
    assert dest.join('bin', 'cargo').readlink() == dest.join('bin', 'rustenv-proxy').strpath
    assert dest.join('bin', 'rustc').readlink() == dest.join('bin', 'rustenv-proxy').strpath
