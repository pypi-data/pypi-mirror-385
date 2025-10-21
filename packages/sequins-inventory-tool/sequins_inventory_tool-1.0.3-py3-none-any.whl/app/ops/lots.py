"""CLI for interacting with the lots database."""

from datetime import timezone
import logging
from typing import Optional

from dateutil.parser import parse
from dateutil.tz import tzlocal
import requests
from rich.table import Table
import typer
from typing_extensions import Annotated

from app.console import get_console
from app.constants import API_KEY_NAME, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.datetime_utils import format_utc_to_local
from app.utils.response_utils import handle_response

logger = logging.getLogger(__name__)

lots_app = typer.Typer()


def _format_date_utc_or_none(date_str: str | None) -> str:
    """Format a date string or return an empty string if None."""
    if date_str:
        return format_utc_to_local(date_str)
    return ''


def _set_date_to_end_of_day(date_str: str) -> str:
    """Set the date to the end of the day for the given YYYY-MM-DD string.

    Args:
        date_str (str): A date string in the format 'YYYY-MM-DD'.

    Returns:
        str: The ISO 8601 formatted string representing the date at 23:59:59
        UTC.

    Raises:
        ValueError: If the input string does not match the 'YYYY-MM-DD' format.
    """
    logger.debug('Parsing date string: %s', date_str)
    date_dt = parse(date_str).replace(hour=23, minute=59, second=59)
    if date_dt.tzinfo is None:
        date_dt = date_dt.replace(tzinfo=tzlocal())
    return date_dt.astimezone(timezone.utc).isoformat()


def create_table(verbose: bool, archived: bool = False) -> Table:
    """Create a table for displaying lot information."""
    table = Table(title='Lots')
    table.add_column('Lot Key', justify='left')
    table.add_column('Part Number', justify='left')
    table.add_column('Lot Number')
    table.add_column('Constituent Lot Numbers')
    table.add_column('Manufactured At', justify='left')
    table.add_column('Expires At', justify='left')
    if archived:
        table.add_column('Archived', justify='left')
    if verbose:
        table.add_column('Created By')
        table.add_column('Created At')
        table.add_column('Updated By')
        table.add_column('Updated At')
    return table


def add_lot_to_table(
    table: Table, lot: dict, archived=False, verbose=False
) -> None:
    """Add a lot dictionary to the table."""
    row_data = [
        lot['_id'],
        lot['part_number'],
        str(lot['lot_number']).upper(),
        ','.join(
            sorted([lot['lot_number'] for lot in lot['constituent_lots']])
        ).upper(),
        _format_date_utc_or_none(lot.get('manufactured_at_utc')),
        _format_date_utc_or_none(lot.get('expires_at_utc')),
    ]
    if archived:
        row_data.append(str(lot.get('archived', False)))
    if verbose:
        row_data.extend(
            [
                lot.get('created_by') or 'N/A',
                format_utc_to_local(lot['created_at_utc']),
                lot.get('updated_by') or 'N/A',
                format_utc_to_local(lot['updated_at_utc']),
            ]
        )
    table.add_row(*row_data)


def parse_constituent_lots(values: list[str]) -> list[dict[str, str]]:
    if not values:
        return []
    result = []
    for pair in values:
        try:
            description, lot_number = pair.split('=', 1)
            result.append(
                {
                    'description': description.strip(),
                    'lot_number': lot_number.strip(),
                }
            )
        except ValueError:
            raise typer.BadParameter(
                f'Invalid format for lot: "{pair}". Expected format is '
                '"description=lot_number".'
            )
    return result


