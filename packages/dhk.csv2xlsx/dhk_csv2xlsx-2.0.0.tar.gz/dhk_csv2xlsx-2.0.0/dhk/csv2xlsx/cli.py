#   -*- coding: utf-8 -*-

##############################################################################
# copyrights and license
#
# Copyright (c) 2025 David Harris Kiesel
#
# Licensed under the MIT License. See LICENSE in the project root for license
# information.
##############################################################################

import argparse
import json
import logging
import os.path
import sys

from dhk.csv2xlsx import csv2xlsx


sample_settings = \
    '''{
    "workbook_options": {
    },
    "workbook_format": {
        "font_size": 12,
        "valign": "top"
    },
    "worksheet_settings": {
        "freeze_panes": [
            1,
            0
        ],
        "autofilter": [
            0,
            0,
            -1,
            -1
        ]
    },
    "cell_format_settings": {
        "header": {
            "valign": "bottom",
            "bold": true,
            "text_wrap": true
        },
        "date": {
            "num_format": "yyyy-mm-dd"
        },
        "datetime": {
            "num_format": "yyyy-mm-dd HH:MM:SS.000"
        },
        "num0": {
            "num_format": "0"
        },
        "numc0": {
            "num_format": "#,##0"
        },
        "num2": {
            "num_format": "0.00"
        },
        "numc2": {
            "num_format": "#,##0.00"
        },
        "dollar0": {
            "num_format": "$#,##0"
        },
        "dollar2": {
            "num_format": "$#,##0.00"
        },
        "textwrap": {
            "text_wrap": true
        }
    },
    "column_settings": [
        {
            "span": 2,
            "width": 40,
            "cell_format": "textwrap"
        },
        {
            "width": 40
        },
        {
            "data_type": "bool",
            "width": 10
        },
        {
            "data_type": "date",
            "width": 20,
            "cell_format": "date"
        },
        {
            "data_type": "datetime",
            "width": 40,
            "cell_format": "datetime"
        },
        {
            "data_type": "decimal",
            "width": 20,
            "cell_format": "num0",
            "options": {
                "hidden": true
            }
        },
        {
            "data_type": "decimal",
            "width": 20,
            "cell_format": "dollar2"
        }
    ],
    "row_settings": [
        {
            "data_type": "string",
            "cell_format": "header"
        }
    ]
}'''


