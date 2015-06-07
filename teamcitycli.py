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

default_build_list_columns = 'status,id,number,buildTypeId,branchName'
default_project_list_columns = 'name,id,parentProjectId'
default_agent_list_columns = 'name,id'


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
@click.option('--parent-project-id', default=None,
              help='parent_project_id to filter on')
@click.option('--output-format', default='table',
              type=click.Choice(['table', 'json']),
              help='Output format')
@click.option('--columns', default=default_project_list_columns,
              help='comma-separated list of columns to show in table')
@click.pass_context
def project_list(ctx, parent_project_id, output_format, columns):
    """Display list of projects"""
    data = ctx.obj.get_projects(parent_project_id=parent_project_id)
    if output_format == 'table':
        column_names = columns.split(',')
        output_table(column_names, data['project'])
    elif output_format == 'json':
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
@click.option('--project', default=None, help='project to filter on')
@click.option('--build-type-id', default=None, help='buildTypeId to filter on')
@click.option('--branch', default=None, help='branch to filter on')
@click.option('--status', default=None, help='filter on build status',
              type=click.Choice(['success', 'failure', 'error']))
@click.option('--tags', default=None,
              help='comma-delimited list of build tags '
                   '(only builds containing all the specified tags '
                   'are returned)')
@click.option('--user', default=None,
              help='limit builds to only those triggered '
                   'by the user specified')
@click.option('--output-format', default='table',
              type=click.Choice(['table', 'json']),
              help='Output format')
@click.option('--columns', default=default_build_list_columns,
              help='comma-separated list of columns to show in table')
@click.pass_context
def build_list(ctx, show_url, show_data,
               start, count,
               project, build_type_id, branch, status, tags, user,
               output_format, columns):
    """Display list of builds"""
    kwargs = {'start': start,
              'count': count}
    if build_type_id:
        kwargs['build_type_id'] = build_type_id
    if branch:
        kwargs['branch'] = branch
    if status:
        kwargs['status'] = status
    if tags:
        kwargs['tags'] = tags
    if user:
        kwargs['user'] = user
    if project:
        kwargs['project'] = project

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
        output_table(column_names, data['build'])
    elif output_format == 'json':
        output_json_data(data)


@build.command(name='trigger')
@click.pass_context
@click.option('--build-type-id', default=None, help='buildTypeId to filter on')
def build_trigger(ctx, build_type_id):
    """Trigger a new build"""
    data = ctx.obj.trigger_build(build_type_id=build_type_id)
    output_json_data(data)


def output_table(column_names, data):
    table_data = [column_names]
    for item in data:
        row = [str(item.get(column_name, 'N/A'))
               for column_name in column_names]
        colorize_row(row)
        table_data.append(row)
    table = terminaltables.SingleTable(table_data)
    click.echo(table.table)


def colorize_row(row):
    for idx, value in enumerate(row):
        if value == 'SUCCESS':
            row[idx] = colorize(value, 'green')
        elif value in ('ERROR', 'FAILURE'):
            row[idx] = colorize(value, 'red')


def colorize(s, color, auto=True):
    tag = '%s%s' % ('auto' if auto else '', color)
    return Color('{%s}%s{/%s}' % (tag, s, tag))


@build.group(name='queue',
             short_help='Commands for build queue management')
def build_queue():
    pass


@build_queue.command(name='list')
@click.pass_context
def build_queue_list(ctx):
    """List queued build(s)"""
    data = ctx.obj.get_queued_builds()
    output_json_data(data)


@build.group(name='show',
             short_help='Commands for showing statistics/tags/etc. for builds')
def build_show():
    pass

@build_show.command(name='statistics')
@click.pass_context
@click.argument('args', nargs=-1)
def build_show_statistics(ctx, args):
    """Display statistics for selected build(s)"""
    for build_id in args:
        data = ctx.obj.get_build_statistics_by_build_id(build_id)
        output_json_data(data)


@build_show.command(name='log')
@click.pass_context
@click.argument('args', nargs=-1)
def build_show_log(ctx, args):
    """Display log for selected build(s)"""
    for build_id in args:
        data = ctx.obj.get_build_log_by_build_id(build_id)
        click.echo(data.text)


@build_show.command(name='artifacts')
@click.pass_context
@click.argument('build_id')
@click.argument('data_type', default='')
@click.argument('artifact_relative_name', default='')
def build_show_artifacts(ctx, build_id, data_type, artifact_relative_name):
    """Display artifacts for selected build(s)"""
    data = ctx.obj.get_build_artifacts_by_build_id(
        build_id,
        data_type=data_type,
        artifact_relative_name=artifact_relative_name)
    if hasattr(data, 'startswith'):
        click.echo(data)
    else:
        output_json_data(data)


@build_show.command(name='parameters')
@click.pass_context
@click.option('--output-format', default='table',
              type=click.Choice(['table', 'json']),
              help='Output format')
@click.argument('args', nargs=-1)
def build_show_parameters(ctx, output_format, args):
    """Display parameters for selected build(s)"""
    column_names = ['name', 'value']
    for build_id in args:
        response = ctx.obj.get_build_parameters_by_build_id(build_id)
        data = response['property']
        if output_format == 'table':
            output_table(column_names, data)
        elif output_format == 'json':
            output_json_data(data)


@build_show.command(name='tags')
@click.pass_context
@click.argument('args', nargs=-1)
def build_show_tags(ctx, args):
    """Display tags for selected build(s)"""
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
@click.option('--output-format', default='table',
              type=click.Choice(['table', 'json']),
              help='Output format')
@click.option('--columns', default=default_agent_list_columns,
              help='comma-separated list of columns to show in table')
@click.pass_context
def server_agent_list(ctx, output_format, columns):
    """Display list of agents"""
    data = ctx.obj.get_agents()
    if output_format == 'table':
        column_names = columns.split(',')
        output_table(column_names, data['agent'])
    elif output_format == 'json':
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
