"""Command-line interface for tenzir-changelog."""

from __future__ import annotations

import json
import sys
import textwrap
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Optional

import click
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .config import Config, default_config_path, load_config, save_config
from .entries import (
    ENTRY_TYPES,
    Entry,
    entry_directory,
    iter_entries,
    sort_entries_desc,
    write_entry,
)
from .releases import (
    ReleaseManifest,
    build_entry_release_index,
    collect_release_entries,
    iter_release_manifests,
    load_release_entry,
    release_directory,
    unused_entries,
    used_entry_ids,
    write_release_manifest,
)
from .validate import run_validation
from .utils import console, extract_excerpt, guess_git_remote, slugify

INFO_PREFIX = "\033[94;1mi\033[0m "
ENTRY_TYPE_STYLES = {
    "feature": "green",
    "bugfix": "red",
    "change": "blue",
}
ENTRY_TYPE_EMOJIS = {
    "feature": "🌟",
    "bugfix": "🐞",
    "change": "🔧",
}
ENTRY_TYPE_CHOICES = (
    ("feature", "1"),
    ("bugfix", "2"),
    ("change", "3"),
)
ENTRY_TYPE_SHORTCUTS = {
    "feature": "feature",
    "f": "feature",
    "1": "feature",
    "bugfix": "bugfix",
    "b": "bugfix",
    "2": "bugfix",
    "change": "change",
    "c": "change",
    "3": "change",
}
DEFAULT_ENTRY_TYPE = ENTRY_TYPES[0]
TYPE_SECTION_TITLES = {
    "feature": "Features",
    "change": "Changes",
    "bugfix": "Bug fixes",
}
ENTRY_EXPORT_ORDER = ("feature", "change", "bugfix")


@dataclass
class CLIContext:
    """Shared command context."""

    project_root: Path
    config_path: Path
    _config: Optional[Config] = None

    def ensure_config(self) -> Config:
        if self._config is None:
            if not self.config_path.exists():
                project_root = self.config_path.parent
                message = "\n".join(
                    [
                        f"{INFO_PREFIX}no tenzir-changelog project detected at {project_root}.",
                        f"{INFO_PREFIX}run from your project root or provide --root.",
                    ]
                )
                click.echo(message, err=True)
                raise click.exceptions.Exit(1)
            self._config = load_config(self.config_path)
        return self._config

    def reset_config(self, config: Config) -> None:
        self._config = config


def _resolve_project_root(value: Path) -> Path:
    return value.resolve()


def _normalize_optional(value: Optional[str]) -> Optional[str]:
    """Convert Click sentinel values to None."""

    if value is None:
        return None
    value_class = value.__class__.__name__
    if value_class == "Sentinel":
        return None
    return value


def _prompt_project(existing: Optional[str], project_root: Path) -> str:
    """Prompt for the primary project slug."""
    default_value = existing or slugify(project_root.name)
    project = click.prompt(
        "Project name (used in entry metadata)",
        default=default_value,
        show_default=True,
    ).strip()
    if not project:
        raise click.ClickException("Project name cannot be empty.")
    return slugify(project)


def _mask_comment_block(text: str) -> str:
    """Strip comment lines (starting with '#') from editor input."""
    lines = []
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        lines.append(line.rstrip())
    return "\n".join(lines).strip()


@click.group(invoke_without_command=True, context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--root",
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    default=Path("."),
    help="Project root containing config and changelog files.",
)
@click.option(
    "--config",
    type=click.Path(path_type=Path, dir_okay=False),
    help="Path to an explicit changelog config YAML file.",
)
@click.pass_context
def cli(ctx: click.Context, root: Path, config: Optional[Path]) -> None:
    """Manage changelog entries and release manifests."""
    root = _resolve_project_root(root)
    config_path = config.resolve() if config else default_config_path(root)
    ctx.obj = CLIContext(project_root=root, config_path=config_path)

    if ctx.invoked_subcommand is None:
        ctx.invoke(show)


