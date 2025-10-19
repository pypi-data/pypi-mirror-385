<p align="center">
<a href="https://github.com/lucasastorian/edgartools">
    <img src="docs/images/edgartools-logo.png" alt="EdgarTools Python SEC EDGAR library logo" height="80">
</a>
</p>

<h3 align="center">Async-Enabled Python Library for SEC EDGAR Data Extraction</h3>

<p align="center">
  <a href="https://pypi.org/project/edgartools-async"><img src="https://img.shields.io/pypi/v/edgartools-async.svg" alt="PyPI - Version"></a>
  <a href="https://github.com/pypa/hatch"><img src="https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg" alt="Hatch project"></a>
  <a href="https://github.com/lucasastorian/edgartools/blob/main/LICENSE"><img src="https://img.shields.io/github/license/lucasastorian/edgartools" alt="GitHub"></a>
</p>

<p align="center">
  <b>Async fork of edgartools with enhanced XBRL support for non-US GAAP statements (IFRS, etc.). Extract financial data without blocking your event loop - perfect for high-throughput financial data pipelines.</b>
</p>

> **⭐ ALL CREDIT GOES TO [EDGARTOOLS](https://github.com/dgunning/edgartools) ⭐**
> This is a temporary fork created solely to add async support for immediate production needs. **ALL** the heavy lifting, design, and core functionality is from the brilliant work of [Dwight Gunning](https://github.com/dgunning) and the edgartools community.
>
> **Use the original [edgartools](https://github.com/dgunning/edgartools) for production** - it's actively maintained, has extensive documentation, and a strong community. This fork exists only to add async APIs until they're merged upstream.
>
> If you find this useful, please ⭐ star and support the original project: https://github.com/dgunning/edgartools</p>

![EdgarTools SEC filing data extraction demo](docs/images/edgartools-demo.gif)

## SEC Filing Data Extraction with Python

| With EdgarTools                               | Without EdgarTools                          |
|-----------------------------------------------|---------------------------------------------|
| ✅ Instant access to any filing since 1994     | ❌ Hours spent navigating SEC.gov            |
| ✅ Clean Python API with intuitive methods     | ❌ Complex web scraping code                 |
| ✅ Automatic parsing into pandas DataFrames    | ❌ Manual extraction of financial data       |
| ✅ Specialized data objects for each form type | ❌ Custom code for each filing type          |
| ✅ One-line conversion to clean, readable text | ❌ Messy HTML parsing for text extraction    |
| ✅ LLM-ready text extraction for AI pipelines  | ❌ Extra processing for AI/LLM compatibility |
| ✅ Automatic throttling to avoid blocks        | ❌ Rate limiting headaches                   |

## Apple's income statement in 1 line of code

```python
balance_sheet = Company("AAPL").get_financials().balance_sheet()         
```

## 🚀 Quick Start (2-minute tutorial)

```python
# 1. Import the library
from edgar import *

# 2. Tell the SEC who you are (required by SEC regulations)
set_identity("your.name@example.com")  # Replace with your email

# 3. Find a company
company = Company("MSFT")  # Microsoft

# 4. Get company filings
filings = company.get_filings() 

# 5. Filter by form 
insider_filings = filings.filter(form="4")  # Insider transactions

# 6. Get the latest filing
insider_filing = insider_filings[0]

# 7. Convert to a data object
ownership = insider_filing.obj()
```

![Apple SEC Form 4 insider transaction data extraction with Python](docs/images/aapl-insider.png)

## ⚡ Async API (New in edgartools-async)

Perfect for high-throughput pipelines and concurrent processing:

```python
import asyncio
from edgar import get_company_async, set_identity

async def main():
    # Set identity BEFORE async operations
    set_identity("your.name@example.com")

    # Load company data without blocking event loop
    company = await get_company_async("AAPL", user_agent="your.name@example.com")

    # Load SGML data asynchronously
    filings = company.get_filings(form="10-K")
    sgml = await filings[0].sgml_async()

    # Batch load multiple filings concurrently
    from edgar._filings import load_sgmls_concurrently
    filings_list = list(company.get_filings(form="10-Q"))[:10]
    sgmls = await load_sgmls_concurrently(filings_list, max_in_flight=32)
    print(f"Loaded {len(sgmls)} filings concurrently!")

asyncio.run(main())
```

### Key Async Features:
- **`get_company_async()`**: Non-blocking company instantiation
- **`filing.sgml_async()`**: Async SGML file loading
- **`load_sgmls_concurrently()`**: Batch concurrent loading with rate limiting
- **Thread-safe identity management**: No stdin blocking in async contexts

## 🌍 Enhanced Non-US GAAP Support (New in edgartools-async)

Improved handling of international financial statements (IFRS, etc.):

### Key Enhancements:
- **IFRS taxonomy support**: Better detection and parsing of IFRS statements
- **Quarterly vs YTD fallback**: Intelligently selects best available periods (prefers 3-month, falls back to YTD for cash flow)
- **Sparse period filtering**: Removes comparison periods with incomplete data
- **Improved concept matching**: Better revenue/income detection across taxonomies
- **Abstract element inference**: Automatically identifies abstract/header rows
- **Revenue deduplication**: Smarter handling of dimensional breakdowns vs parent totals

### Example: Foreign Filer with IFRS
```python
from edgar import Company

# Works seamlessly with non-US GAAP filers
company = Company("SAP")  # German company using IFRS
financials = company.income_statement(periods=4, annual=True)
# Automatically detects and parses IFRS taxonomy
```

## SEC Filing Analysis: Real-World Solutions

### Company Financial Analysis

**Problem:** Need to analyze a company's financial health across multiple periods.

![Microsoft SEC 10-K financial data analysis with EdgarTools](docs/images/MSFT_financial_complex.png)

[See full code](docs/examples.md#company_financial_analysis)



## 📚 Documentation


- [User Journeys / Examples](https://edgartools.readthedocs.io/en/latest/examples/)
- [Quick Guide](https://edgartools.readthedocs.io/en/latest/quick-guide/)
- [Full API Documentation](https://edgartools.readthedocs.io/)
- [EdgarTools Blog](https://www.edgartools.io)

## 👥 Community & Support

- [GitHub Issues](https://github.com/dgunning/edgartools/issues) - Bug reports and feature requests
- [Discussions](https://github.com/dgunning/edgartools/discussions) - Questions and community discussions

## 🔮 Roadmap

- **Coming Soon**: Enhanced visualization tools for financial data
- **In Development**: Machine learning integrations for financial sentiment analysis
- **Planned**: Interactive dashboard for filing exploration

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

- **Code**: Fix bugs, add features, improve documentation
- **Examples**: Share interesting use cases and examples
- **Feedback**: Report issues or suggest improvements
- **Spread the Word**: Star the repo, share with colleagues

See our [Contributing Guide](CONTRIBUTING.md) for details.

## ❤️ Sponsors & Support

If you find EdgarTools valuable, please consider supporting its development:

<a href="https://www.buymeacoffee.com/edgartools" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 144px !important;" >
</a>

Your support helps maintain and improve EdgarTools for the entire community!

## Key Features for SEC Data Extraction and Analysis

- **Comprehensive Filing Access**: Retrieve **any** SEC filing (10-K, 10-Q, 8-K, 13F, S-1, Form 4, etc.) since 1994.
- **Financial Statement Extraction**: Easily access **Balance Sheets, Income Statements, Cash Flows**, and individual line items using XBRL tags or common names.
- **SEC EDGAR API**: Programmatic access to the complete SEC database.
- **Smart Data Objects**: Automatic parsing of filings into structured Python objects.
- **Fund Holdings Analysis**: Extract and analyze **13F holdings** data for investment managers.
- **Insider Transaction Monitoring**: Get structured data from **Form 3, 4, 5** filings.
- **Clean Text Extraction**: One-line conversion from filing HTML to clean, readable text suitable for NLP.
- **Targeted Section Extraction**: Pull specific sections like **Risk Factors (Item 1A)** or **MD&A (Item 7)**.
- **AI/LLM Ready**: Text formatting and chunking optimized for AI pipelines.
- **Performance Optimized**: Leverages libraries like `lxml` and potentially `PyArrow` for efficient data handling.
- **XBRL Support**: Extract and analyze XBRL-tagged data.
- **Intuitive API**: Simple, consistent interface for all data types.

EdgarTools is distributed under the [MIT License](LICENSE).

## 📊 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=dgunning/edgartools&type=Timeline)](https://star-history.com/#dgunning/edgartools&Timeline)