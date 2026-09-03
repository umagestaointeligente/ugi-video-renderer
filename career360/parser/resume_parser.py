#!/usr/bin/env python3
"""LSI Career 360 — parser determinístico de currículo Beta 1.0.

Escopo:
- PDF textual via pypdf;
- DOCX via zip/XML da biblioteca padrão;
- nenhuma inferência silenciosa vira fato;
- saída = candidate_profile_draft para confirmação humana.

Não persiste arquivos, não envia dados a terceiros e não executa conteúdo do documento.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from dataclasses import dataclass, asdict
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_DOCX_ENTRIES = 500
MAX_DOCX_UNCOMPRESSED_BYTES = 40 * 1024 * 1024
MAX_DOCX_COMPRESSION_RATIO = 120
MAX_TEXT_CHARS = 250_000

ALLOWED_EXTENSIONS = {".pdf", ".docx"}

EMAIL_RE = re.compile(r"(?<![\w.+-])([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})(?![\w.-])", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?(?:9\s*)?\d{4}[-\s]?\d{4}(?!\d)")
URL_RE = re.compile(r"\b(?:https?://|www\.)[^\s<>]+", re.I)
LINKEDIN_RE = re.compile(r"\b(?:https?://)?(?:www\.)?linkedin\.com/in/[^\s<>]+", re.I)

SECTION_ALIASES = {
    "experiencia": {"experiência", "experiencia", "experiência profissional", "experiencia profissional", "histórico profissional", "historico profissional"},
    "formacao": {"formação", "formacao", "formação acadêmica", "formacao academica", "educação", "educacao"},
    "competencias": {"competências", "competencias", "habilidades", "skills", "conhecimentos"},
    "idiomas": {"idiomas", "línguas", "linguas"},
    "certificacoes": {"certificações", "certificacoes", "cursos", "cursos e certificações", "cursos e certificacoes"},
    "resumo": {"resumo", "resumo profissional", "perfil", "perfil profissional", "objetivo"},
}


class ResumeParseError(Exception):
    """Erro controlado do pipeline de currículo."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class EvidenceField:
    value: Any
    confidence: str
    source_excerpt: str | None
    inferred: bool = False
    user_confirmed: bool = False


@dataclass
class ParseEnvelope:
    parser_version: str
    status: str
    document: dict[str, Any]
    candidate_profile_draft: dict[str, Any]
    warnings: list[str]


PARSER_VERSION = "career360-resume-parser/1.0.0"


def _normalize_spaces(value: str) -> str:
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[\t\r ]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def _clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip(" \t•·▪◦-–—|")


