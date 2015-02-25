#!/usr/bin/env python

import json

import click
from pyteamcity import TeamCity


@click.group()
def cli():
    """CLI for interacting with TeamCity"""


@cli.group()
def build():
    """Commands related to builds"""


@cli.group()
def project():
    """Commands related to projects"""


@cli.group()
def server():
    """Commands related to the server instance"""


@server.command(name='info')
def server_info():
    """Display info about TeamCity server"""
    tc = TeamCity()
    data = tc.get_server_info()
    output = json.dumps(data, indent=4)
    click.echo(output)


@project.command(name='list')
def project_list():
    """Display list of projects"""
    tc = TeamCity()
    data = tc.get_all_projects()
    output = json.dumps(data, indent=4)
    click.echo(output)


@build.command(name='list')
def build_list():
    """Display list of builds"""
    tc = TeamCity()
    data = tc.get_all_builds(start=0, count=100)
    output = json.dumps(data, indent=4)
    click.echo(output)


if __name__ == '__main__':
    cli()
