-- LSI Career 360 — idempotência do parser V1

begin;

create unique index if not exists uq_career_draft_document_parser
  on public.career_profile_drafts(document_id, parser_version)
  where document_id is not null;

commit;