@cli.command("bootstrap")
@click.option("--update", is_flag=True, help="Update an existing configuration.")
@click.pass_obj
def bootstrap_cmd(ctx: CLIContext, update: bool) -> None:
    """Create or update the changelog project."""
    repo_root = ctx.project_root
    config_path = ctx.config_path
    default_repo_config = default_config_path(repo_root)

    # When operating from a repository root, place the project under ./changelog/.
    if not config_path.exists() and config_path == default_repo_config:
        workspace_root = repo_root / "changelog"
        config_path = default_config_path(workspace_root)
        ctx.config_path = config_path
    else:
        workspace_root = config_path.parent

    ctx.project_root = workspace_root

    existing_config: Optional[Config] = None
    if config_path.exists():
        if not update:
            raise click.ClickException(
                f"Config already exists at {config_path}. Re-run with --update to modify it."
            )
        existing_config = load_config(config_path)

    project_name_default = existing_config.name if existing_config else repo_root.name
    project_description_default = existing_config.description if existing_config else ""
    repo_default = existing_config.repository if existing_config else None
    repo_guess = guess_git_remote(repo_root)
    if repo_default is None and repo_guess:
        repo_default = repo_guess

    project_name = click.prompt("Project name", default=project_name_default, show_default=True)
    project_description = click.prompt(
        "Project description", default=project_description_default, show_default=False
    )
    repository = (
        click.prompt(
            "GitHub repository (owner/name)",
            default=repo_default or "",
            show_default=bool(repo_default),
        ).strip()
        or None
    )

    slug_base = repo_root if repo_root != workspace_root else workspace_root
    project = _prompt_project(existing_config.id if existing_config else None, slug_base)

    config = Config(
        id=project,
        name=project_name,
        description=project_description,
        repository=repository,
        intro_template=existing_config.intro_template if existing_config else None,
        assets_dir=existing_config.assets_dir if existing_config else None,
    )

    save_config(config, config_path)
    ctx.reset_config(config)

    # Ensure directories exist.
    entry_directory(workspace_root).mkdir(parents=True, exist_ok=True)
    release_directory(workspace_root).mkdir(parents=True, exist_ok=True)

    console.print(
        Panel.fit(
            f"[bold green]Changelog project ready[/bold green]\nConfig: {config_path}",
            title="Bootstrap",
        )
    )


def _filter_entries_by_project(
    entries: Iterable[Entry], projects: set[str], default_project: str
) -> list[Entry]:
    if not projects:
        return list(entries)
    filtered: list[Entry] = []
    for entry in entries:
        entry_project = entry.project or default_project
        if entry_project and entry_project in projects:
            filtered.append(entry)
    return filtered


def _entries_before_or_equal_version(project_root: Path, version: str) -> set[str]:
    releases = list(iter_release_manifests(project_root))
    releases.sort(key=lambda manifest: (manifest.created, manifest.version))
    seen: set[str] = set()
    for manifest in releases:
        seen.update(manifest.entries)
        if manifest.version == version:
            return seen
    raise click.ClickException(f"Unknown release version '{version}'")


def _render_project_header(config: Config) -> None:
    legend = "  ".join(
        f"{ENTRY_TYPE_EMOJIS.get(entry_type, '•')} {entry_type}"
        for entry_type in ENTRY_EXPORT_ORDER
    )
    header = Text.assemble(
        ("Name: ", "bold"),
        config.name or "—",
        ("\nID: ", "bold"),
        config.id or "—",
        ("\nRepository: ", "bold"),
        config.repository or "—",
        ("\nTypes: ", "bold"),
        legend or "—",
    )
    console.print(Panel.fit(header, title="Project"))


