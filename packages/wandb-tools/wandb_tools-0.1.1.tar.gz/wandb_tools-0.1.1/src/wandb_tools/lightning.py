import os
import re
import shutil
from pathlib import Path

import wandb
from dotenv import load_dotenv
from lightning.pytorch.loggers import WandbLogger

assert load_dotenv(override=True)


class LitWandbLogger(WandbLogger):
    """Enhanced WandB logger with automatic proxy configuration and cache cleanup."""

    def __init__(self, config: dict, **kwargs):
        """Initialize LitWandbLogger with proxy handling and optimized settings.

        Args:
            config: Configuration dictionary to log to WandB
            **kwargs: Additional arguments passed to parent WandbLogger
        """
        # Prevent user from forgetting to convert special configuration object to dict
        if not isinstance(config, dict):
            raise TypeError(f"Configuration must be a dictionary. But got {type(config)}.")

        # Assure not being blocked by the enterprise firewall
        if "no_proxy" in os.environ:
            ip_base = re.findall(r"http://(.+):", os.environ["WANDB_BASE_URL"])[0]
            os.environ["no_proxy"] = f"{ip_base},{os.environ['no_proxy']}"

        super().__init__(
            save_dir=None,
            config=config,
            # Disable logging machine info to prevent heavy transeferring traffic
            settings=wandb.Settings(
                _disable_stats=True,
                _disable_machine_info=True,
            ),
            **kwargs,
        )

    def finish(self):
        """Finish the WandB run and clean up local cache directories."""
        # Identify the local cache directory before `run` object vanishes
        run_dir = None
        if wandb.run:
            run_dir = Path(wandb.run.dir).parent

        # Finish the run
        wandb.finish()

        # Remove the local cache directory
        if run_dir:
            shutil.rmtree(run_dir)  # Wandb's local cache
        if Path("~/.cache/wandb/artifacts").exists():
            shutil.rmtree("~/.cache/wandb/artifacts")
