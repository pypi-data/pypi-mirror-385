#!/usr/bin/python3
"""
Copyright (c) 2024 Penterep Security s.r.o.

ptkibana is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ptkibana is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ptkibana.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import importlib
import os
import sys
import threading
from http import HTTPStatus
from io import StringIO
from types import ModuleType

from ptlibs.threads import ptthreads

sys.path.append(__file__.rsplit("/", 1)[0])

from _version import __version__
from ptlibs import ptjsonlib, ptprinthelper, ptmisclib, ptnethelper
from ptlibs.ptprinthelper import ptprint
from ptlibs.http.http_client import HttpClient
from helpers.helpers import Helpers
import requests
from modules.is_kibana import IsKibana

from helpers._thread_local_stdout import ThreadLocalStdout


class PtKibana:
    def __init__(self, args):
        self.ptjsonlib = ptjsonlib.PtJsonLib()
        self.args = args
        self.http_client = HttpClient(args=self.args, ptjsonlib=self.ptjsonlib)
        self.helpers = Helpers(args=self.args, ptjsonlib=self.ptjsonlib, http_client=self.http_client)
        self._lock = threading.Lock()
        self.ptthreads = ptthreads.PtThreads()

        # Activate ThreadLocalStdout stdout proxy
        self.thread_local_stdout = ThreadLocalStdout(sys.stdout)


    def run(self) -> None:
        """Main method"""

        self._fetch_initial_response()

        tests = self.args.tests or _get_all_available_modules()

        if "is_kibana" in tests:
            tests.remove("is_kibana")

        self._check_if_target_runs_kibana()

        if "es_proxy" in tests:
            tests.remove("es_proxy")
            self.ptthreads.threads(["es_proxy"], self.run_single_module, self.args.threads)

        self.thread_local_stdout.activate()

        self.ptthreads.threads(tests, self.run_single_module, self.args.threads)

        self.ptjsonlib.set_status("finished")
        ptprint(self.ptjsonlib.get_result_json(), "", self.args.json)


    def _check_if_target_runs_kibana(self) -> None:
        """
        Executes the IS_KIBANA pre-check to determine if the target is running Kibana.

        This method:
        - Instantiates the `_IS_KIBANA` module
        - Calls its `run()` method
        - If the module determines that Kibana is NOT running,
        it calls `ptjsonlib.end_error()` internally and terminates the program.

        Notes:
            The `_IS_KIBANA` module is responsible for handling the error state
            and ending execution if the target does not appear to run Kibana.
        """
        IsKibana(
            args=self.args,
            ptjsonlib=self.ptjsonlib,
            helpers=self.helpers,
            http_client=self.http_client,
            base_response=self.base_response
        ).run()
        ptprint(" ", "TEXT", not self.args.json)


    def _try_https(self) -> bool:
        if "https://" not in self.args.url:
            self.args.url = f"https://{self.args.url[7:]}"

        ptprint(f"Trying to connect with HTTPS at: {self.args.url}", "ADDITIONS",
                self.args.verbose, indent=4, colortext=True)

        try:
            self.base_response = self.http_client.send_request(url=self.args.url, method="GET", headers=self.args.headers, allow_redirects=True)
        except requests.exceptions.RequestException as error_msg:
            ptprint(f"Error trying to connect with HTTPS: {error_msg}.", "ADDITIONS",
                    self.args.verbose, indent=4, colortext=True)
            self.ptjsonlib.end_error(f"Error retrieving initial responses:", details=error_msg,
                                     condition=self.args.json)

        return self.base_response.status_code == HTTPStatus.OK


    def _fetch_initial_response(self) -> None:
        """
        Sends initial HTTP requests to the requested URL. Follows redirects
        If a non-200 status code is returned, the script exits early.
        """

        try:
            # Send request to user specified page via <args.url>
            self.base_response = self.http_client.send_request(url=self.args.url, method="GET", headers=self.args.headers, allow_redirects=True)

            if self.base_response.status_code != 200 and not self._try_https():
                self.ptjsonlib.end_error(f"Webpage returns status code: {self.base_response.status_code}", self.args.json)

        except requests.exceptions.RequestException as error_msg:
            ptprint(f"Error retrieving initial response: {error_msg}.", "ADDITIONS",
                    self.args.verbose, indent=4, colortext=True)
            if not self._try_https():
                self.ptjsonlib.end_error(f"Error retrieving initial responses:", details=error_msg, condition=self.args.json)


    def run_single_module(self, module_name: str) -> None:
        """
        Safely loads and executes a specified module's `run()` function.

        The method locates the module file in the "modules" directory, imports it dynamically,
        and executes its `run()` method with provided arguments and a shared `ptjsonlib` object.
        It also redirects stdout/stderr to a thread-local buffer for isolated output capture.

        If the module or its `run()` method is missing, or if an error occurs during execution,
        it logs appropriate messages to the user.

        Args:
            module_name (str): The name of the module (without `.py` extension) to execute.
        """
        try:
            with self._lock:
                module = _import_module_from_path(module_name)

            if hasattr(module, "run") and callable(module.run):
                buffer = StringIO()
                self.thread_local_stdout.set_thread_buffer(buffer)
                try:
                    module.run(
                        args=self.args,
                        ptjsonlib=self.ptjsonlib,
                        helpers=self.helpers,
                        http_client=self.http_client,
                        base_response=self.base_response
                    )

                except Exception as e:
                    ptprint(f"{e}", "ERROR", not self.args.json)
                    error = e
                else:
                    error = None
                finally:
                    self.thread_local_stdout.clear_thread_buffer()
                    with self._lock:
                        ptprint(buffer.getvalue(), "TEXT", not self.args.json, end="\n")
            else:
                ptprint(f"Module '{module_name}' does not have 'run' function", "WARNING", not self.args.json)

        except FileNotFoundError as e:
            ptprint(f"Module '{module_name}' not found", "ERROR", not self.args.json)
        except Exception as e:
            ptprint(f"Error running module '{module_name}': {e}", "ERROR", not self.args.json)


def _import_module_from_path(module_name: str, file=__file__) -> ModuleType:
    """
    Dynamically imports a Python module from a given file path.

    This method uses `importlib` to load a module from a specific file location.
    The module is then registered in `sys.modules` under the provided name.

    Args:
        module_name (str): Name under which to register the module.

    Returns:
        ModuleType: The loaded Python module object.

    Raises:
        ImportError: If the module cannot be found or loaded.
    """
    module_path = os.path.join(os.path.dirname(file), "modules", f"{module_name}.py")

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise ImportError(f"Cannot find spec for {module_name} at {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _get_all_available_modules(file=__file__) -> list:
    """
    Returns a list of available Python module names from the 'modules' directory.

    Modules must:
    - Not start with an underscore
    - Have a '.py' extension
    """
    modules_folder = os.path.join(os.path.dirname(file), "modules")
    available_modules = [
        f.rsplit(".py", 1)[0]
        for f in sorted(os.listdir(modules_folder))
        if f.endswith(".py") and not f.startswith("_")
    ]
    return available_modules


def get_help():
    """
    Generate structured help content for the CLI tool.

    This function dynamically builds a list of help sections including general
    description, usage, examples, and available options. The list of tests (modules)
    is generated at runtime by scanning the 'modules' directory and reading each module's
    optional '__TESTLABEL__' attribute to describe it.

        Returns:
            list: A list of dictionaries, where each dictionary represents a section of help
                  content (e.g., description, usage, options). The 'options' section includes
                  available command-line flags and dynamically discovered test modules.
    """

    # Build dynamic help from available modules
    def _get_available_modules_help() -> list:
        rows = []
        available_modules = _get_all_available_modules()
        modules_folder = os.path.join(os.path.dirname(__file__), "modules")
        for module in available_modules:
            mod = _import_module_from_path(module)
            label = getattr(mod, "__TESTLABEL__", f"Test for {module.upper()}")
            row = ["", "", f" {module.upper()}", label]
            rows.append(row)
        return sorted(rows, key=lambda x: x[2])

    return [
        {"description": [""]},
        {"usage": ["ptkibana <options>"]},
        {"usage_example": [
            "ptkibana -u https://www.example.com",
        ]},
        {"options": [
            ["-u",  "--url",                    "<url>",                            "Connect to URL"],
            ["-ts", "--tests",                  "<test>",                           "Specify one or more tests to perform:"],
            *_get_available_modules_help(),
            ["-t", "--threads",                 "<threads>",                        "Set thread count (default 10)"],
            ["-p",  "--proxy",                  "<proxy>",                          "Set proxy (e.g. http://127.0.0.1:8080)"],
            ["-T",  "--timeout",                "",                                 "Set timeout (default 10)"],
            ["-c",  "--cookie",                 "<cookie>",                         "Set cookie"],
            ["-a",  "--user-agent",             "<a>",                              "Set User-Agent header"],
            ["-H",  "--headers",                "<header:value>",                   "Set custom header(s)"],
            ["-r",  "--redirects",              "",                                 "Follow redirects (default False)"],
            ["-C",  "--cache",                  "",                                 "Cache HTTP communication (load from tmp in future)"],
            ["-v",  "--version",                "",                                 "Show script version and exit"],
            ["-vv", "--verbose",                "",                                 "Enable verbose mode"],
            ["-h",  "--help",                   "",                                 "Show this help message and exit"],
            ["-j",  "--json",                   "",                                 "Output in JSON format"],
            ["-U", "--user",                    "",                                 "Set user to authenticate as"],
            ["-P", "--password",                "",                                 "Set password to authenticate with"],
            ["-A", "--api-key",                 "",                                 "Set API key to authenticate with"],
            ["-F", "--file",                    "</path/to/file>",                  "File to read if host is vulnerable to CVE-2015-5531 (default /etc/passwd)"],
            ["-di", "--dump-index"              "<index1, index2, ...>",            "Specify index to dump with data_dump module"],
            ["-df", "--dump-field",             "<field1,field2, field3.subfield>", "Specify fields to dump with data_dump module"],
            ["-o", "--output",                  "<filename>",                       "Specify the name of the file to store structure/data dump to"],
            ["-ests", "--elasticsearch-tests"   "<test>",                           "Specify one or more tests to perform on Elasticsearch through the Kibana proxy"],
            ["-b", "--built-in",                "",                                 "Enumerate/dump built-in Elasticsearch indexes"]
        ]
        }]


def parse_args():
    def _check_url(url: str) -> str:
        """
        This method edits the provided URL.

        Adds '\\http://' to the begging of the URL if no protocol is provided

        www.example.com:9200 -> \\http://www.example.com:9200

        Doesn't do anything if a protocol is provided

        Also adds trailing '/' if missing

        :return: Edited URL
        """

        if "http://" not in url and "https://" not in url:
            url = "http://" + url

        if url[-1] != '/':
            url += '/'

        return url

    parser = argparse.ArgumentParser(add_help="False", description=f"{SCRIPTNAME} <options>")
    parser.add_argument("-u",  "--url",             type=str, required=True)
    parser.add_argument("-ts", "--tests",           type=lambda s: s.lower(), nargs="+")
    parser.add_argument("-p",  "--proxy",           type=str)
    parser.add_argument("-T",  "--timeout",         type=int, default=10)
    parser.add_argument("-t", "--threads",          type=int, default=10)
    parser.add_argument("-a",  "--user-agent",      type=str, default="Penterep Tools")
    parser.add_argument("-c",  "--cookie",          type=str)
    parser.add_argument("-H",  "--headers",         type=ptmisclib.pairs, nargs="+")
    parser.add_argument("-r",  "--redirects",       action="store_true")
    parser.add_argument("-C",  "--cache",           action="store_true")
    parser.add_argument("-j",  "--json",            action="store_true")
    parser.add_argument("-vv", "--verbose",         action="store_true")
    parser.add_argument("-v",  "--version",         action='version', version=f'{SCRIPTNAME} {__version__}')
    parser.add_argument("--socket-address",         type=str, default=None)
    parser.add_argument("--socket-port",            type=str, default=None)
    parser.add_argument("--process-ident",          type=str, default=None)
    parser.add_argument("-U", "--user",             type=str, default=None)
    parser.add_argument("-P", "--password",         type=str, default=None)
    parser.add_argument("-A", "--api-key",          type=str, default=None)
    parser.add_argument("-F", "--file",             type=str, default="/etc/passwd")
    parser.add_argument("-di", "--dump-index",      type=lambda f: f.split(","), default="")
    parser.add_argument("-df", "--dump-field",      type=lambda f: f.split(","), default=None)
    parser.add_argument("-o", "--output",           type=lambda o: f"{o}.json" if "json" not in o else o, default=None)
    parser.add_argument("-ests", "--elasticsearch-tests",           type=lambda s: s.lower(), nargs="+")
    parser.add_argument("-b", "--built-in",         action="store_true")

    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptprinthelper.help_print(get_help(), SCRIPTNAME, __version__)
        sys.exit(0)

    args = parser.parse_args()

    if args.proxy:
        args.proxy = {"http": args.proxy, "https": args.proxy}

    args.url = _check_url(args.url)

    if args.user and args.password:
        proto = args.url.find("//")+2
        args.url = f"{args.url[:proto]}{args.user}:{args.password}@{args.url[proto:]}"

    args.headers = ptnethelper.get_request_headers(args)

    if args.api_key:
        args.headers.update({"Authorization": f"ApiKey {args.api_key}"})

    ptprinthelper.print_banner(SCRIPTNAME, __version__, args.json)
    return args


def main():
    global SCRIPTNAME
    SCRIPTNAME = "ptkibana"
    args = parse_args()
    script = PtKibana(args)
    script.run()


if __name__ == "__main__":
    main()