def _render_entries(
    entries: Iterable[Entry],
    release_index: dict[str, list[str]],
    config: Config,
    show_banner: bool = False,
) -> None:
    if show_banner:
        _render_project_header(config)

    table = Table(show_lines=False, expand=True)
    table.add_column("Date", style="yellow", no_wrap=True)
    table.add_column("Version", style="cyan", no_wrap=True, max_width=12)
    table.add_column("Title", style="bold", overflow="fold", max_width=44)
    table.add_column("Type", style="magenta", no_wrap=True, justify="center")
    table.add_column("PR", style="yellow", no_wrap=True)
    table.add_column("Authors", style="blue", overflow="fold", max_width=20)
    table.add_column("ID", style="cyan", no_wrap=True, max_width=28)

    has_rows = False
    sorted_entries = sort_entries_desc(list(entries))

    for entry in sorted_entries:
        metadata = entry.metadata
        created_display = entry.created_at.isoformat() if entry.created_at else "—"
        type_value = metadata.get("type", "change")
        versions = release_index.get(entry.entry_id)
        version_display = ", ".join(versions) if versions else "—"
        type_emoji = ENTRY_TYPE_EMOJIS.get(type_value, "•")
        type_display = Text(type_emoji, style=ENTRY_TYPE_STYLES.get(type_value, ""))
        table.add_row(
            created_display,
            version_display,
            metadata.get("title", "Untitled"),
            type_display,
            str(metadata.get("pr") or "—"),
            ", ".join(metadata.get("authors") or []) or "—",
            Text(entry.entry_id, style="cyan", overflow="ellipsis", no_wrap=True),
        )
        has_rows = True

    if has_rows:
        console.print(table)
    else:
        console.print("[yellow]No entries found.[/yellow]")


def _render_release(
    manifest: ReleaseManifest,
    project_root: Path,
    *,
    project_id: str,
) -> None:
    console.rule(f"Release {manifest.version}")
    header = Text.assemble(
        ("Title: ", "bold"),
        manifest.title or manifest.version or "—",
        ("\nDescription: ", "bold"),
        manifest.description or "—",
        ("\nCreated: ", "bold"),
        manifest.created.isoformat(),
        ("\nProject: ", "bold"),
        project_id or "—",
    )
    console.print(header)

    if manifest.intro:
        console.print(
            Panel(
                manifest.intro,
                title="Introduction",
                subtitle="Markdown",
                expand=False,
            )
        )

    all_entries = {entry.entry_id: entry for entry in iter_entries(project_root)}
    table = Table(title="Included Entries")
    table.add_column("Order")
    table.add_column("Entry ID", style="cyan")
    table.add_column("Title")
    table.add_column("Type", style="magenta")
    for index, entry_id in enumerate(manifest.entries, 1):
        entry = all_entries.get(entry_id)
        if entry is None:
            entry = load_release_entry(project_root, manifest, entry_id)
        if entry:
            table.add_row(
                str(index),
                entry_id,
                entry.metadata.get("title", "Untitled"),
                entry.metadata.get("type", "change"),
            )
        else:
            table.add_row(str(index), entry_id, "[red]Missing entry[/red]", "—")
    console.print(table)


@cli.command("show")
@click.option("--project", "project_filter", multiple=True, help="Filter by project key.")
@click.option(
    "--release",
    "release_version",
    default=None,
    help="Show a specific release.",
)
@click.option(
    "--since",
    "since_version",
    help="Only show entries newer than the specified release version.",
)
@click.option("--banner", is_flag=True, help="Show a project banner above entries.")
@click.pass_obj
def show(
    ctx: CLIContext,
    project_filter: tuple[str, ...],
    release_version: Optional[str],
    since_version: Optional[str],
    banner: bool,
) -> None:
    """Display the current changelog or a specific release."""
    config = ctx.ensure_config()
    project_root = ctx.project_root
    projects = set(project_filter)

    release_version = _normalize_optional(release_version)
    since_version = _normalize_optional(since_version)

    if release_version:
        manifests = [
            m for m in iter_release_manifests(project_root) if m.version == release_version
        ]
        if not manifests:
            raise click.ClickException(f"Release '{release_version}' not found.")
        manifest = manifests[0]
        _render_release(manifest, project_root, project_id=config.id)
        return

    entries = list(iter_entries(project_root))
    entry_map = {entry.entry_id: entry for entry in entries}
    released_entries = collect_release_entries(project_root)
    for entry_id, entry in released_entries.items():
        if entry_id not in entry_map:
            entry_map[entry_id] = entry

    entries = list(entry_map.values())
    release_index = build_entry_release_index(project_root, project=config.id)
    if since_version:
        excluded = _entries_before_or_equal_version(project_root, since_version)
        entries = [entry for entry in entries if entry.entry_id not in excluded]

    entries = _filter_entries_by_project(entries, projects, config.id)
    _render_entries(entries, release_index, config, show_banner=banner)