def get_parser() -> argparse.ArgumentParser:
    'Get parser.'

    parser = \
        argparse.ArgumentParser(
            prog='csv2xlsx',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='''Read a CSV file and write an XLSX file.

The program exposes much of the formatting functionality of the XlsxWriter
packages Workbook class through the optional SETTINGS_FILE.  For details about
the Workbook class, see https://xlsxwriter.readthedocs.io/workbook.html.  For
details about the Worksheet class, see
https://xlsxwriter.readthedocs.io/worksheet.html.  For details about the Format
class, see https://xlsxwriter.readthedocs.io/format.html.
''',
            add_help=True,
            epilog="""
examples:

    %(prog)s \\
        --generate-settings-file

    %(prog)s \\
        CSV_FILE

    %(prog)s \\
        --settings-file SETTINGS_FILE \\
        CSV_FILE

    %(prog)s \\
        --settings-file SETTINGS_FILE \\
        --output OUTPUT \\
        CSV_FILE

execution details:

The Workbook class instance attribute `options` is set to `{'constant_memory':
True}` merged with the SETTINGS_FILE `workbook_options` dictionary.

The Workbook class instance attribute `formats[0]` stores a default Format
object.  The SETTINGS_FILE `workbook_format` dictionary can be used to set the
attributes of this default Format object.  The available dictionary keywords
correspond to the list of properties in the table at
https://xlsxwriter.readthedocs.io/format.html#format-methods-and-format-properties.

The Workbook class instance method `add_format()` is used to add Format class
instances to the Workbook class instance.  The program iterates over each of
the SETTINGS_FILE `cell_format_settings` dictionary key-value pairs.  The
SETTINGS_FILE `workbook_format` dictionary is merged with the value of the
`cell_format_settings` key-value pair, and this merged value is the argument to
`add_format()`.  The key-value pair formed by the key from the
`cell_format_settings` key-value pair and the `add_format()` return value is
stored in a `cell_formats` dictionary for later use when setting Worksheet
class instance columns and rows.

The Worksheet class instance method `set_column()` is used to set the width,
cell format, and options for specified columns.  The program iterates over each
of the SETTINGS_FILE `column_settings` list elements.  For each element, the
`first_col` and `last_col` arguments to `set_column()` can be specified in
absolute terms via a `columns` key-value pair with the string value specified
by ordinal number (`'1'`, `'1:2'`, etc.) or by `A1` style notation (`'A'`,
`'A:B'`).  Alternatively, if the `columns` key-value pair is not present, then
`first_col` is simply the next column, and `last_col` is either the same as
`first_col` or is set based on a `span` key-value pair.  The `width` argument
to `set_column()` is set to the value of the `width` key-value pair, defaulting
to 10 if not specified.  The `cell_format` argument to `set_column()` is set
based on the value of the `cell_format` key-value pair.  This value must
correspond to the key of one of the SETTINGS_FILE `cell_format_settings`
key-value pairs.  If a `cell_format` key-value pair is not provided, then the
argument defaults to the Workbook class instance attribute `formats[0]`.  The
`options` argument to `set_column()` is set to the value of the `options`
key-pair.  The value of the `data_type` key-pair is stored for each column for
later use when parsing CSV data.

The Worksheet class instance method `set_row()` is used to set the cell format
for specified rows.  The program iterates over each of the SETTINGS_FILE
`row_settings` list elements.  For each element, `first_row` and `last_row` can
be specified in absolute terms via a `rows` key-value pair with the string
value specified by ordinal number (`'1'`, `'1:2'`, etc.).  Alternatively, if
the `rows` key-value pair is not present, then `first_row` is simply the next
column, and `last_row` is either the same as `first_row` or is set based on a
`span` key-value pair.  For each `row` in the sequence determined by
`first_row` and `last_row`, `set_row()` is called with `row` as the first
positional argument and the argument `cell_format` set based on the value of
the `cell_format` key-value pair.  This value must correspond to the key of one
of the SETTINGS_FILE `cell_format_settings` key-value pairs.  If a
`cell_format` key-value pair is not provided, then the argument defaults to
the Workbook class instance attribute `formats[0]`.  The value of the
`data_type` key-pair is stored for each row for later use when parsing CSV
data.

Each row of the CSV file is read.  The value of each column of the row is
handled.  If there was a `data_type` specified in the SETTINGS_FILE for the
row, then that is used.  Otherwise, an attempt is made to get a `data_type`
that was specified in the SETTINGS_FILE for the column.  Valid values for
`data_type` are: `decimal`, `bool`, `date`, `datetime`, `formula`, and
`string`.  If `data_type` was not specified or an exception occurs when
attempting to parse the CSV value in terms of the given `data_type`, then the
CSV value is written as a `string`.

The Worksheet class instance method `autofilter` is called with arguments based
on the `autofilter` object in the SETTINGS_FILE `workbook_settings` dictionary.
Both row-column notation (`(first_row, first_col, last_row, last_col)`) and
`A1` style notation (`'A1:D11'`) are supported.  If row-column notation is
used, then a negative number is replaced with the maximum row or column
available in the data.

The Worksheet class instance method `freeze_panes` is called with arguments
based on the `freeze_panes` object in the SETTINGS_FILE `workbook_settings`
dictionary.  Both row-column notation (`(row, col[, top_row, left_col])`) and
`A1` style notation (`'A2'`) are supported.
"""
        )

    parser.add_argument(
        '--force',
        '-f',
        action='store_true',
        help='force; suppress prompts'
    )

    parser.add_argument(
        '--output',
        '-o',
        dest='output_file',
        default=None,
        help='output file; default: CSV_FILE - .csv + .xlsx'
    )

    parser.add_argument(
        '--settings-file',
        '-s',
        metavar='SETTINGS_FILE',
        default=None,
        help='settings file'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='count',
        default=0,
        help='verbose'
    )

    parser.add_argument(
        'csv_fd',
        metavar='CSV_FILE',
        type=argparse.FileType('r'),
        nargs='?',
        help='CSV file'
    )

    mutually_exclusive_group = \
        parser.add_mutually_exclusive_group()

    mutually_exclusive_group.add_argument(
        '--generate-settings-file',
        '-g',
        action='store_true',
        help='generate settings file; file defaults to sample.settings.json'
    )

    mutually_exclusive_group.add_argument(
        '--transform-csv',
        '-t',
        action='store_true',
        help='transform CSV to XLSX; default True'
    )

    return parser


def configure_logging(
    level: int
) -> None:
    'Configure logging.'

    logging.basicConfig(
        level=level
    )


def main(
    args: argparse.Namespace
) -> None:
    '``main`` entry point.'

    logging_levels = \
        (
            logging.WARNING,
            logging.INFO,
            logging.DEBUG,
        )

    configure_logging(
        logging_levels[
            min(
                len(logging_levels) - 1,
                args.verbose
            )
        ]
    )

    if args.generate_settings_file:
        for incompatible_option in (
            args.output_file,
        ):
            if incompatible_option is not None:
                print(
                    'Incompatible option.'
                )

                sys.exit()

        if args.settings_file is None:
            args.settings_file = 'sample.settings.json'

        if not args.force:
            while os.path.exists(args.settings_file):
                response = \
                    input(
                        "Settings file '{0}' exists.  Continue? (y/n) ".format(
                            args.settings_file
                        )
                    )

                if response == 'y':
                    break
                elif response == 'n':
                    sys.exit()

        with open(
            args.settings_file,
            'w',
            encoding='utf-8'
        ) as settings_fd:
            print(
                sample_settings,
                file=settings_fd
            )
    else:
        if args.settings_file is not None:
            with open(
                args.settings_file,
                'r'
            ) as settings_fd:
                workbook_settings = \
                    json.load(settings_fd)
        else:
            workbook_settings = {}

        workbook_path = args.output_file

        if workbook_path is None:
            root, ext = \
                os.path.splitext(
                    args.csv_fd.name
                )

            workbook_path = \
                root + '.xlsx'

        if not args.force:
            if os.path.exists(workbook_path):
                while True:
                    response = \
                        input(
                            """Output file '{0}' exists.\
  Continue? (y/n) """.format(
                                workbook_path
                            )
                        )

                    if response == 'y':
                        break
                    elif response == 'n':
                        sys.exit()

        csv2xlsx.transform(
            args.csv_fd,
            workbook_path,
            workbook_settings=workbook_settings
        )

        args.csv_fd.close()
