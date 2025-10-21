import json
import os
import sys
import time
import traceback

from metaflow import util, Run
from metaflow._vendor import click
from metaflow.exception import METAFLOW_EXIT_DISALLOW_RETRY
from metaflow.metadata_provider.util import sync_local_metadata_from_datastore
from metaflow.metaflow_config import (
    CARD_S3ROOT,
    DATASTORE_LOCAL_DIR,
    DATASTORE_SYSROOT_S3,
    DATATOOLS_S3ROOT,
    DEFAULT_METADATA,
    SERVICE_HEADERS,
    SERVICE_URL,
    DEFAULT_SECRETS_BACKEND_TYPE,
    DEFAULT_AWS_CLIENT_PROVIDER,
    AWS_SECRETS_MANAGER_DEFAULT_REGION,
    S3_ENDPOINT_URL,
    AZURE_STORAGE_BLOB_SERVICE_ENDPOINT,
    DATASTORE_SYSROOT_AZURE,
    CARD_AZUREROOT,
    DATASTORE_SYSROOT_GS,
    CARD_GSROOT,
    KUBERNETES_SANDBOX_INIT_SCRIPT,
    OTEL_ENDPOINT,
    NVIDIA_HEARTBEAT_THRESHOLD,
)
from metaflow.mflog import TASK_LOG_SOURCE

from .nvcf import Nvcf
from .exceptions import NvcfKilledException


@click.group()
def cli():
    pass


@cli.group(help="Commands related to nvidia.")
def nvidia():
    pass


@nvidia.command(help="List steps / tasks running as an nvidia job.")
@click.option(
    "--run-id",
    default=None,
    required=True,
    help="List unfinished tasks corresponding to the run id.",
)
@click.pass_context
def list(ctx, run_id):
    flow_name = ctx.obj.flow.name
    run_obj = Run(pathspec=f"{flow_name}/{run_id}", _namespace_check=False)
    running_invocations = []

    for each_step in run_obj:
        for each_task in each_step:
            if not each_task.finished and "nvcf-function-id" in each_task.metadata_dict:

                task_pathspec = each_task.pathspec
                attempt = each_task.metadata_dict.get("attempt")
                flow_name, run_id, step_name, task_id = task_pathspec.split("/")
                running_invocations.append(
                    f"Flow Name: {flow_name}, Run ID: {run_id}, Step Name: {step_name}, Task ID: {task_id}, Retry Count: {attempt}"
                )

    if running_invocations:
        for each_invocation in running_invocations:
            ctx.obj.echo(each_invocation)


@nvidia.command(help="Kill steps / tasks running as an nvidia job.")
@click.option(
    "--run-id",
    default=None,
    required=True,
    help="Terminate unfinished tasks corresponding to the run id.",
)
@click.pass_context
def kill(ctx, run_id):
    from metaflow_extensions.outerbounds.plugins.nvcf.heartbeat_store import (
        HeartbeatStore,
    )

    datastore_root = ctx.obj.datastore_impl.datastore_root
    store = HeartbeatStore(
        main_pid=None,
        storage_backend=ctx.obj.datastore_impl(datastore_root),
    )

    flow_name = ctx.obj.flow.name
    tombstone_prefix = f"{flow_name}/{run_id}"
    store.emit_tombstone(
        tombstone_prefix=tombstone_prefix, folder_name="nvcf_heartbeats"
    )