def _prompt_entry_body(initial: str = "") -> str:
    edited = click.edit(
        textwrap.dedent(
            """\
            # Write the entry body below. Lines starting with '#' are ignored.
            # Save and close the editor to finish. Leave empty to skip.
            """
        )
        + ("\n" + initial if initial else "\n")
    )
    if edited is None:
        return ""
    return _mask_comment_block(edited)


def _prompt_text(label: str, **kwargs: Any) -> str:
    prompt_suffix = kwargs.pop("prompt_suffix", ": ")
    result = click.prompt(click.style(label, bold=True), prompt_suffix=prompt_suffix, **kwargs)
    return str(result)


def _prompt_optional(prompt: str, default: Optional[str] = None) -> Optional[str]:
    value = _prompt_text(
        prompt,
        default=default or "",
        show_default=bool(default),
    )
    return value.strip() or None


def _normalize_entry_type(value: str) -> Optional[str]:
    value = value.strip().lower()
    if not value:
        return DEFAULT_ENTRY_TYPE
    return ENTRY_TYPE_SHORTCUTS.get(value)


def _prompt_entry_type(default: str = DEFAULT_ENTRY_TYPE) -> str:
    prompt_text = Text("Type: ", style="bold")
    for idx, (name, key) in enumerate(ENTRY_TYPE_CHOICES):
        prompt_text.append(name)
        prompt_text.append(" [")
        prompt_text.append(key, style="bold cyan")
        prompt_text.append("]")
        if idx < len(ENTRY_TYPE_CHOICES) - 1:
            prompt_text.append(", ")
    console.print(prompt_text)

    while True:
        key = click.getchar()
        if key in {"\r", "\n"}:
            selection = default
            break
        normalized = _normalize_entry_type(key)
        if normalized:
            selection = normalized
            break
    console.print(Text(f"  {selection}", style=ENTRY_TYPE_STYLES.get(selection, "")))
    return selection


def _entry_to_dict(
    entry: Entry,
    config: Config,
    versions: list[str] | None = None,
    *,
    compact: bool = False,
) -> dict[str, object]:
    metadata = entry.metadata
    prs_value = metadata.get("prs")
    prs_list: list[int] = []
    if isinstance(prs_value, list):
        for pr in prs_value:
            try:
                prs_list.append(int(str(pr).strip()))
            except (TypeError, ValueError):
                continue
    else:
        pr_single = metadata.get("pr")
        if pr_single is not None:
            try:
                prs_list.append(int(str(pr_single).strip()))
            except (TypeError, ValueError):
                pass
    data = {
        "id": entry.entry_id,
        "title": metadata.get("title", "Untitled"),
        "type": metadata.get("type", "change"),
        "created": entry.created_at.isoformat() if entry.created_at else None,
        "project": entry.project or config.id,
        "pr": prs_list[0] if prs_list else None,
        "prs": prs_list,
        "authors": metadata.get("authors") or [],
        "versions": versions or [],
        "body": entry.body,
    }
    if compact:
        data["excerpt"] = extract_excerpt(entry.body)
    return data