@lots_app.command(name='display')
@require_api_endpoint_and_key()
def display_lots(
    ctx: typer.Context,
    verbose: Annotated[
        bool, typer.Option('--verbose', '-v', help='Display verbose output')
    ] = False,
    archived: Annotated[
        bool,
        typer.Option(
            '--archived',
            help='Include archived lots in the display',
        ),
    ] = False,
):
    """Display a table of lots in the database."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']
    console = get_console()

    parts_url = f'{api_endpoint}{ApiPaths.PARTS}'
    headers = {API_KEY_NAME: api_key}

    filters = {
        'archived': archived,
    }

    filters_query = {k: v for k, v in filters.items() if v is not None}
    page = 1
    size = 50
    lots = []
    while True:
        result = requests.get(
            parts_url,
            headers=headers,
            params={'page': page, 'size': size} | filters_query,
        )
        handle_response(result)
        data = result.json()
        items = data.get('items', [])
        lots.extend(items)
        if len(items) < size:
            break
        page += 1

    if not lots:
        console.print('No lots found.')
        raise typer.Exit()

    table = create_table(verbose=verbose, archived=archived)
    for lot in lots:
        add_lot_to_table(table, lot, archived=archived, verbose=verbose)

    console.print(table)


@lots_app.command(name='create')
@require_api_endpoint_and_key()
def create_lot(
    ctx: typer.Context,
    part_number: Annotated[str, typer.Option(..., help='Part number')],
    constituent_lots: Annotated[
        list[str],
        typer.Option(
            ..., help='Key=value pair of the constituents of this lot.'
        ),
    ],
    manufactured_at: Annotated[
        str,
        typer.Option(..., help='Manufacturing date in YYYY-MM-DD format'),
    ],
    expires_at: Annotated[
        Optional[str],
        typer.Option(help='Expiration date in YYYY-MM-DD format (optional)'),
    ] = None,
    force: Annotated[
        bool,
        typer.Option('--force', help='Force creation without confirmation.'),
    ] = False,
):
    """Create a lot in the database."""
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    console = get_console()

    if not part_number:
        console.print("Missing option '--part-number'")
        raise typer.Exit(code=2)

    if not manufactured_at:
        console.print("Missing option '--manufactured-at'")
        raise typer.Exit(code=2)

    parts_url = f'{api_endpoint}{ApiPaths.PARTS}'
    headers = {API_KEY_NAME: api_key}

    data = {
        'part_number': part_number,
        'constituent_lots': parse_constituent_lots(constituent_lots),
    }

    try:
        manufactured_at_utc = _set_date_to_end_of_day(manufactured_at)
        data['manufactured_at_utc'] = manufactured_at_utc
    except ValueError as e:
        console.print(f'Invalid manufacturing date format: {e}')
        raise typer.Exit(code=1)

    if expires_at:
        try:
            expires_at_utc = _set_date_to_end_of_day(expires_at)
            data['expires_at_utc'] = expires_at_utc
        except ValueError as e:
            console.print(f'Invalid expiration date format: {e}')
            raise typer.Exit(code=1)

    if not force:
        console.print('About to create a new lot with the following details:')
        table = Table()
        table.add_column('Part Number', justify='left')
        table.add_column('Constituent Lot Numbers', justify='left')
        table.add_column('Manufactured At', justify='left')
        table.add_column('Expires At', justify='left')

        table.add_row(
            # pyrefly: ignore  # bad-argument-type
            data['part_number'],
            ', '.join(
                [
                    # Validate lot structure to avoid index errors
                    '='.join(
                        [
                            str(lot.get('description', 'N/A')),
                            str(lot.get('lot_number', 'N/A')).upper(),
                        ]
                    )
                    for lot in data.get('constituent_lots', [])
                    if isinstance(lot, dict)
                ]
            ),
            format_utc_to_local(data['manufactured_at_utc']),
            format_utc_to_local(str(data['expires_at_utc']))
            if data.get('expires_at_utc')
            else 'N/A',
        )

        console.print(table)
        confirm = typer.confirm('Do you want to continue?')
        if not confirm:
            console.print('Lot creation cancelled.')
            raise typer.Exit(code=1)

    result = requests.post(parts_url, headers=headers, json=data)
    handle_response(result)
    lot = result.json()

    console.log('Lot created successfully.')

    table = create_table(verbose=True, archived=True)
    add_lot_to_table(table, lot, archived=True, verbose=True)
    console.print(table)


@lots_app.command(name='count')
@require_api_endpoint_and_key()
def count_lots(
    ctx: typer.Context,
    part_number: Annotated[
        Optional[str], typer.Option(help='Part number to filter by')
    ] = None,
    location: Annotated[
        Optional[str], typer.Option(help='Location to filter by')
    ] = None,
):
    """Count the number of lots in the database."""
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    parts_url = f'{api_endpoint}{ApiPaths.PARTS}count'
    headers = {API_KEY_NAME: api_key}

    filter_params = {
        k: v
        for k, v in {'part_number': part_number, 'location': location}.items()
        if v is not None
    }

    result = requests.get(parts_url, headers=headers, params=filter_params)
    handle_response(result)
    data = result.json()

    table = Table(title='counts')
    table.add_column('Part Number', justify='left')
    table.add_column('Location')
    table.add_column('Available')
    table.add_column('Reserved')

    for item in data:
        part_number = item.get('part_number', '')
        for country, status_counts in item['count'].items():
            available = str(status_counts.get('Available', '0'))
            reserved = str(status_counts.get('Reserved', '0'))
            table.add_row(part_number, country, available, reserved)

    console = get_console()
    console.print(table)


@lots_app.command(name='update')
@require_api_endpoint_and_key()
def update_lot(
    ctx: typer.Context,
    lot_key: Annotated[str, typer.Argument(help='Lot key to update')],
    expires_at: Annotated[
        Optional[str],
        typer.Option(help='Expiration date in YYYY-MM-DD format (optional)'),
    ] = None,
    archived: Annotated[
        Optional[bool],
        typer.Option(
            '--archived',
            help='Mark the lot as archived',
        ),
    ] = None,
):
    """Update a lot in the database."""
    api_endpoint: str = ctx.obj['api_endpoint']
    api_key: str = ctx.obj['api_key']

    url = f'{api_endpoint}{ApiPaths.PARTS}{lot_key}'
    headers = {API_KEY_NAME: api_key}

    console = get_console()
    if not expires_at and archived is None:
        console.print('No fields to update.')
        raise typer.Exit(code=1)

    payload: dict[str, str | bool | list[str]] = {}

    if expires_at:
        try:
            payload['expires_at_utc'] = _set_date_to_end_of_day(expires_at)
        except ValueError:
            console.print(f'Invalid expiration date: {expires_at}')
            raise typer.Exit(code=1)

    if archived is not None:
        payload['archived'] = archived

    result = requests.patch(url, headers=headers, json=payload)
    handle_response(result)

    console.log('Lot updated successfully')
    lot = result.json()

    table = create_table(verbose=True, archived=True)
    add_lot_to_table(table, lot, verbose=True, archived=True)
    console.print(table)
