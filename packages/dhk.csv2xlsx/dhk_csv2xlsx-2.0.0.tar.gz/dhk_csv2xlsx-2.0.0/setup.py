#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'dhk.csv2xlsx',
        version = '2.0.0',
        description = 'Read a CSV file and write an XLSX file with optional formatting.',
        long_description = 'dhk.csv2xlsx\n============\n\n[![GitHub](https://img.shields.io/badge/github-python--csv2xlsx-blue?logo=github)](https://github.com/DavidKiesel/python-csv2xlsx)\n\n[![Latest Version](https://img.shields.io/pypi/v/dhk.csv2xlsx?logo=pypi)](https://pypi.org/project/dhk.csv2xlsx/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/dhk.csv2xlsx?logo=pypi)](https://pypi.org/project/dhk.csv2xlsx/)\n\n[![Downloads Per Day](https://img.shields.io/pypi/dd/dhk.csv2xlsx?logo=pypi)](https://pypi.org/project/dhk.csv2xlsx/)\n[![Downloads Per Week](https://img.shields.io/pypi/dw/dhk.csv2xlsx?logo=pypi)](https://pypi.org/project/dhk.csv2xlsx/)\n[![Downloads Per Month](https://img.shields.io/pypi/dm/dhk.csv2xlsx?logo=pypi)](https://pypi.org/project/dhk.csv2xlsx/)\n\n# Introduction\n\n`dhk.csv2xlsx` is a Python command-line tool for reading a CSV file and writing an XLSX file with optional formatting.\nIt leverages the Python standard library [`csv`](https://docs.python.org/3/library/csv.html) module and the [`XlsxWriter`](https://pypi.org/project/XlsxWriter/) package.\n\n# Simple Installation\n\nA pedestrian command for installing the package is given below.\nAlternatively, for a more rewarding installation exercise, see section [Recommended Installation](#recommended-installation).\n\n```bash\npip install dhk.csv2xlsx\n```\n\n# Usage\n\n```console\n$ csv2xlsx --help\nusage: csv2xlsx [-h] [--force] [--output OUTPUT_FILE]\n                [--settings-file SETTINGS_FILE] [--verbose]\n                [--generate-settings-file | --transform-csv]\n                [CSV_FILE]\n\nRead a CSV file and write an XLSX file.\n\nThe program exposes much of the formatting functionality of the XlsxWriter\npackages Workbook class through the optional SETTINGS_FILE.  For details about\nthe Workbook class, see https://xlsxwriter.readthedocs.io/workbook.html.  For\ndetails about the Worksheet class, see\nhttps://xlsxwriter.readthedocs.io/worksheet.html.  For details about the Format\nclass, see https://xlsxwriter.readthedocs.io/format.html.\n\npositional arguments:\n  CSV_FILE              CSV file\n\noptions:\n  -h, --help            show this help message and exit\n  --force, -f           force; suppress prompts\n  --output, -o OUTPUT_FILE\n                        output file; default: CSV_FILE - .csv + .xlsx\n  --settings-file, -s SETTINGS_FILE\n                        settings file\n  --verbose, -v         verbose\n  --generate-settings-file, -g\n                        generate settings file; file defaults to\n                        sample.settings.json\n  --transform-csv, -t   transform CSV to XLSX; default True\n\nexamples:\n\n    csv2xlsx \\\n        --generate-settings-file\n\n    csv2xlsx \\\n        CSV_FILE\n\n    csv2xlsx \\\n        --settings-file SETTINGS_FILE \\\n        CSV_FILE\n\n    csv2xlsx \\\n        --settings-file SETTINGS_FILE \\\n        --output OUTPUT \\\n        CSV_FILE\n\nexecution details:\n\nThe Workbook class instance attribute `options` is set to `{\'constant_memory\':\nTrue}` merged with the SETTINGS_FILE `workbook_options` dictionary.\n\nThe Workbook class instance attribute `formats[0]` stores a default Format\nobject.  The SETTINGS_FILE `workbook_format` dictionary can be used to set the\nattributes of this default Format object.  The available dictionary keywords\ncorrespond to the list of properties in the table at\nhttps://xlsxwriter.readthedocs.io/format.html#format-methods-and-format-properties.\n\nThe Workbook class instance method `add_format()` is used to add Format class\ninstances to the Workbook class instance.  The program iterates over each of\nthe SETTINGS_FILE `cell_format_settings` dictionary key-value pairs.  The\nSETTINGS_FILE `workbook_format` dictionary is merged with the value of the\n`cell_format_settings` key-value pair, and this merged value is the argument to\n`add_format()`.  The key-value pair formed by the key from the\n`cell_format_settings` key-value pair and the `add_format()` return value is\nstored in a `cell_formats` dictionary for later use when setting Worksheet\nclass instance columns and rows.\n\nThe Worksheet class instance method `set_column()` is used to set the width,\ncell format, and options for specified columns.  The program iterates over each\nof the SETTINGS_FILE `column_settings` list elements.  For each element, the\n`first_col` and `last_col` arguments to `set_column()` can be specified in\nabsolute terms via a `columns` key-value pair with the string value specified\nby ordinal number (`\'1\'`, `\'1:2\'`, etc.) or by `A1` style notation (`\'A\'`,\n`\'A:B\'`).  Alternatively, if the `columns` key-value pair is not present, then\n`first_col` is simply the next column, and `last_col` is either the same as\n`first_col` or is set based on a `span` key-value pair.  The `width` argument\nto `set_column()` is set to the value of the `width` key-value pair, defaulting\nto 10 if not specified.  The `cell_format` argument to `set_column()` is set\nbased on the value of the `cell_format` key-value pair.  This value must\ncorrespond to the key of one of the SETTINGS_FILE `cell_format_settings`\nkey-value pairs.  If a `cell_format` key-value pair is not provided, then the\nargument defaults to the Workbook class instance attribute `formats[0]`.  The\n`options` argument to `set_column()` is set to the value of the `options`\nkey-pair.  The value of the `data_type` key-pair is stored for each column for\nlater use when parsing CSV data.\n\nThe Worksheet class instance method `set_row()` is used to set the cell format\nfor specified rows.  The program iterates over each of the SETTINGS_FILE\n`row_settings` list elements.  For each element, `first_row` and `last_row` can\nbe specified in absolute terms via a `rows` key-value pair with the string\nvalue specified by ordinal number (`\'1\'`, `\'1:2\'`, etc.).  Alternatively, if\nthe `rows` key-value pair is not present, then `first_row` is simply the next\ncolumn, and `last_row` is either the same as `first_row` or is set based on a\n`span` key-value pair.  For each `row` in the sequence determined by\n`first_row` and `last_row`, `set_row()` is called with `row` as the first\npositional argument and the argument `cell_format` set based on the value of\nthe `cell_format` key-value pair.  This value must correspond to the key of one\nof the SETTINGS_FILE `cell_format_settings` key-value pairs.  If a\n`cell_format` key-value pair is not provided, then the argument defaults to\nthe Workbook class instance attribute `formats[0]`.  The value of the\n`data_type` key-pair is stored for each row for later use when parsing CSV\ndata.\n\nEach row of the CSV file is read.  The value of each column of the row is\nhandled.  If there was a `data_type` specified in the SETTINGS_FILE for the\nrow, then that is used.  Otherwise, an attempt is made to get a `data_type`\nthat was specified in the SETTINGS_FILE for the column.  Valid values for\n`data_type` are: `decimal`, `bool`, `date`, `datetime`, `formula`, and\n`string`.  If `data_type` was not specified or an exception occurs when\nattempting to parse the CSV value in terms of the given `data_type`, then the\nCSV value is written as a `string`.\n\nThe Worksheet class instance method `autofilter` is called with arguments based\non the `autofilter` object in the SETTINGS_FILE `workbook_settings` dictionary.\nBoth row-column notation (`(first_row, first_col, last_row, last_col)`) and\n`A1` style notation (`\'A1:D11\'`) are supported.  If row-column notation is\nused, then a negative number is replaced with the maximum row or column\navailable in the data.\n\nThe Worksheet class instance method `freeze_panes` is called with arguments\nbased on the `freeze_panes` object in the SETTINGS_FILE `workbook_settings`\ndictionary.  Both row-column notation (`(row, col[, top_row, left_col])`) and\n`A1` style notation (`\'A2\'`) are supported.\n```\n\n# Recommended Installation\n\n[`pyenv`](https://github.com/pyenv/pyenv) is a tool for installing multiple Python environments and controlling which one is in effect in the current shell.\n\n[`pipx`](https://github.com/pipxproject/pipx) is a tool for installing and running Python applications in isolated environments.\n\nAssuming these have been installed correctly...\n\n## Install Python Under `pyenv`\n\nThe version of Python under which this package was last developed and tested is stored in [`.python-version`](https://raw.githubusercontent.com/DavidKiesel/python-csv2xlsx/refs/heads/main/.python-version).\n\nTo capture this Python version to a shell variable, execute the commands below.\n`PYTHON_VERSION` should be set to something like `3.13.3`.\n\n```bash\nPYTHON_VERSION="$(\n    wget \\\n        -O - \\\n        https://raw.githubusercontent.com/DavidKiesel/python-csv2xlsx/refs/heads/main/.python-version\n)"\n\necho "$PYTHON_VERSION"\n```\n\nTo determine if the `.python-version` version of Python has already been installed under `pyenv`, execute the command below.\nIf it has not been installed, then a warning message will be displayed.\n\n```bash\nPYENV_VERSION="$PYTHON_VERSION" \\\npython --version\n```\n\nIf it has already been installed, then proceed to section [Install Package Using `pipx`](#install-package-using-pipx).\n\nOtherwise, to install the given version of Python under `pyenv`, execute the command below.\n\n```bash\npyenv install "$PYTHON_VERSION"\n```\n\nIf the install was successful, then proceed to section [Install Package Using `pipx`](#install-package-using-pipx).\n\nIf instead there is a warning that the definition was not found, then you will need to upgrade `pyenv`.\n\nIf `pyenv` was installed through a package manager, then consider upgrading it through that package manager.\nFor example, if `pyenv` was installed through `brew`, then execute the commands below.\n\n```bash\nbrew update\n\nbrew upgrade pyenv\n```\n\nAlternatively, you could attempt to upgrade `pyenv` through the command below.\n\n```bash\npyenv update\n```\n\nOnce `pyenv` has been upgraded, to install the given version of Python under `pyenv`, execute the command below.\n\n```bash\npyenv install "$PYTHON_VERSION"\n```\n\n## Install Package Using `pipx`\n\nOnly proceed from here if the instructions in section [Install Python Under `pyenv`](#install-python-under-pyenv) have been completed successfully.\n\nAt this point, shell variable `PYTHON_VERSION` should already contain the appropriate Python version.\nIf not, execute the commands below.\n\n```bash\nPYTHON_VERSION="$(\n    wget \\\n        -O - \\\n        https://raw.githubusercontent.com/DavidKiesel/python-csv2xlsx/refs/heads/main/.python-version\n)"\n\necho "$PYTHON_VERSION"\n```\n\nTo install the package hosted at PyPI using `pipx`, execute the command below.\n\n```bash\npipx \\\n    install \\\n    --python "$(PYENV_VERSION="$PYTHON_VERSION" pyenv which python3)" \\\n    dhk.csv2xlsx\n```\n',
        long_description_content_type = 'text/markdown',
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Programming Language :: Python :: 3.13'
        ],
        keywords = '',

        author = 'David Harris Kiesel',
        author_email = 'david.sw@suddenthought.net',
        maintainer = 'David Harris Kiesel',
        maintainer_email = 'david.sw@suddenthought.net',

        license = 'MIT',

        url = 'https://github.com/DavidKiesel/python-csv2xlsx',
        project_urls = {
            'Homepage': 'https://github.com/DavidKiesel/python-csv2xlsx'
        },

        scripts = ['scripts/csv2xlsx'],
        packages = ['dhk.csv2xlsx'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = ['XlsxWriter==3.2.3'],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '>=3.9',
        obsoletes = [],
    )
