-- Career 360 Beta 1.0 — private quarantine bucket
-- No direct anon/authenticated storage policy is created.
-- Uploads must enter through the authenticated LSI_DOCUMENT_INGEST adapter.

insert into storage.buckets (
  id,
  name,
  public,
  file_size_limit,
  allowed_mime_types
)
values (
  'career-resumes-quarantine',
  'career-resumes-quarantine',
  false,
  10485760,
  array[
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ]::text[]
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;
