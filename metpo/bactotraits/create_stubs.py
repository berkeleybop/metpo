"""Create ROBOT template stubs from multiple input files.

This module reads multiple ROBOT template files and creates a single "stubs" file
containing only the ID, label, and TYPE for each METPO entity.
"""

import csv

import click


@click.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True, path_type=str),
    required=True,
    help="Output file for the generated stubs"
)
@click.argument(
    "input_files",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=str)
)
def main(output, input_files):
    """
    Create ROBOT template stubs from multiple INPUT_FILES.

    Reads multiple ROBOT template files and creates a single "stubs" file
    containing only the ID, label, and TYPE for each METPO entity.

    Example:
        uv run create-stubs --output stubs.tsv template1.tsv template2.tsv
    """
    stubs = set()

    for file_path in input_files:
        try:
            with open(file_path, newline="") as infile:
                reader = csv.reader(infile, delimiter="\t")

                # Find the ROBOT header row (the one with 'LABEL')
                file_header = []
                while not file_header or "LABEL" not in [h.strip() for h in file_header]:
                    file_header = next(reader)

                # Strip headers before finding index
                stripped_header = [h.strip() for h in file_header]
                id_index = stripped_header.index("ID")
                label_index = stripped_header.index("LABEL")
                type_index = stripped_header.index("TYPE")

                for row in reader:
                    if row and len(row) > max(id_index, label_index, type_index) and row[id_index].startswith("METPO:"):
                        stubs.add((row[id_index], row[label_index], row[type_index]))
        except FileNotFoundError:
            click.echo(f"Warning: Input file not found: {file_path}", err=True)
        except StopIteration:
            click.echo(f"Warning: Could not find a valid ROBOT template header in {file_path}", err=True)
        except ValueError:
            click.echo(f"Warning: Could not find required columns (ID, LABEL, TYPE) in {file_header} in {file_path}", err=True)

    with open(output, "w", newline="") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(("ID", "label", "TYPE"))  # Human-readable header
        writer.writerow(("ID", "LABEL", "TYPE"))  # ROBOT template header
        # Sort for consistent output
        sorted_stubs = sorted(stubs)
        writer.writerows(sorted_stubs)

    click.echo(f"Created stubs file with {len(sorted_stubs)} entities: {output}")


if __name__ == "__main__":
    main()
