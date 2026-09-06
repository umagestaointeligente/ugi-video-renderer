-- Career 360 V16 — Application Submission Receipt smoke
-- Transactional by design: must leave zero persistent application/follow-up/mail test data.

begin;

create temporary table _receipt_smoke(user_id uuid, opportunity_id uuid, application_id uuid);
insert into _receipt_smoke(user_id,opportunity_id)
select u.id,o.id
from auth.users u
cross join public.career_opportunities o
where o.status='active'
limit 1;

insert into public.career_applications(user_id,opportunity_id,status,evidence_safe)
select user_id,opportunity_id,'awaiting_user','{}'::jsonb
from _receipt_smoke;

update _receipt_smoke s
set application_id=(
  select ca.id
  from public.career_applications ca
  where ca.user_id=s.user_id and ca.opportunity_id=s.opportunity_id
);

create temporary table _receipt_results(test text, pass boolean, detail text);

insert into _receipt_results
select 'first_receipt',
       (r.new_status='applied' and r.idempotent=false and r.followup_id is not null),
       r.new_status||':'||r.idempotent::text||':'||(r.followup_id is not null)::text
from _receipt_smoke s
cross join lateral public.career_record_application_submission_receipt(
  s.user_id,s.application_id,'smoke-provider','external-ref-001',
  now()-interval '1 minute',now()+interval '1 day'
) r;

insert into _receipt_results
select 'idempotent_replay',
       (r.new_status='applied' and r.idempotent=true and r.followup_id is not null),
       r.new_status||':'||r.idempotent::text||':'||(r.followup_id is not null)::text
from _receipt_smoke s
cross join lateral public.career_record_application_submission_receipt(
  s.user_id,s.application_id,'smoke-provider','external-ref-001',
  now()-interval '1 minute',now()+interval '1 day'
) r;

insert into _receipt_results
select 'hash_not_raw_ref',
       (ca.external_application_ref_hash is not null
        and ca.external_application_ref_hash<>'external-ref-001'
        and length(ca.external_application_ref_hash)=64),
       left(ca.external_application_ref_hash,8)||'...'
from _receipt_smoke s
join public.career_applications ca on ca.id=s.application_id;

insert into _receipt_results
select 'provider_safe_metadata',
       (ca.evidence_safe->>'submission_provider'='smoke-provider'
        and ca.evidence_safe::text not like '%external-ref-001%'),
       ca.evidence_safe->>'submission_provider'
from _receipt_smoke s
join public.career_applications ca on ca.id=s.application_id;

insert into _receipt_results
select 'followup_single_idempotent',count(*)=1,count(*)::text
from _receipt_smoke s
join public.career_followups f on f.application_id=s.application_id;

insert into _receipt_results
select 'no_mail_side_effect',count(*)=0,count(*)::text
from public.career_mail_actions;

do $$
declare s record;
begin
  select * into s from _receipt_smoke limit 1;
  begin
    perform * from public.career_record_application_submission_receipt(
      s.user_id,s.application_id,'smoke-provider','different-ref',now(),null
    );
    insert into _receipt_results values('conflicting_receipt_rejected',false,'NOT_REJECTED');
  exception when others then
    insert into _receipt_results values(
      'conflicting_receipt_rejected',
      position('APPLICATION_SUBMISSION_RECEIPT_CONFLICT' in sqlerrm)>0,
      left(sqlerrm,120)
    );
  end;
end $$;

select test,pass,detail from _receipt_results order by test;

rollback;
