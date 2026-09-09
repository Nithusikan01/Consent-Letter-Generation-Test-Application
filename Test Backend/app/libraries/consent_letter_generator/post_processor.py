import re


class MarkdownPostProcessor:
    """
    Deterministic tidy-up of the letter's Markdown.

    This used to make a second LLM call to "polish formatting". That call was
    removed: it cost ~1,600 tokens of the 8,000-per-minute budget — enough on
    its own to push every letter over the limit — while doing nothing the passes
    below do not already do deterministically. It was also actively harmful at
    times, flattening the per-option structure the generation prompt had just
    produced and stripping greetings only intermittently. Greeting removal and
    section-heading levels are now enforced in `generator.py`.
    """

    def process(self, text: str) -> str:
        text = self._normalize_headings(text)
        text = self._normalize_bullets(text)
        text = self._normalize_numbering(text)
        return text

    def _normalize_headings(self, text: str) -> str:
        # Ensure consistent heading hashes (at most 3 levels deep)
        lines = text.splitlines()
        new_lines = []
        for line in lines:
            if re.match(r'^\s*#+\s', line):
                line = re.sub(r'^\s*#+', lambda m: '#' * min(len(m.group(0)), 3), line)  # max ### level
                line = re.sub(r'\s+', ' ', line).strip()  # remove extra spaces
            new_lines.append(line)
        return "\n".join(new_lines)

    def _normalize_bullets(self, text: str) -> str:
        # Convert all bullets to '-'
        return re.sub(r'^\s*[\*\+]\s+', '- ', text, flags=re.MULTILINE)

    def _normalize_numbering(self, text: str) -> str:
        # Ensure numbered lists are sequential (1., 2., 3., …)
        lines = text.splitlines()
        new_lines = []
        counter = 1
        for line in lines:
            if re.match(r'^\s*\d+\.\s+', line):
                line = re.sub(r'^\s*\d+\.', f"{counter}.", line)
                counter += 1
            else:
                counter = 1  # reset if list breaks
            new_lines.append(line)
        return "\n".join(new_lines)

    def _remove_extra_blank_lines(self, text: str) -> str:
        # Collapse multiple blank lines into one
        return re.sub(r'\n{3,}', '\n\n', text)