def _join_with_conjunction(items: list[str]) -> str:
    items = [item for item in items if item]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _format_author_line(entry: Entry, config: Config) -> str:
    metadata = entry.metadata
    authors = metadata.get("authors") or []
    if isinstance(authors, str):
        authors = [authors]
    authors = [author.strip() for author in authors if author and author.strip()]

    author_links = [f"[{author}](https://github.com/{author})" for author in authors]
    author_text = _join_with_conjunction(author_links)

    prs_value = metadata.get("prs")
    prs: list[int] = []
    if isinstance(prs_value, list):
        for pr in prs_value:
            try:
                prs.append(int(str(pr).strip()))
            except (TypeError, ValueError):
                continue
    else:
        pr_single = metadata.get("pr")
        if pr_single is not None:
            try:
                prs.append(int(str(pr_single).strip()))
            except (TypeError, ValueError):
                pass

    repo = config.repository
    pr_links: list[str] = []
    for pr in prs:
        label = f"#{pr}"
        if repo:
            pr_links.append(f"[{label}](https://github.com/{repo}/pull/{pr})")
        else:
            pr_links.append(label)

    pr_text = _join_with_conjunction(pr_links)

    if not author_text and not pr_text:
        return ""

    parts = []
    if author_text:
        parts.append(f"By {author_text}")
    if pr_text:
        parts.append(f"in {pr_text}")
    return "*" + " ".join(parts) + ".*"


@cli.command("add")
@click.option("--title", help="Title for the changelog entry.")
@click.option(
    "--type",
    "entry_type",
    help="Entry type.",
)
@click.option(
    "--project",
    "project_override",
    help="Assign the entry to a project (must match the configured project).",
)
@click.option("--author", "authors", multiple=True, help="GitHub username of an author.")
@click.option(
    "--pr",
    "prs",
    multiple=True,
    type=str,
    help="Related pull request number (repeat for multiple).",
)
@click.option(
    "--description",
    help="Short body text for the entry (skips opening an editor).",
)
@click.pass_obj
def add(
    ctx: CLIContext,
    title: Optional[str],
    entry_type: Optional[str],
    project_override: Optional[str],
    authors: tuple[str, ...],
    prs: tuple[str, ...],
    description: Optional[str],
) -> None:
    """Create a new changelog entry."""
    config = ctx.ensure_config()
    project_root = ctx.project_root

    title = title or _prompt_text("Title")
    if entry_type:
        normalized_type = _normalize_entry_type(entry_type)
        if normalized_type is None:
            raise click.ClickException(
                f"Unknown entry type '{entry_type}'. Expected one of: {', '.join(ENTRY_TYPES)}"
            )
        entry_type = normalized_type
    else:
        entry_type = _prompt_entry_type()

    project_value = (project_override or "").strip() or config.id
    if project_value != config.id:
        raise click.ClickException(f"Unknown project '{project_value}'. Expected '{config.id}'.")

    if authors:
        authors_list = [author.strip() for author in authors if author.strip()]
    else:
        author_value = _prompt_optional("Authors (comma separated)", default="")
        authors_list = (
            [item.strip() for item in author_value.split(",") if item.strip()]
            if author_value
            else []
        )

    body = description or _prompt_entry_body()

    pr_numbers: list[int] = []
    for pr_value in prs:
        pr_value = pr_value.strip()
        if not pr_value:
            continue
        try:
            pr_numbers.append(int(pr_value))
        except ValueError as exc:
            raise click.ClickException(f"PR value '{pr_value}' must be numeric.") from exc

    metadata: dict[str, Any] = {
        "title": title,
        "type": entry_type,
        "project": project_value,
        "authors": authors_list or None,
    }
    if pr_numbers:
        if len(pr_numbers) == 1:
            metadata["pr"] = pr_numbers[0]
        else:
            metadata["prs"] = pr_numbers

    path = write_entry(project_root, metadata, body, default_project=config.id)
    console.print(f"[green]Entry created:[/green] {path.relative_to(project_root)}")


def _collect_unused_entries_for_release(project_root: Path, config: Config) -> list[Entry]:
    all_entries = list(iter_entries(project_root))
    used = used_entry_ids(project_root)
    unused = unused_entries(all_entries, used)
    filtered = [entry for entry in unused if entry.project is None or entry.project == config.id]
    return filtered


