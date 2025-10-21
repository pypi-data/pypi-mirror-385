import logging
import re
from typing import List, Literal

from duowen_agent.rag.models import Document

from .base import BaseChunk


class JinaTextChunker(BaseChunk):
    """移植 https://gist.github.com/hanxiao/3f60354cf6dc5ac698bc9154163b4e6a

    最新版似乎有bug 对接初期版本
    https://gist.github.com/hanxiao/3f60354cf6dc5ac698bc9154163b4e6a/1354e0fd7598ee9a2d704852e22f0010d07eb56d
    """

    def __init__(
        self,
        chunk_size: int = 512,
        token_count_type: Literal["o200k", "cl100k"] = "cl100k",
    ):
        super().__init__(token_count_type=token_count_type)
        self.chunk_size = chunk_size
        self.regex_patterns = {
            "headings": "(?:^(?:[#*=-]{1,7}|\\w[^\\r\\n]{0,200}\\r?\\n[-=]{2,200}|<h[1-6][^>]{0,100}>)[^\\r\\n]{1,200}(?:</h[1-6]>)?(?:\\r?\\n|$))",
            "citations": "(?:\\$[0-9]+\\$[^\\r\\n]{1,800})",
            "list_items": "(?:(?:^|\\r?\\n)[ \\t]{0,3}(?:[-*+•]|\\d{1,3}\\.\\w\\.|\\$[ xX]\\$)[ \\t]+(?:(?:\\b[^\\r\\n]{1,200}\\b(?:[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?=\\s|$))|(?:\\b[^\\r\\n]{1,200}\\b(?=[\\r\\n]|$))|(?:\\b[^\\r\\n]{1,200}\\b(?=[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?:.{1,100}(?:[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?=\\s|$))?))(?:\\r?\\n[ \\t]{2,5}(?:[-*+•]|\\d{1,3}\\.\\w\\.|\\$[ xX]\\$)[ \\t]+(?:(?:\\b[^\\r\\n]{1,200}\\b(?:[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?=\\s|$))|(?:\\b[^\\r\\n]{1,200}\\b(?=[\\r\\n]|$))|(?:\\b[^\\r\\n]{1,200}\\b(?=[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?:.{1,100}(?:[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?=\\s|$))?))){0,6}(?:\\r?\\n[ \\t]{4,7}(?:[-*+•]|\\d{1,3}\\.\\w\\.|\\$[ xX]\\$)[ \\t]+(?:(?:\\b[^\\r\\n]{1,200}\\b(?:[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?=\\s|$))|(?:\\b[^\\r\\n]{1,200}\\b(?=[\\r\\n]|$))|(?:\\b[^\\r\\n]{1,200}\\b(?=[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?:.{1,100}(?:[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?=\\s|$))?))){0,6})",
            "block_quote": "(?:(?:^>\\s?(?:>|\\s{2,}){0,2}(?:(?:\\b[^\\r\\n]{0,200}\\b(?:[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?=\\s|$))|(?:\\b[^\\r\\n]{0,200}\\b(?=[\\r\\n]|$))|(?:\\b[^\\r\\n]{0,200}\\b(?=[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?:.{1,100}(?:[.!?…。！？]|\\.3|[\\u2026\\u2047-\\u2049]|[\\U0001F600-\\U0001F64F])(?=\\s|$))?))\\r?\\n?){1,15})",
            "code_block": "(?:(?:^|\\r?\\n)(?:```|~~~)(?:\\w{0,20})?\\r?\\n[\\s\\S]{0,1500}?(?:```|~~~)\\r?\\n?|(?:(?:^|\\r?\\n)(?: {4}|\\t)[^\\r\\n]{0,200}(?:\\r?\\n(?: {4}|\\t)[^\\r\\n]{0,200}){0,20}\\r?\\n?)|(?:<pre>(?:<code>)?[\\s\\S]{0,1500}?(?:</code>)?</pre>))",
            "table": "(?:(?:^|\r?\n)(?:\\|[^\\r\\n]{0,1000}\\|(?:\\r?\\n\\|[-:]{1,1000}\\|){0,1}(?:\\r?\\n\\|[^\\r\\n]{0,1000}\\|){0,50})|<table>[\\s\\S]{0,2000}?</table>)",
            "horizontal_rule": "(?:^(?:[-*_]){1,3}\\s*$|<hr\\s*/?>)",
            "sentence": "(?:(?:[^\r\n]{1,400}(?:[.!?…。！？]|\\.{3}|[…⁇-⁉]|[🌀-🗿😀-🙏🚀-\U0001f6ff🜀-\U0001f77f🞀-\U0001f7ff🠀-\U0001f8ff🤀-🧿🨀-\U0001fa6f🩰-\U0001faff])(?=\\s|$))|(?:[^\r\n]{1,400}(?=[\r\n]|$))|(?:[^\r\n]{1,400}(?=[.!?…。！？]|\\.\\.\\.|[…⁇-⁉]|[🌀-🗿😀-🙏🚀-\U0001f6ff🜀-\U0001f77f🞀-\U0001f7ff🠀-\U0001f8ff🤀-🧿🨀-\U0001fa6f🩰-\U0001faff])(?:.{1,100}(?:[.!?…。！？]|\\.\\.\\.|[…⁇-⁉]|[🌀-🗿😀-🙏🚀-\U0001f6ff🜀-\U0001f77f🞀-\U0001f7ff🠀-\U0001f8ff🤀-🧿🨀-\U0001fa6f🩰-\U0001faff])(?=\\s|$))?))",
            "quoted_text": '(?:(?<!\\w)\\"\\"\\"[^\\"]{0,300}\\"\\"\\"(?!\\w)|(?<!\\w)(?:\\"[^\\r\\n]{0,300}\\"|\\\'[^\\r\\n]{0,300}\\\'|\\`[^\\r\\n]{0,300}\\`)(?!\\w)|\\([^\\r\\n()]{0,200}(?:\\([^\\r\\n()]{0,200}\\)[^\\r\\n()]{0,200}){0,5}\\)|$[^\\r\\n$$]{0,200}(?:$[^\\r\\n$$]{0,200}$[^\\r\\n$$]{0,200}){0,5}$|\\$[^\\r\\n$]{0,100}\\$|\\`[^\\`\\r\\n]{0,100}\\`)',
            "paragraph": "(?:(?:^|\\r?\\n\\r?\\n)(?:<p>)?(?:(?:[^\\r\\n]{1,1000}(?:[.!?…。！？]|\\.\\.\\.|[\\u2026\\u2047-\\u2049]|[\\U0001F300-\\U0001F5FF\\U0001F600-\\U0001F64F\\U0001F680-\\U0001F6FF\\U0001F700-\\U0001F77F\\U0001F780-\\U0001F7FF\\U0001F800-\\U0001F8FF\\U0001F900-\\U0001F9FF\\U0001FA00-\\U0001FA6F\\U0001FA70-\\U0001FAFF])(?=\\s|$))|(?:[^\\r\\n]{1,1000}(?=[\\r\\n]|$))|(?:[^\\r\\n]{1,1000}(?=[.!?…。！？]|\\.\\.\\.|[\\u2026\\u2047-\\u2049]|[\\U0001F300-\\U0001F5FF\\U0001F600-\\U0001F64F\\U0001F680-\\U0001F6FF\\U0001F700-\\U0001F77F\\U0001F780-\\U0001F7FF\\U0001F800-\\U0001F8FF\\U0001F900-\\U0001F9FF\\U0001FA00-\\U0001FA6F\\U0001FA70-\\U0001FAFF])(?:.{1,100}(?:[.!?…。！？]|\\.\\.\\.|[\\u2026\\u2047-\\u2049]|[\\U0001F300-\\U0001F5FF\\U0001F600-\\U0001F64F\\U0001F680-\\U0001F6FF\\U0001F700-\\U0001F77F\\U0001F780-\\U0001F7FF\\U0001F800-\\U0001F8FF\\U0001F900-\\U0001F9FF\\U0001FA00-\\U0001FA6F\\U0001FA70-\\U0001FAFF])(?=\\s|$))?))(?:</p>)?(?=\\r?\\n\\r?\\n|$))",
            "html_style": "(?:<[a-zA-Z][^>]{0,100}(?:>[\\s\\S]{0,1000}?</[a-zA-Z]+>|\\s*/>))",
            "latex_style": "(?:(?:\\$\\$[\\s\\S]{0,500}?\\$\\$)|(?:\\$[^\\$\\r\\n]{0,100}\\$))",
            "fallback": "(?:(?:[^\\r\\n]{1,800}(?:[.!?…。！？]|\\.\\.\\.|[\\u2026\\u2047-\\u2049]|[\\U0001F300-\\U0001F5FF\\U0001F600-\\U0001F64F\\U0001F680-\\U0001F6FF\\U0001F700-\\U0001F77F\\U0001F780-\\U0001F7FF\\U0001F800-\\U0001F8FF\\U0001F900-\\U0001F9FF\\U0001FA00-\\U0001FA6F\\U0001FA70-\\U0001FAFF])(?=\\s|$))|(?:[^\\r\\n]{1,800}(?=[\\r\\n]|$))|(?:[^\\r\\n]{1,800}(?=[.!?…。！？]|\\.\\.\\.|[\\u2026\\u2047-\\u2049]|[\\U0001F300-\\U0001F5FF\\U0001F600-\\U0001F64F\\U0001F680-\\U0001F6FF\\U0001F700-\\U0001F77F\\U0001F780-\\U0001F7FF\\U0001F800-\\U0001F8FF\\U0001F900-\\U0001F9FF\\U0001FA00-\\U0001FA6F\\U0001FA70-\\U0001FAFF])(?:.{1,100}(?:[.!?…。！？]|\\.\\.\\.|[\\u2026\\u2047-\\u2049]|[\\U0001F300-\\U0001F5FF\\U0001F600-\\U0001F64F\\U0001F680-\\U0001F6FF\\U0001F700-\\U0001F77F\\U0001F780-\\U0001F7FF\\U0001F800-\\U0001F8FF\\U0001F900-\\U0001F9FF\\U0001FA00-\\U0001FA6F\\U0001FA70-\\U0001FAFF])(?=\\s|$))?))",
            "email": "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
            "url": "https?:\\/\\/(www\\.)?[a-zA-Z0-9\\-\\.]+\\.[a-zA-Z]{2,}(/[a-zA-Z0-9\\-\\.]+)*\\/?",
            "phone": "\\b(\\+\\d{1,3}[- ]?)?\\d{10}\\b",
            "hashtag": "#\\w+",
            "mention": "@\\w+",
            "ipv4": "\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b",
            "ipv6": "\\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\\b",
            "date": "\\b\\d{4}-\\d{1,2}-\\d{1,2}\\b",
            "time": "\\b\\d{1,2}:\\d{2}(?::\\d{2})?\\b",
        }

        self.patterns_dict = self.regex_patterns
        self.chunk_regex = re.compile(
            "|".join(list(self.regex_patterns.values())),
            re.DOTALL | re.MULTILINE | re.UNICODE,
        )

    def chunk(self, text: str) -> List[Document]:
        data = self.chunk_text(text)

        if not len(text.replace(" ", "").replace("\n", "")) == len(
            "".join(data).replace(" ", "").replace("\n", "")
        ):
            logging.warning(f"regex切分异常: {repr(text[0:50])} ")
            raise ValueError("regex切分错误")

        _chunk = []
        _curr_chunk = []
        for t in data:
            if self.token_len("".join(_curr_chunk + [t])) <= self.chunk_size:
                _curr_chunk.append(t)
            else:
                _chunk.append("".join(_curr_chunk))
                _curr_chunk = [t]

        if _curr_chunk:
            _chunk.append("".join(_curr_chunk))

        return [
            Document(
                page_content=i,
                metadata=dict(token_count=self.token_len(i), chunk_index=idx),
            )
            for idx, i in enumerate(_chunk)
            if len(i.strip()) > 0
        ]

    def chunk_text(self, text):
        matches = self.chunk_regex.finditer(text)
        chunks = []
        for match in matches:
            chunk_text = match.group()
            if chunk_text:
                chunks.append(chunk_text)
        return chunks

    def chunk_text_with_meta(self, text):
        matches = self.chunk_regex.finditer(text)
        chunks = []
        for match in matches:
            chunk_text = match.group()
            if chunk_text:  # Check if the chunk is not empty
                for name, pattern in self.patterns_dict.items():
                    if re.fullmatch(pattern, chunk_text):
                        chunks.append({"type": name, "text": chunk_text})
                        break
        return chunks
