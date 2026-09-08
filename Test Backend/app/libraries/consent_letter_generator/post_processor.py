import re
from typing import Optional
import openai
import time


class MarkdownPostProcessor:
    def __init__(self, use_llm: bool = False, api_key: str = None, base_url: str = None):
        self.use_llm = use_llm
        if use_llm and api_key:
            self.llm_client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url or "https://api.groq.com/openai/v1"
            )
        else:
            self.llm_client = None

    def process(self, text: str) -> str:
        text = self._normalize_headings(text)
        text = self._normalize_bullets(text)
        text = self._normalize_numbering(text)

        if self.use_llm and self.llm_client:
            text = self._llm_cleanup(text)

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

    def _llm_cleanup(self, text: str) -> str:
        """Optional: use an LLM to polish formatting."""
        if not self.llm_client:
            return text

        prompt = f"""
        Fix the Markdown formatting only. Do not change, add, or remove any clinical
        information, and do not reword sentences beyond what these formatting fixes require:
        - Ensure consistent heading levels (max ###).
        - Fix broken Markdown syntax only (stray symbols, inconsistent bullet markers, malformed tables).
        - PRESERVE all bullet points, numbered lists, headings, and tables exactly as structured — do NOT convert them into paragraphs.


        Input:
        {text}

        Output:
        """
        response = self.llm_client.responses.create(
            model="openai/gpt-oss-120b",  # or your chosen model
            input=prompt
        )
        return response.output_text.strip()