def _render_release_notes(entries: list[Entry], config: Config) -> str:
    """Render Markdown sections for the provided entries."""

    if not entries:
        return ""

    entries_by_type: dict[str, list[Entry]] = {}
    for entry in entries:
        entry_type = entry.metadata.get("type", DEFAULT_ENTRY_TYPE)
        entries_by_type.setdefault(entry_type, []).append(entry)

    lines: list[str] = []
    for type_key in ENTRY_EXPORT_ORDER:
        type_entries = entries_by_type.get(type_key) or []
        if not type_entries:
            continue
        section_title = TYPE_SECTION_TITLES.get(type_key, type_key.title())
        lines.append(f"## {section_title}")
        lines.append("")
        for entry in type_entries:
            title = entry.metadata.get("title", "Untitled")
            lines.append(f"### {title}")
            lines.append("")
            body = entry.body.strip()
            if body:
                lines.append(body)
                lines.append("")
            author_line = _format_author_line(entry, config)
            if author_line:
                lines.append(author_line)
                lines.append("")

    return "\n".join(lines).strip()


def _render_release_notes_compact(entries: list[Entry], config: Config) -> str:
    """Render compact Markdown bullet list for the provided entries."""

    if not entries:
        return ""

    entries_by_type: dict[str, list[Entry]] = {}
    for entry in entries:
        entry_type = entry.metadata.get("type", DEFAULT_ENTRY_TYPE)
        entries_by_type.setdefault(entry_type, []).append(entry)

    lines: list[str] = []
    for type_key in ENTRY_EXPORT_ORDER:
        type_entries = entries_by_type.get(type_key) or []
        if not type_entries:
            continue
        section_title = TYPE_SECTION_TITLES.get(type_key, type_key.title())
        lines.append(f"## {section_title}")
        lines.append("")
        for entry in type_entries:
            title = entry.metadata.get("title", "Untitled")
            excerpt = extract_excerpt(entry.body)
            bullet = f"- **{title}**"
            if excerpt:
                bullet = f"{bullet}: {excerpt}"
            lines.append(bullet)
        lines.append("")

    return "\n".join(lines).strip()


@cli.group("release")
def release() -> None:
    """Release management commands."""


@release.command("create")
@click.argument("version")
@click.option("--title", help="Display title for the release.")
@click.option("--description", default="", help="Short release description.")
@click.option(
    "--date",
    "release_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Release date (YYYY-MM-DD). Defaults to today.",
)
@click.option(
    "--intro-file",
    type=click.Path(path_type=Path, dir_okay=False),
    help="Markdown file containing introductory notes for the release.",
)
@click.option(
    "--compact/--no-compact",
    default=False,
    show_default=True,
    help="Render release notes in the compact format.",
)
@click.option(
    "--yes",
    "assume_yes",
    is_flag=True,
    help="Skip confirmation prompts and run non-interactively.",
)
@click.pass_obj
def release_create(
    ctx: CLIContext,
    version: str,
    title: Optional[str],
    description: str,
    release_date: Optional[datetime],
    intro_file: Optional[Path],
    compact: bool,
    assume_yes: bool,
) -> None:
    """Create a release manifest from unused entries."""
    config = ctx.ensure_config()
    project_root = ctx.project_root

    unused = _collect_unused_entries_for_release(project_root, config)
    if not unused:
        raise click.ClickException("No unused entries available for release creation.")

    version = version.strip()
    title = title or f"{config.name} {version}"
    release_dt = release_date.date() if release_date else date.today()

    custom_intro = ""
    if intro_file:
        custom_intro = intro_file.read_text(encoding="utf-8").strip()

    entries_sorted = sorted(unused, key=lambda entry: entry.metadata.get("title", ""))
    table = Table(title="Entries to Include")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Type")
    for entry in entries_sorted:
        table.add_row(
            entry.entry_id,
            entry.metadata.get("title", "Untitled"),
            entry.metadata.get("type", "change"),
        )
    console.print(table)

    if not assume_yes and not click.confirm(
        "Create release manifest with these entries?", default=True
    ):
        console.print("[yellow]Aborted release creation.[/yellow]")
        return

    manifest_intro = custom_intro.strip() if custom_intro else ""
    release_notes = (
        _render_release_notes_compact(entries_sorted, config)
        if compact
        else _render_release_notes(entries_sorted, config)
    )
    readme_parts: list[str] = []
    if description:
        readme_parts.append(description.strip())
    if manifest_intro:
        readme_parts.append(manifest_intro)
    if release_notes:
        readme_parts.append(release_notes)
    readme_content = "\n\n".join(part.strip() for part in readme_parts if part and part.strip())

    manifest = ReleaseManifest(
        version=version,
        created=release_dt,
        entries=[entry.entry_id for entry in entries_sorted],
        title=title or "",
        description=description,
        intro=manifest_intro or None,
    )

    path = write_release_manifest(project_root, manifest, readme_content)

    release_dir = path.parent
    release_entries_dir = release_dir / "entries"
    release_entries_dir.mkdir(parents=True, exist_ok=True)
    for entry in entries_sorted:
        source_path = entry.path
        destination_path = release_entries_dir / source_path.name
        if destination_path.exists():
            raise click.ClickException(
                f"Cannot move entry '{entry.entry_id}' because {destination_path} already exists."
            )
        source_path.rename(destination_path)

    console.print(f"[green]Release manifest written:[/green] {path.relative_to(project_root)}")
    relative_release_dir = release_entries_dir.relative_to(project_root)
    console.print(f"[green]Moved {len(entries_sorted)} entries to:[/green] {relative_release_dir}")


