create or replace function public.career_log_match_activity()
returns trigger language plpgsql security definer set search_path=public as $$
begin
  if new.classification in ('QUALIFIED','QUALIFIED_SALARY_CONFIRM') and (tg_op='INSERT' or old.classification is distinct from new.classification) then
    insert into public.career_activity_ledger(user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe,importance,metadata_safe,occurred_at)
    select new.user_id,'opportunity_qualified','qualified','career_agent','career_opportunities',new.opportunity_id,'Nova oportunidade qualificada',coalesce(o.title,'Oportunidade')||' · '||coalesce(o.employer_name,'Empresa não informada'),'high',jsonb_build_object('score',new.score,'classification',new.classification,'engine_version',new.engine_version,'salary_state',new.salary_state),now()
    from public.career_opportunities o where o.id=new.opportunity_id;
  end if;
  return new;
end;$$;
revoke all on function public.career_log_match_activity() from public,anon,authenticated;
create trigger trg_career_match_activity after insert or update of classification on public.career_matches for each row execute function public.career_log_match_activity();

create or replace function public.career_log_application_activity()
returns trigger language plpgsql security definer set search_path=public as $$
declare v_title text; v_importance text := 'normal';
begin
  if tg_op='INSERT' or old.status is distinct from new.status then
    v_title:=case new.status when 'draft_ready' then 'Candidatura preparada' when 'awaiting_user' then 'Candidatura aguardando você' when 'applied' then 'Candidatura enviada' when 'recruiter_reply' then 'Empresa respondeu' when 'interview_pending' then 'Entrevista em andamento' when 'interview_confirmed' then 'Entrevista confirmada' when 'finalist' then 'Você avançou para finalista' when 'offer' then 'Proposta recebida' when 'hired' then 'Contratação confirmada' when 'rejected' then 'Processo encerrado' else 'Processo seletivo atualizado' end;
    v_importance:=case when new.status in ('recruiter_reply','interview_pending','interview_confirmed','finalist','offer','hired') then 'high' when new.status='awaiting_user' then 'critical' else 'normal' end;
    insert into public.career_activity_ledger(user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe,importance,metadata_safe,occurred_at)
    values(new.user_id,'application_'||new.status,new.status,'career_agent','career_applications',new.id,v_title,null,v_importance,jsonb_build_object('opportunity_id',new.opportunity_id),coalesce(new.last_activity_at,now()));
    if new.status='awaiting_user' then
      insert into public.career_notifications(user_id,kind,title,body,source_event_key,action_type,action_payload_safe)
      values(new.user_id,'action_required',v_title,'Há uma ação necessária para continuar esta candidatura.','application:'||new.id::text||':awaiting_user','open_application',jsonb_build_object('application_id',new.id))
      on conflict(user_id,source_event_key) do update set title=excluded.title,body=excluded.body,status='unread';
    end if;
  end if;
  return new;
end;$$;
revoke all on function public.career_log_application_activity() from public,anon,authenticated;
create trigger trg_career_application_activity after insert or update of status on public.career_applications for each row execute function public.career_log_application_activity();

create or replace function public.career_log_mail_activity()
returns trigger language plpgsql security definer set search_path=public as $$
begin
  if tg_op='INSERT' or old.status is distinct from new.status then
    insert into public.career_activity_ledger(user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe,importance,metadata_safe,occurred_at)
    values(new.user_id,case when new.direction='inbound' then 'mail_received' when new.status='sent' then 'mail_sent' else 'mail_'||new.status end,new.status,case when new.direction='inbound' then 'external' else 'career_agent' end,'career_mail_actions',new.id,case when new.direction='inbound' then coalesce(new.sender_display,'Empresa')||' enviou uma mensagem' when new.status='draft_ready' then 'Resposta sugerida preparada' when new.status='sent' then 'Resposta enviada' else 'E-mail atualizado' end,new.summary_safe,case when new.critical then 'critical' when new.requires_human then 'high' else 'normal' end,jsonb_build_object('message_kind',new.message_kind,'requires_human',new.requires_human,'sensitive_category',new.sensitive_category),coalesce(new.received_at,new.sent_at,now()));
  end if;
  return new;
end;$$;
revoke all on function public.career_log_mail_activity() from public,anon,authenticated;
create trigger trg_career_mail_activity after insert or update of status on public.career_mail_actions for each row execute function public.career_log_mail_activity();