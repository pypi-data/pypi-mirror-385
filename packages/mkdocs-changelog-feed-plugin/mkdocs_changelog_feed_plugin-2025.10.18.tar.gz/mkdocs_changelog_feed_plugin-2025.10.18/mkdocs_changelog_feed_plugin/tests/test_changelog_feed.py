# mkdocs-changelog-feed-plugin
# Copyright (C) 2025 Tobias Bölz
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
from pathlib import Path
from xml.etree.ElementTree import ElementTree

import pytest
from bs4 import BeautifulSoup
from click.testing import CliRunner
from mkdocs.__main__ import cli
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError

from mkdocs_changelog_feed_plugin.changelog_feed import ChangelogFeedPlugin


@pytest.fixture(scope='module')
def site_dir(tmp_path_factory) -> Path:
    site_dir = tmp_path_factory.mktemp('site')
    config_file = Path(__file__).parent / 'mkdocs.yaml'
    runner = CliRunner()
    result = runner.invoke(
        cli, ['build', '--site-dir', str(site_dir), '--config-file', str(config_file)]
    )
    assert result.exit_code == 0
    return site_dir


def test_atom_feed(site_dir: Path):
    atom_feed = ElementTree(file=site_dir / 'CHANGELOG.atom.xml')
    assert (
        atom_feed.find(
            './atom:entry/atom:title', {'atom': 'http://www.w3.org/2005/Atom'}
        ).text
        == 'Unreleased'
    )
    assert (
        atom_feed.find(
            './atom:entry[2]/atom:title', {'atom': 'http://www.w3.org/2005/Atom'}
        ).text
        == '1.0.1'
    )
    assert (
        atom_feed.find(
            './atom:entry[2]/atom:published', {'atom': 'http://www.w3.org/2005/Atom'}
        ).text
        == '2023-03-05T12:00:00+00:00'
    )


def test_rss_feed(site_dir: Path):
    rss_feed = ElementTree(file=site_dir / 'CHANGELOG.rss.xml')
    assert rss_feed.find('./channel/item/title').text == 'Unreleased'
    assert rss_feed.find('./channel/item[2]/title').text == '1.0.1'
    assert (
        rss_feed.find('./channel/item[2]/pubDate').text
        == 'Sun, 05 Mar 2023 12:00:00 +0000'
    )


def test_links(site_dir: Path):
    changelog_output = site_dir / 'CHANGELOG' / 'index.html'
    soup = BeautifulSoup(changelog_output.read_text(), 'html.parser')
    assert soup.find('link', rel='alternate', href='../CHANGELOG.atom.xml')
    assert soup.find('link', rel='alternate', href='../CHANGELOG.rss.xml')
    assert soup.find('a', string='Atom feed', href='../CHANGELOG.atom.xml')
    assert soup.find('a', string='RSS feed', href='../CHANGELOG.rss.xml')


def test_no_site_url():
    config = MkDocsConfig(str(Path(__file__).parent / 'mkdocs.yaml'))
    config.site_url = None
    plugin = ChangelogFeedPlugin()

    with pytest.raises(PluginError):
        plugin.on_config(config)