@cli.command("validate")
@click.pass_obj
def validate_cmd(ctx: CLIContext) -> None:
    """Validate entries and release manifests."""
    config = ctx.ensure_config()
    issues = run_validation(ctx.project_root, config)
    if not issues:
        console.print("[green]All changelog files look good![/green]")
        return

    for issue in issues:
        console.print(f"[red]{issue.severity.upper()}[/red] {issue.path}: {issue.message}")
    raise SystemExit(1)


def _export_markdown_release(
    manifest: Optional[ReleaseManifest],
    entries: list[Entry],
    config: Config,
    release_index: dict[str, list[str]],
) -> str:
    lines: list[str] = []
    if manifest:
        if manifest.description:
            lines.append(manifest.description.strip())
            lines.append("")
    else:
        lines.append("# Unreleased Changes")
        lines.append("")

    if not entries:
        lines.append("No changes found.")
        return "\n".join(lines).strip() + "\n"

    entries_by_type: dict[str, list[Entry]] = {}
    for entry in entries:
        entry_type = entry.metadata.get("type", DEFAULT_ENTRY_TYPE)
        entries_by_type.setdefault(entry_type, []).append(entry)

    for type_key in ENTRY_EXPORT_ORDER:
        type_entries = entries_by_type.get(type_key) or []
        if not type_entries:
            continue
        section_title = TYPE_SECTION_TITLES.get(type_key, type_key.title())
        lines.append(f"## {section_title}")
        lines.append("")
        for entry in type_entries:
            metadata = entry.metadata
            title = metadata.get("title", "Untitled")
            lines.append(f"### {title}")
            lines.append("")
            body = entry.body.strip()
            if body:
                lines.append(body)
                lines.append("")
            author_line = _format_author_line(entry, config)
            if author_line:
                lines.append(author_line)
                lines.append("")

    return "\n".join(lines).strip() + "\n"


