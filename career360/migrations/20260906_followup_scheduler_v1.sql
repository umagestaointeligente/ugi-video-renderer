-- Career 360 — Follow-up Scheduler V1
-- Infrastructure-only scheduler. It never sends mail and never invents application state.
-- A follow-up requires an explicit due_at and an already receipt-backed application status='applied'.

create table if not exists public.career_followups (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  application_id uuid not null references public.career_applications(id) on delete cascade,
  followup_kind text not null default 'application_followup',
  due_at timestamptz not null,
  status text not null default 'scheduled',
  reason_code text,
  requires_connector boolean not null default true,
  last_evaluated_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint career_followups_kind_check
    check (followup_kind in ('application_followup')),
  constraint career_followups_status_check
    check (status in (
      'scheduled',
      'due_waiting_permission',
      'due_waiting_connector',
      'due_ready_for_orchestration',
      'completed',
      'cancelled'
    ))
);

create unique index if not exists uq_career_followups_user_app_kind_due
  on public.career_followups(user_id, application_id, followup_kind, due_at);

create index if not exists idx_career_followups_due_status
  on public.career_followups(status, due_at);

create index if not exists idx_career_followups_user_due
  on public.career_followups(user_id, due_at desc);

alter table public.career_followups enable row level security;

revoke all on table public.career_followups from public, anon, authenticated;
grant select on table public.career_followups to authenticated;
grant select, insert, update, delete on table public.career_followups to service_role;

drop policy if exists career_followups_select_own on public.career_followups;
create policy career_followups_select_own
  on public.career_followups
  for select
  to authenticated
  using (auth.uid() = user_id);

comment on table public.career_followups is
  'Fail-closed follow-up schedule. Tracks due intent only; it does not create drafts or send email.';

insert into public.career_engine_control(component,champion_version,rollback_version,status,notes_safe)
values(
  'mail_delivery',
  'none',
  null,
  'paused',
  jsonb_build_object(
    'reason','MAIL_DELIVERY_CONNECTOR_NOT_LIVE',
    'contract','provider receipt required before sent',
    'updated_by','followup-scheduler-v1'
  )
)
on conflict (component) do nothing;

insert into public.career_engine_control(component,champion_version,rollback_version,status,notes_safe)
values(
  'followup_scheduler',
  'v1.0',
  null,
  'active',
  jsonb_build_object(
    'mode','due-intent-only',
    'delivery_side_effects',false,
    'explicit_due_at_required',true,
    'permission_gate','allow_followup_draft',
    'connector_gate','career_engine_control.mail_delivery'
  )
)
on conflict (component) do nothing;

create or replace function public.career_schedule_followup(
  p_user_id uuid,
  p_application_id uuid,
  p_due_at timestamptz,
  p_followup_kind text default 'application_followup'
)
returns table(followup_id uuid, followup_status text, idempotent boolean)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_kind text := lower(btrim(coalesce(p_followup_kind,'application_followup')));
  v_app public.career_applications%rowtype;
  v_id uuid;
  v_status text;
begin
  if p_user_id is null or p_application_id is null or p_due_at is null then
    raise exception 'FOLLOWUP_REQUIRED_FIELDS_MISSING';
  end if;
  if v_kind <> 'application_followup' then
    raise exception 'FOLLOWUP_KIND_NOT_SUPPORTED';
  end if;

  select * into v_app
  from public.career_applications
  where id=p_application_id and user_id=p_user_id;

  if not found then
    raise exception 'APPLICATION_NOT_FOUND';
  end if;
  if v_app.status <> 'applied' then
    raise exception 'APPLICATION_NOT_WAITING_FOR_FOLLOWUP';
  end if;
  if v_app.applied_at is null or v_app.external_application_ref_hash is null then
    raise exception 'APPLICATION_RECEIPT_NOT_PROVEN';
  end if;
  if p_due_at < v_app.applied_at then
    raise exception 'FOLLOWUP_DUE_BEFORE_APPLICATION';
  end if;

  insert into public.career_followups(user_id,application_id,followup_kind,due_at,status,reason_code)
  values(p_user_id,p_application_id,v_kind,p_due_at,'scheduled',null)
  on conflict (user_id,application_id,followup_kind,due_at) do nothing
  returning id,status into v_id,v_status;

  if v_id is not null then
    insert into public.career_activity_ledger(
      user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe,importance,metadata_safe,occurred_at
    ) values (
      p_user_id,'followup_scheduled','followup','system','career_followups',v_id,
      'Follow-up agendado',
      'Um prazo de follow-up foi registrado. Nenhum e-mail foi criado ou enviado.',
      'normal',jsonb_build_object('application_id',p_application_id,'due_at',p_due_at),now()
    );
    return query select v_id,v_status,false;
    return;
  end if;

  select id,status into v_id,v_status
  from public.career_followups
  where user_id=p_user_id
    and application_id=p_application_id
    and followup_kind=v_kind
    and due_at=p_due_at;

  return query select v_id,v_status,true;
end;
$$;

revoke all on function public.career_schedule_followup(uuid,uuid,timestamptz,text) from public, anon, authenticated;
grant execute on function public.career_schedule_followup(uuid,uuid,timestamptz,text) to service_role;

comment on function public.career_schedule_followup(uuid,uuid,timestamptz,text) is
  'Service-only idempotent scheduler. Requires an applied application with external receipt evidence and an explicit due_at.';

