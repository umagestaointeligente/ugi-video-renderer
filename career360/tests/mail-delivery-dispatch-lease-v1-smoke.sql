-- Career 360 — mail delivery dispatch lease V1 smoke
-- Non-delivery database contract test. Uses fake .invalid recipients, restores controls and deletes all fixture rows.

create temp table if not exists mail_dispatch_smoke_result(
  test text primary key,
  pass boolean,
  detail text
) on commit preserve rows;
truncate mail_dispatch_smoke_result;

do $$
declare
  v_user uuid;
  v_a uuid:=gen_random_uuid();
  v_b uuid:=gen_random_uuid();
  v_token text;
  v_recipient text;
  v_status text;
  v_idem boolean;
  v_count integer;
  old_bridge text;
  old_delivery text;
begin
  select user_id into v_user from public.career_action_permissions order by updated_at desc limit 1;
  if v_user is null then raise exception 'NO_PILOT_USER'; end if;
  select status into old_bridge from public.career_engine_control where component='mail_background_bridge';
  select status into old_delivery from public.career_engine_control where component='mail_delivery';

  insert into public.career_mail_actions(id,user_id,direction,message_kind,subject_safe,proposed_reply,status,requires_human)
  values
    (v_a,v_user,'outbound','followup','Career 360 smoke','Mensagem de smoke que nunca sai do banco.','approved',true),
    (v_b,v_user,'outbound','followup','Career 360 lease smoke','Mensagem de lease que nunca sai do banco.','approved',true);
  insert into public.career_activity_ledger(user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe)
  values
    (v_user,'mail_approved','mail_decision','user','career_mail_actions',v_a,'Smoke approval','Transactional smoke'),
    (v_user,'mail_approved','mail_decision','user','career_mail_actions',v_b,'Smoke approval','Transactional smoke');

  perform public.career_set_mail_recipient(v_user,v_a,'dispatch-smoke@example.invalid');
  perform public.career_set_mail_recipient(v_user,v_b,'lease-smoke@example.invalid');
  insert into mail_dispatch_smoke_result values('encrypted_recipient',
    (select recipient_email_ciphertext is not null and recipient_email_hash is not null and position('dispatch-smoke@example.invalid' in row_to_json(m)::text)=0 from public.career_mail_actions m where id=v_a),
    'raw recipient absent from row json; ciphertext/hash present');

  begin
    perform * from public.career_claim_mail_delivery(v_user,v_a,300);
    insert into mail_dispatch_smoke_result values('paused_gate',false,'claim unexpectedly passed while controls paused');
  exception when others then
    insert into mail_dispatch_smoke_result values('paused_gate',position('NOT_ACTIVE' in sqlerrm)>0,left(sqlerrm,180));
  end;

  update public.career_engine_control set status='active' where component in ('mail_background_bridge','mail_delivery');

  select claim_token,recipient_email into v_token,v_recipient from public.career_claim_mail_delivery(v_user,v_a,300);
  insert into mail_dispatch_smoke_result values('claim_ready',
    v_token is not null and length(v_token)>=32 and v_recipient='dispatch-smoke@example.invalid' and (select status='dispatching' and delivery_attempt_count=1 from public.career_mail_actions where id=v_a),
    'claim token transient; recipient decrypted only by service RPC');

  begin
    perform * from public.career_claim_mail_delivery(v_user,v_a,300);
    insert into mail_dispatch_smoke_result values('double_claim_blocked',false,'second claim unexpectedly passed');
  exception when others then
    insert into mail_dispatch_smoke_result values('double_claim_blocked',position('ALREADY_CLAIMED' in sqlerrm)>0,left(sqlerrm,180));
  end;

  begin
    perform * from public.career_record_mail_delivery_receipt_v2(v_user,v_a,'wrong-token','gmail','m-smoke','t-smoke',now());
    insert into mail_dispatch_smoke_result values('wrong_token_blocked',false,'wrong token unexpectedly passed');
  exception when others then
    insert into mail_dispatch_smoke_result values('wrong_token_blocked',position('TOKEN_MISMATCH' in sqlerrm)>0,left(sqlerrm,180));
  end;

  select new_status,idempotent into v_status,v_idem from public.career_record_mail_delivery_receipt_v2(v_user,v_a,v_token,'gmail','m-smoke','t-smoke',now());
  insert into mail_dispatch_smoke_result values('receipt_to_sent',v_status='sent' and v_idem=false and (select status='sent' and sent_at is not null and delivery_receipt_hash is not null from public.career_mail_actions where id=v_a),'provider receipt required');

  select new_status,idempotent into v_status,v_idem from public.career_record_mail_delivery_receipt_v2(v_user,v_a,v_token,'gmail','m-smoke','t-smoke',now());
  insert into mail_dispatch_smoke_result values('receipt_replay_idempotent',v_status='sent' and v_idem=true,'same receipt replay does not duplicate state');

  select claim_token into v_token from public.career_claim_mail_delivery(v_user,v_b,120);
  update public.career_mail_actions set delivery_claim_expires_at=now()-interval '1 second' where id=v_b;
  select count(*) into v_count from public.career_claim_mail_delivery(v_user,v_b,120);
  insert into mail_dispatch_smoke_result values('expired_lease_uncertain',v_count=0 and (select status='delivery_uncertain' from public.career_mail_actions where id=v_b),'expired lease persists uncertain and yields no new claim');

  insert into mail_dispatch_smoke_result values('legacy_v1_retired',not has_function_privilege('service_role','public.career_record_mail_delivery_receipt(uuid,uuid,text,text,text,timestamptz)','EXECUTE'),'V1 cannot bypass claim route');

  delete from public.career_activity_ledger where entity_type='career_mail_actions' and entity_id in (v_a,v_b);
  delete from public.career_mail_actions where id in (v_a,v_b);
  update public.career_engine_control set status=old_bridge where component='mail_background_bridge';
  update public.career_engine_control set status=old_delivery where component='mail_delivery';
end $$;

select test,pass,detail from mail_dispatch_smoke_result order by test;
