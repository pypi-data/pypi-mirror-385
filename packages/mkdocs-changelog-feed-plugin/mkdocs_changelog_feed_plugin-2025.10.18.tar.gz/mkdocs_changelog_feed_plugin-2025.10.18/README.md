# MkDocs changelog feed plugin

[MkDocs](https://www.mkdocs.org/) plugin that adds RSS and Atom feeds for a changelog.

This plugin takes the rendered HTML output of the page specified by the [`changelog_file` setting](#changelog_file), splits  it into sections for each changelog entry, and generates RSS and Atom feeds with items for each of those entries. Then, links to the feeds are added to the page.

The page is expected to be in the [Keep a Changelog](https://keepachangelog.com/) format, e.g. every entry starts with a second level heading, the version title and the date have to be separated by -[^dash], the date has to be in ISO 8601 format, etc.

## Installation

```shell
pip install mkdocs-changelog-feed-plugin
```

## Usage

In `mkdocs.yaml`, set `site_url` and add the plugin to `plugins`:  

```yaml
site_name: My Docs
site_url: https://mydocs.example.com/
plugins:
- search
- changelog_feed
```

## Plugin configuration

### `changelog_file`

The file within your `docs` directory containing the changelog.

**default**: `CHANGELOG.md`

### `feed_title`

The feed's title.

Defaults to "*page name* - *site name*", if not set.

**default**: `null`

### `feed_description`

The feed's description (RSS)/subtitle (Atom).

**default**: `null`

### `links_icon`

Icon to be displayed next to the links to the feeds at the top of the page.

**default**: `<i class="fa fa-square-rss"></i>`

## Licence

This project is licenced under the AGPL-3.0 license.

[^dash]: Or &ndash; or &mdash;, in case something like the SmartyPants extension replaces the `-` character.
