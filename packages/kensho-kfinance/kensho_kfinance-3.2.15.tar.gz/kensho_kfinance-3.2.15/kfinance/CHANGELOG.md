# Changelog

## v3.2.15
- Add smart line item validation with intelligent suggestions and descriptions to reduce token consumption by 75%

# 3.2.14
- Fix Capitalizations validator to handle nulls

# 3.2.13
- Fix Prices validator to handle null OHLC price data

# 3.2.12
- Remove multiples line item support

# 3.2.11
- Add Handling of status code 400 for Capitalizations, Modify EV/TEV ratio to target quarterly or LTM

# 3.2.10
- Add CIQ company_id to GetInfoFromIdentifiersResp

# v3.2.9
- Update tool descriptions for line items, segments, and statements to mention that all period-based inputs and outputs refer only to the calendar year.

# v3.2.8
- Add support for None to LineItemResponse & empty behavior for line items, segments, and statements

# v3.2.7
- Fix validator for UnifiedIdTripleResponse

# v3.2.6
- Return pydantic models from KfinanceTool._run

## v3.2.5
- Add requested EV ratio line items

## v3.2.4
- Add Mergers & Acquisitions tools to ALL_TOOLS

## v3.2.3
- Disable low level MCP SDK input validation

## v3.2.2
- Use ValidQuarter for statement and line item tools

## v3.2.1
- Add Company Intelligence tools to ALL_TOOLS

## v3.2.0
- Add Company Intelligence tools

## v3.1.1
- Update client base prompt

## v3.1.0
- Use unified endpoint for company resolution

## v3.0.3
- Add LineItemResponse model

## v3.0.2
- Add kfinance.mcp back to simplify transition to 3.0

## v3.0.1
- Add Private Company Financials Permissions and descriptions

## v3.0.0
- Add tool calls that accept lists of identifiers.

## v2.9.0
- Limit FastMCP version

## v2.8.0
- Add currency to get_capitalization and get_prices tools.

## v2.7.0
 - Expose a new list of LLM tools `grounding_tools` that return a list of all endpoint urls called

## v2.6.5
 - Add competitor company_name

## v2.6.4
- Add transcript permission and update accepted_permissions type to set[Permission]

## v2.6.3
- Bump urllib3 to 2.5 to address CVEs

## v2.6.2
 - Safely check for incomplete merger information

## v2.6.1
 - Remove get_earnings_call_datetimes_from_identifier tool

## v2.6.0
 - Add mergers & acquisitions.

## v2.5.0
 - Add competitors function and llm tools

## v2.4.4
- Replace `cached_property` with `property` to enable batching

## v2.4.3
- Improve MCP tool build process

## v2.4.2
- Update missing permission warning

## v2.4.1
- Fix SegmentsPermission typo

## v2.4.0
- Add MCP server

## v2.3.1
- Add llm tools for retrieving earnings and transcripts

## v2.3.0
- Add earnings and transcript objects

## v2.2.5
- Add parsing for relationship response with name

## v2.2.4
- Add segments as llm tools

## v2.2.3
- Change segments return type to nested dictionary

## v2.2.2
- Add segments

## v2.2.1
- Make number of employees optional to reflect backend changes

## v2.2.0
- Replace get company id, get security id, get trading item id tools with resolve identifier tool

## v2.1.2
- Allow batch executor to handle multiple requests

## v2.1.1
- Use cachetools cache

## v2.1.0
- Filter llm tools by user permissions

## v2.0.2
- Add Client.tickers() method for ticker industry filters for ISRCS and GICS

## v2.0.1
- Fix readthedocs integration for llm tools.

## v2.0.0
- Refactor llm tools to use langchain `BaseTool`.

## v1.2.2
- Add tabulate and pydantic as dependencies

## v1.2.1
- Add fetch for industry_code, industry_classification and gics_code.

## v1.2.0
- Add batch requests for iterable classes

## v1.1.0
- Add market cap, TEV, and shares outstanding

## v1.0.3
- Fix typo for get_history_metadata_from_identifier.

## v1.0.2
- Relaxing requirements for urllib3 dependency.

## v1.0.1
- Correct installation instructions in README.

## v1.0.0
- Initial public release

## v0.99.1
- Update llm tools to use identifier instead of ticker

## v0.99.0
- Initial KFinance Client
