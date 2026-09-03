-- Career 360 Beta 1.0 — covering indexes for FK paths
create index if not exists idx_career_drafts_document_id
  on public.career_profile_drafts(document_id)
  where document_id is not null;

create index if not exists idx_career_facts_draft_id
  on public.career_confirmed_facts(draft_id)
  where draft_id is not null;

create index if not exists idx_career_facts_source_document_id
  on public.career_confirmed_facts(source_document_id)
  where source_document_id is not null;