@nvidia.command(
    help="Execute a single task using @nvidia. This command calls the "
    "top-level step command inside an nvidia job with the given options. "
    "Typically you do not call this command directly; it is used internally by "
    "Metaflow."
)
@click.argument("step-name")
@click.argument("code-package-sha")
@click.argument("code-package-url")
@click.option("--function-id", help="NVCF function id.")
@click.option("--ngc-api-key", help="NGC API key.")
@click.option(
    "--queue-timeout", default=5 * 24 * 3600, help="Queue timeout in seconds."
)
@click.option("--run-id", help="Passed to the top-level 'step'.")
@click.option("--task-id", help="Passed to the top-level 'step'.")
@click.option("--input-paths", help="Passed to the top-level 'step'.")
@click.option("--split-index", help="Passed to the top-level 'step'.")
@click.option("--clone-path", help="Passed to the top-level 'step'.")
@click.option("--clone-run-id", help="Passed to the top-level 'step'.")
@click.option(
    "--tag", multiple=True, default=None, help="Passed to the top-level 'step'."
)
@click.option("--namespace", default=None, help="Passed to the top-level 'step'.")
@click.option("--retry-count", default=0, help="Passed to the top-level 'step'.")
@click.option(
    "--max-user-code-retries", default=0, help="Passed to the top-level 'step'."
)
@click.pass_context
def step(
    ctx,
    step_name,
    code_package_sha,
    code_package_url,
    function_id,
    ngc_api_key,
    queue_timeout,
    **kwargs,
):
    def echo(msg, stream="stderr", _id=None, **kwargs):
        msg = util.to_unicode(msg)
        if _id:
            msg = "[%s] %s" % (_id, msg)
        ctx.obj.echo_always(msg, err=(stream == sys.stderr), **kwargs)

    executable = ctx.obj.environment.executable(step_name)
    entrypoint = "%s -u %s" % (executable, os.path.basename(sys.argv[0]))

    top_args = " ".join(util.dict_to_cli_options(ctx.parent.parent.params))

    input_paths = kwargs.get("input_paths")
    split_vars = None
    if input_paths:
        max_size = 30 * 1024
        split_vars = {
            "METAFLOW_INPUT_PATHS_%d" % (i // max_size): input_paths[i : i + max_size]
            for i in range(0, len(input_paths), max_size)
        }
        kwargs["input_paths"] = "".join("${%s}" % s for s in split_vars.keys())

    step_args = " ".join(util.dict_to_cli_options(kwargs))
    step_cli = "{entrypoint} {top_args} step {step} {step_args}".format(
        entrypoint=entrypoint,
        top_args=top_args,
        step=step_name,
        step_args=step_args,
    )
    node = ctx.obj.graph[step_name]

    # Get retry information
    retry_count = kwargs.get("retry_count", 0)
    retry_deco = [deco for deco in node.decorators if deco.name == "retry"]
    minutes_between_retries = None
    if retry_deco:
        minutes_between_retries = int(
            retry_deco[0].attributes.get("minutes_between_retries", 1)
        )

    task_spec = {
        "flow_name": ctx.obj.flow.name,
        "step_name": step_name,
        "run_id": kwargs["run_id"],
        "task_id": kwargs["task_id"],
        "retry_count": str(retry_count),
    }

    env = {
        "METAFLOW_CODE_SHA": code_package_sha,
        "METAFLOW_CODE_URL": code_package_url,
        "METAFLOW_CODE_DS": ctx.obj.flow_datastore.TYPE,
        "METAFLOW_SERVICE_URL": SERVICE_URL,
        "METAFLOW_SERVICE_HEADERS": json.dumps(SERVICE_HEADERS),
        "METAFLOW_DATASTORE_SYSROOT_S3": DATASTORE_SYSROOT_S3,
        "METAFLOW_DATATOOLS_S3ROOT": DATATOOLS_S3ROOT,
        "METAFLOW_DEFAULT_DATASTORE": ctx.obj.flow_datastore.TYPE,
        "METAFLOW_USER": util.get_username(),
        "METAFLOW_DEFAULT_METADATA": DEFAULT_METADATA,
        "METAFLOW_CARD_S3ROOT": CARD_S3ROOT,
        "METAFLOW_RUNTIME_ENVIRONMENT": "nvcf",
        "METAFLOW_DEFAULT_SECRETS_BACKEND_TYPE": DEFAULT_SECRETS_BACKEND_TYPE,
        "METAFLOW_DEFAULT_AWS_CLIENT_PROVIDER": DEFAULT_AWS_CLIENT_PROVIDER,
        "METAFLOW_AWS_SECRETS_MANAGER_DEFAULT_REGION": AWS_SECRETS_MANAGER_DEFAULT_REGION,
        "METAFLOW_S3_ENDPOINT_URL": S3_ENDPOINT_URL,
        "METAFLOW_AZURE_STORAGE_BLOB_SERVICE_ENDPOINT": AZURE_STORAGE_BLOB_SERVICE_ENDPOINT,
        "METAFLOW_DATASTORE_SYSROOT_AZURE": DATASTORE_SYSROOT_AZURE,
        "METAFLOW_CARD_AZUREROOT": CARD_AZUREROOT,
        "METAFLOW_DATASTORE_SYSROOT_GS": DATASTORE_SYSROOT_GS,
        "METAFLOW_CARD_GSROOT": CARD_GSROOT,
        "METAFLOW_INIT_SCRIPT": KUBERNETES_SANDBOX_INIT_SCRIPT,
        "METAFLOW_OTEL_ENDPOINT": OTEL_ENDPOINT,
        "METAFLOW_NVIDIA_HEARTBEAT_THRESHOLD": str(NVIDIA_HEARTBEAT_THRESHOLD),
    }

    env_deco = [deco for deco in node.decorators if deco.name == "environment"]
    if env_deco:
        env.update(env_deco[0].attributes["vars"])

    # Add the environment variables related to the input-paths argument
    if split_vars:
        env.update(split_vars)

    if retry_count:
        ctx.obj.echo_always(
            "Sleeping %d minutes before the next retry" % minutes_between_retries
        )
        time.sleep(minutes_between_retries * 60)

    # this information is needed for log tailing
    ds = ctx.obj.flow_datastore.get_task_datastore(
        mode="w",
        run_id=kwargs["run_id"],
        step_name=step_name,
        task_id=kwargs["task_id"],
        attempt=int(retry_count),
    )
    stdout_location = ds.get_log_location(TASK_LOG_SOURCE, "stdout")
    stderr_location = ds.get_log_location(TASK_LOG_SOURCE, "stderr")

    def _sync_metadata():
        if ctx.obj.metadata.TYPE == "local":
            sync_local_metadata_from_datastore(
                DATASTORE_LOCAL_DIR,
                ctx.obj.flow_datastore.get_task_datastore(
                    kwargs["run_id"], step_name, kwargs["task_id"]
                ),
            )

    nvcf = Nvcf(
        ctx.obj.metadata,
        ctx.obj.flow_datastore,
        ctx.obj.environment,
        function_id,
        ngc_api_key,
        queue_timeout,
    )
    try:
        with ctx.obj.monitor.measure("metaflow.nvcf.launch_job"):
            nvcf.launch_job(
                step_name,
                step_cli,
                task_spec,
                code_package_sha,
                code_package_url,
                ctx.obj.flow_datastore.TYPE,
                env=env,
            )
    except Exception as e:
        traceback.print_exc()
        _sync_metadata()
        sys.exit(METAFLOW_EXIT_DISALLOW_RETRY)
    try:
        nvcf.wait(stdout_location, stderr_location, echo=echo)
    except NvcfKilledException:
        # don't retry killed tasks
        traceback.print_exc()
        sys.exit(METAFLOW_EXIT_DISALLOW_RETRY)
    finally:
        _sync_metadata()
