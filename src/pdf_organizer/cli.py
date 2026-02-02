"""Click CLI entry point for pdf-organizer."""

from pathlib import Path

import click

from pdf_organizer.renamer import rename_files, write_csv_log


@click.command()
@click.argument(
    "folder",
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview renames without actually renaming files.",
)
@click.option(
    "--output-csv",
    default="rename_log.csv",
    type=click.Path(path_type=Path),
    help="Path for the CSV rename log.",
)
def main(folder: Path, dry_run: bool, output_csv: Path) -> None:
    """Scan FOLDER for PDFs, classify them, and rename intelligently."""
    if dry_run:
        click.secho("=== DRY RUN (no files will be renamed) ===", fg="yellow")

    results = rename_files(folder, dry_run=dry_run)

    renamed = 0
    skipped = 0
    errors = 0

    for r in results:
        status = r["status"]
        original = r["original_name"]
        new = r["new_name"]

        if status == "renamed":
            label = "RENAME" if not dry_run else "WOULD RENAME"
            click.secho(f"  {label}: {original} -> {new}", fg="green")
            renamed += 1
        elif status == "skipped":
            click.secho(f"  SKIP: {original}", fg="yellow")
            skipped += 1
        else:
            click.secho(f"  ERROR: {original}", fg="red")
            errors += 1

    click.echo()
    click.secho(
        f"Summary: {renamed} renamed, {skipped} skipped, {errors} errors",
        bold=True,
    )

    if not dry_run:
        write_csv_log(results, output_csv)
        click.echo(f"Log written to {output_csv}")
