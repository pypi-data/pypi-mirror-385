from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict
import subprocess
import shutil
import sys
from metaflow import current

__mf_promote_submodules__ = ["plugins.torchtune"]


class TorchTune:
    def __init__(
        self,
        use_multi_node_config: bool = False,
        config_overrides: Optional[Dict] = None,
    ):
        """
        Initialize the Tune launcher.

        :param use_multi_node_config: If True, attempt to build a distributed configuration
                                      from current.torch.torchrun_args.
        :param config_overrides: Optional dictionary of config overrides for tune run.
        """
        self.multi_node_config = {}
        if use_multi_node_config:
            if getattr(current, "torch", None):
                print(
                    "[Metaflow Tune] Since @torchrun is used, multi-node config can be used to launch the job."
                )
                # For distributed torchtune launches, we use similar parameters as torchrun.
                # (You might need to adjust the keys according to your environment.)
                self.multi_node_config = {
                    "nnodes": current.torch.torchrun_args["nnodes"],
                    "master_addr": current.torch.torchrun_args["master_addr"],
                    "master_port": int(current.torch.torchrun_args["master_port"]),
                    "node_rank": current.torch.torchrun_args["node_rank"],
                    "nproc_per_node": current.torch.torchrun_args["nproc_per_node"],
                    "num_processes": current.torch.torchrun_args["nproc_per_node"]
                    * current.torch.torchrun_args["nnodes"],
                }
                if config_overrides:
                    self.multi_node_config.update(config_overrides)
                print(
                    f"[Metaflow Tune] Discovered multi-node config for torchrun: {self.multi_node_config}"
                )
            else:
                print(
                    "[Metaflow Tune] Since @torchrun is not used, default multi-node config cannot be used to launch the job."
                )

    def run(
        self,
        recipe: str,
        config_dict: Dict,
        additional_cli_options: Optional[List[str]] = None,
    ):
        """
        Launch the torchtune job via its CLI.

        :param recipe: The path to the recipe (or name of the recipe) to run.
        :param config_dict: Optional dictionary that will be dumped to a YAML file and passed via --config.
        :param additional_cli_options: Optional list of additional CLI options.
        :raises: subprocess.CalledProcessError if the subprocess returns a nonzero exit code.
        """
        import yaml
        import tempfile
        import os

        _temp_dir = tempfile.mkdtemp()
        try:
            config_path = os.path.join(_temp_dir, "config.yaml")
            with open(config_path, "w") as f:
                yaml.dump(config_dict, f)

            additional_options = (
                additional_cli_options if additional_cli_options else []
            )

            # Build the command. Here we use "tune run" as the base command.
            cmd = ["tune", "run"]

            # If distributed configuration is present, add torchrun–style flags.
            if self.multi_node_config:
                cmd.extend(
                    [
                        "--nnodes",
                        str(self.multi_node_config.get("nnodes")),
                        "--nproc-per-node",
                        str(self.multi_node_config.get("nproc_per_node")),
                        # "--rdzv_conf", f"rdzv_endpoint={self.multi_node_config.get('master_addr')}:{self.multi_node_config.get('master_port')}"
                        "--rdzv-backend",
                        "c10d",
                        "--rdzv-endpoint",
                        f"{self.multi_node_config.get('master_addr')}:{self.multi_node_config.get('master_port')}",
                        "--rdzv-id",
                        "1234567890",
                        "--node-rank",
                        str(self.multi_node_config.get("node_rank")),
                        # TODO: should there be a masterip/port here ?
                    ]
                )

            cmd.extend(additional_options)

            cmd.append(recipe)
            # If a recipe configuration was provided, pass it via the --config flag.
            cmd.extend(["--config", config_path])

            # Append any additional CLI options.

            # Launch the subprocess.
            print(f"[Metaflow tune] {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            # Stream the output in real-time.
            for out_line, err_line in read_popen_pipes(process):
                print(out_line, end="", flush=True)
                print(err_line, end="", file=sys.stderr, flush=True)

            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
        finally:
            shutil.rmtree(_temp_dir)


def enqueue_output(file, queue):
    for line in iter(file.readline, ""):
        queue.put(line)
    file.close()


def read_popen_pipes(p):

    with ThreadPoolExecutor(2) as pool:
        q_stdout, q_stderr = Queue(), Queue()

        pool.submit(enqueue_output, p.stdout, q_stdout)
        pool.submit(enqueue_output, p.stderr, q_stderr)

        while True:

            if p.poll() is not None and q_stdout.empty() and q_stderr.empty():
                break

            out_line = err_line = ""

            try:
                out_line = q_stdout.get_nowait()
            except Empty:
                pass
            try:
                err_line = q_stderr.get_nowait()
            except Empty:
                pass

            yield (out_line, err_line)