create or replace function public.career_process_due_followups(p_limit integer default 100)
returns table(
  scanned integer,
  ready_for_orchestration integer,
  waiting_permission integer,
  waiting_connector integer,
  cancelled integer
)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_limit integer := greatest(1,least(coalesce(p_limit,100),500));
  v_scanned integer := 0;
  v_ready integer := 0;
  v_wait_permission integer := 0;
  v_wait_connector integer := 0;
  v_cancelled integer := 0;
  v_delivery_active boolean := false;
  v_allow_draft boolean;
  v_new_status text;
  v_reason text;
  v_title text;
  v_summary text;
  f record;
  a record;
begin
  select coalesce(status='active',false) into v_delivery_active
  from public.career_engine_control
  where component='mail_delivery';
  v_delivery_active := coalesce(v_delivery_active,false);

  for f in
    select cf.*
    from public.career_followups cf
    where cf.due_at <= now()
      and cf.status in ('scheduled','due_waiting_permission','due_waiting_connector','due_ready_for_orchestration')
    order by cf.due_at,cf.id
    limit v_limit
    for update skip locked
  loop
    v_scanned := v_scanned + 1;
    v_new_status := null;
    v_reason := null;
    v_title := null;
    v_summary := null;

    select ca.status,ca.last_activity_at into a
    from public.career_applications ca
    where ca.id=f.application_id and ca.user_id=f.user_id;

    if not found then
      v_new_status := 'cancelled';
      v_reason := 'APPLICATION_MISSING';
      v_cancelled := v_cancelled + 1;
    elsif a.status <> 'applied' then
      v_new_status := 'cancelled';
      v_reason := 'APPLICATION_NO_LONGER_WAITING_RESPONSE';
      v_cancelled := v_cancelled + 1;
    else
      select cap.allow_followup_draft into v_allow_draft
      from public.career_action_permissions cap
      where cap.user_id=f.user_id;

      if coalesce(v_allow_draft,false)=false then
        v_new_status := 'due_waiting_permission';
        v_reason := 'FOLLOWUP_DRAFT_NOT_ALLOWED';
        v_wait_permission := v_wait_permission + 1;
        v_title := 'Follow-up chegou ao prazo';
        v_summary := 'O prazo planejado chegou, mas rascunhos de follow-up não estão autorizados. Nenhum e-mail foi criado ou enviado.';
      elsif v_delivery_active=false then
        v_new_status := 'due_waiting_connector';
        v_reason := 'MAIL_DELIVERY_CONNECTOR_NOT_LIVE';
        v_wait_connector := v_wait_connector + 1;
      else
        v_new_status := 'due_ready_for_orchestration';
        v_reason := 'FOLLOWUP_GATES_PASSED';
        v_ready := v_ready + 1;
        v_title := 'Follow-up pronto para preparação';
        v_summary := 'O prazo planejado chegou e os gates atuais permitem preparar o próximo passo. Nenhum e-mail foi enviado.';
      end if;
    end if;

    if f.status is distinct from v_new_status or f.reason_code is distinct from v_reason then
      update public.career_followups
      set status=v_new_status,
          reason_code=v_reason,
          last_evaluated_at=now(),
          updated_at=now()
      where id=f.id;

      insert into public.career_activity_ledger(
        user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe,importance,metadata_safe,occurred_at
      ) values (
        f.user_id,
        'followup_'||v_new_status,
        'followup',
        'system',
        'career_followups',
        f.id,
        case
          when v_new_status='cancelled' then 'Follow-up cancelado'
          when v_new_status='due_waiting_permission' then 'Follow-up aguardando permissão'
          when v_new_status='due_waiting_connector' then 'Follow-up aguardando integração'
          else 'Follow-up pronto para preparação'
        end,
        case
          when v_new_status='cancelled' then 'A candidatura não está mais aguardando este follow-up.'
          when v_new_status='due_waiting_permission' then v_summary
          when v_new_status='due_waiting_connector' then 'O prazo chegou, mas a integração de entrega de e-mail ainda não está LIVE. Nenhum e-mail foi criado ou enviado.'
          else v_summary
        end,
        case when v_new_status='due_waiting_permission' then 'high' else 'normal' end,
        jsonb_build_object('application_id',f.application_id,'reason_code',v_reason,'due_at',f.due_at),
        now()
      );

      if v_new_status in ('due_waiting_permission','due_ready_for_orchestration') then
        insert into public.career_notifications(
          user_id,kind,title,body,source_event_key,action_type,action_payload_safe,status
        ) values (
          f.user_id,
          'action_required',
          v_title,
          v_summary,
          'followup:'||f.id::text||':'||v_new_status,
          'open_application',
          jsonb_build_object('application_id',f.application_id,'followup_id',f.id,'followup_status',v_new_status),
          'unread'
        )
        on conflict(user_id,source_event_key) do update
          set title=excluded.title,
              body=excluded.body,
              action_payload_safe=excluded.action_payload_safe,
              status='unread';
      end if;
    else
      update public.career_followups
      set last_evaluated_at=now(),updated_at=now()
      where id=f.id;
    end if;
  end loop;

  return query select v_scanned,v_ready,v_wait_permission,v_wait_connector,v_cancelled;
end;
$$;

revoke all on function public.career_process_due_followups(integer) from public, anon, authenticated;
grant execute on function public.career_process_due_followups(integer) to service_role;

comment on function public.career_process_due_followups(integer) is
  'Service-only/cron evaluator. It changes only follow-up orchestration state and notifications; it never creates or sends mail.';

-- Internal database cron. No external HTTP call and no mail side effect.
do $$
declare v_job bigint;
begin
  select jobid into v_job from cron.job where jobname='career-followup-evaluator' limit 1;
  if v_job is not null then perform cron.unschedule(v_job); end if;
end $$;

select cron.schedule(
  'career-followup-evaluator',
  '23,53 * * * *',
  $cron$select public.career_process_due_followups(100);$cron$
);
