#!/usr/bin/env python

import json

import click
from pyteamcity import TeamCity


@click.group()
@click.pass_context
def cli(ctx):
    """CLI for interacting with TeamCity"""
    ctx.obj = TeamCity()


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
@click.pass_context
def server_info(ctx):
    """Display info about TeamCity server"""
    data = ctx.obj.get_server_info()
    output = json.dumps(data, indent=4)
    click.echo(output)


@project.command(name='list')
@click.pass_context
def project_list(ctx):
    """Display list of projects"""
    data = ctx.obj.get_all_projects()
    output = json.dumps(data, indent=4)
    click.echo(output)


@project.command(name='show')
@click.pass_context
@click.argument('args', nargs=-1)
def project_show(ctx, args):
    """Display info for selected projects"""
    for project_id in args:
        data = ctx.obj.get_project_by_project_id(project_id)
        output = json.dumps(data, indent=4)
        click.echo(output)


@build.command(name='list')
@click.pass_context
def build_list(ctx):
    """Display list of builds"""
    data = ctx.obj.get_all_builds(start=0, count=100)
    output = json.dumps(data, indent=4)
    click.echo(output)


@build.group(name='show')
def build_show():
    """Show statistics/tags/etc. for builds"""


@build_show.command(name='statistics')
@click.pass_context
@click.argument('args', nargs=-1)
def build_show_statistics(ctx, args):
    """Display info for selected build(s)"""
    for build_id in args:
        data = ctx.obj.get_build_statistics_by_build_id(build_id)
        output = json.dumps(data, indent=4)
        click.echo(output)


@build_show.command(name='tags')
@click.pass_context
@click.argument('args', nargs=-1)
def build_show_tags(ctx, args):
    """Display info for selected build(s)"""
    for build_id in args:
        data = ctx.obj.get_build_tags_by_build_id(build_id)
        output = json.dumps(data, indent=4)
        click.echo(output)


if __name__ == '__main__':
    cli()
