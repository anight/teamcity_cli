#!/usr/bin/env python

import json
import sys
import time
import webbrowser

import click
from colorclass import Color
import pygments.formatters
import pygments.lexers
from pyteamcity import TeamCity, HTTPError
import terminaltables


lexer = pygments.lexers.get_lexer_by_name('json')
formatter = pygments.formatters.TerminalFormatter()

default_build_list_columns = 'status,statusText,id,buildTypeId,number,branchName,user'
default_build_configs_list_columns = 'id,projectName,name'
default_queued_build_list_columns = 'state,id,buildTypeId,branchName,user'
default_project_list_columns = 'name,id,parentProjectId'
default_agent_list_columns = 'name,id,ip,pool,build_type,build_text'


def output_json_data(data):
    output = json.dumps(data, indent=4)
    output = pygments.highlight(output, lexer, formatter).strip()
    click.echo(output)


def error_handler(e):
    sys.stderr.write('ERROR: %s\n' % e)
    raise click.Abort()


@click.group()
@click.pass_context
def cli(ctx):
    """CLI for interacting with TeamCity"""
    ctx.obj = TeamCity()
    ctx.obj.error_handler = error_handler


@cli.group()
def build():
    """Commands related to builds"""


@cli.group()
def build_configs():
    """Commands related to build configs"""


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
@click.option('--branch', default='default:any', help='branch to filter on')
@click.option('--status', default=None, help='filter on build status',
              type=click.Choice(['success', 'failure', 'error']))
@click.option('--running', default='any', help='filter on build state',
              type=click.Choice(['true', 'false', 'any']))
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
               project, build_type_id, branch, status, running, tags, user,
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
    if running:
        kwargs['running'] = running
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

    for build in data['build']:
        details = ctx.obj.get_build_by_build_id(build['id'])
        try:
            build['user'] = details['triggered']['user']['username']
            build['statusText'] = details['statusText']
            build['details'] = details
        except KeyError:
            build['user'] = 'N/A'

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
@click.option('--branch', default=None, help='branch to filter on')
@click.option('--comment', help='comment message for build')
@click.option('--parameter', multiple=True, help='Specify custom parameters')
@click.option('--agent-id', default=None,
              help='ID of agent to force build to run on')
@click.option('--wait-for-run/--no-wait-for-run', default=False,
              help='Wait for the build to start running')
def build_trigger(ctx, build_type_id, branch, comment, parameter, agent_id,
                  wait_for_run):
    """Trigger a new build"""
    parameters = dict([p.split('=', 1) for p in parameter])
    data = ctx.obj.trigger_build(
        build_type_id=build_type_id,
        branch=branch,
        comment=comment,
        parameters=parameters,
        agent_id=agent_id)
    build_id = data['id']
    ctx.invoke(build_queue_show, args=[build_id])
    url = data['webUrl'] + '&tab=buildLog'
    webbrowser.open(url)
    while wait_for_run and data['state'] == 'queued':
        data = ctx.obj.get_queued_build_by_build_id(build_id)
        click.echo('state: %s' % data['state'])
        time.sleep(5)
    ctx.invoke(build_queue_show, args=[build_id])


def output_table(column_names, data):
    table_data = [column_names]
    for item in data:
        if item.get('state') == 'running':
            item['status'] = 'RUNNING'
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
        elif value in ('RUNNING'):
            row[idx] = colorize(value, 'yellow')


def colorize(s, color, auto=True):
    tag = '%s%s' % ('auto' if auto else '', color)
    return Color('{%s}%s{/%s}' % (tag, s, tag))


@build.command(name='browse')
@click.pass_context
@click.argument('args', nargs=-1)
def build_browse(ctx, args):
    """Open selected build(s) in web browser"""
    for build_id in args:
        data = ctx.obj.get_build_by_build_id(build_id)
        webbrowser.open(data['webUrl'])


@build.group(name='queue',
             short_help='Commands for build queue management')
def build_queue():
    pass


@build_configs.command(name='list')
@click.pass_context
@click.option('--show-url/--no-show-url', default=False,
              help='Show URL for request')
@click.option('--project', default=None, help='project to filter on')
@click.option('--affected-project', default=None, help='project to filter on (recursive)')
@click.option('--template-flag', default='any', help='boolean value to get only templates or only non-templates')
@click.option('--output-format', default='table',
              type=click.Choice(['table', 'json']),
              help='Output format')
@click.option('--columns', default=default_build_configs_list_columns,
              help='comma-separated list of columns to show in table')
