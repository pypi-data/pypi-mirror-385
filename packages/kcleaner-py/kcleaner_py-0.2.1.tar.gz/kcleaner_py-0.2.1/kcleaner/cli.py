import os
import sys
import argparse
from pathlib import Path
from .core.styles import SmartStyles as st
from .core.config import ConfigManager
from .utils.file_utils import FileSystemHandler


def parse_args():
    parser = argparse.ArgumentParser(
        description="Delete files by pattern matching (e.g., *~ or .*~) with user confirmation."
    )
    parser.add_argument(
        "--pattern", "-p", action="append", help="Pattern to match files (e.g., '*~')"
    )
    parser.add_argument(
        "--path",
        "-d",
        action="append",
        type=str,
        help="Directory to search in",
    )
    parser.add_argument(
        "--no-recursive", action="store_true", help="Disable recursive search"
    )
    parser.add_argument(
        "--empty-dirs",
        action="store_true",
        help="Scan empty directories/folders fordeletion ",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only display matched files without deleting",
    )

    return parser.parse_args()


class CliHandler:
    def __init__(self):
        self.manager = ConfigManager()
        self.config = self.manager._config_to_dict()

        self._fh = FileSystemHandler(self.config["ignore"])
        self.args = parse_args()

        # Resolve CLI over config
        self.paths = self.args.path or self.config.get("search_paths")
        self.patterns = self.args.pattern or self.config.get("patterns")
        self.recursive = (
            not self.args.no_recursive
            if self.args.pattern or self.args.path
            else self.config.get("recursive", True)
        )

    def run(self):
        print(f"{st.INFO} Using search paths: {self.paths}")
        print(f"{st.INFO} Using patterns: {self.patterns}")
        print(f"{st.INFO} Recursive: {self.recursive}")

        if self.args.empty_dirs:
            print(f"{st.INFO} Target: {st.EPH}empty_dirs{st.RESET}")
            self.dir_handler()
        else:
            self.file_handler()

    def file_handler(self):
        try:
            candidates = self._fh.find_files(self.paths, self.patterns, self.recursive)

            if not candidates:
                print(f"{st.OK} No matching files found.")
                return

            if self.args.dry_run:
                print(f"\n{st.INFO} Dry run mode. Files matched:")
                for f in candidates:
                    print(f"  {f}")
                return

            to_delete = FileSystemHandler.confirm_deletion(candidates)

            if not to_delete:
                print(f"{st.ERR} No files selected for deletion.")
                return

            confirm = (
                input(
                    f"\n{st.WARN} Confirm deletion of {len(to_delete)} files? Type 'yes' to proceed: "
                )
                .strip()
                .lower()
            )
            if confirm == "yes":
                FileSystemHandler.delete_files(to_delete)
            else:
                print(f"{st.ERR} Deletion aborted.")
        except KeyboardInterrupt:
            sys.exit("\nQuit")
        except Exception as e:
            print(f"{st.ERR}{e}{st.RESET}")

    def dir_handler(self):
        try:
            candidates = self._fh.find_directories(
                self.paths, self.patterns, self.recursive
            )

            if not candidates:
                print(f"{st.OK} No matching dir found.")
                return

            if self.args.dry_run:
                print(f"\n{st.INFO} Dry run mode. Directories matched:")
                for d in candidates:
                    print(f"  {d}")
                return

            to_delete = FileSystemHandler.confirm_deletion(candidates)

            if not to_delete:
                print(f"{st.ERR} No dirs selected for deletion.")
                return

            confirm = (
                input(
                    f"\n{st.WARN} Confirm deletion of {len(to_delete)} dirs? Type 'yes' to proceed: "
                )
                .strip()
                .lower()
            )
            if confirm == "yes":
                FileSystemHandler.delete_folders(to_delete)
            else:
                print(f"{st.ERR} Deletion aborted.")
        except KeyboardInterrupt:
            sys.exit("\nQuit")
        except Exception as e:
            print(f"{st.ERR}{e}{st.RESET}")

        def _entry_(self):
            self.run()


if __name__ == "__main__":
    runner = CliHandler().run()
