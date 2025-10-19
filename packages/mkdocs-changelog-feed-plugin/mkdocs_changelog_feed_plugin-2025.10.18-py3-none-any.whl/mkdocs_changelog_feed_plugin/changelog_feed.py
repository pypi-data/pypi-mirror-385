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
import re
from datetime import date, datetime, time, timezone
from itertools import takewhile
from pathlib import Path

from bs4 import BeautifulSoup
from feedgenerator import Atom1Feed, Rss201rev2Feed
from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page


class ChangelogFeedPluginConfig(Config):
    """Plugin config schema.

    See <https://www.mkdocs.org/dev-guide/plugins/#config_scheme>.
    """

    changelog_file = config_options.Type(str, default='CHANGELOG.md')
    feed_title = config_options.Optional(config_options.Type(str))
    feed_description = config_options.Optional(config_options.Type(str))
    links_icon = config_options.Type(str, default='<i class="fa fa-square-rss"></i>')


class ChangelogFeedPlugin(BasePlugin[ChangelogFeedPluginConfig]):
    """MkDocs plugin that adds RSS and Atom feeds for a changelog in the Keep a
    Changelog format.
    """

    def on_config(self, config: MkDocsConfig):
        """Make sure that the `site_url` setting, which is required to build absolute
        URLs, is present.

        > The config event is the first event called on build and is run immediately
        > after the user configuration is loaded and validated. Any alterations to the
        > config should be made here.

        See <https://www.mkdocs.org/dev-guide/plugins/#on_config>.
        """
        if not config.site_url:
            raise PluginError(
                'The site_url setting is required by the changelog feed plugin.'
            )

    def on_page_content(
        self, html: str, page: Page, config: MkDocsConfig, files: Files
    ):
        """If `page` is the changelog as specified by the `changelog_file`, this method
        splits the HTML it into sections for each changelog entry and generates RSS and
        Atom feeds with items for each of those entries. Then, links to the feeds are
        added at the top of the page.

        > The `page_content` event is called after the Markdown text is rendered to
        > HTML (but before being passed to a template) and can be used to alter the HTML
        > body of the page.

        See <https://www.mkdocs.org/dev-guide/plugins/#on_page_content>.
        """
        if page.file.src_uri != self.config.changelog_file:
            return

        feed_title = self.config.feed_title or f'{page.title} - {config.site_name}'
        feeds = {
            'Atom': Atom1Feed(
                feed_title,
                page.canonical_url,
                self.config.feed_description,
                author_name=config.site_author,
                feed_copyright=config.copyright,
            ),
            'RSS': Rss201rev2Feed(
                feed_title,
                page.canonical_url,
                self.config.feed_description,
                author_name=config.site_author,
                feed_copyright=config.copyright,
            ),
        }

        soup = BeautifulSoup(html, features='html.parser')

        for h2 in soup.find_all('h2'):
            try:
                fragment = h2['id']
            except KeyError:
                fragment = None

            try:
                heading_version, heading_date = (
                    s.strip() for s in re.split(r'\s[-‒––]\s', h2.text, maxsplit=2)
                )
            except ValueError:
                heading_version, heading_date = h2.text, None

            if heading_date:
                try:
                    day = date.fromisoformat(heading_date[:10])
                except ValueError as e:
                    raise PluginError(
                        f'Unable to parse date "{heading_date}" in section heading.'
                    ) from e
                pubdate = datetime.combine(day, time(12, 00), tzinfo=timezone.utc)
            else:
                pubdate = datetime.fromtimestamp(
                    Path(page.file.abs_src_path).stat().st_mtime, tz=timezone.utc
                )

            section_content = ''.join(
                str(s) for s in takewhile(lambda s: s.name != 'h2', h2.next_siblings)
            ).strip()

            for feed in feeds.values():
                link = (
                    f'{page.canonical_url}#{fragment}'
                    if fragment
                    else page.canonical_url
                )

                # Workaround for feedgenerator's “backwards-compatibility not in Django”
                if isinstance(feed, Atom1Feed):
                    description = None
                    content = section_content
                else:
                    description = section_content
                    content = None

                feed.add_item(
                    heading_version,
                    link,
                    description,
                    content=content,
                    pubdate=pubdate,
                    unique_id=link,
                    unique_id_is_permalink=True,
                )

        link_tags = []
        a_tags = []

        for feed_type, feed in feeds.items():
            feed_file = File.generated(
                config,
                Path(page.file.src_uri).with_suffix(f'.{feed_type.lower()}.xml'),
                content=feed.writeString('utf-8'),
            )
            files.append(feed_file)

            feed_url = feed_file.url_relative_to(page.file)

            link_tags.append(
                soup.new_tag(
                    'link',
                    attrs={
                        'rel': 'alternate',
                        'type': feed.content_type,
                        'href': feed_url,
                        'title': f'{page.title} {feed_type} feed',
                    },
                )
            )
            a_tags.append(
                soup.new_tag('a', attrs={'href': feed_url}, string=f'{feed_type} feed')
            )

        page.meta['changelog_feed'] = {'link_tags': link_tags}

        div = soup.new_tag('div', attrs={'style': 'float: inline-end'})
        div.append(BeautifulSoup(self.config.links_icon, 'html.parser'))
        for a_tag in a_tags:
            div.append(' ')
            div.append(a_tag)

        html = '\n'.join([str(div), html])

        return html

    def on_post_page(self, output: str, page: Page, config: MkDocsConfig):
        """Add `<link rel="alternate" …>` tags to the head of the HTML document for
        each generated feed, if stored in the [`Page`][mkdocs.structure.pages.Page]'s
        metadata by
        [`on_page_content`][mkdocs_changelog_feed_plugin.changelog_feed.ChangelogFeedPlugin.on_page_content].

        > The `post_page` event is called after the template is rendered, but before it
        > is written to disc and can be used to alter the output of the page.

        See <https://www.mkdocs.org/dev-guide/plugins/#on_post_page>.
        """
        try:
            link_tags = page.meta['changelog_feed']['link_tags']
        except KeyError:
            return

        # Split at the beginning of the line with with the closing head tag.
        parts = re.split(r'^(\s*</head>)', output, maxsplit=1, flags=re.M)

        output = ''.join(
            [parts[0], *[f'        {tag}\n' for tag in link_tags], *parts[1:]]
        )

        return output
