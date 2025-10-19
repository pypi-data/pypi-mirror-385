# kcleaner

**kcleaner** is a secure command-line tool designed to identify and delete [KATE](https://kate-editor.org/) backup files such as:

- `*.~`
- `.*~`

It provides:
- Safe preview of deletable files
- Interactive confirmation with deselection options
- Persistent configuration file
- Default scan in the current directory

## Installation
```bash
pip install kcleaner-py
```

```bash
git clone https://github.com/skye-cyber/kcleaner.git
pip install .
```

Or, if you prefer PEP 517:
```bash
pip install . --use-pep517
```

## Usage
```bash
kcleaner
```

- with cmda **rgs
```bash
# Use saved config
kcleaner

# Custom pattern (no config needed)
kcleaner --pattern '*~' --pattern '.*~'

# Search a specific folder
kcleaner -d src/ -d docs/

# Disable recursion
kcleaner --no-recursive

# Dry run only
kcleaner --dry-run
```

- Use command-line arguments to override default config:
```bash
kcleaner --pattern '*~' --dry-run
```

## Configuration
On first run, kcleaner creates a .kcleaner_config.json file in the same directory. You can edit it to change:

- Search pattern (e.g., `.*~`, `*~`)

- Default behavior

## License
This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
  See the LICENSE file for more details. See the [LICENSE](LICENSE) file for details.
