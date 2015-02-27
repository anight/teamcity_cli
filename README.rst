teamcity_cli
============

::

    $ teamcity_cli
    Usage: teamcity_cli [OPTIONS] COMMAND [ARGS]...

      CLI for interacting with TeamCity

    Options:
      --help  Show this message and exit.

    Commands:
      build    Commands related to builds
      change   Commands related to changes
      project  Commands related to projects
      server   Commands related to the server instance
      user     Commands related to users

    $ teamcity_cli build list --build-type-id=Ansvc_Branches_Py34 --branch=develop
    count: 5
    +---------+--------+---------------------+------------+
    | status  | number | buildTypeId         | branchName |
    +---------+--------+---------------------+------------+
    | SUCCESS | 50     | Ansvc_Branches_Py34 | develop    |
    | SUCCESS | 47     | Ansvc_Branches_Py34 | develop    |
    | FAILURE | 3      | Ansvc_Branches_Py34 | develop    |
    | SUCCESS | 2      | Ansvc_Branches_Py34 | develop    |
    | FAILURE | 1      | Ansvc_Branches_Py34 | develop    |
    +---------+--------+---------------------+------------+
