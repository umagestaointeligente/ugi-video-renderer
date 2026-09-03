#!/usr/bin/env python3

import io
import unittest
import zipfile

from resume_parser import (
    ResumeParseError,
    build_candidate_profile_draft,
    detect_type,
    extract_docx_text,
    parse_resume_bytes,
)


def make_docx(paragraphs):
    content_types = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''
    ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    body = ''.join(f'<w:p><w:r><w:t>{p}</w:t></w:r></w:p>' for p in paragraphs)
    document = f'''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="{ns}"><w:body>{body}</w:body></w:document>'''.encode()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', content_types)
        zf.writestr('word/document.xml', document)
    return buf.getvalue()


class ResumeParserTests(unittest.TestCase):
    def test_docx_valid_and_draft_requires_confirmation(self):
        data = make_docx([
            'Maria Silva',
            'maria@example.com | (21) 99999-1111',
            'Experiência Profissional',
            'Gerente Comercial — Empresa Exemplo — 2022–Atual',
            'Formação',
            'Administração — Universidade Exemplo',
            'Competências',
            'Negociação',
            'Liderança',
        ])
        result = parse_resume_bytes(data, 'curriculo.docx')
        self.assertEqual(result.status, 'DRAFT_REQUIRES_CONFIRMATION')
        self.assertEqual(result.document['detected_type'], 'docx')
        self.assertTrue(result.candidate_profile_draft['requires_user_confirmation'])
        self.assertEqual(result.candidate_profile_draft['emails'][0]['value'], 'maria@example.com')
        self.assertFalse(result.candidate_profile_draft['emails'][0]['user_confirmed'])
        self.assertTrue(result.candidate_profile_draft['experience_evidence'])

    def test_extension_mismatch_fails_closed(self):
        with self.assertRaises(ResumeParseError) as ctx:
            detect_type(b'%PDF-1.7\n', 'arquivo.docx')
        self.assertEqual(ctx.exception.code, 'TYPE_MISMATCH')

    def test_unknown_extension_blocked(self):
        with self.assertRaises(ResumeParseError) as ctx:
            detect_type(b'qualquer coisa', 'arquivo.exe')
        self.assertEqual(ctx.exception.code, 'EXTENSION_NOT_ALLOWED')

    def test_empty_file_blocked(self):
        with self.assertRaises(ResumeParseError) as ctx:
            detect_type(b'', 'arquivo.pdf')
        self.assertEqual(ctx.exception.code, 'EMPTY_FILE')

    def test_docx_requires_real_word_container(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('foo.txt', 'bar')
        with self.assertRaises(ResumeParseError) as ctx:
            detect_type(buf.getvalue(), 'arquivo.docx')
        self.assertEqual(ctx.exception.code, 'TYPE_MISMATCH')

    def test_docx_path_traversal_blocked(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml', '<Types/>')
            zf.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body/></w:document>')
            zf.writestr('../escape.txt', 'x')
        with self.assertRaises(ResumeParseError) as ctx:
            extract_docx_text(buf.getvalue())
        self.assertEqual(ctx.exception.code, 'DOCX_PATH_TRAVERSAL')

    def test_docx_dtd_entity_blocked(self):
        content_types = b'<Types/>'
        malicious = b'''<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>&xxe;</w:t></w:r></w:p></w:body></w:document>'''
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('[Content_Types].xml', content_types)
            zf.writestr('word/document.xml', malicious)
        with self.assertRaises(ResumeParseError) as ctx:
            extract_docx_text(buf.getvalue())
        self.assertEqual(ctx.exception.code, 'DOCX_XML_UNSAFE')

    def test_name_heuristic_is_not_fact(self):
        draft = build_candidate_profile_draft('João da Silva\njoao@example.com')
        self.assertEqual(draft['name']['value'], 'João da Silva')
        self.assertTrue(draft['name']['inferred'])
        self.assertFalse(draft['name']['user_confirmed'])

    def test_sensitive_fields_are_not_in_draft_schema(self):
        draft = build_candidate_profile_draft('Ana Souza\nExperiência\nGerente — Empresa X')
        forbidden = {'age', 'race', 'religion', 'health', 'political_opinion', 'sexual_orientation'}
        self.assertTrue(forbidden.isdisjoint(draft.keys()))


if __name__ == '__main__':
    unittest.main()