def _excerpt(text: str, value: str, radius: int = 80) -> str | None:
    if not value:
        return None
    idx = text.lower().find(value.lower())
    if idx < 0:
        return None
    start = max(0, idx - radius)
    end = min(len(text), idx + len(value) + radius)
    return _normalize_spaces(text[start:end])


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def detect_type(data: bytes, filename: str) -> str:
    if not data:
        raise ResumeParseError("EMPTY_FILE", "O arquivo está vazio.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ResumeParseError("FILE_TOO_LARGE", "O arquivo excede o limite do Beta 1.0.")

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ResumeParseError("EXTENSION_NOT_ALLOWED", "Envie um arquivo PDF ou DOCX.")

    if data.startswith(b"%PDF-"):
        real_type = "pdf"
    elif data.startswith(b"PK\x03\x04") or data.startswith(b"PK\x05\x06") or data.startswith(b"PK\x07\x08"):
        real_type = "docx" if _is_docx_container(data) else "zip_unknown"
    else:
        real_type = "unknown"

    if ext == ".pdf" and real_type != "pdf":
        raise ResumeParseError("TYPE_MISMATCH", "A extensão PDF não corresponde ao conteúdo real do arquivo.")
    if ext == ".docx" and real_type != "docx":
        raise ResumeParseError("TYPE_MISMATCH", "A extensão DOCX não corresponde a um documento Word válido.")
    return real_type


def _is_docx_container(data: bytes) -> bool:
    try:
        with zipfile.ZipFile(BytesIO(data)) as zf:
            names = set(zf.namelist())
            return "[Content_Types].xml" in names and "word/document.xml" in names
    except (zipfile.BadZipFile, OSError):
        return False


def _validate_docx_archive(zf: zipfile.ZipFile) -> None:
    infos = zf.infolist()
    if len(infos) > MAX_DOCX_ENTRIES:
        raise ResumeParseError("DOCX_TOO_COMPLEX", "O DOCX contém arquivos internos demais.")

    total = 0
    for info in infos:
        total += info.file_size
        if total > MAX_DOCX_UNCOMPRESSED_BYTES:
            raise ResumeParseError("DOCX_EXPANDED_TOO_LARGE", "O DOCX expandido excede o limite de segurança.")
        if info.file_size and info.compress_size == 0:
            raise ResumeParseError("DOCX_SUSPICIOUS_COMPRESSION", "O DOCX possui compressão suspeita.")
        if info.compress_size:
            ratio = info.file_size / max(info.compress_size, 1)
            if ratio > MAX_DOCX_COMPRESSION_RATIO and info.file_size > 1_000_000:
                raise ResumeParseError("DOCX_SUSPICIOUS_COMPRESSION", "O DOCX possui taxa de compressão suspeita.")
        name = info.filename.replace("\\", "/")
        if name.startswith("/") or "../" in name or name == "..":
            raise ResumeParseError("DOCX_PATH_TRAVERSAL", "O DOCX contém um caminho interno inválido.")


def extract_docx_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(data)) as zf:
            _validate_docx_archive(zf)
            raw = zf.read("word/document.xml")
    except KeyError as exc:
        raise ResumeParseError("DOCX_MISSING_DOCUMENT_XML", "O DOCX não contém o documento principal.") from exc
    except zipfile.BadZipFile as exc:
        raise ResumeParseError("DOCX_CORRUPT", "O DOCX está corrompido.") from exc

    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ResumeParseError("DOCX_XML_UNSAFE", "O DOCX contém construções XML não permitidas.")

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ResumeParseError("DOCX_XML_INVALID", "O XML interno do DOCX é inválido.") from exc

    w_ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for paragraph in root.iter(f"{w_ns}p"):
        pieces: list[str] = []
        for node in paragraph.iter():
            if node.tag == f"{w_ns}t" and node.text:
                pieces.append(node.text)
            elif node.tag == f"{w_ns}tab":
                pieces.append("\t")
            elif node.tag == f"{w_ns}br":
                pieces.append("\n")
        line = _clean_line("".join(pieces))
        if line:
            paragraphs.append(line)

    text = "\n".join(paragraphs)
    if len(text) > MAX_TEXT_CHARS:
        raise ResumeParseError("TEXT_TOO_LARGE", "O texto extraído excede o limite do Beta 1.0.")
    if not text.strip():
        raise ResumeParseError("NO_TEXT", "Não encontramos texto utilizável no DOCX.")
    return _normalize_spaces(text)


def extract_pdf_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ImportError as exc:
        raise ResumeParseError("PDF_DEPENDENCY_MISSING", "O parser PDF não está instalado neste ambiente.") from exc

    try:
        reader = PdfReader(BytesIO(data), strict=True)
    except Exception as exc:
        raise ResumeParseError("PDF_CORRUPT", "O PDF não pôde ser lido com segurança.") from exc

    if getattr(reader, "is_encrypted", False):
        raise ResumeParseError("PDF_PASSWORD_PROTECTED", "PDF protegido por senha não é aceito no Beta 1.0.")

    chunks: list[str] = []
    try:
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                chunks.append(page_text)
    except Exception as exc:
        # pypdf possui exceções específicas, mas falhamos fechado para qualquer erro de parsing.
        raise ResumeParseError("PDF_EXTRACTION_FAILED", "Falha ao extrair texto do PDF.") from exc

    text = _normalize_spaces("\n".join(chunks))
    if len(text) > MAX_TEXT_CHARS:
        raise ResumeParseError("TEXT_TOO_LARGE", "O texto extraído excede o limite do Beta 1.0.")
    if not text:
        raise ResumeParseError("NO_TEXT", "Este PDF não possui texto utilizável. Envie um PDF textual ou DOCX.")
    return text


