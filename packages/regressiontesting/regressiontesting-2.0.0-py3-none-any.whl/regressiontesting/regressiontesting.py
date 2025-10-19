# RegressionTesting
# Copyright (c) 2025 Lionel Guo
# Author: Lionel Guo
# Email: lionelliguo@gmail.com
# GitHub: https://github.com/lionelliguo/regressiontesting

import gspread
from google.oauth2.service_account import Credentials
import subprocess
import json
import re
import time
import sys
import random
from datetime import datetime
from gspread_formatting import CellFormat, Color, format_cell_range
from gspread.exceptions import APIError

class RegressionTesting:
    """
    Encapsulated Google Sheets-based regression testing workflow:
      - Create a new sheet and copy CURL_1/CURL_2 from 'TEST CASE'
      - Run curl for each row, compare headers with rules
      - Batch write results and color rows (PASS=green / FAIL=red)
      - Auto-resize RESULT_1 (B) and RESULT_2 (D) columns
      - Robust Google API calls with transient-aware retries
    """

    TRANSIENT_KEYWORDS = (
        "rate limit", "quota", "exceeded", "429", "502", "503", "504",
        "deadline", "timeout", "temporar", "connection", "reset", "unavailable"
    )

    # ----------------- Construction -----------------
    def __init__(self,
                 spreadsheet_url: str,
                 service_account_file: str,
                 sleep_seconds: float = 1.0,
                 ignore_case: bool = True,
                 output_batch_size: int = 0,
                 copy_batch_size: int = 0):
        self.spreadsheet_url = spreadsheet_url
        self.service_account_file = service_account_file
        self.sleep_seconds = float(sleep_seconds)
        self.ignore_case = bool(ignore_case)
        self.output_batch_size = int(output_batch_size)
        self.copy_batch_size = int(copy_batch_size)

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        # Auth (no prints changed)
        creds = Credentials.from_service_account_file(self.service_account_file, scopes=scopes)
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_url(self.spreadsheet_url)

    # Optional factory from settings.json
    @staticmethod
    def load_settings(path: str = "settings.json") -> dict:
        """Load settings from a JSON file."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    @classmethod
    def from_settings(cls, path: str = "settings.json") -> "RegressionTesting":
        cfg = cls.load_settings(path)
        return cls(
            spreadsheet_url=cfg.get("SPREADSHEET_URL", ""),
            service_account_file=cfg.get("SERVICE_ACCOUNT_FILE", ""),
            sleep_seconds=cfg.get("SLEEP_SECONDS", 1.0),
            ignore_case=cfg.get("IGNORE_CASE", True),
            output_batch_size=cfg.get("OUTPUT_BATCH_SIZE", 0),
            copy_batch_size=cfg.get("copy_batch_size", cfg.get("COPY_BATCH_SIZE", 0)),
        )

    # ----------------- Retry wrapper -----------------
    @staticmethod
    def _is_transient_error(exc: Exception) -> bool:
        """Heuristically decide if an exception is transient (quota/network)."""
        msg = str(exc).lower()
        if isinstance(exc, APIError):
            try:
                code = getattr(exc, "response", {}).get("status", None) or getattr(exc, "response", {}).get("code", None)
            except Exception:
                code = None
            if code in (429, 500, 502, 503, 504):
                return True
        return any(k in msg for k in RegressionTesting.TRANSIENT_KEYWORDS)

    @staticmethod
    def gapi_call(callable_fn, desc: str, retries: int = 3, base_delay: float = 0.8):
        """
        Execute a Google API call with transient-aware retries.
        - On transient error: exponential backoff retry up to `retries` times.
        - On non-transient or after retries exhausted: print error and exit.
        """
        attempt = 0
        while True:
            try:
                return callable_fn()
            except Exception as e:
                if RegressionTesting._is_transient_error(e) and attempt < retries:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 0.3)
                    time.sleep(delay)
                    attempt += 1
                    continue
                print(f"Google API error: {type(e).__name__} - {e}")
                sys.exit(1)

    # ----------------- Small helpers -----------------
    @staticmethod
    def parse_json_to_obj(s):
        """Safely parse JSON string into Python dict."""
        if not s:
            return {}
        try:
            return json.loads(s)
        except Exception:
            return {"__raw": s}

    @staticmethod
    def col_letter(idx: int) -> str:
        """Convert 0-based column index to Excel-style letter."""
        return chr(65 + idx)

    # ----------------- Config loading -----------------
    def load_config_rules(self):
        """Load selection rules and comparison rules from CONFIG sheet."""
        try:
            config_sheet = self.gapi_call(
                lambda: self.spreadsheet.worksheet("CONFIG"),
                desc="spreadsheet.worksheet(CONFIG)",
            )
        except SystemExit:
            raise
        except Exception:
            print("CONFIG sheet not found. Using empty rules.")
            return [], [], []  # lists for order-sensitive rules

        config_header = self.gapi_call(
            lambda: config_sheet.row_values(1),
            desc="config_sheet.row_values(1)",
        )
        config_index = {name: i for i, name in enumerate(config_header) if name}
        col_num1 = config_index.get("SELECTION_RULE_1")
        col_num2 = config_index.get("SELECTION_RULE_2")
        col_comp = config_index.get("COMPARISON_RULE")

        SELECTION_RULE_1, SELECTION_RULE_2, COMPARISON_RULE = [], [], []

        values = self.gapi_call(
            lambda: config_sheet.get_all_values(),
            desc="config_sheet.get_all_values",
        )
        for row in values[1:]:
            if col_num1 is not None and col_num1 < len(row):
                val1 = row[col_num1].strip()
                if val1:
                    SELECTION_RULE_1.append(val1)
            if col_num2 is not None and col_num2 < len(row):
                val2 = row[col_num2].strip()
                if val2:
                    SELECTION_RULE_2.append(val2)
            if col_comp is not None and col_comp < len(row):
                valc = row[col_comp].strip()
                if valc:
                    COMPARISON_RULE.append(valc)  # preserve order and case

        print("Loaded CONFIG rules:")
        print("SELECTION_RULE_1:", SELECTION_RULE_1)
        print("SELECTION_RULE_2:", SELECTION_RULE_2)
        print("COMPARISON_RULE:", COMPARISON_RULE)

        return SELECTION_RULE_1, SELECTION_RULE_2, COMPARISON_RULE

    # ----------------- Curl runner -----------------
    def run_curl_and_get_headers(self, curl_cmd: str, exclude_headers=None):
        """Execute a curl command, parse HTTP headers, remove excluded headers (respects self.ignore_case), return JSON string."""
        if not curl_cmd or not curl_cmd.strip().startswith("curl"):
            return None

        exclude_list = exclude_headers if exclude_headers else []
        exclude_set = {h.lower() for h in exclude_list} if self.ignore_case else set(exclude_list)

        try:
            completed = subprocess.run(
                curl_cmd + " -s -i",
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            response_text = completed.stdout or ""
        except Exception as e:
            return json.dumps({"error": f"curl failed: {str(e)}"}, ensure_ascii=False)

        parts = re.split(r"\r\n\r\n|\n\n", response_text, maxsplit=1)
        header_lines = parts[0].splitlines() if parts else []
        if not header_lines:
            return json.dumps({"error": "No response headers"}, ensure_ascii=False)

        status_line = header_lines[0].strip()
        status_parts = status_line.split(" ", 2)
        http_version = status_parts[0] if len(status_parts) > 0 else ""
        status_code = int(status_parts[1]) if len(status_parts) > 1 and status_parts[1].isdigit() else None
        status_message = status_parts[2] if len(status_parts) > 2 else ""

        headers = {}
        for line in header_lines[1:]:
            if ": " in line:
                k, v = line.split(": ", 1)
            elif ":" in line:
                k, v = line.split(":", 1)
            else:
                continue

            key_raw = k.strip()
            key_norm = key_raw.lower() if self.ignore_case else key_raw

            # Respect IGNORE_CASE for selection rules
            if key_norm in exclude_set:
                continue

            headers[key_raw] = v.strip()

        return json.dumps(
            {
                "http_version": http_version,
                "status_code": status_code,
                "status_message": status_message,
                "headers": headers,
            },
            ensure_ascii=False,
            indent=2,
        )

    # ----------------- Column auto-resize -----------------
    def auto_resize_result_columns(self, sheet):
        """Auto resize only RESULT_1 (col B) and RESULT_2 (col D) after data is written."""
        sheet_id = sheet._properties.get("sheetId") or sheet.id
        self.gapi_call(
            lambda: self.spreadsheet.batch_update(
                {
                    "requests": [
                        {
                            "autoResizeDimensions": {
                                "dimensions": {
                                    "sheetId": sheet_id,
                                    "dimension": "COLUMNS",
                                    "startIndex": 1,  # B
                                    "endIndex": 2,
                                }
                            }
                        },
                        {
                            "autoResizeDimensions": {
                                "dimensions": {
                                    "sheetId": sheet_id,
                                    "dimension": "COLUMNS",
                                    "startIndex": 3,  # D
                                    "endIndex": 4,
                                }
                            }
                        },
                    ]
                }
            ),
            desc="auto resize RESULT_1 and RESULT_2",
        )

    # ----------------- Batch update (values + color) -----------------
    def batch_update(self, sheet, col_index, result1_list, result2_list, status_list, start_row):
        """Batch update values for RESULT_1, RESULT_2, and STATUS columns, and color rows per batch."""
        num_rows = len(result1_list)
        end_row = start_row + num_rows - 1

        # Write values (keep original prints)
        self.gapi_call(
            lambda: sheet.update(
                range_name=f"{self.col_letter(col_index['RESULT_1'])}{start_row}:{self.col_letter(col_index['RESULT_1'])}{end_row}",
                values=result1_list,
            ),
            desc="sheet.update RESULT_1",
        )
        self.gapi_call(
            lambda: sheet.update(
                range_name=f"{self.col_letter(col_index['RESULT_2'])}{start_row}:{self.col_letter(col_index['RESULT_2'])}{end_row}",
                values=result2_list,
            ),
            desc="sheet.update RESULT_2",
        )
        self.gapi_call(
            lambda: sheet.update(
                range_name=f"{self.col_letter(col_index['STATUS'])}{start_row}:{self.col_letter(col_index['STATUS'])}{end_row}",
                values=status_list,
            ),
            desc="sheet.update STATUS",
        )

        print(f"Batch updated {num_rows} rows from {start_row} to {end_row}.")

        # Row color (A..E) + keep original print lines
        green = CellFormat(
            backgroundColor=Color(0.8, 0.94, 0.8),  # #C6EFCE
            horizontalAlignment="LEFT",
            verticalAlignment="TOP",
        )
        red = CellFormat(
            backgroundColor=Color(1.0, 0.78, 0.78),  # #FFC7CE
            horizontalAlignment="LEFT",
            verticalAlignment="TOP",
        )

        for offset, status in enumerate(status_list):
            rownum = start_row + offset
            color_fmt = green if (status[0] or "").strip().upper() == "PASS" else red
            self.gapi_call(
                lambda rn=rownum, fmt=color_fmt: format_cell_range(sheet, f"A{rn}:E{rn}", fmt),
                desc=f"format_cell_range row {rownum}",
            )

        for i, status in enumerate(status_list, start=start_row):
            print(f"Row {i} STATUS: {status[0]}")

    # ----------------- Core processing -----------------
    def process_sheet(self, sheet, selection_rule_1, selection_rule_2, comparison_rule):
        """Process main sheet, run CURL, store results, compare headers, batch update."""
        header = self.gapi_call(lambda: sheet.row_values(1), desc="sheet.row_values(1)")
        col_index = {name: i for i, name in enumerate(header) if name}

        required_cols = ["CURL_1", "RESULT_1", "CURL_2", "RESULT_2", "STATUS"]
        missing = [c for c in required_cols if c not in col_index]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        all_values = self.gapi_call(lambda: sheet.get_all_values(), desc="sheet.get_all_values")
        num_rows = len(all_values)

        result1_list, result2_list, status_list = [], [], []

        # IGNORE_CASE for comparison rules
        if self.ignore_case:
            comparison_rule = [rule.lower() for rule in comparison_rule]

        for idx, row in enumerate(all_values[1:], start=2):
            curl1 = row[col_index["CURL_1"]] if col_index["CURL_1"] < len(row) else ""
            curl2 = row[col_index["CURL_2"]] if col_index["CURL_2"] < len(row) else ""

            result1 = self.run_curl_and_get_headers(curl1, selection_rule_1) if curl1 else ""
            result2 = self.run_curl_and_get_headers(curl2, selection_rule_2) if curl2 else ""

            parsed1 = self.parse_json_to_obj(result1)
            parsed2 = self.parse_json_to_obj(result2)

            headers1 = parsed1.get("headers", {})
            headers2 = parsed2.get("headers", {})

            http_version_1 = parsed1.get("http_version")
            http_version_2 = parsed2.get("http_version")
            status_code_1 = parsed1.get("status_code")
            status_code_2 = parsed2.get("status_code")
            status_message_1 = parsed1.get("status_message")
            status_message_2 = parsed2.get("status_message")

            # IGNORE_CASE logic for comparison
            if self.ignore_case:
                headers1_filtered = {k.lower(): v for k, v in headers1.items() if k.lower() not in comparison_rule}
                headers2_filtered = {k.lower(): v for k, v in headers2.items() if k.lower() not in comparison_rule}
                if "http_version" not in comparison_rule:
                    headers1_filtered["http_version"] = http_version_1
                    headers2_filtered["http_version"] = http_version_2
                if "status_code" not in comparison_rule:
                    headers1_filtered["status_code"] = status_code_1
                    headers2_filtered["status_code"] = status_code_2
                if "status_message" not in comparison_rule:
                    headers1_filtered["status_message"] = status_message_1
                    headers2_filtered["status_message"] = status_message_2
            else:
                headers1_filtered = {k: v for k, v in headers1.items() if k not in comparison_rule}
                headers2_filtered = {k: v for k, v in headers2.items() if k not in comparison_rule}
                if "http_version" not in comparison_rule:
                    headers1_filtered["http_version"] = http_version_1
                    headers2_filtered["http_version"] = http_version_2
                if "status_code" not in comparison_rule:
                    headers1_filtered["status_code"] = status_code_1
                    headers2_filtered["status_code"] = status_code_2
                if "status_message" not in comparison_rule:
                    headers1_filtered["status_message"] = status_message_1
                    headers2_filtered["status_message"] = status_message_2

            status = "PASS" if headers1_filtered == headers2_filtered else "FAIL"

            result1_list.append([result1])
            result2_list.append([result2])
            status_list.append([status])

            # Batch write
            if self.output_batch_size > 0 and len(result1_list) >= self.output_batch_size:
                self.batch_update(
                    sheet, col_index, result1_list, result2_list, status_list,
                    idx - len(result1_list) + 1
                )
                result1_list, result2_list, status_list = [], [], []
                if self.sleep_seconds and self.sleep_seconds > 0:
                    time.sleep(self.sleep_seconds)

        # Flush tail
        if result1_list:
            self.batch_update(
                sheet, col_index, result1_list, result2_list, status_list,
                num_rows - len(result1_list) + 1
            )

        # Auto resize RESULT_1 (B) and RESULT_2 (D)
        self.auto_resize_result_columns(sheet)

    # ----------------- Create working sheet -----------------
    def create_new_sheet_with_current_datetime(self):
        """Create a new sheet with current date and time as sheet name."""
        current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M")

        try:
            new_sheet = self.gapi_call(
                lambda: self.spreadsheet.add_worksheet(title=current_datetime, rows="100", cols="100"),
                desc="spreadsheet.add_worksheet",
            )
            print(f"New sheet created: {current_datetime}")

            # Copy from 'TEST CASE'
            try:
                test_case_sheet = self.gapi_call(
                    lambda: self.spreadsheet.worksheet("TEST CASE"),
                    desc="spreadsheet.worksheet(TEST CASE)",
                )
            except SystemExit:
                raise
            except Exception:
                print("TEST CASE sheet not found.")
                return None

            all_values = self.gapi_call(
                lambda: test_case_sheet.get_all_values(),
                desc="test_case_sheet.get_all_values",
            )
            if not all_values:
                print(f"All rows copied from TEST CASE to {current_datetime}")
                return new_sheet

            header = all_values[0]
            idx_map = {name: i for i, name in enumerate(header) if name}
            if "CURL_1" not in idx_map or "CURL_2" not in idx_map:
                print(f"All rows copied from TEST CASE to {current_datetime}")
                return new_sheet

            c1 = idx_map["CURL_1"]
            c2 = idx_map["CURL_2"]

            self.gapi_call(
                lambda: new_sheet.update(range_name="A1", values=[["CURL_1", "RESULT_1", "CURL_2", "RESULT_2", "STATUS"]]),
                desc="new_sheet.update header",
            )

            data_rows = []
            for row in all_values[1:]:
                v1 = row[c1] if c1 < len(row) else ""
                v2 = row[c2] if c2 < len(row) else ""
                data_rows.append([v1, "", v2, "", ""])

            if self.copy_batch_size == 0:
                if data_rows:
                    self.gapi_call(
                        lambda: new_sheet.update(range_name="A2", values=data_rows),
                        desc="new_sheet.update all data rows",
                    )
                print(f"All rows copied from TEST CASE to {current_datetime}")
            else:
                num_rows = len(data_rows)
                batch_size = self.copy_batch_size
                start_row = 2
                for i in range(0, num_rows, batch_size):
                    chunk = data_rows[i:i + batch_size]
                    end_row = start_row + len(chunk) - 1
                    self.gapi_call(
                        lambda sr=start_row, er=end_row, ch=chunk: new_sheet.update(range_name=f"A{sr}:E{er}", values=ch),
                        desc=f"new_sheet.update rows {start_row}-{end_row}",
                    )
                    print(f"Copied rows {start_row} to {end_row} from TEST CASE.")
                    start_row = end_row + 1

            return new_sheet

        except SystemExit:
            raise
        except Exception as e:
            print(f"Failed to create new sheet: {str(e)}")
            sys.exit(1)


# ----------------- Optional: CLI main (keeps your original logs) -----------------
if __name__ == "__main__":
    # Keep parity with the original script default behavior
    settings = RegressionTesting.load_settings()
    SPREADSHEET_URL = settings.get("SPREADSHEET_URL", "")
    SERVICE_ACCOUNT_FILE = settings.get("SERVICE_ACCOUNT_FILE", "")
    SLEEP_SECONDS = settings.get("SLEEP_SECONDS", 1.0)
    IGNORE_CASE = settings.get("IGNORE_CASE", True)
    OUTPUT_BATCH_SIZE = settings.get("OUTPUT_BATCH_SIZE", 0)
    COPY_BATCH_SIZE = settings.get("COPY_BATCH_SIZE", 0)

    rt = RegressionTesting(
        spreadsheet_url=SPREADSHEET_URL,
        service_account_file=SERVICE_ACCOUNT_FILE,
        sleep_seconds=SLEEP_SECONDS,
        ignore_case=IGNORE_CASE,
        output_batch_size=OUTPUT_BATCH_SIZE,
        copy_batch_size=COPY_BATCH_SIZE,
    )

    sel1, sel2, comp = rt.load_config_rules()
    new_ws = rt.create_new_sheet_with_current_datetime()
    if new_ws is not None:
        rt.process_sheet(new_ws, sel1, sel2, comp)
        print("All rows processed.")
    else:
        print("Sheet creation failed. Exiting.")
