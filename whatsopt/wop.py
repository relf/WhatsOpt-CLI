import click
from whatsopt import __version__
from .whatsopt_client import WhatsOpt
from logging import error


@click.group()
@click.version_option(__version__)
@click.option("--credentials", help="specify authentication information (API key)")
@click.option(
    "--url",
    help="specify WhatsOpt application server URL (default: {})".format(
        WhatsOpt(login=False).default_url
    ),
)
@click.pass_context
def cli(ctx, credentials, url):
    ctx.obj["api_key"] = credentials
    ctx.obj["url"] = url


@cli.command()
def url():
    """ WhatsOpt server url """
    print(WhatsOpt(login=False).url)


@cli.command()
@click.argument("url")
@click.pass_context
def login(ctx, url):
    """ Authenticate to the specified WhatsOpt server given its URL """
    ctx.obj["url"] = url
    WhatsOpt(**ctx.obj).login(echo=True)


@cli.command()
def logout():
    """ Deconnect from WhatsOpt server """
    WhatsOpt(login=False).logout()


@cli.command()
@click.pass_context
def list(ctx):
    """ List analyses """
    WhatsOpt(**ctx.obj).list_analyses()


@cli.command()
@click.option(
    "-n",
    "--dry-run",
    is_flag=True,
    default=False,
    help="generate analysis push data without actually pushing",
)
@click.option(
    "--scalar-format",
    is_flag=True,
    default=False,
    help="manage (1,) shape variables as scalar variables",
)
@click.option("--name", help="find analysis with given name")
@click.argument("py_filename")
@click.pass_context
def push(ctx, dry_run, scalar_format, name, py_filename):
    """ Push analysis from given PY_FILENAME """
    wop = WhatsOpt(**ctx.obj)
    options = {"--dry-run": dry_run, "--scalar-format": scalar_format, "--name": name}
    wop.execute(py_filename, wop.push_mda_cmd, options)
    # if not exited successfully in execute
    if name:
        error("Analysis %s not found" % name)
    else:
        error("Analysis not found")
    exit(-1)


@cli.command()
@click.option(
    "-n",
    "--dry-run",
    is_flag=True,
    default=False,
    help="print analysis pull infos without actually pulling",
)
@click.option(
    "-f", "--force", is_flag=True, default=False, help="overwrite existing files"
)
@click.option(
    "-s", "--server", is_flag=True, default=False, help="generate Thrift server as well"
)
@click.option(
    "-o", "--run-ops", is_flag=True, default=False, help="update operation run scripts"
)
@click.option(
    "-u",
    "--test-units",
    is_flag=True,
    default=False,
    help="update discipline test scripts",
)
@click.argument("analysis_id")
@click.pass_context
def pull(ctx, dry_run, force, server, run_ops, test_units, analysis_id):
    """ Pull analysis given its identifier """
    options = {
        "--dry-run": dry_run,
        "--force": force,
        "--server": server,
        "--run-ops": run_ops,
        "--test-units": test_units,
    }
    WhatsOpt(**ctx.obj).pull_mda(analysis_id, options)


@cli.command()
@click.option(
    "-a" "--analysis-id",
    help="specify the analysis to update from (otherwise guessed from current files)",
)
@click.option(
    "-f", "--force", is_flag=True, default=False, help="overwrite existing files"
)
@click.option(
    "-s" "--server", is_flag=True, default=False, help="update Thrift server as well"
)
@click.option(
    "-o" "--run-ops", is_flag=True, default=False, help="update operation run scripts"
)
@click.option(
    "-u" "--test-units",
    is_flag=True,
    default=False,
    help="update discipline test scripts",
)
@click.pass_context
def update(ctx, analysis_id, force, server, run_ops, test_units):
    """ Update analysis connections """
    options = {
        "--force": force,
        "--server": server,
        "--run-ops": run_ops,
        "--test-units": test_units,
    }
    WhatsOpt(**ctx.obj).update_mda(analysis_id, options)


@cli.command()
@click.argument("filename")
@click.option(
    "-k",
    "--driver-kind",
    type=click.Choice(["doe", "optimizer", "screening"]),
    help="used with csv data upload to specify driver kind",
)
@click.option(
    "-a",
    "--analysis-id",
    help="specify the analysis to create a new operation otherwise use default analysis",
)
@click.option(
    "-o", "--operation-id", help="specify the operation to be updated with new cases"
)
@click.option(
    "-n",
    "--dry-run",
    is_flag=True,
    default=False,
    help="parse data file and display content without uploading",
)
@click.option(
    "-c",
    "--outvar-count",
    type=int,
    default=1,
    help="number of output variable (>0) only used when uploading csv file",
)
@click.option(
    "-x",
    "--only-success",
    is_flag=True,
    default=False,
    help="keep only data from successful executions",
)
@click.option(
    "-p", "--parallel", is_flag=True, default=False, help="use filename as first",
)
@click.pass_context
def upload(
    ctx,
    filename,
    driver_kind,
    analysis_id,
    operation_id,
    dry_run,
    outvar_count,
    only_success,
    parallel,
):
    """ Upload data stored in given FILENAME being in results in sqlite or csv format or run parameters file"""
    WhatsOpt(**ctx.obj).upload(
        filename,
        driver_kind,
        analysis_id,
        operation_id,
        dry_run,
        outvar_count,
        only_success,
        parallel,
    )


@cli.command()
@click.pass_context
def version(ctx):
    """ Show versions of WhatsOpt app and recommended wop command line """
    WhatsOpt(**ctx.obj).check_versions()


@cli.command()
def serve():
    """ Launch analysis server """
    WhatsOpt(login=False).serve()


cli(prog_name="wop", obj={})
