"""Main CLI application for Bitbucket Code Reviewer."""

import asyncio
import sys
from typing import Optional

import click

from . import __version__
from .core.config import get_available_models, get_config_manager
from .core.logger import logger
from .core.models import LLMProvider
from .reviewer.review_orchestrator import create_review_orchestrator


@click.group()
@click.version_option(version=__version__, prog_name="bb-review")
def cli():
    """🤖 AI-powered Bitbucket Code Reviewer.

    Perform comprehensive code reviews using advanced AI models.
    Supports OpenAI GPT-4, Grok, and other LLM providers.
    """
    pass


@cli.command()
def version():
    """Show the version and exit."""
    logger.info(f"bb-review version {__version__}")


@cli.command()
@click.argument("repository")
@click.option("--pr", "-p", type=int, help="Pull request ID to review")
@click.option("--branch", "-b", help="Branch name to review (requires --base-branch)")
@click.option(
    "--base-branch", help="Base branch to compare against (required with --branch)"
)
@click.option(
    "--llm",
    "-l",
    type=click.Choice([p.value for p in LLMProvider], case_sensitive=False),
    default="openai",
    help="LLM provider to use for code review (default: openai)",
)
@click.option(
    "--model",
    "-m",
    default="gpt-5",
    help="Specific model to use (default: gpt-5)",
)
@click.option(
    "--token", "-t", help="Bitbucket API token (can also set BITBUCKET_TOKEN env var)"
)
@click.option(
    "--username",
    help="Bitbucket username (can also set BB_AUTH_USERNAME env var)",
)
@click.option(
    "--submit", "-s", is_flag=True, help="Submit review comments to Bitbucket PR"
)
@click.option(
    "--working-dir",
    "-wd",
    default=".",
    help="Working directory for local repository operations (default: current directory)",
)
@click.option(
    "--max-iterations",
    "-mi",
    type=int,
    default=None,
    help="Maximum number of tool iterations (default: 500)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def review(
    repository: str,
    pr: Optional[int],
    branch: Optional[str],
    base_branch: Optional[str],
    llm: str,
    model: str,
    token: Optional[str],
    username: Optional[str],
    submit: bool,
    working_dir: str,
    max_iterations: Optional[int],
    verbose: bool,
):
    """🤖 Perform AI-powered code review on Bitbucket repositories.

    This command analyzes code changes using advanced AI models to provide
    comprehensive code review feedback including:

    • Code quality assessment
    • Security vulnerability detection
    • Performance optimization suggestions
    • Best practice recommendations

    The AI reviewer can examine files, understand context, and provide
    actionable feedback with specific code suggestions.

    Examples:
        # Review a pull request (uses defaults: openai/gpt-5, temperature 1.0)
        bb-review review myworkspace/myrepo --pr 123
        
        # Review with custom model
        bb-review review myworkspace/myrepo --pr 123 --llm xai --model grok-code-fast-1
        bb-review review myworkspace/myrepo --pr 123 --model gpt-4o --submit

        # Review a branch (coming soon)
        bb-review review myworkspace/myrepo --branch feature-branch --base-branch main
    """
    try:
        # Validate arguments
        if pr is None and branch is None:
            raise click.BadParameter("Either --pr or --branch must be specified")
        if pr is not None and branch is not None:
            raise click.BadParameter("Cannot specify both --pr and --branch")
        if branch is not None and base_branch is None:
            raise click.BadParameter("--base-branch is required when using --branch")
        if submit and branch is not None:
            raise click.BadParameter(
                "Cannot submit comments when reviewing branches (only PRs)"
            )

        # Temperature is hardcoded to 1.0 for optimal tool-calling reliability

        # Parse repository argument
        workspace, repo_slug = _parse_repository_argument(repository)

        logger.header("🤖 AI Code Review Starting")
        logger.key_value("Repository", f"{workspace}/{repo_slug}")

        if pr is not None:
            logger.key_value("Pull Request", f"#{pr}")
            review_type = "PR"
        else:
            logger.key_value("Branch", f"{branch} → {base_branch}")
            review_type = "Branch"

        logger.key_value("Review Type", review_type)
        logger.key_value("LLM Provider", llm)
        logger.key_value("Model", model)
        logger.key_value("Temperature", "1.0")

        # Create the review orchestrator
        if pr is not None:
            orchestrator = create_review_orchestrator(
                workspace=workspace,
                repo_slug=repo_slug,
                pr_id=pr,
                llm_provider=LLMProvider(llm),
                model_name=model,
                temperature=1.0,  # Hardcoded for optimal tool-calling reliability
                bitbucket_token=token,
                bitbucket_auth_username=username,
                working_directory=working_dir,
                max_iterations=max_iterations,
                verbose=verbose,
            )
        else:
            # For branch reviews, we'll need to extend the orchestrator
            # For now, raise an error as this feature is not fully implemented yet
            raise click.BadParameter(
                "Branch review is not yet implemented. Please use --pr for now."
            )

        # Run the review
        logger.progress_start("Analyzing code changes")
        review_result = asyncio.run(orchestrator.run_review())
        logger.progress_end("Analysis completed")

        # Log results summary
        issue_count = len(review_result.changes)
        if issue_count > 0:
            logger.info(f"Found {issue_count} issue(s) to comment on")
        else:
            logger.info("No issues found")

        # Submit comments if requested
        if submit:
            logger.step("Submitting review comments to Bitbucket")
            asyncio.run(orchestrator.submit_review_comments(review_result))
            logger.success("Review comments submitted successfully")

        # Format elapsed time
        elapsed = getattr(orchestrator, '_review_elapsed_time', None)
        if elapsed:
            if elapsed < 60:
                time_str = f"{elapsed:.1f}s"
            else:
                mins = int(elapsed // 60)
                secs = int(elapsed % 60)
                time_str = f"{mins}m {secs}s"
            logger.success(f"🎉 Code review completed in {time_str}")
        else:
            logger.success("🎉 Code review completed successfully")

    except Exception as e:
        logger.error(f"Error during code review: {str(e)}")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option("--show", is_flag=True, help="Show current configuration")
@click.option("--token", help="Set Bitbucket access token")
@click.option("--workspace", help="Set default workspace")
@click.option("--clear", is_flag=True, help="Clear all configuration")
@click.option("--delete", help="Delete a specific configuration key")
def config(
    show: bool,
    token: Optional[str],
    workspace: Optional[str],
    clear: bool,
    delete: Optional[str],
):
    """Manage configuration settings."""
    config_manager = get_config_manager()

    if clear:
        config_manager.clear()
        logger.success("Configuration cleared")
        return

    if delete:
        config_manager.delete(delete)
        logger.success(f"Configuration key '{delete}' deleted")
        return

    if show:
        logger.header("Current Configuration")
        config = config_manager.get_all()

        if not config:
            logger.info("No configuration saved (using environment variables)")
            logger.info("Use --token or --workspace to save configuration")
        else:
            for key, value in config.items():
                if "token" in key.lower():
                    masked_value = (
                        "****" + str(value)[-4:] if len(str(value)) > 4 else "****"
                    )
                    logger.key_value(key, masked_value)
                else:
                    logger.key_value(key, str(value))

        # Show environment variables too
        import os

        env_vars = {}
        env_vars_list = [
            "BITBUCKET_TOKEN",
            "BITBUCKET_WORKSPACE",
            "OPENAI_API_KEY",
            "GROK_API_KEY",
        ]
        for env_var in env_vars_list:
            if env_var in os.environ:
                if "token" in env_var.lower() or "key" in env_var.lower():
                    env_value = os.environ[env_var]
                    env_vars[env_var] = (
                        "****" + env_value[-4:] if len(env_value) > 4 else "****"
                    )
                else:
                    env_vars[env_var] = os.environ[env_var]

        if env_vars:
            logger.header("Environment Variables")
            for key, value in env_vars.items():
                logger.key_value(key, value)

    elif token:
        config_manager.set("bitbucket_token", token)
        logger.success("Bitbucket access token saved to config file")
    elif workspace:
        config_manager.set("default_workspace", workspace)
        logger.success(f"Default workspace set to: {workspace}")
    else:
        logger.info("Configuration Commands:")
        logger.info("  --show              Show current configuration")
        logger.info("  --token TOKEN       Set Bitbucket access token")
        logger.info("  --workspace WS      Set default workspace")
        logger.info("  --clear             Clear all saved configuration")
        logger.info("  --delete KEY        Delete a specific config key")
        logger.info("")
        logger.info("Configuration is saved to ~/.bb-review-config.json")


@cli.command()
def models():
    """Show available LLM models for each provider."""
    logger.header("🤖 Available LLM Models")

    for provider in LLMProvider:
        available_models = get_available_models(provider)
        logger.key_value(f"{provider.value.upper()}", ", ".join(available_models))

    logger.info("")
    logger.info("💡 Tips:")
    logger.info("• For best code review quality: Use gpt-4o or grok-code-fast-1 (xAI)")
    logger.info("• For faster/cheaper reviews: Use gpt-4o-mini or gpt-3.5-turbo")
    logger.info("• Configure with: bb-review config --token YOUR_API_KEY")


def _parse_repository_argument(repository: str) -> tuple[str, str]:
    """Parse repository argument in format 'workspace/repo-slug'.

    Args:
        repository: Repository string

    Returns:
        Tuple of (workspace, repo_slug)

    Raises:
        ValueError: If repository format is invalid
    """
    parts = repository.split("/")
    if len(parts) != 2:
        raise click.BadParameter(
            f"Repository must be in format 'workspace/repo-slug', got: {repository}"
        )

    workspace, repo_slug = parts
    if not workspace or not repo_slug:
        raise click.BadParameter("Workspace and repository slug cannot be empty")

    return workspace, repo_slug


if __name__ == "__main__":
    cli()