def _export_markdown_compact(
    manifest: Optional[ReleaseManifest],
    entries: list[Entry],
    config: Config,
    release_index: dict[str, list[str]],
) -> str:
    lines: list[str] = []
    if manifest:
        if manifest.description:
            lines.append(manifest.description.strip())
            lines.append("")
    else:
        lines.append("# Unreleased Changes")
        lines.append("")

    if not entries:
        lines.append("No changes found.")
        return "\n".join(lines).strip() + "\n"

    entries_by_type: dict[str, list[Entry]] = {}
    for entry in entries:
        entry_type = entry.metadata.get("type", DEFAULT_ENTRY_TYPE)
        entries_by_type.setdefault(entry_type, []).append(entry)

    for type_key in ENTRY_EXPORT_ORDER:
        type_entries = entries_by_type.get(type_key) or []
        if not type_entries:
            continue
        section_title = TYPE_SECTION_TITLES.get(type_key, type_key.title())
        lines.append(f"## {section_title}")
        lines.append("")
        for entry in type_entries:
            title = entry.metadata.get("title", "Untitled")
            excerpt = extract_excerpt(entry.body)
            bullet = f"- **{title}**"
            if excerpt:
                bullet = f"{bullet}: {excerpt}"
            lines.append(bullet)
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def _export_json_payload(
    manifest: Optional[ReleaseManifest],
    entries: list[Entry],
    config: Config,
    release_index: dict[str, list[str]],
    *,
    compact: bool = False,
) -> dict[str, object]:
    data: dict[str, object] = {}
    if manifest:
        data.update(
            {
                "version": manifest.version,
                "title": manifest.title or manifest.version,
                "description": manifest.description or None,
                "project": config.id,
                "created": manifest.created.isoformat(),
            }
        )
    else:
        data.update(
            {
                "version": None,
                "title": None,
                "description": None,
                "project": config.id,
                "created": date.today().isoformat(),
            }
        )
    payload_entries = []
    for entry in entries:
        versions = list(release_index.get(entry.entry_id, []))
        if manifest and manifest.version and manifest.version not in versions:
            versions.append(manifest.version)
        payload_entries.append(_entry_to_dict(entry, config, versions, compact=compact))
    data["entries"] = payload_entries
    if compact:
        data["compact"] = True
    return data


@cli.command("export")
@click.option(
    "--format",
    "export_format",
    type=click.Choice(["markdown", "json"], case_sensitive=False),
    default="markdown",
    show_default=True,
    help="Output format",
)
@click.option(
    "--compact/--no-compact",
    default=False,
    show_default=True,
    help="Use compact layout for the exported content.",
)
@click.option("--release", "release_version", help="Release version to export.")
@click.pass_obj
def export_cmd(
    ctx: CLIContext,
    export_format: str,
    compact: bool,
    release_version: Optional[str],
) -> None:
    """Export changelog content as Markdown or JSON."""

    config = ctx.ensure_config()
    project_root = ctx.project_root

    release_version = _normalize_optional(release_version)

    entries = list(iter_entries(project_root))
    entry_map = {entry.entry_id: entry for entry in entries}
    release_index = build_entry_release_index(project_root, project=config.id)

    manifest: Optional[ReleaseManifest] = None
    export_entries: list[Entry]

    if release_version:
        manifests = [
            m for m in iter_release_manifests(project_root) if m.version == release_version
        ]
        if not manifests:
            raise click.ClickException(f"Release '{release_version}' not found.")
        manifest = manifests[0]
        missing_entries: list[str] = []
        export_entries = []
        for entry_id in manifest.entries:
            entry = entry_map.get(entry_id)
            if entry is None:
                entry = load_release_entry(project_root, manifest, entry_id)
            if entry is None:
                missing_entries.append(entry_id)
                continue
            entry_map[entry_id] = entry
            export_entries.append(entry)
        if missing_entries:
            missing_list = ", ".join(sorted(missing_entries))
            raise click.ClickException(
                f"Release '{manifest.version}' is missing entry files for: {missing_list}"
            )
    else:
        export_entries = _collect_unused_entries_for_release(project_root, config)

    export_entries = sort_entries_desc(export_entries)

    export_format = export_format.lower()
    if export_format == "markdown":
        if compact:
            content = _export_markdown_compact(manifest, export_entries, config, release_index)
        else:
            content = _export_markdown_release(manifest, export_entries, config, release_index)
        click.echo(content, nl=False)
    else:
        payload = _export_json_payload(
            manifest,
            export_entries,
            config,
            release_index,
            compact=compact,
        )
        click.echo(json.dumps(payload, indent=2))


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point for console_scripts."""
    argv = argv if argv is not None else sys.argv[1:]
    try:
        cli.main(args=list(argv), prog_name="tenzir-changelog", standalone_mode=False)
    except click.ClickException as exc:
        exc.show(file=sys.stderr)
        exit_code = getattr(exc, "exit_code", 1)
        return exit_code if isinstance(exit_code, int) else 1
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 0
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
