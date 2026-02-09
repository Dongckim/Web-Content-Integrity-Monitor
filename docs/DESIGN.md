# Design and technical notes

## 1. HTML cleaning strategy

- **Target**: Main content is extracted from MediaWiki-style pages using the `mw-parser-output` div.
- **Removed elements**:
  - Tags: `table`, `img`, `figure`, `script`, `style`, `math`, `iframe`
  - Classes: `navbox`, `infobox`, `reference`, `reflist`, `toc`, `hatnote`, etc. (navigation, references, print-only)
  - Section IDs: `References`, `External_links`, `See_also`, `Notes` — the section from that header to the end is removed
- **Goal**: Comparisons react only to changes in main body text; sidebar, references, and ads are ignored.

## 2. Comparison logic (diffcheck)

- **Normalization**: For each `.md` file, the `<!-- URL: ... -->` metadata and blank lines/leading-trailing whitespace are stripped, then lines are joined into a single string for comparison.
- **Scope**: Only pages present in both archives (same filename) are compared. New or removed pages are not listed.
- **Output**: Only pages whose body content changed are printed as “Title (URL)” so you can see which URLs changed.

## 3. Archive strategy

- **Format**: Archives are named with the run timestamp: `YYYY-MM-DD_HH-MM-SS.tar.gz`.
- **Date matching**: diffcheck looks up archives by **date prefix** (`YYYY-MM-DD`). If multiple archives share that date prefix, the latest one (by name sort) is used.
- **Effect**: You can keep one snapshot per day or run multiple times per day and automatically use the latest run for that date.

## 4. Filenames and input format

- **Filenames**: The title is lowercased, non-alphanumeric characters are replaced with `_`, and the result is used as `title.md`. Same resulting filename is treated as the same page even if URL/title differ.
- **CSV**: Pipe-separated `title|url|date`. Rows with a future `date` are skipped, so you can use the CSV to schedule “collect after this date”.

## 5. Local file support

- `html2md` accepts `file://` URLs so you can convert and test with local HTML files.
