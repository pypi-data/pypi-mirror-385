# Changelog

All notable changes to this project will be documented in this file.

The format is based on [*Keep a
Changelog*](https://keepachangelog.com/en/1.0.0/) and this project
adheres to [*Calendar Versioning*](https://calver.org/).

The **first number** of the version is the year.

The **second number** is incremented with each release, starting at 1
for each year.

The **third number** is when we need to start branches for older
releases (only for emergencies).

Committed changes for the next release can be found in the ["changelog.d"
directory](https://github.com/kpfleming/jinjanator-plugin-format-toml/tree/main/changelog.d)
in the project repository.

<!--
Do *NOT* add changelog entries here!

This changelog is managed by towncrier and is compiled at release time.

See https://github.com/kpfleming/jinjanator-plugin-format-toml/blob/main/.github/CONTRIBUTING.md#changelog for details.
-->

<!-- towncrier release notes start -->

## [25.1.0](https://github.com/kpfleming/jinjanator-plugin-format-toml/tree/25.1.0) - 2025-10-18

### Backwards-incompatible Changes

- Support for Python 3.9 has been removed, and support for Python 3.14
  has been added. Since the minimum supported version is now 3.10, the
  code has been updated to use features introduced in that version.
  
- Upgraded to version 25.1.0 of jinjanator-plugins.
  


### Additions

- Added testing against Python 3.13 (again).
  

## [24.2.0](https://github.com/kpfleming/jinjanator-plugin-format-toml/tree/24.2.0) - 2024-10-13

### Backwards-incompatible Changes

- Added support for Python 3.13, and removed support for Python 3.8.
  
- Upgraded to version 24.2.0 of jinjanator-plugins.
  

## [24.1.0](https://github.com/kpfleming/jinjanator-plugin-format-toml/tree/24.1.0) - 2024-04-27

### Changes

- Upgraded to version 24.1 of jinjanator-plugins.
  

## [23.2.0](https://github.com/kpfleming/jinjanator-plugin-format-toml/tree/23.2.0) - 2023-10-07

### Additions

- Added Python 3.12 support.
  [#2](https://github.com/kpfleming/jinjanator-plugin-format-toml/issues/2)


## [23.1.0](https://github.com/kpfleming/jinjanator-plugin-format-toml/tree/23.1.0) - 2023-08-03

Initial release!
