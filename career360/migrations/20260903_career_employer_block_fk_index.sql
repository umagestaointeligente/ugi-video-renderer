begin;
create index if not exists idx_career_blocks_employer_entity_id
  on public.career_employer_blocks(employer_entity_id)
  where employer_entity_id is not null;
commit;
