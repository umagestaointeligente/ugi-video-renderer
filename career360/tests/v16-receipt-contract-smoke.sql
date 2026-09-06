-- Career 360 V16 — receipt contract smoke
-- Safe to run against a configured environment: all test rows are rolled back.
-- Requires at least one auth.users row.

begin;
create temp table _career_receipt_test(name text primary key, passed boolean, detail text) on commit drop;

do $$
declare
  v_uid uuid;
  v_mail uuid;
  v_app uuid;
  r record;
  v_bad boolean := false;
begin
  select id into v_uid from auth.users order by created_at asc limit 1;
  if v_uid is null then raise exception 'NO_AUTH_USER_FOR_TEST'; end if;

  insert into public.career_mail_actions(user_id,direction,message_kind,status)
  values(v_uid,'draft','other','approved') returning id into v_mail;
  select * into r from public.career_record_mail_delivery_receipt(v_uid,v_mail,'gmail','test-msg-v16','test-thread-v16',now());
  insert into _career_receipt_test values('delivery_first', r.new_status='sent' and r.idempotent=false, r.new_status||':'||r.idempotent::text);
  select * into r from public.career_record_mail_delivery_receipt(v_uid,v_mail,'gmail','test-msg-v16','test-thread-v16',now());
  insert into _career_receipt_test values('delivery_idempotent', r.new_status='sent' and r.idempotent=true, r.new_status||':'||r.idempotent::text);

  select * into r from public.career_record_inbound_mail_event(v_uid,'gmail','test-in-msg-v16','test-in-thread-v16',now(),'Test Sender','Test Subject','Test Summary','recruiter',false,false,null,null);
  insert into _career_receipt_test values('inbound_first', r.event_status='detected' and r.idempotent=false, r.event_status||':'||r.idempotent::text);
  select * into r from public.career_record_inbound_mail_event(v_uid,'gmail','test-in-msg-v16','test-in-thread-v16',now(),'Test Sender','Test Subject','Test Summary','recruiter',false,false,null,null);
  insert into _career_receipt_test values('inbound_idempotent', r.event_status='detected' and r.idempotent=true, r.event_status||':'||r.idempotent::text);

  insert into public.career_applications(user_id,status) values(v_uid,'considered') returning id into v_app;
  select * into r from public.career_record_application_milestone(v_uid,v_app,'recruiter_reply','gmail','test-app-event-v16',now());
  insert into _career_receipt_test values('milestone_first', r.new_status='recruiter_reply' and r.idempotent=false, r.new_status||':'||r.idempotent::text);
  select * into r from public.career_record_application_milestone(v_uid,v_app,'recruiter_reply','gmail','test-app-event-v16',now());
  insert into _career_receipt_test values('milestone_idempotent', r.new_status='recruiter_reply' and r.idempotent=true, r.new_status||':'||r.idempotent::text);

  begin
    insert into public.career_mail_actions(user_id,direction,message_kind,status,received_at)
    values(v_uid,'inbound','other','detected',now());
  exception when check_violation then v_bad := true;
  end;
  insert into _career_receipt_test values('reject_inbound_without_ids',v_bad,case when v_bad then 'CHECK_REJECTED' else 'UNEXPECTED_ACCEPT' end);

  v_bad := false;
  begin
    insert into public.career_mail_actions(user_id,direction,message_kind,status,mail_provider,sent_at)
    values(v_uid,'outbound','other','sent','gmail',now());
  exception when check_violation then v_bad := true;
  end;
  insert into _career_receipt_test values('reject_sent_without_receipt',v_bad,case when v_bad then 'CHECK_REJECTED' else 'UNEXPECTED_ACCEPT' end);

  v_bad := false;
  begin
    insert into public.career_applications(user_id,status,external_status_provider,external_status_observed_at)
    values(v_uid,'offer','gmail',now());
  exception when check_violation then v_bad := true;
  end;
  insert into _career_receipt_test values('reject_milestone_without_ref',v_bad,case when v_bad then 'CHECK_REJECTED' else 'UNEXPECTED_ACCEPT' end);
end $$;

-- Expect 9 rows, all passed=true.
select name,passed,detail from _career_receipt_test order by name;

rollback;
