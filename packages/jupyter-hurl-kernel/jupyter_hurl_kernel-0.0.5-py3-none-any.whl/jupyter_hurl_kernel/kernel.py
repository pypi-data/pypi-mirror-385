"""Hurl Jupyter Kernel implementation."""

import re
import subprocess
import tempfile
from pathlib import Path

from ipykernel.kernelbase import Kernel


class HurlKernel(Kernel):
    """A Jupyter kernel for executing Hurl commands."""

    implementation = "Hurl"
    implementation_version = "0.1.0"
    language = "hurl"
    language_version = "0.1"
    language_info = {
        "name": "hurl",
        "mimetype": "text/x-hurl",
        "file_extension": ".hurl",
        "codemirror_mode": "hurl",
        "pygments_lexer": "text",
    }
    banner = "Hurl kernel - Execute HTTP requests with Hurl"

    def __init__(self, **kwargs):
        """Initialize the kernel."""
        super().__init__(**kwargs)
        self._check_hurl_installation()

    def _check_hurl_installation(self):
        """Check if hurl is installed and available."""
        try:
            result = subprocess.run(
                ["hurl", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                self.hurl_version = result.stdout.strip()
            else:
                self.hurl_version = "unknown"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.hurl_version = None

    def _parse_magic_line(self, code):
        """Parse magic line (%%include or %%verbose) from code.

        Args:
            code: The code to parse

        Returns:
            tuple: (hurl_code, mode) where mode is 'normal', 'include', or 'verbose'
        """
        lines = code.split('\n')
        mode = 'normal'
        hurl_code_lines = []

        for line in lines:
            if line.strip().startswith('%%'):
                # Parse magic line
                magic = line.strip()[2:].lower()
                if magic == 'include':
                    mode = 'include'
                elif magic == 'verbose':
                    mode = 'verbose'
            else:
                hurl_code_lines.append(line)

        return '\n'.join(hurl_code_lines), mode

    def do_execute(
        self,
        code,
        silent,
        store_history=True,
        user_expressions=None,
        allow_stdin=False,
    ):
        """Execute a Hurl command.

        Args:
            code: The Hurl code to execute
            silent: If True, don't send output to the client
            store_history: Whether to store this execution in history
            user_expressions: User expressions to evaluate
            allow_stdin: Whether to allow stdin

        Returns:
            dict: Execution result
        """
        if not code.strip():
            return {
                "status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {},
            }

        # Check if hurl is installed
        if self.hurl_version is None:
            error_message = (
                "Error: hurl is not installed or not found in PATH.\n"
                "Please install hurl from https://hurl.dev/docs/installation.html"
            )
            if not silent:
                self.send_response(
                    self.iopub_socket,
                    "stream",
                    {"name": "stderr", "text": error_message},
                )
            return {
                "status": "error",
                "execution_count": self.execution_count,
                "ename": "HurlNotFound",
                "evalue": "hurl is not installed",
                "traceback": [error_message],
            }

        # Parse magic lines and get hurl code
        hurl_code, mode = self._parse_magic_line(code)

        if not hurl_code.strip():
            return {
                "status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {},
            }

        # Create a temporary file to store the Hurl code
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".hurl", delete=False
        ) as f:
            f.write(hurl_code)
            hurl_file = f.name

        try:
            # Build hurl command based on mode
            cmd = ["hurl", "--color", hurl_file]

            if mode == 'include':
                # --include shows response headers and body
                cmd.insert(1, "--include")
            elif mode == 'verbose':
                # --verbose shows all information (request, response, headers, timing, etc.)
                cmd.insert(1, "--verbose")

            # Execute hurl command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Send stdout to the client
            if result.stdout and not silent:
                self.send_response(
                    self.iopub_socket,
                    "stream",
                    {"name": "stdout", "text": result.stdout},
                )

            # Send stderr to the client
            if result.stderr and not silent:
                self.send_response(
                    self.iopub_socket,
                    "stream",
                    {"name": "stderr", "text": result.stderr},
                )

            # Determine execution status
            if result.returncode == 0:
                status = "ok"
                return_dict = {
                    "status": status,
                    "execution_count": self.execution_count,
                    "payload": [],
                    "user_expressions": {},
                }
            else:
                status = "error"
                return_dict = {
                    "status": status,
                    "execution_count": self.execution_count,
                    "ename": "HurlExecutionError",
                    "evalue": f"Hurl command failed with exit code {result.returncode}",
                    "traceback": [result.stderr] if result.stderr else [],
                }

            return return_dict

        except subprocess.TimeoutExpired:
            error_message = "Error: Hurl command timed out (exceeded 30 seconds)"
            if not silent:
                self.send_response(
                    self.iopub_socket,
                    "stream",
                    {"name": "stderr", "text": error_message},
                )
            return {
                "status": "error",
                "execution_count": self.execution_count,
                "ename": "HurlTimeout",
                "evalue": "Command timed out",
                "traceback": [error_message],
            }
        except Exception as e:
            error_message = f"Error executing Hurl command: {e}"
            if not silent:
                self.send_response(
                    self.iopub_socket,
                    "stream",
                    {"name": "stderr", "text": error_message},
                )
            return {
                "status": "error",
                "execution_count": self.execution_count,
                "ename": type(e).__name__,
                "evalue": str(e),
                "traceback": [error_message],
            }
        finally:
            # Clean up temporary file
            try:
                Path(hurl_file).unlink()
            except Exception:
                pass

    def do_complete(self, code, cursor_pos):
        """Provide autocompletion suggestions.

        Args:
            code: The code to complete
            cursor_pos: The cursor position in the code

        Returns:
            dict: Completion results
        """
        # Get the text before the cursor
        code_before_cursor = code[:cursor_pos]

        # Find the current word being typed
        match = re.search(r'(\S+)$', code_before_cursor)
        if match:
            current_word = match.group(1)
            cursor_start = match.start(1)
        else:
            current_word = ""
            cursor_start = cursor_pos

        # Define completion lists
        http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'CONNECT', 'TRACE']

        common_headers = [
            'Accept:', 'Accept-Encoding:', 'Accept-Language:', 'Authorization:',
            'Cache-Control:', 'Connection:', 'Content-Type:', 'Content-Length:',
            'Cookie:', 'Host:', 'Origin:', 'Referer:', 'User-Agent:',
        ]

        content_types = [
            'Content-Type: application/json',
            'Content-Type: application/x-www-form-urlencoded',
            'Content-Type: multipart/form-data',
            'Content-Type: text/plain',
            'Content-Type: text/html',
            'Content-Type: application/xml',
        ]

        hurl_sections = ['[QueryStringParams]', '[FormParams]', '[MultipartFormData]',
                        '[Cookies]', '[Captures]', '[Asserts]', '[Options]', '[BasicAuth]']

        magic_lines = ['%%include', '%%verbose']

        # Determine context and provide relevant completions
        matches = []

        # Check if we're at the start of a line (magic line)
        if code_before_cursor.strip().startswith('%%') or current_word.startswith('%%'):
            matches = [m for m in magic_lines if m.startswith(current_word)]

        # Check if we're in a section header
        elif '[' in code_before_cursor.split('\n')[-1]:
            matches = [s for s in hurl_sections if s.lower().startswith(current_word.lower())]

        # Check if we're on a line that looks like headers
        elif ':' in code_before_cursor.split('\n')[-1] or any(h.split(':')[0] in current_word for h in common_headers):
            # Suggest content types if typing Content-Type
            if 'Content-Type' in code_before_cursor.split('\n')[-1]:
                matches = [ct for ct in content_types if ct.lower().startswith(current_word.lower())]
            else:
                matches = [h for h in common_headers if h.lower().startswith(current_word.lower())]

        # Check if we're at the start of a line (HTTP method)
        elif code_before_cursor.endswith('\n') or len(code_before_cursor.split('\n')[-1].strip()) == 0:
            matches = http_methods + magic_lines

        # Default: suggest HTTP methods and common keywords
        else:
            all_completions = http_methods + common_headers + hurl_sections + magic_lines
            matches = [c for c in all_completions if c.lower().startswith(current_word.lower())]

        return {
            'matches': matches,
            'cursor_start': cursor_start,
            'cursor_end': cursor_pos,
            'metadata': {},
            'status': 'ok'
        }

    def do_inspect(self, code, cursor_pos, detail_level=0):
        """Provide documentation/inspection for code.

        Args:
            code: The code to inspect
            cursor_pos: The cursor position
            detail_level: Level of detail (0 or 1)

        Returns:
            dict: Inspection results with documentation
        """
        # Get the word at cursor position
        # Find word boundaries
        start = cursor_pos
        while start > 0 and code[start - 1].isalnum():
            start -= 1

        end = cursor_pos
        while end < len(code) and code[end].isalnum():
            end += 1

        word = code[start:end].upper()

        # Documentation for HTTP methods
        http_methods_docs = {
            'GET': 'GET method requests a representation of the specified resource. Requests using GET should only retrieve data.',
            'POST': 'POST method submits an entity to the specified resource, often causing a change in state or side effects on the server.',
            'PUT': 'PUT method replaces all current representations of the target resource with the request payload.',
            'DELETE': 'DELETE method deletes the specified resource.',
            'PATCH': 'PATCH method applies partial modifications to a resource.',
            'HEAD': 'HEAD method asks for a response identical to a GET request, but without the response body.',
            'OPTIONS': 'OPTIONS method describes the communication options for the target resource.',
        }

        # Documentation for sections
        sections_docs = {
            'QUERYSTRINGPARAMS': '[QueryStringParams] section defines query parameters to send with the request.\nExample:\n[QueryStringParams]\nkey1: value1\nkey2: value2',
            'FORMPARAMS': '[FormParams] section defines form parameters (application/x-www-form-urlencoded).\nExample:\n[FormParams]\nusername: john\npassword: secret',
            'MULTIPARTFORMDATA': '[MultipartFormData] section defines multipart form data.\nExample:\n[MultipartFormData]\nfile: file,data.txt; text/plain',
            'ASSERTS': '[Asserts] section defines assertions to validate the response.\nExample:\n[Asserts]\nstatus == 200\njsonpath "$.name" == "John"',
            'CAPTURES': '[Captures] section captures values from the response for use in subsequent requests.\nExample:\n[Captures]\ntoken: jsonpath "$.token"',
            'COOKIES': '[Cookies] section defines cookies to send with the request.\nExample:\n[Cookies]\nsession_id: abc123',
            'BASICAUTH': '[BasicAuth] section defines HTTP Basic Authentication credentials.\nExample:\n[BasicAuth]\nusername: password',
            'OPTIONS': '[Options] section defines Hurl-specific options for the request.\nExample:\n[Options]\nvery-verbose: true\ninsecure: true',
        }

        # Check for magic lines
        if word in ['INCLUDE', 'VERBOSE']:
            doc_text = {
                'INCLUDE': '%%include magic line\nShows response headers and body (equivalent to hurl --include flag)',
                'VERBOSE': '%%verbose magic line\nShows all request/response details including headers, timing, etc. (equivalent to hurl --verbose flag)',
            }.get(word, '')
        elif word in http_methods_docs:
            doc_text = f"HTTP {word} Method\n\n{http_methods_docs[word]}"
        elif word in sections_docs:
            doc_text = sections_docs[word]
        else:
            doc_text = ''

        return {
            'status': 'ok',
            'found': bool(doc_text),
            'data': {
                'text/plain': doc_text
            },
            'metadata': {}
        }


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=HurlKernel)
