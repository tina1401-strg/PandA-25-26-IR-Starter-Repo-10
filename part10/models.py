from typing import List, Dict, Any, Tuple

class Sonnet:
    def __init__(self, sonnet_data: Dict[str, Any]):
        self.title = sonnet_data["title"]
        self.lines = sonnet_data["lines"]

    @staticmethod
    def find_spans(text: str, pattern: str):
        """Return [(start, end), ...] for all (possibly overlapping) matches.
        Inputs should already be lowercased by the caller."""
        spans = []
        if not pattern:
            return spans

        for i in range(len(text) - len(pattern) + 1):
            if text[i:i + len(pattern)] == pattern:
               spans.append((i, i + len(pattern)))
        return spans

    def search_for(self, query: str) -> "SearchResult":
        title_raw = str(self.title)
        lines_raw = self.lines  # list[str]

        q = query.lower()
        title_spans = self.find_spans(title_raw.lower(), q)

        line_matches = []
        for idx, line_raw in enumerate(lines_raw, start=1):  # 1-based line numbers
            spans = self.find_spans(line_raw.lower(), q)
            if spans:
                line_matches.append(
                    LineMatch(idx, line_raw, spans)
                )

        total = len(title_spans) + sum(len(lm.spans) for lm in line_matches)
        search_result = SearchResult(title_raw, title_spans, line_matches, total)
        return search_result

class LineMatch:
    def __init__(self, line_no: int, text: str, spans: List[Tuple[int, int]]):
        self.line_no = line_no
        self.text = text
        self.spans = spans

    def copy(self):
        return LineMatch(self.line_no, self.text, self.spans)

class SearchResult:
    def __init__(self, title: str, title_spans: List[Tuple[int, int]], line_matches: List[LineMatch], matches: int) -> None:
        self.title = title
        self.title_spans = title_spans
        self.line_matches = line_matches
        self.matches = matches

    def copy(self):
        return SearchResult(self.title, self.title_spans, self.line_matches, self.matches)

    def combine(self, result2: "SearchResult") -> "SearchResult":
        """Combine two search results."""

        combined = self.copy()  # shallow copy

        combined.matches = self.matches + result2.matches
        combined.title_spans = sorted(self.title_spans + result2.title_spans)

        # Merge line_matches by line number

        lines_by_no = {lm.line_no: lm.copy() for lm in self.line_matches}
        for lm in result2.line_matches:
            ln = lm.line_no
            if ln in lines_by_no:
                # extend spans & keep original text
                lines_by_no[ln].spans.extend(lm.spans)
            else:
                lines_by_no[ln] = lm.copy()

        combined.line_matches = sorted(lines_by_no.values(), key=lambda lm: lm.line_no)

        return combined

    @staticmethod
    def ansi_highlight(text: str, spans, highlight_mode):
        """Return text with ANSI highlight escape codes inserted."""
        if not spans:
            return text

        spans = sorted(spans)
        merged = []

        # Merge overlapping spans
        current_start, current_end = spans[0]
        for s, e in spans[1:]:
            if s <= current_end:
                current_end = max(current_end, e)
            else:
                merged.append((current_start, current_end))
                current_start, current_end = s, e
        merged.append((current_start, current_end))

        # Build highlighted string
        out = []
        i = 0
        for s, e in merged:
            out.append(text[i:s])
            # ToDo 2: You will need to use the new setting and for it a different ANSI color code: "\033[1;92m"

            if highlight_mode == "DEFAULT":
                out.append("\033[43m\033[30m")  # yellow background, black text
            if highlight_mode == "GREEN":
                out.append("\033[1;92m")  # text bold green (appears black in my terminal)
            out.append("\033[30m")
            out.append(text[s:e])
            # ToDo 2: DONE This stays the same. It just means "continue with default colors"
            out.append("\033[0m")  # reset
            i = e
        out.append(text[i:])
        return "".join(out)

    def print(self, highlight: str, highlight_mode: str, idx, total_docs):
        title_line = (

            # ToDo 2: DONE You will need to pass the new setting, the highlight_mode to ansi_highlight and use it there
            self.ansi_highlight(self.title, self.title_spans, highlight_mode)
            if highlight == "ON"
            else self.title
        )
        print(f"\n[{idx}/{total_docs}] {title_line}")
        for lm in self.line_matches:
            line_out = (
                # ToDo 2: DONE You will need to pass the new setting, the highlight_mode to ansi_highlight and use it there
                self.ansi_highlight(lm.text, lm.spans, highlight_mode)
                if highlight == "ON"
                else lm.text
            )
            print(f"  [{lm.line_no:2}] {line_out}")

class SearchResults:
    def __init__(self) -> None:
        self.search_results: List[SearchResult] = []

    def __len__(self) -> int:
        return len(self.search_results)

    def __getitem__(self, idx: int) -> SearchResult:
        return self.search_results[idx]

    def __setitem__(self, idx: int, result: SearchResult) -> None:
        self.search_results[idx] = result

    def append(self, search_result: SearchResult) -> None:
        self.search_results.append(search_result)

    def print(
            self,
            query: str,
            highlight: str,
            highlight_mode: str,
            query_time_ms: float | None = None,
        ) -> None:

        total_docs = len(self.search_results)
        matched = [r for r in self.search_results if r.matches > 0]

        line = f'{len(matched)} out of {total_docs} sonnets contain "{query}".'
        if query_time_ms is not None:
            line += f" Your query took {query_time_ms:.2f}ms."
        print(line)

        for idx, r in enumerate(matched, start=1):
            r.print(highlight, highlight_mode, idx, total_docs)
