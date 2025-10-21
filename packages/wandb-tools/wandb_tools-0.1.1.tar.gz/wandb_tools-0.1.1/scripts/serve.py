import argparse
import getpass
import subprocess
from pathlib import Path

# Command line interface
parser = argparse.ArgumentParser(description="Serve wandb local project")
parser.add_argument(
    "--project",
    type=str,
    required=True,
    help="Project name. Used in naming storage directory and container name.",
)
parser.add_argument(
    "--port",
    type=int,
    required=True,
    help="Port number.",
)
parser.add_argument(
    "--volume",
    type=str,
    required=False,
    default=None,
    help="Path to the volumne to mount. If not provided, a new directory `/volume/share/wandb-local/volume/<project>` wiil be created.",
)
args = parser.parse_args()

# Form docker container name
username = getpass.getuser()
container_name = f"{username}-wandb-{args.project}"

# Identify Volume path
if args.volume:
    directory = Path(args.volume)
    assert directory.is_dir(), f'No directory named "{directory}".'
else:
    directory = Path("/volume/share/wandb-local/volume") / args.project
    directory.mkdir(exist_ok=True)

# Check whether the volume is being used by other containers
for volume_record in (
    subprocess.run(
        "docker inspect -f '{{.Name}}: {{range .Mounts}}{{.Source}}{{end}}' $(docker ps -q)",
        shell=True,
        check=True,
        capture_output=True,
    )
    .stdout.decode("utf-8")
    .strip()
    .split("\n")
):
    container, volume = volume_record.split(": ")
    if str(directory.expanduser().resolve()) in volume:
        raise RuntimeError(f"Volume {volume} is already being used by container {container}.")

# Launch the docker container
docker_cmd = [
    "docker",
    "run",
    "-d",  # run in background
    f"-v={directory}:/vol",  # Map storage volume
    f"-p={args.port}:8080",  # Port forwarding
    f"--name={container_name}",  # Container name
    "--restart=unless-stopped",  # Restart policy
    "wandb/local:latest",  # Docker image
]
subprocess.run(docker_cmd, check=True)
