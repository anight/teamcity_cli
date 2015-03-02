#!/usr/bin/env python

import json

import click
from colorclass import Color
import pygments.formatters
import pygments.lexers
from pyteamcity import TeamCity, HTTPError
import terminaltables


lexer = pygments.lexers.get_lexer_by_name('json')
formatter = pygments.formatters.TerminalFormatter()

default_build_list_columns = 'status,number,buildTypeId,branchName'


def output_json_data(data):
    output = json.dumps(data, indent=4)
    output = pygments.highlight(output, lexer, formatter).strip()
    click.echo(output)


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
    output_json_data(data)


@project.command(name='list')
@click.pass_context
def project_list(ctx):
    """Display list of projects"""
    data = ctx.obj.get_all_projects()
    output_json_data(data)


@project.command(name='show')
@click.pass_context
@click.argument('args', nargs=-1)
def project_show(ctx, args):
    """Display info for selected projects"""
    for project_id in args:
        data = ctx.obj.get_project_by_project_id(project_id)
        output_json_data(data)


@build.command(name='list')
@click.option('--show-url/--no-show-url', default=False,
              help='Show URL for request')
@click.option('--show-data/--no-show-data', default=True,
              help='Show data retrieved from request')
@click.option('--start', default=0, help='Start index')
@click.option('--count', default=100, help='Max number of items to show')
@click.option('--build-type-id', default=None, help='buildTypeId to filter on')
@click.option('--branch', default=None, help='branch to filter on')
@click.option('--output-format', default='table',
              type=click.Choice(['table', 'json']),
              help='Output format')
@click.option('--columns', default=default_build_list_columns,
              help='comma-separated list of columns to show in table')
@click.pass_context
def build_list(ctx, show_url, show_data,
               start, count,
               build_type_id, branch,
               output_format, columns):
    """Display list of builds"""
    kwargs = {'start': start,
              'count': count}
    if build_type_id:
        kwargs['build_type_id'] = build_type_id
    if branch:
        kwargs['branch'] = branch

    func = ctx.obj.get_builds

    if show_url:
        kwargs['return_type'] = 'url'
        url = func(**kwargs)
        del kwargs['return_type']
        click.echo(url)

    if not show_data:
        return

    try:
        data = func(**kwargs)
    except HTTPError as e:
        click.echo('url: %s' % e.url)
        click.echo('status_code: %s' % e.status_code)
        click.echo()
        click.echo(e)
        return

    click.echo('count: %d' % data['count'])
    if data['count'] == 0:
        return

    if output_format == 'table':
        column_names = columns.split(',')
        output_table(column_names, data)
    elif output_format == 'json':
        output_json_data(data)


def output_table(column_names, data):
    table_data = [column_names]
    for build in data['build']:
        row = [build.get(column_name, 'N/A')
               for column_name in column_names]
        colorize_row(row)
        table_data.append(row)
    table = terminaltables.SingleTable(table_data)
    click.echo(table.table)


def colorize_row(row):
    for idx, value in enumerate(row):
        if value == 'SUCCESS':
            row[idx] = colorize(value, 'green')
        elif value == 'FAILURE':
            row[idx] = colorize(value, 'red')


def colorize(s, color, auto=True):
    tag = '%s%s' % ('auto' if auto else '', color)
    return Color('{%s}%s{/%s}' % (tag, s, tag))


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
        output_json_data(data)


@build_show.command(name='tags')
@click.pass_context
@click.argument('args', nargs=-1)
def build_show_tags(ctx, args):
    """Display info for selected build(s)"""
    for build_id in args:
        data = ctx.obj.get_build_tags_by_build_id(build_id)
        output_json_data(data)


@user.command(name='list')
@click.pass_context
def user_list(ctx):
    """Display list of users"""
    data = ctx.obj.get_all_users()
    output_json_data(data)


@user.command(name='show')
@click.pass_context
@click.argument('args', nargs=-1)
def user_show(ctx, args):
    """Display info for selected users"""
    for user_id in args:
        data = ctx.obj.get_user_by_username(user_id)
        output_json_data(data)


@server.group(name='plugin')
def server_plugin():
    """Show info about server plugins"""


@server_plugin.command(name='list')
@click.pass_context
def server_plugin_list(ctx):
    """Display list of plugins"""
    data = ctx.obj.get_all_plugins()
    output_json_data(data)


@server.group(name='agent')
def server_agent():
    """Show info about agents"""


@server_agent.command(name='list')
@click.pass_context
def server_agent_list(ctx):
    """Display list of agents"""
    data = ctx.obj.get_agents()
    output_json_data(data)


@server_agent.command(name='show')
@click.pass_context
@click.argument('args', nargs=-1)
def server_agent_show(ctx, args):
    """Display info for selected agent(s)"""
    for agent_id in args:
        data = ctx.obj.get_agent_by_agent_id(agent_id)
        output_json_data(data)


@change.command(name='list')
@click.pass_context
def change_list(ctx):
    """Display list of changes"""
    data = ctx.obj.get_all_changes()
    output_json_data(data)


@change.command(name='show')
@click.pass_context
@click.argument('args', nargs=-1)
def change_show(ctx, args):
    """Display info for selected changes"""
    for change_id in args:
        data = ctx.obj.get_change_by_change_id(change_id)
        output_json_data(data)


if __name__ == '__main__':
    cli()
