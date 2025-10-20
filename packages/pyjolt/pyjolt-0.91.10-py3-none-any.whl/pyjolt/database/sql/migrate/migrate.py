"""
migrate.py
Alembic integration for database migrations, with argparse subparsers for CLI commands.
"""

import os
import shutil
from typing import Optional, cast, Any
from alembic.config import Config
from alembic import command
from pydantic import BaseModel, Field, ConfigDict

from ....pyjolt import PyJolt
from ..sql_database import SqlDatabase
from ....base_extension import BaseExtension

def register_db_commands(app: PyJolt, migrate: 'Migrate'):
    """
    Registers subparsers (CLI commands) for database migrations to the app's CLI.
    This replaces the old app.add_cli_command(...) calls with subparser definitions
    so that we can parse arguments like "db-upgrade <revision>" or "db-migrate --message '...'",
    etc.
    """

    # db-init
    sp_init = app.subparsers.add_parser(f"{migrate.command_prefix}db-init", help="Initialize the Alembic migration environment.")
    sp_init.set_defaults(func=lambda args: migrate.init())

    # db-migrate
    sp_migrate = app.subparsers.add_parser(f"{migrate.command_prefix}db-migrate", help="Generate a new revision file (autogenerate).")
    sp_migrate.add_argument("--message", default="", help="Revision message.")
    sp_migrate.set_defaults(func=lambda args: migrate.migrate(message=args.message))

    # db-upgrade
    sp_upgrade = app.subparsers.add_parser(f"{migrate.command_prefix}db-upgrade", help="Upgrade the database to a specified (or head) revision.")
    sp_upgrade.add_argument("--revision", nargs="?", default="head", help="Revision identifier (default=head).")
    sp_upgrade.set_defaults(func=lambda args: migrate.upgrade(revision=args.revision))

    # db-downgrade
    sp_downgrade = app.subparsers.add_parser(f"{migrate.command_prefix}db-downgrade", help="Downgrade the database to a specified (or one step) revision.")
    sp_downgrade.add_argument("--revision", nargs="?", default="-1", help="Revision identifier (default=-1, i.e. one step down).")
    sp_downgrade.set_defaults(func=lambda args: migrate.downgrade(revision=args.revision))

    # db-history
    sp_history = app.subparsers.add_parser(f"{migrate.command_prefix}db-history", help="Show revision history.")
    sp_history.add_argument("--verbose", action="store_true", help="Show more details about each revision.")
    sp_history.add_argument("--indicate-current", action="store_true", help="Mark the current revision in the log.")
    sp_history.set_defaults(func=lambda args: migrate.history(verbose=args.verbose, indicate_current=args.indicate_current))

    # db-current
    sp_current = app.subparsers.add_parser(f"{migrate.command_prefix}db-current", help="Show the current revision of the database.")
    sp_current.add_argument("--verbose", action="store_true", help="Show more details about the current revision.")
    sp_current.set_defaults(func=lambda args: migrate.current(verbose=args.verbose))

    # db-heads
    sp_heads = app.subparsers.add_parser(f"{migrate.command_prefix}db-heads", help="Show all current 'head' revisions.")
    sp_heads.add_argument("--verbose", action="store_true", help="Show more details.")
    sp_heads.set_defaults(func=lambda args: migrate.heads(verbose=args.verbose))

    # db-show
    sp_show = app.subparsers.add_parser(f"{migrate.command_prefix}db-show", help="Show details of a given revision.")
    sp_show.add_argument("--revision", nargs="?", default="head", help="The revision to show (default=head).")
    sp_show.set_defaults(func=lambda args: migrate.show(revision=args.revision))

    # db-stamp
    sp_stamp = app.subparsers.add_parser(f"{migrate.command_prefix}db-stamp", help="Stamp the database with a given revision (no actual migration).")
    sp_stamp.add_argument("--revision", nargs="?", default="head", help="Revision to stamp (default=head).")
    sp_stamp.set_defaults(func=lambda args: migrate.stamp(revision=args.revision))

class MigrateConfig(BaseModel):
    """Configuration options for Migrate extension"""
    model_config = ConfigDict(extra="allow")

    ALEMBIC_MIGRATION_DIR: str = Field("migrations", description="Connection string for the database")
    ALEMBIC_DATABASE_URI_SYNC: str = Field(description="AsyncSession variable name for use with @managed_session decorator and @readonly_session decorator")

