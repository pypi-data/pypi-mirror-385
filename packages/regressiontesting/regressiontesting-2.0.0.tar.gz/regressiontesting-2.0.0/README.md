# RegressionTesting
**Copyright (c) 2025 Lionel Guo**  
**Author:** Lionel Guo  
**Email:** [lionelliguo@gmail.com](mailto:lionelliguo@gmail.com)  
**GitHub:** [https://github.com/lionelliguo/regressiontesting](https://github.com/lionelliguo/regressiontesting)

---

## 🧩 Overview
`RegressionTesting` is a Python package for Automated Regression Testing with Google Sheets. This package allows you to:

- Fetch and compare HTTP Status Line and Header Fields using `curl` commands stored in Google Sheets.  
- Process these commands and store results (PASS/FAIL) back to Google Sheets.  
- Automatically manage the testing process using batch updates and configurable settings.

### Google Sheet Structure

#### 1. **TEST CASE Sheet (`TEST CASE`)**

The **TEST CASE** sheet is used for storing the test scripts and their results. It contains the following columns:

- **CURL_1**: Stores the first `curl` scripts for execution.
- **RESULT_1**: Stores the HTTP Status Line and Header Fields returned by the first `curl` script. The HTTP Status Line and Header Fields listed in `SELECTION_RULE_1` will not appear in `RESULT_1`.
- **CURL_2**: Stores the second `curl` scripts for execution.
- **RESULT_2**: Stores the HTTP Status Line and Header Fields returned by the second `curl` script. The HTTP Status Line and Header Fields listed in `SELECTION_RULE_2` will not appear in `RESULT_2`.
- **STATUS**: Stores the comparison results between `RESULT_1` and `RESULT_2`. If the results match, it will be PASS, otherwise, it will be FAIL. The HTTP Status Line and Header Fields listed in `COMPARISON_RULE` will be excluded when checking if the results match.

Example:

| CURL_1                      | RESULT_1 | CURL_2                      | RESULT_2 | STATUS |
|-----------------------------|----------|-----------------------------|----------|--------|
| `curl https://example1.com` |          | `curl https://example2.com` |          |        |
| `curl https://example3.com` |          | `curl https://example4.com` |          |        |

Each row represents one test case. You can add as many rows as needed for more test cases.

#### 2. **Config Sheet (`CONFIG`)**

The **CONFIG** sheet defines selection and comparison rules for the HTTP Status Line and Header Fields. It contains the following columns:

- **SELECTION_RULE_1**: Stores the HTTP Status Line and Header Fields that should be ignored during the first curl script execution. The HTTP Status Line and Header Fields will not appear in `RESULT_1`.
- **SELECTION_RULE_2**: Stores the HTTP Status Line and Header Fields that should be ignored during the second curl script execution. The HTTP Status Line and Header Fields will not appear in `RESULT_2`.
- **COMPARISON_RULE**: Stores the HTTP Status Line and Header Fields that should be ignored during the comparison between `RESULT_1` and `RESULT_2`. The HTTP Status Line and Header Fields will be excluded when checking if the results match.

Example:

| SELECTION_RULE_1      | SELECTION_RULE_2      | COMPARISON_RULE       |
|-----------------------|-----------------------|-----------------------|
| `Content-Length`      | `Content-Length`      | `Date`                |
| `Content-Type`        | `Content-Type`        | `Server`              |

You can add as many rows as needed for additional rules.

---

### 3. **Automatic Creation of a New Sheet**

Each time regression testing is executed, a new sheet is automatically created with the current date and time. The **`curl`** scripts from the **TEST CASE** sheet are copied into the new sheet.

The new sheet includes the following structure:
- **CURL_1** and **CURL_2** from the original **TEST CASE** sheet.
- New regression testing results are recorded for documentation and future reference.

---

## ⚙️ Requirements
- Python 3.x  
- Required Python packages:
  ```bash
  pip3 install gspread google-auth google-auth-oauthlib regressiontesting
  ```
- `curl` command-line tool  
- A valid Google Service Account JSON key

---

## 🚀 Setup

### 1. Clone repository
```bash
git clone https://github.com/lionelliguo/regressiontesting.git
cd regressiontesting
```

### 2. Install dependencies
```bash
pip3 install -r requirements.txt
```

---

## 🛠️ Configuration (`settings.json`)
Example configuration file:

```json
{
  "SPREADSHEET_URL": "Your Google Spreadsheets URL",
  "SERVICE_ACCOUNT_FILE": "Your Google Service Account Key.json",
  "SLEEP_SECONDS": 1.0,
  "IGNORE_CASE": true,
  "COPY_BATCH_SIZE": 1,
  "OUTPUT_BATCH_SIZE": 1
}
```

> **Note:**  
> `0` means all in one batch — no batching process.

---

## 🌐 Google Sheets and Service Account Setup

### 1. **Create a Google Sheet**
   - Go to [Google Sheets](https://sheets.google.com).
   - Create a blank spreadsheet (e.g., `regressiontesting`).
   - Share the sheet with your Service Account email.

### 2. **Enable APIs**
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Enable **Google Sheets API** and **Google Drive API**.

### 3. **Create a Service Account**
   - In **IAM & Admin → Service Accounts**, create a new account and download the JSON key file.

### 4. **Share Sheet with Service Account**
   - Open your Google Sheet → **Share** → add Service Account email.

---

## ▶️ Example Usage

After configuring `settings.json`, run the regression test and check the results in the Google Sheet.

```bash
python3 main.py
```

---

## ⚡ Quick Start

For a quick start, you can use the provided `settings-sample.json` instead of `settings.json` to quickly run the program.  
You can also view the regression testing results directly at:  
👉 [Google Sheet Link](https://docs.google.com/spreadsheets/d/1SFENuDWai_mZlKA74h7kkGE4hsU9KKtuigpx0-w3vbI/)

---

## 📄 License

Licensed under the **Apache License, Version 2.0** (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at:

> https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software  
distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and  
limitations under the License.