def _normalized_heading(line: str) -> str:
    line = _clean_line(line).lower().rstrip(":")
    line = re.sub(r"\s+", " ", line)
    return line


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"cabecalho": []}
    current = "cabecalho"
    lookup: dict[str, str] = {}
    for canonical, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            lookup[alias] = canonical

    for raw_line in text.splitlines():
        line = _clean_line(raw_line)
        if not line:
            continue
        heading = _normalized_heading(line)
        if heading in lookup and len(line) <= 60:
            current = lookup[heading]
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def _first_unique(matches: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in matches:
        clean = item.strip().rstrip(".,;)")
        key = clean.lower()
        if clean and key not in seen:
            seen.add(key)
            result.append(clean)
    return result


def _candidate_name(lines: list[str]) -> EvidenceField | None:
    for line in lines[:8]:
        if "@" in line or re.search(r"\d{4}", line) or len(line) > 80:
            continue
        words = line.split()
        if 2 <= len(words) <= 6 and all(re.search(r"[A-Za-zÀ-ÿ]", w) for w in words):
            return EvidenceField(value=line, confidence="MEDIUM", source_excerpt=line, inferred=True)
    return None


def build_candidate_profile_draft(text: str) -> dict[str, Any]:
    sections = split_sections(text)
    header = sections.get("cabecalho", [])

    emails = _first_unique(m.group(1) for m in EMAIL_RE.finditer(text))
    phones = _first_unique(m.group(0) for m in PHONE_RE.finditer(text))
    linkedin = _first_unique(m.group(0) for m in LINKEDIN_RE.finditer(text))
    urls = [u for u in _first_unique(m.group(0) for m in URL_RE.finditer(text)) if "linkedin.com/in/" not in u.lower()]

    draft: dict[str, Any] = {
        "name": None,
        "emails": [],
        "phones": [],
        "linkedin": [],
        "links": [],
        "summary": None,
        "experience_evidence": [],
        "education_evidence": [],
        "skills_evidence": [],
        "languages_evidence": [],
        "certifications_evidence": [],
        "raw_sections": {},
        "requires_user_confirmation": True,
    }

    name = _candidate_name(header)
    if name:
        draft["name"] = asdict(name)

    for value in emails[:5]:
        draft["emails"].append(asdict(EvidenceField(value=value, confidence="HIGH", source_excerpt=_excerpt(text, value))))
    for value in phones[:5]:
        draft["phones"].append(asdict(EvidenceField(value=value, confidence="HIGH", source_excerpt=_excerpt(text, value))))
    for value in linkedin[:5]:
        draft["linkedin"].append(asdict(EvidenceField(value=value, confidence="HIGH", source_excerpt=_excerpt(text, value))))
    for value in urls[:10]:
        draft["links"].append(asdict(EvidenceField(value=value, confidence="HIGH", source_excerpt=_excerpt(text, value))))

    mapping = {
        "resumo": "summary",
        "experiencia": "experience_evidence",
        "formacao": "education_evidence",
        "competencias": "skills_evidence",
        "idiomas": "languages_evidence",
        "certificacoes": "certifications_evidence",
    }
    for section, target in mapping.items():
        lines = sections.get(section, [])
        if not lines:
            continue
        if target == "summary":
            value = "\n".join(lines[:12])
            draft[target] = asdict(EvidenceField(value=value, confidence="HIGH", source_excerpt=value, inferred=False))
        else:
            for line in lines[:80]:
                draft[target].append(asdict(EvidenceField(value=line, confidence="MEDIUM", source_excerpt=line, inferred=False)))

    for key, lines in sections.items():
        if lines:
            draft["raw_sections"][key] = lines[:100]
    return draft


def parse_resume_bytes(data: bytes, filename: str) -> ParseEnvelope:
    real_type = detect_type(data, filename)
    if real_type == "pdf":
        text = extract_pdf_text(data)
    elif real_type == "docx":
        text = extract_docx_text(data)
    else:
        raise ResumeParseError("UNSUPPORTED_REAL_TYPE", "Tipo real do arquivo não suportado.")

    draft = build_candidate_profile_draft(text)
    return ParseEnvelope(
        parser_version=PARSER_VERSION,
        status="DRAFT_REQUIRES_CONFIRMATION",
        document={
            "filename_display": Path(filename).name,
            "detected_type": real_type,
            "size_bytes": len(data),
            "sha256": _sha256(data),
            "text_chars": len(text),
        },
        candidate_profile_draft=draft,
        warnings=[
            "Nenhum campo deste rascunho é considerado confirmado até a ação explícita do usuário.",
            "Nome identificado por heurística permanece como inferência e exige confirmação.",
        ],
    )


def parse_path(path: Path) -> ParseEnvelope:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ResumeParseError("FILE_READ_ERROR", "Não foi possível ler o arquivo.") from exc
    return parse_resume_bytes(data, path.name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LSI Career 360 — parser de currículo Beta 1.0")
    parser.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    try:
        envelope = parse_path(args.file)
    except ResumeParseError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": exc.code, "message": exc.message}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(asdict(envelope), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
