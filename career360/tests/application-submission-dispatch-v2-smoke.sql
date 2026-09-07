begin;

do $$
declare
  v_user uuid;
  v_app1 uuid := gen_random_uuid();
  v_app2 uuid := gen_random_uuid();
  v_zero integer;
  v_claim record;
  v_claim2 record;
  v_receipt record;
  v_bad_claim_rejected boolean := false;
begin
  select user_id into v_user
  from public.career_action_permissions
  order by updated_at desc
  limit 1;

  if v_user is null then
    raise exception 'SMOKE_NO_USER';
  end if;

  insert into public.career_applications(
    id,user_id,opportunity_id,status,application_url,evidence_safe,submission_confirmed_at
  ) values (
    v_app1,v_user,null,'awaiting_user',
    'https://jobs.quickin.io/smoke/jobs/test-claim-v2',
    '{}'::jsonb,now()
  );

  select count(*) into v_zero
  from public.career_claim_application_submission(10,600);
  if v_zero <> 0 then
    raise exception 'SMOKE_PERMISSION_OFF_CLAIMED_%',v_zero;
  end if;

  update public.career_action_permissions
  set allow_application_submit=true, updated_at=now()
  where user_id=v_user;

  select * into v_claim
  from public.career_claim_application_submission(10,600)
  limit 1;

  if v_claim.application_id is distinct from v_app1 or v_claim.claim_token is null then
    raise exception 'SMOKE_EXPECTED_SINGLE_CLAIM';
  end if;

  select * into v_receipt
  from public.career_record_application_submission_receipt_v2(
    v_user,
    v_app1,
    v_claim.claim_token,
    'quickin',
    'SMOKE-EXT-REF-CLAIM-V2',
    now(),
    null
  )
  limit 1;

  if v_receipt.new_status <> 'applied' or v_receipt.idempotent then
    raise exception 'SMOKE_RECEIPT_FIRST_WRITE_FAILED';
  end if;

  if (select submission_dispatch_state from public.career_applications where id=v_app1) <> 'receipt_confirmed' then
    raise exception 'SMOKE_RECEIPT_STATE_FAILED';
  end if;

  select * into v_receipt
  from public.career_record_application_submission_receipt_v2(
    v_user,
    v_app1,
    v_claim.claim_token,
    'quickin',
    'SMOKE-EXT-REF-CLAIM-V2',
    now(),
    null
  )
  limit 1;

  if not v_receipt.idempotent then
    raise exception 'SMOKE_RECEIPT_IDEMPOTENCE_FAILED';
  end if;

  insert into public.career_applications(
    id,user_id,opportunity_id,status,application_url,evidence_safe,submission_confirmed_at
  ) values (
    v_app2,v_user,null,'awaiting_user',
    'https://jobs.quickin.io/smoke/jobs/test-bad-claim',
    '{}'::jsonb,now()
  );

  select * into v_claim2
  from public.career_claim_application_submission(10,600)
  where application_id=v_app2
  limit 1;

  if v_claim2.claim_token is null then
    raise exception 'SMOKE_SECOND_CLAIM_MISSING';
  end if;

  begin
    perform *
    from public.career_record_application_submission_receipt_v2(
      v_user,
      v_app2,
      'definitely-wrong-claim',
      'quickin',
      'SMOKE-EXT-REF-BAD-CLAIM',
      now(),
      null
    );
  exception when others then
    if position('APPLICATION_SUBMISSION_CLAIM_MISMATCH' in sqlerrm) > 0 then
      v_bad_claim_rejected := true;
    else
      raise;
    end if;
  end;

  if not v_bad_claim_rejected then
    raise exception 'SMOKE_BAD_CLAIM_NOT_REJECTED';
  end if;
end $$;

rollback;