class Migrate(BaseExtension):
    """
    Integrates Alembic with the application for managing database migrations.
    Uses the same variables prefix as the SqlDatabase instance

    The command prefix is used to differentiate between different Migration instances
    when using the CLI.
    """
    def __init__(self, db: SqlDatabase, command_prefix: str = ""):
        self._app: "PyJolt"
        self._root_path: str
        self._db: SqlDatabase = db
        self._configs_name: str = db.configs_name
        self._configs: Optional[dict[str, Any]] = None
        self._migrations_path: Optional[str] = None
        self._migration_dir: Optional[str] = None
        self._database_uri: Optional[str] = None
        self._command_prefix: str = command_prefix

    def init_app(self, app: PyJolt):
        """
        Initializes Alembic for the given app.
        """
        self._app = app
        self._root_path = self._app.root_path
        self._configs = app.get_conf(self._configs_name, None)
        if self._configs is None:
            raise ValueError(f"Configurations for {self._configs_name} for {self.__class__.__name__} not found in app configurations.")
        self._configs = self.validate_configs(self._configs, MigrateConfig)
        self._migration_dir = self._configs.get("ALEMBIC_MIGRATION_DIR")
        self._migrations_path = os.path.join(self._root_path, cast(str, self._migration_dir))
        # use a SYNC database driver for migrations
        self._database_uri = self._configs.get("ALEMBIC_DATABASE_URI_SYNC")
        app.add_extension(self)
        # Register all the subparser commands
        register_db_commands(self._app, self)

    def get_alembic_config(self) -> Config:
        """
        Returns an Alembic configuration object.
        """
        cfg_path = os.path.join(cast(str, self._migrations_path), "alembic.ini")
        config = Config(cfg_path)
        config.set_main_option("sqlalchemy.url", cast(str, self._database_uri))
        #pylint: disable-next=W0212
        associated_models = self._app._db_models.get(self._db.db_name, None)
        if not associated_models or len(associated_models) == 0:
            #pylint: disable-next=W0719
            raise Exception(f"No models associated with db: {self._db.db_name}")
        config.attributes["target_metadata"] = associated_models[0].metadata
        return config

    def _copy_env_template(self):
        """
        Copies the env.py template to the migrations directory.
        """
        template_path = os.path.join(os.path.dirname(__file__), "env_template.py")
        destination_path = os.path.join(self._migrations_path, "env.py")
        shutil.copy(template_path, destination_path)

    def init(self):
        """
        Initializes the Alembic migration environment (if not done already).
        """
        if not os.path.exists(self._migrations_path):
            os.makedirs(self._migrations_path)
        command.init(self.get_alembic_config(), self._migrations_path, template="generic")
        self._copy_env_template()

    def migrate(self, message="Generate migration"):
        """
        Creates a new Alembic revision script (autogenerated) with the given message.
        """
        config = self.get_alembic_config()
        command.revision(config, autogenerate=True, message=message)

    def upgrade(self, revision="head"):
        """
        Upgrades the database to the given revision (default=head).
        """
        config = self.get_alembic_config()
        command.upgrade(config, revision)

    def downgrade(self, revision="-1"):
        """
        Downgrades the database to the given revision (default=-1, i.e. one step).
        """
        config = self.get_alembic_config()
        command.downgrade(config, revision)

    def history(self, verbose=False, indicate_current=False):
        """
        Shows the revision history.
        """
        config = self.get_alembic_config()
        command.history(config, verbose=verbose, indicate_current=indicate_current)

    def current(self, verbose=False):
        """
        Shows the current revision of the database.
        """
        config = self.get_alembic_config()
        command.current(config, verbose=verbose)

    def stamp(self, revision="head"):
        """
        Stamps the database with a given revision, without running migrations.
        """
        config = self.get_alembic_config()
        command.stamp(config, revision)

    def heads(self, verbose=False):
        """
        Displays all current head revisions.
        """
        config = self.get_alembic_config()
        command.heads(config, verbose=verbose)

    def show(self, revision="head"):
        """
        Shows details of a specific revision (default=head).
        """
        config = self.get_alembic_config()
        command.show(config, revision)

    @property
    def command_prefix(self) -> str:
        """
        Returns the command prefix for the CLI
        """
        return self._command_prefix