def build_configs_list(ctx, show_url, project, affected_project, template_flag, output_format, columns):
    """List build configs"""
    kwargs = {}

    if show_url:
        kwargs['return_type'] = 'url'
        url = ctx.obj.get_build_types(**kwargs)
        del kwargs['return_type']
        click.echo(url)

    if project:
        kwargs['project'] = project
    if affected_project:
        kwargs['affected_project'] = affected_project
    if template_flag:
        kwargs['template_flag'] = template_flag

    data = ctx.obj.get_build_types(**kwargs)

    click.echo('count: %d' % data['count'])
    if data['count'] == 0:
        return

    if output_format == 'table':
        column_names = columns.split(',')
        output_table(column_names, data['buildType'])
    elif output_format == 'json':
        output_json_data(data)


@build_queue.command(name='list')
@click.pass_context
@click.option('--build-type-id', default=None, help='buildTypeId to filter on')
@click.option('--branch', default=None, help='branch to filter on')
@click.option('--output-format', default='table',
              type=click.Choice(['table', 'json']),
              help='Output format')
@click.option('--columns', default=default_queued_build_list_columns,
              help='comma-separated list of columns to show in table')
def build_queue_list(ctx, build_type_id, branch, output_format, columns):
    """List queued build(s)"""
    data = ctx.obj.get_queued_builds()
    click.echo('count: %d' % data['count'])
    if data['count'] == 0:
        return

    if output_format == 'table':
        column_names = columns.split(',')
        output_table(column_names, data['build'])
    elif output_format == 'json':
        output_json_data(data)


@build_queue.command(name='show',
                     short_help='Show info about a queued build')
@click.pass_context
@click.option('--show-all/--no-show-all', default=False,
              help='Show all data for build (very verbose)')
@click.argument('args', nargs=-1)
def build_queue_show(ctx, show_all, args):
    for build_id in args:
        all_data = ctx.obj.get_queued_build_by_build_id(build_id)
        if show_all:
            output_json_data(all_data)
        else:
            data = {
                'id': all_data['id'],
                'number': all_data.get('number'),
                'startEstimate': all_data.get('startEstimate'),
                'startDate': all_data.get('startDate'),
                'queuedDate': all_data['queuedDate'],
                'finishDate': all_data.get('finishDate'),
                'branchName': all_data['branchName'],
                'projectId': all_data['buildType']['projectId'],
                'projectName': all_data['buildType']['projectName'],
                'webUrl': all_data['webUrl'],
                'state': all_data['state'],
                'waitReason': all_data.get('waitReason'),
            }
            if all_data['triggered'].get('type') == 'user':
                data['username'] = all_data['triggered']['user']['username']
            output_json_data(data)


@build.group(name='show',
             short_help='Commands for showing statistics/tags/etc. for builds')
def build_show():
    pass


@build_show.command(name='details')
@click.option('--show-all/--no-show-all', default=False,
              help='Show all data for build (very verbose)')
@click.pass_context
@click.argument('args', nargs=-1)
def build_show_details(ctx, show_all, args):
    """Display details for selected build(s)"""
    for build_id in args:
        all_data = ctx.obj.get_build_by_build_id(build_id)
        if show_all:
            output_json_data(all_data)
        else:
            data = {
                'number': all_data['number'],
                'id': all_data['id'],
                'startDate': all_data['startDate'],
                'queuedDate': all_data['queuedDate'],
                'finishDate': all_data.get('finishDate'),
                'branchName': all_data['branchName'],
                'agent': all_data['agent']['name'],
                'projectId': all_data['buildType']['projectId'],
                'projectName': all_data['buildType']['projectName'],
                'webUrl': all_data['webUrl'],
                'status': all_data['status'],
                'state': all_data['state'],
                'statusText': all_data['statusText'],
            }
            if all_data['triggered'].get('type') == 'user':
                data['username'] = all_data['triggered']['user']['username']
            output_json_data(data)


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


@server_agent.command(name='statistics')
@click.pass_context
def server_agent_statistics(ctx):
    """Display statistics for agents - num_idle, etc."""
    data = ctx.obj.get_agent_statistics()
    output_json_data(data)


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

    for agent in data['agent']:
        agent_info = ctx.obj.get_agent_by_agent_id(agent['id'])
        agent['ip'] = agent_info['ip']
        agent['pool'] = agent_info['pool']['name']
        agent['build_type'] = ctx.obj.get_agent_build_type(agent['id'])
        agent['build_text'] = ctx.obj.get_agent_build_text(agent['id'])

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
@click.option('--start', default=0, help='Start index')
@click.option('--count', default=10, help='Max number of items to show')
def change_list(ctx, start, count):
    """Display list of changes"""
    data = ctx.obj.get_all_changes(start=start, count=count)
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
