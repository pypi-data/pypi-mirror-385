import logging
from typing import Optional, Self

import typer
from rich.console import Console
from typer import Option

from .integrations import (
    CloudflareApiTokenManager,
    GitHubDeviceFlow,
    GitHubOAuthConfig,
    GitHubTokenManager,
    HetznerApiKeyManager,
    KeyringSecretStore,
)

logger = logging.getLogger(__name__)


class LinkSubCommand:
    """Link subcommands for EasyRunner."""

    typer_app: typer.Typer = typer.Typer(
        name="link",
        no_args_is_help=True,
        rich_markup_mode="rich",
        help="[bold green]Link[/bold green] commands for EasyRunner. Manage authentication with external service provider like Github and Hetzner.",
    )

    debug: bool = False
    silent: bool = False

    _console: Console = Console()
    _print = _console.print

    # Define progress callback with CLI-specific formatting
    @staticmethod
    def _progress_callback(message: str, end: str) -> None:
        if not LinkSubCommand.silent:
            LinkSubCommand._print(message, end=end)

    def __init__(self: Self) -> None:
        @self.typer_app.callback(invoke_without_command=True)
        def set_global_options(  # type: ignore
            debug: bool = Option(
                False,
                "--debug",
                help="Enables extra debug messages to be output. Independent of --silent.",
                rich_help_panel="Global Options",
            ),
            silent: bool = Option(
                False,
                "--silent",
                help="Suppresses all output messages.",
                rich_help_panel="Global Options",
            ),
        ) -> None:
            LinkSubCommand.debug = debug
            LinkSubCommand.silent = silent
            if debug:
                logger.setLevel(logging.DEBUG)
            elif silent:
                logger.setLevel(logging.ERROR)

    @typer_app.command(
        name="github",
        help="Authenticate and link with GitHub using OAuth. This will allow EasyRunner to manage deploy keys for your repositories.",
        no_args_is_help=False,
    )
    @staticmethod
    def github_auth(
        unlink: bool = Option(
            False,
            "--unlink",
            help="Unlink GitHub account by removing the stored GitHub authentication token."
        ),
        status: bool = Option(
            False,
            "--status", 
            help="Check current GitHub authentication status."
        )
    ) -> None:
        """Authenticate with GitHub for repository access."""

        token_manager = GitHubTokenManager(secret_store=KeyringSecretStore())

        if unlink:
            if token_manager.delete_token():
                LinkSubCommand._progress_callback(
                    "[green]✅ Successfully unlinked GitHub account[/green]", "\n"
                )
            else:
                LinkSubCommand._progress_callback(
                    "[red]❌ Failed to remove GitHub authentication[/red]", "\n"
                )
            return

        if status:
            stored_token = token_manager.get_token()
            if stored_token:
                config = GitHubOAuthConfig()
                device_flow = GitHubDeviceFlow(
                    client_id=config.client_id,
                    scopes=config.scopes,
                    progress_callback=LinkSubCommand._progress_callback,
                )
                if device_flow.test_token(stored_token):
                    LinkSubCommand._progress_callback(
                        "[green]✅ GitHub authentication active[/green]", "\n"
                    )
                else:
                    LinkSubCommand._progress_callback(
                        "[red]❌ GitHub authentication invalid (token expired or revoked)[/red]",
                        "\n",
                    )
            else:
                LinkSubCommand._progress_callback(
                    "[yellow]⚠️  Not authenticated with GitHub[/yellow]", "\n"
                )
            return

        # if token:
        #     # Manual token input
        #     config = GitHubOAuthConfig()
        #     device_flow = GitHubDeviceFlow(
        #         client_id=config.client_id,
        #         scopes=config.scopes,
        #         progress_callback=LinkSubCommand._progress_callback,
        #     )
        #     if device_flow.test_token(token):
        #         if token_manager.store_token(token):
        #             LinkSubCommand._progress_callback(
        #                 "[green]✅ GitHub token saved successfully[/green]", "\n"
        #             )
        #         else:
        #             LinkSubCommand._progress_callback(
        #                 "[red]❌ Failed to save token[/red]", "\n"
        #             )
        #     else:
        #         LinkSubCommand._progress_callback(
        #             "[red]❌ Invalid GitHub token[/red]", "\n"
        #         )
        #     return

        # Device Flow - OAuth for CLIs
        try:
            LinkSubCommand._progress_callback(
                "[blue]🔐 Starting GitHub Device Flow authentication...[/blue]", "\n"
            )

            config = GitHubOAuthConfig()
            device_flow = GitHubDeviceFlow(
                client_id=config.client_id,
                scopes=config.scopes,
                progress_callback=LinkSubCommand._progress_callback,
            )

            access_token = device_flow.start_device_flow()

            if access_token:
                if token_manager.store_token(access_token):
                    LinkSubCommand._progress_callback(
                        "[green]✅ GitHub authentication successful![/green]", "\n"
                    )
                    LinkSubCommand._progress_callback(
                        "🔑 Access token stored securely in keychain", "\n"
                    )
                    LinkSubCommand._progress_callback(
                        "🚀 EasyRunner can now manage deploy keys for your repositories",
                        "\n",
                    )
                else:
                    LinkSubCommand._progress_callback(
                        "[red]❌ Authentication succeeded but failed to store token[/red]",
                        "\n",
                    )
            else:
                LinkSubCommand._progress_callback(
                    "[red]❌ GitHub authentication failed[/red]", "\n"
                )
                LinkSubCommand._progress_callback(
                    "💡 Try running the command again or use --token to manually provide a token",
                    "\n",
                )

        except KeyboardInterrupt:
            LinkSubCommand._progress_callback(
                "\n[yellow]⚠️  Authentication cancelled[/yellow]", "\n"
            )
        except Exception as e:
            LinkSubCommand._progress_callback(
                f"[red]❌ Authentication error: {e}[/red]", "\n"
            )
            if LinkSubCommand.debug:
                import traceback
                LinkSubCommand._progress_callback(
                    f"[red]{traceback.format_exc()}[/red]", "\n"
                )

    @typer_app.command(
        name="hetzner",
        help="Link Hetzner Cloud to EasyRunner. Provide your Hetzner API key for cloud infrastructure management.",
        no_args_is_help=False,
    )
    @staticmethod
    def hetzner_link(
        project_name: str = typer.Argument(
            "default",
            help="Hetzner project name to link (allows managing multiple projects with different API keys)."
        ),
        api_key: Optional[str] = Option(
            None,
            "--api-key",
            help="Hetzner Cloud API key to store securely."
        ),
        unlink: bool = Option(
            False,
            "--unlink",
            help="Remove Hetzner Cloud link and stored API key."
        ),
        status: bool = Option(
            False,
            "--status",
            help="Check current Hetzner Cloud link status."
        )
    ) -> None:
        """Link Hetzner Cloud for infrastructure management."""

        api_key_manager = HetznerApiKeyManager(
            project_name=project_name, secret_store=KeyringSecretStore()
        )

        if unlink:
            if api_key_manager.delete_api_key():
                LinkSubCommand._progress_callback(
                    f"[green]✅ Successfully unlinked Hetzner Cloud project '{project_name}'[/green]", "\n"
                )
            else:
                LinkSubCommand._progress_callback(
                    f"[red]❌ Failed to remove Hetzner Cloud link for project '{project_name}'[/red]", "\n"
                )
            return

        if status:
            stored_api_key = api_key_manager.get_api_key()
            if stored_api_key:
                # Validate API key format (basic check)
                if len(stored_api_key) > 0:
                    LinkSubCommand._progress_callback(
                        f"[green]✅ Hetzner Cloud project '{project_name}' is linked[/green]", "\n"
                    )
                    LinkSubCommand._progress_callback(
                        f"   Key: {stored_api_key[:8]}...{stored_api_key[-4:]}", "\n"
                    )
                else:
                    LinkSubCommand._progress_callback(
                        f"[red]❌ Hetzner Cloud API key for project '{project_name}' is invalid[/red]", "\n"
                    )
            else:
                LinkSubCommand._progress_callback(
                    f"[yellow]⚠️  Hetzner Cloud project '{project_name}' not linked[/yellow]", "\n"
                )
            return

        if api_key:
            # Validate API key format (basic check)
            if not api_key or len(api_key) < 10:
                LinkSubCommand._progress_callback(
                    "[red]❌ Invalid API key format[/red]", "\n"
                )
                LinkSubCommand._progress_callback(
                    "💡 Hetzner API keys are typically 64 characters long", "\n"
                )
                return

            if api_key_manager.store_api_key(api_key):
                LinkSubCommand._progress_callback(
                    f"[green]✅ Hetzner Cloud API key for project '{project_name}' saved successfully[/green]", "\n"
                )
                LinkSubCommand._progress_callback(
                    "🔑 API key stored securely in keychain", "\n"
                )
                LinkSubCommand._progress_callback(
                    "🚀 EasyRunner can now manage your Hetzner Cloud infrastructure", "\n"
                )
            else:
                LinkSubCommand._progress_callback(
                    f"[red]❌ Failed to save API key for project '{project_name}'[/red]", "\n"
                )
            return

        # No options provided - show help
        LinkSubCommand._progress_callback(
            "[yellow]⚠️  Please provide an API key or use --status/--unlink[/yellow]", "\n"
        )
        LinkSubCommand._progress_callback(
            "\nUsage:", "\n"
        )
        LinkSubCommand._progress_callback(
            "  Link:    er link hetzner [PROJECT_NAME] --api-key YOUR_API_KEY", "\n"
        )
        LinkSubCommand._progress_callback(
            "  Status:  er link hetzner [PROJECT_NAME] --status", "\n"
        )
        LinkSubCommand._progress_callback(
            "  Unlink:  er link hetzner [PROJECT_NAME] --unlink", "\n"
        )
        LinkSubCommand._progress_callback(
            "\n💡 Get your API key from: https://console.hetzner.cloud/", "\n"
        )
        LinkSubCommand._progress_callback(
            "💡 Project name defaults to 'default' if not specified", "\n"
        )

    @typer_app.command(
        name="cloudflare",
        help="Link Cloudflare to EasyRunner. Provide your Cloudflare API token for DNS management.",
        no_args_is_help=False,
    )
    @staticmethod
    def cloudflare_link(
        account_name: str = typer.Argument(
            ...,
            help="Cloudflare account name to link (allows managing multiple accounts with different API tokens).",
        ),
        api_token: Optional[str] = Option(
            None, "--api-token", help="Cloudflare API token to store securely."
        ),
        unlink: bool = Option(
            False, "--unlink", help="Remove Cloudflare link and stored API token."
        ),
        status: bool = Option(
            False, "--status", help="Check current Cloudflare link status."
        ),
    ) -> None:
        """Link Cloudflare for DNS management."""

        api_token_manager = CloudflareApiTokenManager(
            account_name=account_name, secret_store=KeyringSecretStore()
        )

        if unlink:
            if api_token_manager.delete_api_token():
                LinkSubCommand._progress_callback(
                    f"[green]✅ Successfully unlinked Cloudflare account '{account_name}'[/green]",
                    "\n",
                )
            else:
                LinkSubCommand._progress_callback(
                    f"[red]❌ Failed to remove Cloudflare link for account '{account_name}'[/red]",
                    "\n",
                )
            return

        if status:
            stored_api_token = api_token_manager.get_api_token()
            if stored_api_token:
                # Validate API token format (basic check)
                if len(stored_api_token) > 0:
                    LinkSubCommand._progress_callback(
                        f"[green]✅ Cloudflare account '{account_name}' is linked[/green]",
                        "\n",
                    )
                    LinkSubCommand._progress_callback(
                        f"   Token: {stored_api_token[:8]}...{stored_api_token[-4:]}",
                        "\n",
                    )
                else:
                    LinkSubCommand._progress_callback(
                        f"[red]❌ Cloudflare API token for account '{account_name}' is invalid[/red]",
                        "\n",
                    )
            else:
                LinkSubCommand._progress_callback(
                    f"[yellow]⚠️  Cloudflare account '{account_name}' not linked[/yellow]",
                    "\n",
                )
            return

        if api_token:
            # Validate API token format (basic check)
            if not api_token or len(api_token) < 10:
                LinkSubCommand._progress_callback(
                    "[red]❌ Invalid API token format[/red]", "\n"
                )
                LinkSubCommand._progress_callback(
                    "💡 Cloudflare API tokens are typically 40+ characters long", "\n"
                )
                return

            if api_token_manager.store_api_token(api_token):
                LinkSubCommand._progress_callback(
                    f"[green]✅ Cloudflare API token for account '{account_name}' saved successfully[/green]",
                    "\n",
                )
                LinkSubCommand._progress_callback(
                    "🔑 API token stored securely in keychain", "\n"
                )
                LinkSubCommand._progress_callback(
                    "🚀 EasyRunner can now manage your Cloudflare DNS records", "\n"
                )
            else:
                LinkSubCommand._progress_callback(
                    f"[red]❌ Failed to save API token for account '{account_name}'[/red]",
                    "\n",
                )
            return

        # No options provided - show help
        LinkSubCommand._progress_callback(
            "[yellow]⚠️  Please provide an API token or use --status/--unlink[/yellow]",
            "\n",
        )
        LinkSubCommand._progress_callback("\nUsage:", "\n")
        LinkSubCommand._progress_callback(
            "  Link:    er link cloudflare [ACCOUNT_NAME] --api-token YOUR_API_TOKEN",
            "\n",
        )
        LinkSubCommand._progress_callback(
            "  Status:  er link cloudflare [ACCOUNT_NAME] --status", "\n"
        )
        LinkSubCommand._progress_callback(
            "  Unlink:  er link cloudflare [ACCOUNT_NAME] --unlink", "\n"
        )
        LinkSubCommand._progress_callback(
            "\n💡 Get your API token from: https://dash.cloudflare.com/profile/api-tokens",
            "\n",
        )
        LinkSubCommand._progress_callback(
            "💡 Account name defaults to 'default' if not specified", "\n"
        )

    @typer_app.command(
        name="status",
        help="Show link status for all services.",
        no_args_is_help=False,
    )
    @staticmethod
    def link_status() -> None:
        """Show link status for all services."""
        LinkSubCommand._progress_callback(
            "[bold blue]� Link Status[/bold blue]\n", "\n"
        )

        # Check GitHub
        token_manager = GitHubTokenManager(secret_store=KeyringSecretStore())
        stored_token = token_manager.get_token()

        if stored_token:
            config = GitHubOAuthConfig()
            device_flow = GitHubDeviceFlow(
                client_id=config.client_id,
                scopes=config.scopes,
                progress_callback=LinkSubCommand._progress_callback,
            )
            if device_flow.test_token(stored_token):
                LinkSubCommand._progress_callback(
                    "GitHub: [green]✅ Linked[/green]", "\n"
                )
            else:
                LinkSubCommand._progress_callback(
                    "GitHub: [red]❌ Invalid (token expired or revoked)[/red]", "\n"
                )
        else:
            LinkSubCommand._progress_callback(
                "GitHub: [yellow]⚠️  Not linked[/yellow]", "\n"
            )

        # Check Hetzner (default project)
        api_key_manager = HetznerApiKeyManager(
            project_name="default", secret_store=KeyringSecretStore()
        )
        stored_api_key = api_key_manager.get_api_key()

        if stored_api_key:
            LinkSubCommand._progress_callback(
                "Hetzner (default): [green]✅ Linked[/green]", "\n"
            )
        else:
            LinkSubCommand._progress_callback(
                "Hetzner (default): [yellow]⚠️  Not linked[/yellow]", "\n"
            )

        LinkSubCommand._progress_callback(
            "\n💡 Use 'er link github' to authenticate with GitHub", "\n"
        )
        LinkSubCommand._progress_callback(
            "💡 Use 'er link hetzner <PROJECT_NAME>' to link a Hetzner project", "\n"
        )
        LinkSubCommand._progress_callback(
            "💡 Use 'er link cloudflare <ACCOUNT_NAME>' to link a Cloudflare account",
            "\n",
        )
