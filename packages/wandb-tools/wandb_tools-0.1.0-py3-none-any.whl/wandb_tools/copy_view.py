import os
import re
from argparse import ArgumentParser

import wandb_workspaces.workspaces as ws

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "source_url",
        help="The url of source workspace view. Select the source view, click the three dots on the top right, and click copy workspace URL.",
    )
    parser.add_arugment(
        "target_project",
        help="The target project to save the view. Note that the project should have the same groups and metrics with the source project.",
    )
    parser.add_argument("--api-key", required=True, help="Wandb API Key")
    args = parser.parse_args()

    base_url = re.findall(r"(.+)/.+/.+", args.source_url)[0]
    os.environ["WANDB_BASE_URL"] = base_url
    os.environ["WANDB_API_KEY"] = args.api_key

    source_workspace = ws.Workspace.from_url(args.source_url)

    workspace = ws.Workspace(
        entity="sinopac",
        project=args.target_project,
        name=source_workspace.name,
        sections=source_workspace.sections,
        settings=source_workspace.settings,
        runset_settings=source_workspace.runset_settings,
    )

    workspace.save()
