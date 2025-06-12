import subprocess
import os
import tempfile
import logging
from pathlib import Path
from typing import Dict, Optional, Union

logging.basicConfig(level=logging.INFO, format="[html2pdf_chromium] %(levelname)s: %(message)s")

# Expanded list of default executable paths for various Chromium-based browsers.
DEFAULT_PATHS = {
    "chrome": [
        # Windows
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        # macOS
        r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        # Linux
        r"/usr/bin/google-chrome-stable",
        r"/usr/bin/google-chrome",
        r"/usr/bin/chromium-browser",
        r"/snap/bin/chromium",
    ],
    "edge": [
        # Windows
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        # macOS
        r"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        # Linux
        r"/usr/bin/microsoft-edge-stable",
        r"/usr/bin/microsoft-edge",
        r"/opt/microsoft/msedge/msedge",
    ],
}


class PDFConversionError(Exception):
    """Error raised when an error occurs during PDF conversion"""


class Converter:
    """A class to convert HTML files or strings to PDF using a Chromium-based browser."""

    def __init__(
        self,
        browser: str = "chrome",
        executable_path: Optional[str] = None,
        headless_mode: str = "new",
    ):
        """
        Initializes the Chromium converter.

        Args:
            browser (str): The name of the browser to use (e.g., 'chrome', 'edge').
                           Defaults to 'chrome'.
            executable_path (Optional[str]): The explicit path to the browser executable.
                                             If None, searches in default locations.
            headless_mode (str): The headless mode to use ('new' or 'old').
                                 'new' is recommended. Defaults to 'new'.
        """
        self.browser = browser.lower()
        self.executable_path = Path(executable_path or self._find_executable_path()).resolve()
        self.headless_mode = headless_mode

    def _find_executable_path(self) -> str:
        """
        Searches for the browser executable in a list of default paths.

        Returns:
            str: The path to the found executable.

        Raises:
            FileNotFoundError: If the executable cannot be found in any default path.
        """
        paths = DEFAULT_PATHS.get(self.browser, [])
        for path in paths:
            if os.path.exists(path):
                return path
        raise FileNotFoundError(
            f"Unable to find '{self.browser}' executable in default paths. "
            "Please install it or provide its path via the 'executable_path' argument."
        )

    def convert_file(
        self,
        html_input: Union[str, Path],
        pdf_output: Union[str, Path],
        print_options: Optional[Dict[str, Union[str, bool]]] = None,
        timeout: int = 30,
    ) -> bool:
        """
        Converts an HTML file to a PDF file.

        Args:
            html_input (Union[str, Path]): Path to the source HTML file.
            pdf_output (Union[str, Path]): Path for the generated PDF file.
            print_options (Optional[Dict]): Advanced printing options for the browser.
                                            Example: {'--margin-top': '0', '--landscape': True}
            timeout (int): The timeout in seconds for the conversion process.

        Returns:
            bool: True if conversion was successful.

        Raises:
            FileNotFoundError: If the input HTML file is not found.
            RuntimeError: If the PDF conversion process fails.
        """
        html_path = Path(html_input).resolve()
        pdf_path = Path(pdf_output).resolve()

        if not html_path.exists():
            raise FileNotFoundError(f"HTML input file not found at: {html_path}")

        # Use pathlib's as_uri() to create a proper file URI for all OSes
        html_uri = html_path.as_uri()

        command = [
            self.executable_path,
            f"--headless={self.headless_mode}",
            "--disable-gpu",  # Often needed in headless environments
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
        ]

        # Add custom print options
        if print_options:
            for option, value in print_options.items():
                if isinstance(value, bool) and value:
                    command.append(option)
                elif isinstance(value, str):
                    command.append(f"{option}={value}")

        # The final argument must be the input file
        command.append(html_uri)

        # Use a temporary directory for the user profile to avoid conflicts
        with tempfile.TemporaryDirectory(prefix=f"{self.browser}_profile_") as temp_dir:
            profile_command = command.copy()
            profile_command.insert(1, f"--user-data-dir={temp_dir}")

            try:
                process = subprocess.run(
                    profile_command,
                    check=True,
                    capture_output=True,
                    text=True,  # Use text=True for automatic decoding
                    timeout=timeout,
                )
                if process.stdout:
                    logging.info(f"Browser STDOUT: {process.stdout}")
                if process.stderr:
                    logging.warning(f"Browser STDERR: {process.stderr}")

            except FileNotFoundError as e:
                logging.error(f"Executable not found: {self.executable_path}")
                raise PDFConversionError(
                    f"PDF conversion failed because executable was not found: {self.executable_path}"
                ) from e
            except subprocess.TimeoutExpired as e:
                logging.error(f"PDF conversion timed out after {timeout} seconds.")
                raise PDFConversionError(f"PDF conversion timed out: {e.stderr}") from e
            except subprocess.CalledProcessError as e:
                error_message = (
                    f"PDF conversion failed with exit code {e.returncode}.\n" f"STDERR: {e.stderr}"
                )
                logging.error(error_message)
                raise PDFConversionError(error_message) from e

        if not os.path.exists(pdf_path):
            try:
                err = process.stderr
            except Exception:
                err = None

            if err is None:
                raise PDFConversionError("PDF conversion failed: File was not created")
            else:
                raise PDFConversionError(f"PDF conversion failed: File was not created. Err: {err}")

        logging.info(f"Successfully created PDF: {pdf_path}")
        return True

    def convert_string(
        self,
        html_string: str,
        pdf_output: Union[str, Path],
        print_options: Optional[Dict[str, Union[str, bool]]] = None,
        timeout: int = 30,
    ) -> bool:
        """
        Converts an HTML string to a PDF file.

        This is a convenience method that writes the string to a temporary
        HTML file and then converts it.

        Args:
            html_string (str): The HTML content to convert.
            pdf_output (Union[str, Path]): Path for the generated PDF file.
            print_options (Optional[Dict]): Advanced printing options.
            timeout (int): The timeout in seconds for the conversion process.

        Returns:
            bool: True if conversion was successful.
        """
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".html", mode="w", encoding="utf-8"
            ) as temp_html:
                temp_html_path = temp_html.name
                temp_html.write(html_string)

            logging.info(f"Created temporary HTML file: {temp_html_path}")
            return self.convert_file(temp_html_path, pdf_output, print_options, timeout)
        finally:
            # Clean up the temporary file
            if "temp_html_path" in locals() and os.path.exists(temp_html_path):
                try:
                    os.remove(temp_html_path)
                    logging.info(f"Removed temporary HTML file: {temp_html_path}")
                except OSError as e:
                    logging.warning(
                        f"Failed to remove temporary HTML file: {temp_html_path}. Error: {e}"
                    )
