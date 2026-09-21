"""Minimal pure-Python PDF writer (no reportlab dependency).

Used by the "Download PDF" button. A4 pages, Helvetica, word-wrapped,
with correct xref offsets. Unicode beyond Latin-1 is dropped so the file
stays valid.
"""
from __future__ import annotations

import re
import zlib


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\*\*", "", text)
    return "".join(ch for ch in text if ord(ch) < 256 and (ch.isprintable() or ch in "\n\t"))


def _wrap(text: str, width: int = 92) -> list:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


class _Pdf:
    def __init__(self):
        self.buf = bytearray(b"%PDF-1.4\n")
        self.offsets = [0]
        self.objects = []

    def add(self, data: bytes):
        self.offsets.append(len(self.buf))
        self.buf.extend(data)

    def obj(self, body: bytes, oid: int):
        self.add(f"{oid} 0 obj\n".encode() + body + b"\nendobj\n")


def pdf_from_lines(lines: list, title: str = "RFC Securities - Simple Management Report") -> bytes:
    flow = []
    for ln in lines:
        for wl in _wrap(_clean(ln)):
            flow.append(wl)

    lines_per_page = 52
    margin_top = 700.0
    line_h = 13.0
    pages = [flow[i:i + lines_per_page] for i in range(0, len(flow) or 1, lines_per_page)]
    if not pages:
        pages = [[]]
    npages = len(pages)

    pdf = _Pdf()
    pdf.obj(b"<< /Type /Catalog /Pages 2 0 R >>", 1)
    kids = " ".join(f"{7 + i * 2} 0 R" for i in range(npages))
    pdf.obj(f"<< /Type /Pages /Kids [{kids}] /Count {npages} >>".encode(), 2)
    pdf.obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>", 3)
    pdf.obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>", 4)

    next_oid = 5
    for pno, page_lines in enumerate(pages):
        content = []
        y = margin_top
        if pno == 0:
            content.append(f"BT /F2 14 Tf 50 {y + 20} Td ({_escape(title)}) Tj ET")
        for i, ln in enumerate(page_lines):
            y = margin_top - (i + 1) * line_h
            if y < 60:
                break
            if ln.startswith("#TITLE "):
                content.append(f"BT /F2 11 Tf 50 {y} Td ({_escape(ln[7:])}) Tj ET")
            elif ln.startswith("#H "):
                content.append(f"BT /F2 10 Tf 50 {y} Td ({_escape(ln[3:])}) Tj ET")
            else:
                content.append(f"BT /F1 9 Tf 50 {y} Td ({_escape(ln)}) Tj ET")
        content.append(f"BT /F1 8 Tf 50 40 Td (RFC SECURITIES - EXPLAIN ANALYSE PREDICT STRESS-TEST - Page {pno+1}) Tj ET")
        stream = zlib.compress("\n".join(content).encode("latin-1", errors="replace"))
        cid = next_oid
        next_oid += 1
        pid = next_oid
        next_oid += 1
        pdf.obj(f"<< /Length {len(stream)} /Filter /FlateDecode >>\nstream\n".encode("latin-1")
                + stream + b"\nendstream\n", cid)
        page_body = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                     f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
                     f"/Contents {cid} 0 R >>").encode("latin-1")
        pdf.obj(page_body, pid)

    xref_pos = len(pdf.buf)
    pdf.buf.extend(f"xref\n0 {next_oid}\n".encode())
    pdf.buf.extend(b"0000000000 65535 f \n")
    for off in pdf.offsets[1:]:
        pdf.buf.extend(f"{off:010d} 00000 n \n".encode())
    trailer = (f"trailer\n<< /Size {next_oid} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n").encode()
    pdf.buf.extend(trailer)
    return bytes(pdf.buf)