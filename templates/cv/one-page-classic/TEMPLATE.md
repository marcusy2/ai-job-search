# Template: one-page-classic

- **Type:** CV
- **Source extension:** .tex
- **Engine/toolchain:** lualatex
- **Page limit:** 1 page(s)
- **Fonts:** Times New Roman look via the `times` PostScript-Times package (standard, no bundled font files - matches the original Word template's Times New Roman body font)
- **Class/packages:** `article` base class; `times`, `geometry`, `titlesec`, `enumitem`, `hyperref`, `fontawesome5` (all standard CTAN packages)

## Compile command

    cd <output dir> && lualatex -interaction=nonstopmode <file>.tex

## Style rules

- Recreated from a user-supplied Word resume (`Marcus Yang Resume 9.4.26.docx`, extracted 2026-09-08): centered name/contact header, no profile-statement or core-competencies block - the template goes straight from the header into Education.
- Section order and exact headings: Education, Organizational and Technical Experience, Technical Skills, Leadership and Activities. Do not add or drop sections - this is the full set the source template used (the header typo "Leaderships and Activities" in the source was corrected to "Leadership and Activities").
- "Organizational and Technical Experience" is a merged section: it holds both club/organization roles (e.g. Liquid Rocketry at Illinois) and independent projects (e.g. CAD reconstructions, rocket builds) as peer subheading entries - do not split it into separate Experience/Projects sections.
- Subheading rows are left-title / right-date on one line, with an italic subtitle/role line (also left/right) directly below - use `\subheading{}{}{}{}` or `\subheadingnodate{}{}` from the template.
- Tight spacing throughout (`itemsep=0pt`) is intentional - this is what makes a dense 1-page layout with this much content possible. Don't loosen it to "improve" readability; it will overflow the page.
- Add `\vspace{3pt}` after an entry's `\end{itemize}` only when another subheading entry follows it in the same section (not after a section's last entry - `\titlespacing` before the next `\section` already provides that gap). Without it, consecutive entries within one section run together with no visible separation.
- Technical Skills is bolded category-label lines (Computer Languages / Software / Shop Tools / Materials in the source), not bulleted - one line per category, comma-separated items.

## Known pitfalls

- **Hard 1-page limit, no slack.** This layout has none of moderncv's whitespace buffer - a single bullet running two lines instead of one is often enough to push a section onto a phantom page 2. Before compiling, mentally re-read every bullet and shorten any that would wrap; after compiling, if the PDF is 2 pages, cut/tighten content rather than shrinking margins or font size further (both are already near their practical floor).
- **Font is TeX Gyre Termes via `fontspec`, not the classic `times` (PSNFSS) package.** `times` leaves bold/italic shapes undefined under lualatex's default TU/Unicode font encoding and silently substitutes regular weight for both - confirmed by a test compile that threw `Font shape 'TU/ptm/b/n' undefined` / `'TU/ptm/m/it' undefined` warnings. TeX Gyre Termes is a metric-compatible OpenType Times New Roman clone bundled with MiKTeX/TeX Live and resolves bold/italic correctly with zero font warnings.
- **`\subheading`/`\subheadingnodate` position the date in a fixed-width `\makebox` (`\ppdatewidth`, 2.2in), not `\hfill` glue or a per-row `tabular*`.** All three render visually identically, but only the fixed-width box is safe: an `\hfill`-based row, and even a `tabular*{\linewidth}{l@{\extracolsep{\fill}}r}` row (its right cell's start-x still varies per row since each entry is its own tabular*), both broke `pdftotext -layout` extraction - it silently reattaches a date to the wrong entry (a section heading absorbing the next entry's date, a bullet merging with a later date) even though the rendered PDF looks fine. **Even the fixed-width `\makebox` version does not fix `pdftotext -layout`** - confirmed by direct testing, this specific left-title/right-date-on-one-line pattern seems to be a `poppler -layout` column-clustering quirk that box-width tricks can't defeat.
- **Verify this template's ATS text layer with pypdf (or plain `pdftotext`, no `-layout`), never `pdftotext -layout`.** `05-cv-templates.md`'s own ATS section already names pypdf as the preferred extractor and poppler as only the fallback - for this template that preference is load-bearing, not just a nicety. Run `python tools/verify_pdf.py <pdf> --dump-text <txt>` (which tries pypdf first) and read the `.txt` it writes. Confirmed by direct comparison: pypdf and plain `pdftotext` (no `-layout`) both extract this template in correct left-to-right, entry-by-entry reading order every time; `pdftotext -layout` scrambles the same PDF's date attribution regardless of which of the three row-construction methods above produced it. Real ATS backends (Workday, Greenhouse, Lever, pdfminer/PDF.js-based parsers) read PDF text in content-stream order like pypdf does, not poppler's visual-column-reconstruction heuristic, so this is also the more representative check, not just the more convenient one.
- `\subheading`'s 4th argument is often empty (many entries have no separate right-aligned subtitle date) - pass `{}` rather than deleting the argument, or the tabular row's column count breaks.
- **Every `\subheading`/`\subheadingnodate` call must be preceded by nothing but a blank line (no explicit `\noindent` needed at the call site - it's baked into the macros), and its arguments must stay short (a title, a date, a one-line role/subtitle).** A full sentence (e.g. a degree description) does not wrap inside the tabular* cell it's placed in - it silently overflows past the margin and can print on top of the next line. Put any long description as an ordinary paragraph line after the `\subheading` call, not inside one of its arguments - see the Education entry in `template.tex` for the pattern (subheading for the institution/dates row, then a plain `\textit{...}` line for the degree description).
