# WEB SCRAPING

crawl4ai is an asynchronous web crawling and data extraction tool that leverages advanced AI strategies for processing online content. It provides two scraping approaches: one using the DeepSeek AI provider and another using ChatGPT (gpt-4o-mini). Both methods extract structured data from targeted web pages following a common schema.

## Project Structure

- **/scripts/main.py** Employs the AI provider you define in the constant for an extraction process with its own API token.
- **/.env.template**
  Contains environment variable placeholders (`DEEPSEEK_API_KEY` and `OPENAI_API_KEY`) required for authentication.

## Requirements

- Python 3.9+
- Dependencies: `crawl4ai`, `pydantic`, `python-dotenv`
- Environment variables:
  - `DEEPSEEK_API_KEY` for DeepSeek extraction.
  - `OPENAI_API_KEY` for ChatGPT extraction.

## Installation

1. Create a virtual environment:

   ```
   python -m venv virt
   ```
2. Activate the virtual environment:

   - On Windows:
     ```
     .\virt\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source virt/bin/activate
     ```
3. Install dependencies:

   ```
   pip install crawl4ai pydantic python-dotenv
   ```
4. Copy `.env.template` to `.env` and fill in the required tokens.
5. Execute on the console:

   ```
   crawl4ai-setup
   ```

## Usage

- For AI extraction:

  ```
  python scripts/main.py
  ```

The script will perform the following tasks:

- Crawl the specified URL.
- Extract and validate table data using AI.
- Save the validated data as JSON.
- Display a sample of results and usage metrics in the console.

## Contributing

Contributions are welcome. Please feel free to open an issue or submit a pull request with your improvements.
