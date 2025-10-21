import argparse
import shutil
from pathlib import Path

from .base_module import BaseModule
from ..config import Config
from ..error_handler import ValidationError, logger


class AppsModule(BaseModule):
    def __init__(self, config: Config) -> None:
        self.config = config

    def get_command(self) -> str:
        return "apps"

    def add_parser(self, subparsers: argparse._SubParsersAction) -> None:
        app_parser = subparsers.add_parser(
            self.get_command(), help="Manage micro-applications"
        )

        # Create subparsers for app commands
        app_subparsers = app_parser.add_subparsers(dest="app_command", required=True)

        # app init
        init_parser = app_subparsers.add_parser(
            "init", help="Create a new micro-app from template"
        )
        init_parser.add_argument(
            "-d",
            "--directory",
            type=str,
            default=".",
            help="Directory to create the micro-app in (default: current directory)",
        )
        init_parser.set_defaults(func=self._init_app)

        # app deploy
        deploy_parser = app_subparsers.add_parser(
            "deploy", help="Deploy micro-app (same as assistants synchronize)"
        )
        deploy_parser.add_argument(
            "-f",
            "--file",
            type=str,
            default="assistants.json",
            help="Path to assistants.json file (default: assistants.json)",
        )
        deploy_parser.add_argument(
            "--force", action="store_true", help="Force overwrite assistant files"
        )
        deploy_parser.set_defaults(func=self._deploy_app)

    def execute(self, args: argparse.Namespace) -> None:
        """Execute the app command."""
        args.func(args)

    def _choose_micro_app_template(self) -> str:
        """Prompt user to choose micro-app template type."""
        print("\nChoose a micro-app template:")
        print("1. basic - Basic micro-app template")
        print("2. advanced - Advanced micro-app template with more features")

        choice = input("Enter your choice (1-2): ").strip()

        if choice not in ["1", "2"]:
            raise ValidationError("Invalid choice. Please select 1 or 2.")

        return "basic" if choice == "1" else "advanced"

    def _init_app(self, args: argparse.Namespace) -> None:
        """Initialize a new micro-app from template."""
        # Choose template type
        template_type = self._choose_micro_app_template()

        # Create target directory if it doesn't exist
        target_dir = Path(args.directory)
        target_dir.mkdir(exist_ok=True)

        # Only copy the micro-app content to micro-app folder
        self._copy_micro_app_content(target_dir, template_type)

        logger.info(f"Created {template_type} micro-app in '{target_dir}/micro-app'")

    def create_micro_app_for_assistant(self, target_dir: Path) -> str:
        """Create a micro-app for an assistant and return the template type used."""
        # Choose template type using the same method
        template_type = self._choose_micro_app_template()

        # Copy the micro-app content to micro-app folder
        self._copy_micro_app_content(target_dir, template_type)

        return template_type

    def _copy_micro_app_content(self, target_dir: Path, template_type: str) -> None:
        """Copy the micro-app content to micro-app folder."""
        micro_app_dir = target_dir / "micro-app"

        # Copy micro-app template from data/micro-apps/{template_type}/
        micro_app_source = (
            Path(__file__).parent.parent.parent / "data" / "micro-apps" / template_type
        )
        if not micro_app_source.exists():
            logger.warning(
                f"Micro-app template directory not found: {micro_app_source}"
            )
            return

        shutil.copytree(micro_app_source, micro_app_dir)
        logger.info(f"Created {template_type} micro-app: {micro_app_dir}")

    def _deploy_app(self, args: argparse.Namespace) -> None:
        """Deploy micro-app using assistants synchronize."""
        # Import and use existing sync functionality
        from .sync_module import SyncModule
        from .pkg_module import PkgModule

        pkg_module = PkgModule(config=self.config)
        sync_module = SyncModule(config=self.config, pkg_module=pkg_module)

        # Create args compatible with existing sync module
        sync_args = argparse.Namespace()
        sync_args.config = args.file
        sync_args.force = getattr(args, "force", False)

        sync_module.execute(sync_args)
