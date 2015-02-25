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
def change():
    """Commands related to changes"""


@cli.group()
def server():
    """Commands related to the server instance"""


@cli.group()
def user():
    """Commands related to users"""


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


@user.command(name='list')
@click.pass_context
def user_list(ctx):
    """Display list of users"""
    data = ctx.obj.get_all_users()
    output = json.dumps(data, indent=4)
    click.echo(output)


@user.command(name='show')
@click.pass_context
@click.argument('args', nargs=-1)
def user_show(ctx, args):
    """Display info for selected users"""
    for user_id in args:
        data = ctx.obj.get_user_by_username(user_id)
        output = json.dumps(data, indent=4)
        click.echo(output)


@server.group(name='plugin')
def server_plugin():
    """Show info about server plugins"""


@server_plugin.command(name='list')
@click.pass_context
def server_plugin_list(ctx):
    """Display list of plugins"""
    data = ctx.obj.get_all_plugins()
    output = json.dumps(data, indent=4)
    click.echo(output)


@server.group(name='agent')
def server_agent():
    """Show info about agents"""


@server_agent.command(name='list')
@click.pass_context
def server_agent_list(ctx):
    """Display list of agents"""
    data = ctx.obj.get_agents()
    output = json.dumps(data, indent=4)
    click.echo(output)


@server_agent.command(name='show')
@click.pass_context
@click.argument('args', nargs=-1)
def server_agent_show(ctx, args):
    """Display info for selected agent(s)"""
    for agent_id in args:
        data = ctx.obj.get_agent_by_agent_id(agent_id)
        output = json.dumps(data, indent=4)
        click.echo(output)


@change.command(name='list')
@click.pass_context
def change_list(ctx):
    """Display list of changes"""
    data = ctx.obj.get_all_changes()
    output = json.dumps(data, indent=4)
    click.echo(output)


@change.command(name='show')
@click.pass_context
@click.argument('args', nargs=-1)
def change_show(ctx, args):
    """Display info for selected changes"""
    for change_id in args:
        data = ctx.obj.get_change_by_change_id(change_id)
        output = json.dumps(data, indent=4)
        click.echo(output)


if __name__ == '__main__':
    cli()
