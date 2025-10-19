# SeedboxSync frontend

[![Author][ico-bluesky]][link-bluesky]
[![Software License][ico-license]](LICENSE)
[![Build Status][ico-ghactions]][link-ghactions]

[![Latest Version][ico-pypi-version]][link-pypi]
[![Docker Pull][ico-docker]][link-docker]
[![Latest Version][ico-version]][link-docker]

[![Quality Gate Status][ico-sonarcloud-gate]][link-sonarcloud-gate]
[![Coverage][ico-sonarcloud-coverage]][link-sonarcloud-coverage]
[![Maintainability Rating][ico-sonarcloud-maintainability]][link-sonarcloud-maintainability]
[![Reliability Rating][ico-sonarcloud-reliability]][link-sonarcloud-reliability]
[![Security Rating][ico-sonarcloud-security]][link-sonarcloud-security]

<p align="center">
  <a href="https://llaumgui.github.io/seedboxsync/" title="Documentation"><img alt="SeedboxSync logo" src="screenshots/logo.png" /></a>
</p>

SeedboxSyncFront is the frontend of **[SeedboxSync](https://llaumgui.github.io/seedboxsync/)**, which provides powerful synchronization features between your NAS and your seedbox, making torrent management seamless and automated.

Key features of frontend:

* **🌐 Dashboard interface**: Monitor your downloads and syncs in real-time through a user-friendly web interface.
* **📊 Visual statistics**: Access detailed reports of your downloads, including monthly and yearly statistics.
* **🛠️ Manage downloads**: Remove downloads directly from the dashboard to allow re-downloading.
* **🔄 Two-way sync overview**: Quickly see the status of NAS-to-Seedbox and Seedbox-to-NAS synchronization.
* **⚡ Auto-refresh**: Automatically refresh data to keep your dashboard up-to-date without manual reloads.
* **🗄️ API access**: Interact programmatically with your downloads and syncs using a REST API.

<div align="center">
    <table>
    <tr>
        <td align="center">
            <a href="screenshots/homepage.png">
                <img alt="Main page" src="screenshots/homepage.png" width="300"/>
            </a>
            <br><em>Main page</em>
        </td>
        <td align="center">
            <a href="screenshots/downloaded.png">
                <img alt="Downloaded files" src="screenshots/downloaded.png" width="300"/>
            </a>
            <br><em>Downloaded files</em>
        </td>
    </tr>
    <tr>
        <td align="center">
            <a href="screenshots/uploaded.png">
                <img alt="Uploaded torrents" src="screenshots/uploaded.png" width="300"/>
            </a>
            <br><em>Uploaded torrents</em>
        </td>
            <td align="center">
            <a href="screenshots/info.png">
              <img alt="Informations" src="screenshots/info.png" width="300"/>
            </a>
            <br><em>info</em>
        </td>
    </tr>
    <tr>
        <td align="center">
            <a href="screenshots/stats.png">
                <img alt="Statistics" src="screenshots/stats.png" width="300"/>
            </a>
            <br><em>Statistics</em>
        </td>
        <td align="center">
            <a href="screenshots/api-spec.png">
                <img alt="API SPEC" src="screenshots/api-spec.png" width="300"/>
            </a>
            <br><em>API   </em>
        </td>
    </tr>
    </table>
</div>

## Full documentation

Full documentation, see: [https://llaumgui.github.io/seedboxsync/frontend/](https://llaumgui.github.io/seedboxsync/frontend/)

## Powered by

<p style="text-align:center;">
  <a href="https://www.python.org"><img alt="Python logo" src="screenshots/python-powered-w-140x56.png" /></a> <a href="https://flask.palletsprojects.com/"><img alt="Flask logo" src="screenshots/logo-flask.png" /></a> <a href="https://docs.peewee-orm.com"><img alt="peewee logo" src="screenshots/logo-peewee.png" /></a>
</p>

## License

Released under the [GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html).

[ico-bluesky]: https://img.shields.io/static/v1?label=Author&message=llaumgui&color=208bfe&logo=bluesky&style=flat-square
[link-bluesky]: https://bsky.app/profile/llaumgui.kulakowski.fr
[ico-ghactions]: https://img.shields.io/github/actions/workflow/status/llaumgui/seedboxsync-front/devops.yml?branch=main&style=flat-square&logo=github&label=DevOps
[link-ghactions]: https://github.com/llaumgui/seedboxsync-front/actions
[ico-pypi-version]: https://img.shields.io/pypi/v/seedboxsync-front?include_prereleases&label=Package%20version&style=flat-square&logo=python
[link-pypi]:https://pypi.org/project/seedboxsync-front/
[ico-license]: https://img.shields.io/github/license/llaumgui/seedboxsync-front?style=flat-square
[ico-docker]: https://img.shields.io/docker/pulls/llaumgui/seedboxsync-front?color=%2496ed&logo=docker&style=flat-square
[link-docker]: https://hub.docker.com/r/llaumgui/seedboxsync-front
[ico-version]: https://img.shields.io/docker/v/llaumgui/seedboxsync-front?sort=semver&color=%2496ed&logo=docker&style=flat-square
[ico-sonarcloud-gate]: https://sonarcloud.io/api/project_badges/measure?branch=main&project=llaumgui_seedboxsync-front&metric=alert_status
[link-sonarcloud-gate]: https://sonarcloud.io/dashboard?id=llaumgui_seedboxsync-front&branch=main
[ico-sonarcloud-coverage]: https://sonarcloud.io/api/project_badges/measure?project=llaumgui_seedboxsync-front&metric=coverage
[link-sonarcloud-coverage]: https://sonarcloud.io/dashboard?id=llaumgui_seedboxsync-front
[ico-sonarcloud-maintainability]: https://sonarcloud.io/api/project_badges/measure?project=llaumgui_seedboxsync-front&metric=sqale_rating
[link-sonarcloud-maintainability]: https://sonarcloud.io/dashboard?id=llaumgui_seedboxsync-front
[ico-sonarcloud-reliability]: https://sonarcloud.io/api/project_badges/measure?project=llaumgui_seedboxsync-front&metric=reliability_rating
[link-sonarcloud-reliability]: https://sonarcloud.io/dashboard?id=llaumgui_seedboxsync-front
[ico-sonarcloud-security]: https://sonarcloud.io/api/project_badges/measure?project=llaumgui_seedboxsync-front&metric=security_rating
[link-sonarcloud-security]: https://sonarcloud.io/dashboard?id=llaumgui_seedboxsync-front
