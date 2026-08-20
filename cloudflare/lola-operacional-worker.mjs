// ============================================================
// LOLA OPERACIONAL UGI v8 R12 VISUAL SELF-REPAIR CAROUSEL
// Command Hub + Central + R2 + Workers AI + Images + Media + Buffer
//
// R7:
// - preserva autenticação LOLA_AUTH_KEY / LOLA_COMMAND_KEY
// - usa AI para texto, imagem e vídeo
// - usa IMAGES para compor carrossel com texto EXATO sobre fundo raster
// - elimina dependência de IA para escrever texto dentro das artes
// - usa VIDEO (Media Transformations binding) para normalizar vídeos em MP4 9:16
// - música permanece como metadata operacional
// - não finge que Media/Buffer anexam música da biblioteca do Instagram
// - retries e fallback resilientes
// - Central de Aprovação multimídia
//
// R9:
// - preserva integralmente o fluxo estável do R8
// - mantém LOLA_AUTH_KEY para administração e LOLA_COMMAND_KEY para Lola UGI
// - adiciona auditoria semântica pós-geração para aderência a área + ângulo + orientação
// - bloqueia valores financeiros/percentuais e regras universais inventadas
// - endurece filtro contra linguagem genérica típica de IA
// - reescreve automaticamente antes de marcar conteúdo para revisão
// - moderniza o carrossel determinístico sem voltar a depender de IA para desenhar texto
// - adiciona letras minúsculas à fonte bitmap, mais espaço negativo e layouts editoriais variados
// R13:
// - mantém autenticação, Command Hub, R2, Central e Buffer da arquitetura estável
// - comando simples passa a ser suficiente: a Lola cria capa, estrutura e fechamento
// - gate editorial agora tenta autocorreção antes de bloquear a geração
// - cada slide recebe uma fotografia/visual exclusivo gerado por IA
// - a IA visual é proibida de escrever; o texto exato entra depois via Images binding
// - tipografia principal usa SVG/Arial/Helvetica, removendo o aspecto de terminal
// - rodapé deixa de usar bitmap com acentos, eliminando "gestão ?" na arte
// - legenda obrigatória entre 130 e 180 palavras
// R14:
// - corrige o gate da capa: literalidade só é exigida quando o briefing traz capa/gancho explícito
// - auditoria semântica vira gate de reparo, não bloqueio cego após os controles determinísticos
// - aumenta o self-repair editorial antes da renderização
// - mantém Browser Run obrigatório para carrossel, sem fallback para fonte de terminal
// - adiciona política musical UGI para Beatly: moderna, atual, profissional e coerente com o tema
// - padroniza a variável de catálogo musical como MUSIC_CATALOG_JSON
// - suporta catálogo Beatly no R2/variável, rotação sem repetição até esgotar o catálogo e reinício de ciclo
// R14.2:
// - MUSIC_CATALOG_JSON passa a ser fonte direta do catálogo; não exige sincronização manual para funcionar
// - adiciona GET /api/music/catalog/status para teste seguro sem expor faixas nem exigir chave
// - POST /api/music/catalog aceita administração ou Lola UGI autenticada para futuras atualizações
// - remove duplicidade do endpoint musicCatalog no /api/health
// R16:
 // - política musical única para Instagram, TikTok e YouTube
 // - relevância contextual e segurança editorial acima de tendência
 // - bloqueio de conteúdo explícito e inadequado ao posicionamento UGI
 // - elegibilidade/licença tratada separadamente por plataforma
 // - até 500 candidatos e fallback automático sem fabricar IDs de áudio
 // - bibliotecas nativas permanecem dependentes de identificação/autorização real da plataforma
// R44.4.4 BUFFER ERROR DIAGNOSTICS:
 // - preserva integralmente R44.4.3 Publication Eligibility e todos os gates já validados
 // - captura Post.error oficial do Buffer (message, rawError, supportUrl)
 // - preserva __typename e payload diagnóstico das respostas GraphQL
 // - /api/platform-publication-status passa a persistir e retornar o erro real de publicação
 // - nenhuma republicação automática é executada por este diagnóstico
// R44.4.10 COMMAND METADATA + LEGACY DRAFT BRIDGE:
 // - preserva contentId/experimentId/variant/commercialIntent em createCommand
 // - propaga metadata para drafts gerados pelo command hub
 // - /api/video-render aceita draftId editorial explícito para recuperar drafts legados
 // - ao receber draftId + content_id, migra o draft legado para o content_id determinístico
 // - evita duplicidade e preserva o id editorial original
// R44.4.9 EXISTING DRAFT -> GITHUB BRIDGE:
 // - /api/video-render reutiliza automaticamente draft existente pelo content_id
 // - não cria segundo draft quando o conteúdo já existe
 // - associa novo renderId ao mesmo draft e preserva seu id original
 // - /api/video-upload e /api/video-status resolvem o draft pelo approvalDraftId salvo no video result
 // - preserva R44.4.8 helper fix, R44.4.7 lookup/metadata pass, Buffer, GitHub e renderer
// R44.4.8 VEO DURATION HELPER FIX:
 // - restaura helper resolveVeoDurationSeconds ausente no baseline
 // - corrige ReferenceError no normalizeContentMetadata para reel/video
 // - preserva R44.4.7 compact draft lookup + metadata pass
 // - nenhuma alteração de endpoint, schema, Buffer, GitHub ou renderer
// R44.4.6 CAROUSEL SLIDE RECOVERY:
// - preserva integralmente publicação, eligibility e diagnostics já validados
// - adiciona recuperação cirúrgica de um único slide em draft de carrossel existente
// - reutiliza o mesmo draftId e nunca cria novo draft durante recovery
// - preserva slides já renderizados no R2 e reconstrói imageUrls/imageKeys em ordem
// - endpoint: POST /api/carousel-slide-recovery
// - nenhuma aprovação, publicação ou agendamento é executado pelo recovery
//
// R44.4 MULTI-PLATFORM PUBLISHING:
 // - preserva renderer R43.4, storage multi-asset, delivery R43.2 e aprovação R43.3
 // - APROVAR continua diferente de PUBLICAR
 // - adiciona publicação/agendamento individual por Instagram, TikTok e YouTube via Buffer GraphQL
 // - modos: shareNow, customScheduled e addToQueue
 // - resolve canais por env explícito ou descoberta segura no Buffer
 // - registra bufferPostId, status, dueAt, sentAt e externalLink por plataforma
 // - adiciona consulta de status pós-publicação para confirmação de entrega
 // - uma falha de plataforma não altera as demais
 //
// R43.3 CENTRAL MULTI-ASSET APPROVAL:
 // - preserva R42.1 renderer, R43.1 storage e R43.2 delivery
 // - Central exibe Instagram, TikTok e YouTube como previews independentes
 // - aprovação/rejeição passa a ser independente por plataforma
 // - decisão de aprovação NÃO publica automaticamente; publicação multi-canal fica para etapa posterior
 // - /api/approve legado continua disponível para posts/carrosséis/reels legados de ativo único
 // - conteúdo multi-asset usa /api/platform-approval
 // - status consolidado: pending_approval | partially_approved | approved | rejected
 //
 // R43.1 WORKER MULTI-ASSET:
 // - /api/video-upload aceita platform=instagram|tiktok|youtube
 // - armazena masters independentes em geradas/videos/{renderId}/{platform}.mp4
 // - resultado agrega assets por plataforma e só fica ready quando os três masters chegam
 // - preserva videoUrl/videoKey legados apontando para Instagram
 // - Central recebe metadata multi-asset; UI/aprovação independente fica para R43.3
 // R37 APPROVAL + COMMERCIAL MVP:
 // - preserva integralmente o R27 e o pipeline audiovisual validado
 // - conecta automaticamente Reel renderizado à Central de Aprovação
 // - adiciona contentId, experimentId, variant, objective, CTA e commercialIntent
 // - preserva histórico aprovado/rejeitado em R2 sem implementar Growth Engine
 // - registra eventos mínimos para futura observabilidade/MET sem classificar performance
 // - Central continua com aprovação humana e Buffer somente após aprovação
// R27 GITHUB -> R2 DELIVERY FINAL:
// - preserva integralmente o R26 e o renderer gratuito GitHub Actions + FFmpeg
// - adiciona renderId único e rastreável por solicitação
// - adiciona POST /api/video-upload para receber MP4 real do GitHub Actions
// - valida segredo dedicado, Content-Length, MIME e assinatura ISO-BMFF/MP4 (ftyp)
// - grava o MP4 no R2 MEDIA em geradas/videos/{renderId}.mp4
// - grava manifesto de resultado em lola/video-results/{renderId}.json e latest.json
// - adiciona GET /api/video-result/{renderId} e GET /api/video-results/latest
// - GitHub nunca recebe credenciais do R2; upload passa pelo Worker
// - mantém Veo/Runway/Pruna apenas como pipeline legado isolado /api/video-test
// R21 VIDEO ROUTING DIAGNOSTIC:
// - preserva integralmente o carrossel 7/7 validado
// - adiciona /api/video-test: rota direta e exclusiva para generateVideoDraft
// - bypass total do renderer de imagem no teste audiovisual
// - mantém cascata de provedores e validação MP4 real do R20
// R20 VIDEO RECOVERY:
// - preserva integralmente o carrossel 7/7 do R19 FINAL CLOSURE
// - isola a correção exclusivamente no pipeline audiovisual
// - tenta Veo 3.1 Fast -> Runway Gen-4.5 -> Pruna P-Video
// - cada provedor usa parâmetros oficiais próprios
// - registra state, URL, MIME, bytes, assinatura MP4 e erro de cada tentativa
// - JPG/PNG/thumbnail nunca são aceitos nem armazenados como vídeo
// - fallback só ocorre entre modelos de vídeo reais, nunca para modelo de imagem
// - mantém música independente e sem inventar faixa/licença
// R19 FINAL CLOSURE:
// - corrige o hard gate "capa explícita não foi preservada"
// - restaura deterministicamente capa/gancho literal antes de bloquear o carrossel
// - restaura CTA literal quando necessário e reaudita o pacote
// - mantém renderização em duas passagens + cooldown/backoff 429
// - mantém validação binária: JPG nunca pode ser contabilizado como vídeo
// - mantém música pendente quando não houver faixa/licença real elegível
// R19:
// - fila de renderização do carrossel em duas passagens, com cooldown global entre cards
// - backoff 429 mais conservador no Browser Run e respeito ao Retry-After
// - reprocessa somente cards que falharam, sem invalidar os cards já renderizados
// - vídeo passa a seguir o formato oficial de resposta do Veo 3.1 Fast
// - valida state/URL/content-type/assinatura MP4 antes de aceitar mídia audiovisual
// - valida também o MP4 após Media Transformations e após gravação no R2
// - remove qualquer possibilidade de JPG/imagem estática ser contabilizada como vídeo
// - separa duração solicitada da duração real suportada pelo Veo (4s/6s/8s)
// - auditoria editorial do vídeo passa a gerar qualityIssues explícitos
// R44.5.4 MATERIAL STORE + COMMERCE ADAPTER + FULFILLMENT:
// - preserva R44.5.3 Commerce/Copy Lock/Exact Copy/Semantic Bridge e todo pipeline audiovisual
// - adiciona Material Store e Product Catalog persistidos no R2 MEDIA
// - adiciona Commerce Adapter fail-closed com Asaas como primeiro provider implementado
// - checkout real exige credencial e payload do provider; nenhum ID/link é fabricado
// - webhook Asaas exige asaas-access-token e só libera fulfillment após status pago confirmado
// - fulfillment gera token opaco temporário e entrega o asset pelo próprio Worker
// - nenhum checkout, webhook ou fulfillment publica conteúdo ou toca no Buffer
// ============================================================

const IG = "6a7896cdb2d9d57743457e33";

// ------------------------------------------------------------
// MODELOS
// ------------------------------------------------------------

const TXT = "@cf/meta/llama-3.1-8b-instruct-fast";
const IMG = "@cf/black-forest-labs/flux-1-schnell";
const VIDEO_MODEL = "google/veo-3.1-fast";
const VIDEO_FALLBACK_MODEL = "runwayml/gen-4.5";
const VIDEO_FALLBACK_MODEL_2 = "pruna/p-video";
const VIDEO_PROVIDER_ORDER = [
  VIDEO_MODEL,
  VIDEO_FALLBACK_MODEL,
  VIDEO_FALLBACK_MODEL_2
];

const VERSION = "lola-v8-r44-5-4-material-store-commerce-adapter-fulfillment-2026-08-20";

// ------------------------------------------------------------
// STORAGE
// ------------------------------------------------------------

const HISTORY_KEY = "lola/editorial-history-v8.json";
const DRAFT_PREFIX = "lola/drafts/";
const COMMAND_PREFIX = "lola/commands/";
const IMAGE_PREFIX = "geradas/posts/";
const CAROUSEL_PREFIX = "geradas/carrosseis/";
const VIDEO_PREFIX = "geradas/videos/";
const VIDEO_RESULT_PREFIX = "lola/video-results/";
const VIDEO_RESULT_LATEST_KEY = `${VIDEO_RESULT_PREFIX}latest.json`;
const APPROVAL_ARCHIVE_PREFIX = "lola/approval-archive/";
const CONTENT_EVENT_PREFIX = "lola/content-events/";
const MATERIAL_PREFIX = "lola/materials/";
const MATERIAL_ASSET_PREFIX = "lola/material-assets/";
const PRODUCT_PREFIX = "lola/products/";
const CHECKOUT_PREFIX = "lola/commerce/checkouts/";
const ORDER_PREFIX = "lola/commerce/orders/";
const DELIVERY_PREFIX = "lola/commerce/deliveries/";
const MATERIAL_ASSET_MAX_BYTES = 25 * 1024 * 1024;
const DELIVERY_TOKEN_TTL_MS = 7 * 24 * 60 * 60 * 1000;
const VIDEO_UPLOAD_MAX_BYTES = 50 * 1024 * 1024; // 50 MB de proteção operacional
const VIDEO_PLATFORMS = ["instagram", "tiktok", "youtube"];
const VIDEO_PLATFORM_DEFAULT_DURATIONS = {
  instagram: 32,
  tiktok: 24,
  youtube: 36
};

const HISTORY_LIMIT = 96;
const DRAFT_LIMIT = 100;
const COMMAND_LIMIT = 100;

// ------------------------------------------------------------
// TEXTO
// ------------------------------------------------------------

const MIN_WORDS = 110;
const MAX_WORDS = 200;
const TARGET_MIN = 135;
const TARGET_MAX = 175;

const BRAND_HASHTAG = "#UmaGestaoInteligente";

const MAX_SEMANTIC_REWRITES = 2;

const CAROUSEL_MIN_WORDS = 130;
const CAROUSEL_MAX_WORDS = 180;
const CAROUSEL_PACKAGE_REPAIRS = 2;

const CAROUSEL_VISUAL_STEPS = 4;
const CAROUSEL_VISUAL_RETRIES = 2;
const CAROUSEL_COVER_MAX_WORDS = 10;
const CAROUSEL_BODY_MAX_WORDS = 34;

const MONEY_OR_PERCENT_PATTERN =
  /(?:R\$\s*\d|US\$\s*\d|€\s*\d|\b\d+(?:[.,]\d+)?\s*(?:reais|real|dólares|dolares|euros|%|por cento)\b)/i;


// ------------------------------------------------------------
// RETRIES
// ------------------------------------------------------------

const FULL_GENERATION_ATTEMPTS = 2;
const CAPTION_REWRITE_ATTEMPTS = 2;
const IMAGE_ATTEMPTS = 2;
const CAROUSEL_ATTEMPTS = 2;
const CAROUSEL_BG_ATTEMPTS = 2;
const VIDEO_ATTEMPTS = 3;

// R19 — estabilidade de renderização Browser Run
const BROWSER_RENDER_ATTEMPTS = 6;
const BROWSER_BASE_BACKOFF_MS = 6000;
const BROWSER_MAX_BACKOFF_MS = 30000;
const CAROUSEL_SLIDE_SPACING_MS = 6500;
const CAROUSEL_FAILED_PASS_COOLDOWN_MS = 18000;
const CAROUSEL_RENDER_PASSES = 2;

// ------------------------------------------------------------
// MÚSICA / BEATLY
// ------------------------------------------------------------

const BEATLY_CATALOG_KEY = "lola/music/beatly-catalog.json";
const BEATLY_HISTORY_KEY = "lola/music/beatly-history.json";
const BEATLY_HISTORY_LIMIT = 600;
const BEATLY_RANDOM_TOP_N = 18;
const BEATLY_MIN_TREND_SCORE = 0.45;

// R15: motor de fontes reais. O Worker não inventa IDs de Instagram.
// MUSIC_CATALOG_JSON pode continuar contendo somente a política UGI.
// Fontes externas reais podem ser conectadas por MUSIC_PROVIDER_URL + MUSIC_PROVIDER_TOKEN.
// O cache operacional fica limitado a 500 faixas e falhas entram em quarentena temporária.
const MUSIC_CACHE_LIMIT = 500;
const MUSIC_FALLBACK_ATTEMPTS = 5;
const MUSIC_UNAVAILABLE_KEY = "lola/music/unavailable.json";
const MUSIC_UNAVAILABLE_TTL_MS = 24 * 60 * 60 * 1000;

// R16: política musical multiplataforma.
// Não presume que uma licença/áudio válido em uma plataforma seja válido nas demais.
// Tendência é critério secundário; aderência editorial e segurança vêm primeiro.
const MUSIC_PLATFORMS = ["instagram", "tiktok", "youtube"];
const MUSIC_EXPLICIT_TERMS = [
  "explicit", "palavrao", "palavrão", "profanity", "sexual",
  "violence", "violent", "aggressive lyrics"
];
const MUSIC_PLATFORM_POLICY = {
  instagram: {
    discovery: "native_professional_trending_and_sound_collection",
    automaticLibraryAttachment: false,
    commercialSafetyRequired: true,
    fallbackRequired: true
  },
  tiktok: {
    discovery: "commercial_music_library",
    automaticLibraryAttachment: false,
    commercialSafetyRequired: true,
    fallbackRequired: true
  },
  youtube: {
    discovery: "shorts_audio_library_or_royalty_free",
    automaticLibraryAttachment: false,
    commercialSafetyRequired: true,
    fallbackRequired: true
  }
};

// ============================================================
// ESTILOS
// ============================================================

const STYLES = [
  "cinematic editorial business photography, realistic people, natural body language",
  "documentary-style small business photography, candid professional action",
  "premium realistic workplace photography, authentic entrepreneur activity",
  "human-centered leadership photography, subtle emotion, natural interaction",
  "executive workspace photography, practical objects, sophisticated composition",
  "realistic small-business operational photography, visible action, natural environment"
];

// ============================================================
// BRIEFS EDITORIAIS
// ============================================================

const BRIEFS = [
  {
    id: "prioridade-criterios",
    area: "priorização e foco",
    angle: "como definir prioridades quando tudo parece urgente",
    hashtags: ["#GestaoDePrioridades", "#FocoNaGestao", BRAND_HASHTAG],
    instruction:
      "Ensine o gestor a comparar demandas por impacto, urgência real, risco e dependências. Mostre como desempatar duas tarefas aparentemente urgentes com um critério aplicável hoje.",
    cta:
      "Qual demanda da sua lista mudaria de posição se você aplicasse esses critérios hoje?"
  },
  {
    id: "delegacao-controle",
    area: "delegação e autonomia",
    angle: "como delegar sem perder o controle",
    hashtags: ["#Delegacao", "#AutonomiaNaGestao", BRAND_HASHTAG],
    instruction:
      "Ensine delegação usando resultado esperado, limite de autonomia e ponto de acompanhamento. Explique que acompanhar não é refazer a tarefa nem pedir atualização o tempo todo.",
    cta:
      "Na próxima delegação, qual desses três pontos você precisa deixar mais claro?"
  },
  {
    id: "processo-retrabalho",
    area: "processos e padronização",
    angle: "como reduzir retrabalho com processos claros",
    hashtags: ["#GestaoDeProcessos", "#Padronizacao", BRAND_HASHTAG],
    instruction:
      "Estruture um processo mínimo com entrada da tarefa, responsável, padrão de conclusão e ponto de conferência. Use um exemplo operacional simples e reconhecível.",
    cta:
      "Qual etapa do seu processo hoje mais precisa de um critério claro de conclusão?"
  },
  {
    id: "reuniao-assincrona",
    area: "reuniões e comunicação",
    angle: "como reduzir reuniões sem perder alinhamento",
    hashtags: ["#ReunioesProdutivas", "#ComunicacaoNaGestao", BRAND_HASHTAG],
    instruction:
      "Explique o que pode virar atualização assíncrona, o que ainda exige conversa ao vivo e qual critério separa os dois casos.",
    cta:
      "Qual reunião da sua semana poderia virar uma atualização objetiva sem perder alinhamento?"
  },
  {
    id: "lideranca-habito",
    area: "liderança de equipe",
    angle: "um pequeno hábito com grande impacto gerencial",
    hashtags: ["#Lideranca", "#GestaoDeEquipe", BRAND_HASHTAG],
    instruction:
      "Escolha um único hábito gerencial de até cinco minutos, diga quando praticá-lo e qual comportamento da equipe ele melhora. O hábito precisa ser observável e repetível.",
    cta:
      "Que pequeno hábito você consegue testar com sua equipe ainda nesta semana?"
  },
  {
    id: "decisao-regra",
    area: "tomada de decisão",
    angle: "uma decisão que líderes ocupados precisam simplificar",
    hashtags: ["#TomadaDeDecisao", "#DecisaoGerencial", BRAND_HASHTAG],
    instruction:
      "Escolha uma decisão recorrente, crie uma regra simples para reduzi-la e inclua uma exceção em que o gestor deve parar e analisar com mais cuidado.",
    cta:
      "Qual decisão recorrente poderia deixar de consumir sua atenção todos os dias?"
  },
  {
    id: "ia-julgamento",
    area: "IA aplicada à gestão",
    angle: "como usar IA sem terceirizar julgamento",
    hashtags: ["#InteligenciaArtificial", "#IANaGestao", BRAND_HASHTAG],
    instruction:
      "Mostre uma tarefa concreta que a IA pode apoiar e deixe explícito o que continua dependendo de validação, contexto e julgamento humano.",
    cta:
      "Em qual tarefa a IA pode acelerar seu trabalho sem assumir a decisão final?"
  },
  {
    id: "rotina-informal",
    area: "organização operacional",
    angle: "como transformar processos informais em rotinas claras",
    hashtags: ["#GestaoOperacional", "#OrganizacaoEmpresarial", BRAND_HASHTAG],
    instruction:
      "Mostre como transformar conhecimento que está apenas na cabeça das pessoas em sequência de passos, responsável e critério de conclusão. Use um exemplo operacional simples.",
    cta:
      "Qual rotina importante ainda depende mais da memória das pessoas do que de um processo claro?"
  },
  {
    id: "gargalo-gestor",
    area: "delegação e autonomia",
    angle: "um sinal de que o gestor virou gargalo da própria empresa",
    hashtags: ["#Delegacao", "#AutonomiaNaGestao", BRAND_HASHTAG],
    instruction:
      "Mostre um sinal observável de gargalo, explique a causa e indique uma mudança de autonomia ou critério que reduza a dependência do gestor.",
    cta:
      "Que decisão pequena ainda está esperando por você sem realmente precisar estar?"
  },
  {
    id: "autonomia-qualidade",
    area: "liderança de equipe",
    angle: "como criar autonomia sem perder padrão de qualidade",
    hashtags: ["#Lideranca", "#GestaoDeEquipe", BRAND_HASHTAG],
    instruction:
      "Explique três níveis de decisão: equipe decide sozinha; decide e comunica; precisa de aprovação. Relacione aprovação a risco, dinheiro, cliente, exceção ou impacto relevante.",
    cta:
      "Sua equipe sabe quais decisões pode tomar sozinha e quais ainda precisam de você?"
  },
  {
    id: "tempo-estrategico",
    area: "produtividade gerencial",
    angle: "como proteger tempo de trabalho estratégico",
    hashtags: ["#ProdutividadeGerencial", "#GestaoDoTempo", BRAND_HASHTAG],
    instruction:
      "Ensine a reservar blocos protegidos, criar uma regra de disponibilidade e separar interrupções que podem ser agrupadas, delegadas ou adiadas.",
    cta:
      "Qual bloco da sua semana você deveria proteger antes que as urgências ocupem tudo?"
  },
  {
    id: "parar-de-fazer",
    area: "melhoria contínua",
    angle: "como decidir o que parar de fazer",
    hashtags: ["#MelhoriaContinua", "#GestaoEficiente", BRAND_HASHTAG],
    instruction:
      "Dê critérios para eliminar, reduzir ou delegar atividades de baixo impacto e diferencie necessidade real de hábito organizacional.",
    cta:
      "Qual atividade continua na rotina mais por costume do que por resultado?"
  },
  {
    id: "erro-gestao",
    area: "melhoria contínua",
    angle: "um erro comum de gestão e como corrigir",
    hashtags: ["#MelhoriaContinua", "#GestaoEficiente", BRAND_HASHTAG],
    instruction:
      "Escolha um erro gerencial específico, mostre uma consequência concreta e ensine uma correção operacional aplicável. Evite erros genéricos sem comportamento observável.",
    cta:
      "Qual comportamento de gestão você precisa corrigir antes que ele vire um problema maior?"
  },
  {
    id: "framework-hoje",
    area: "tomada de decisão",
    angle: "um framework simples que pode ser aplicado hoje",
    hashtags: ["#TomadaDeDecisao", "#DecisaoGerencial", BRAND_HASHTAG],
    instruction:
      "Entregue um framework real de três etapas ou três perguntas. Cada etapa deve produzir uma decisão ou informação diferente.",
    cta:
      "Em qual decisão você pode testar esse framework ainda hoje?"
  },
  {
    id: "principio-lideranca",
    area: "liderança de equipe",
    angle: "um princípio contraintuitivo de liderança",
    hashtags: ["#Lideranca", "#GestaoDeEquipe", BRAND_HASHTAG],
    instruction:
      "Apresente uma crença comum, um contraponto contraintuitivo e explique por que o contraponto funciona em uma situação real de liderança.",
    cta:
      "Que prática de liderança você mantém por hábito, mesmo sem ter certeza de que funciona?"
  },
  {
    id: "diagnostico-tres-perguntas",
    area: "redução de retrabalho",
    angle: "um diagnóstico em três perguntas",
    hashtags: ["#ReducaoDeRetrabalho", "#EficienciaOperacional", BRAND_HASHTAG],
    instruction:
      "Inclua exatamente três perguntas diagnósticas que investiguem causa, responsabilidade e critério de conclusão antes de alterar o processo.",
    cta:
      "Qual dessas três perguntas revelaria mais rapidamente a origem do seu retrabalho hoje?"
  }
];

// ============================================================
// EXPRESSÕES PROIBIDAS
// ============================================================

const BANNED_PATTERNS = [
  /imagine\s+que/i,
  /imagine\s+um/i,
  /imagine\s+uma/i,
  /\ba arte de\b/i,
  /\bo segredo para\b/i,
  /\ba chave para\b/i,
  /\bo caminho para\b/i,
  /a proposta inédita/i,
  /é chamada de/i,
  /visa ajudar/i,
  /a imagem mostra/i,
  /na imagem/i,
  /nesta imagem/i,
  /nesta cena/i,
  /direção visual/i,
  /ângulo obrigatório/i,
  /área editorial/i,
  /imageprompt/i,
  /liberar seu potencial/i,
  /potencial máximo/i,
  /liderança eficaz/i,
  /garante eficiência/i,
  /garantir eficiência/i,
  /alcançar resultados positivos/i,
  /resultados significativos/i,
  /ambiente mais eficiente e produtivo/i,
  /todos trabalham em harmonia/i,
  /funcionários e equipe/i,
  /áreas de expertise/i,
  /antes de implementar a mudança/i,
  /essa revisão evita transformar uma boa intenção/i
];


// ============================================================
// CRITÉRIOS SEMÂNTICOS R9
// ============================================================

function semanticCriterionForBrief(brief) {
  const byId = {
    "prioridade-criterios":
      "O texto deve ensinar comparação entre prioridades usando pelo menos três critérios concretos. Não basta falar genericamente sobre foco.",

    "delegacao-controle":
      "O texto precisa abordar resultado esperado, autonomia e acompanhamento. Delegação não pode virar simples cobrança ou repasse de tarefa.",

    "processo-retrabalho":
      "O método deve conter entrada, responsável, padrão de conclusão e conferência. O texto precisa ligar esses elementos à redução de retrabalho.",

    "reuniao-assincrona":
      "O texto deve diferenciar comunicação assíncrona de reunião ao vivo e fornecer um critério de escolha entre os dois formatos.",

    "lideranca-habito":
      "O conteúdo deve girar em torno de um único hábito pequeno, com momento ou frequência de aplicação e efeito observável. Não transforme o tema em reunião, crise, motivação ou liderança genérica.",

    "decisao-regra":
      "A regra precisa ser baseada em critérios, não em valores monetários, percentuais ou números arbitrários inventados. Deve haver uma exceção clara.",

    "ia-julgamento":
      "A IA deve aparecer como apoio a uma tarefa concreta, enquanto contexto, validação e decisão final continuam explicitamente humanos.",

    "rotina-informal":
      "O texto deve transformar conhecimento informal em sequência de passos, responsável e critério de conclusão, com exemplo operacional.",

    "gargalo-gestor":
      "O texto precisa apresentar um sinal observável de dependência do gestor, explicar a causa e propor uma mudança concreta de autonomia ou critério.",

    "autonomia-qualidade":
      "O texto deve separar decisões que a equipe toma sozinha, decisões que toma e comunica e decisões que exigem aprovação, relacionando aprovação a risco ou impacto relevante.",

    "tempo-estrategico":
      "O conteúdo deve ensinar proteção de blocos estratégicos, regra de disponibilidade e tratamento das interrupções por agrupamento, delegação ou adiamento.",

    "parar-de-fazer":
      "O texto deve fornecer critérios concretos para eliminar, reduzir ou delegar atividades de baixo impacto e diferenciar necessidade real de hábito organizacional.",

    "erro-gestao":
      "O texto precisa nomear um erro gerencial específico, mostrar consequência observável e ensinar uma correção operacional aplicável.",

    "framework-hoje":
      "O conteúdo deve entregar um framework real de três etapas ou três perguntas, e cada etapa precisa produzir informação ou decisão distinta.",

    "principio-lideranca":
      "O texto deve apresentar uma crença comum, um contraponto contraintuitivo e explicar por que esse contraponto funciona em uma situação real de liderança.",

    "diagnostico-tres-perguntas":
      "O texto deve conter exatamente três perguntas diagnósticas que investiguem causa, responsabilidade e critério de conclusão antes de alterar o processo."
  };

  return (
    brief?.semanticMust ||
    byId[brief?.id] ||
    "A legenda deve cumprir diretamente a área, o ângulo e a orientação do briefing, com aplicação prática concreta e sem trocar o assunto por um tema apenas relacionado."
  );
}

async function semanticAudit(
  env,
  brief,
  caption,
  seed
) {
  try {
    const r = await aiAuditJSON(
      env,
      [
        {
          role: "system",
          content: [
            "Você é uma revisora editorial rigorosa da Uma Gestão Inteligente.",
            "Avalie somente a legenda fornecida.",
            "Não reescreva o texto.",
            "Marque aligned=true apenas se a legenda realmente cumprir o ângulo e a orientação do brief.",
            "Marque specific=true apenas se houver aplicação prática concreta, não apenas conselhos genéricos.",
            "Marque inventedRules=true se houver valores financeiros, percentuais, limites, políticas, números ou regras universais inventadas sem base no próprio brief.",
            "Marque genericLanguage=true se houver linguagem promocional, motivacional, vaga, clichê ou típica de texto de IA.",
            "Se houver dúvida relevante, seja conservadora."
          ].join(" ")
        },
        {
          role: "user",
          content: [
            `Área: ${brief.area}.`,
            `Ângulo: ${brief.angle}.`,
            `Orientação: ${brief.instruction}`,
            `Critério obrigatório: ${semanticCriterionForBrief(brief)}`,
            "Legenda:",
            caption
          ].join("\n")
        }
      ],
      seed
    );

    const aligned = !!r?.aligned;
    const specific = !!r?.specific;
    const inventedRules =
      !!r?.inventedRules ||
      MONEY_OR_PERCENT_PATTERN.test(caption);
    const genericLanguage = !!r?.genericLanguage;

    return {
      pass:
        aligned &&
        specific &&
        !inventedRules &&
        !genericLanguage,
      aligned,
      specific,
      inventedRules,
      genericLanguage,
      reason: String(r?.reason || "").trim()
    };
  } catch (error) {
    return {
      pass: false,
      aligned: false,
      specific: false,
      inventedRules:
        MONEY_OR_PERCENT_PATTERN.test(caption),
      genericLanguage: false,
      reason:
        `Auditoria semântica indisponível: ${error?.message || error}`
    };
  }
}

async function semanticRewrite(
  env,
  brief,
  caption,
  audit,
  seed
) {
  const result = await env.AI.run(
    TXT,
    {
      messages: [
        {
          role: "system",
          content: [
            "Você é editora sênior da Uma Gestão Inteligente.",
            "A legenda passou pela revisão estrutural, mas falhou na aderência semântica ou na voz editorial.",
            "Reescreva a legenda inteira corrigindo exatamente os problemas apontados.",
            `Mantenha preferencialmente entre ${TARGET_MIN} e ${TARGET_MAX} palavras.`,
            "Use 4 ou 5 parágrafos curtos.",
            "Não use título interno, Markdown, listas, hashtags ou linguagem meta.",
            "Não invente valores financeiros, percentuais, limites numéricos, políticas ou regras universais.",
            "Evite frases vagas, motivacionais, promocionais e clichês de IA.",
            "Cada parágrafo deve avançar o raciocínio.",
            `Área: ${brief.area}.`,
            `Ângulo: ${brief.angle}.`,
            `Orientação obrigatória: ${brief.instruction}`,
            `Critério semântico obrigatório: ${semanticCriterionForBrief(brief)}`,
            `Fechamento de referência: ${brief.cta}`
          ].join(" ")
        },
        {
          role: "user",
          content: [
            `aligned: ${audit?.aligned}`,
            `specific: ${audit?.specific}`,
            `inventedRules: ${audit?.inventedRules}`,
            `genericLanguage: ${audit?.genericLanguage}`,
            `Motivo da reprovação: ${audit?.reason || "não informado"}`,
            "Legenda atual:",
            caption,
            "Retorne somente a legenda final corrigida."
          ].join("\n")
        }
      ],
      max_tokens: 1000,
      temperature: 0.18,
      repetition_penalty: 1.15,
      frequency_penalty: 0.5,
    }
  );

  return result?.response || caption;
}

async function aiAuditJSON(
  env,
  messages,
  seed
) {
  let result;

  try {
    result = await env.AI.run(
      TXT,
      {
        messages,
        max_tokens: 350,
        temperature: 0.05,
        response_format: {
          type: "json_schema",
          json_schema: {
            type: "object",
            properties: {
              aligned: { type: "boolean" },
              specific: { type: "boolean" },
              inventedRules: { type: "boolean" },
              genericLanguage: { type: "boolean" },
              reason: { type: "string" }
            },
            required: [
              "aligned",
              "specific",
              "inventedRules",
              "genericLanguage",
              "reason"
            ],
            additionalProperties: false
          }
        }
      }
    );
  } catch {
    result = await env.AI.run(
      TXT,
      {
        messages: [
          ...messages,
          {
            role: "user",
            content:
              'Retorne somente JSON válido: {"aligned":true,"specific":true,"inventedRules":false,"genericLanguage":false,"reason":"..."}'
          }
        ],
        max_tokens: 350,
        temperature: 0.05,
      }
    );
  }

  if (
    result?.response &&
    typeof result.response === "object"
  ) {
    return result.response;
  }

  const raw = String(result?.response || "").trim();

  try {
    return JSON.parse(raw);
  } catch {
    const start = raw.indexOf("{");
    const end = raw.lastIndexOf("}");

    if (start >= 0 && end > start) {
      try {
        return JSON.parse(
          raw.slice(start, end + 1)
        );
      } catch {}
    }
  }

  return {
    aligned: false,
    specific: false,
    inventedRules: false,
    genericLanguage: false,
    reason:
      "A auditoria semântica não retornou JSON válido."
  };
}

// ============================================================
// WORKER
// ============================================================

export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      const path = url.pathname;

      if (request.method === "OPTIONS") {
        return new Response(null, {
          status: 204,
          headers: corsHeaders()
        });
      }

      if (path.startsWith("/media/")) {
        return serveMedia(request, env, path);
      }

      if (path === "/approve") {
        return html(APP);
      }



      // ========================================================
      // R27 — GITHUB -> WORKER -> R2 VIDEO DELIVERY
      // ========================================================

      // Upload técnico chamado exclusivamente pelo GitHub Actions.
      // O GitHub NÃO recebe credenciais do R2; o Worker grava pelo binding MEDIA.
      if (request.method === "POST" && path === "/api/video-upload") {
        if (!isGithubVideoUploadAuthorized(request, env)) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-upload",
            errorClass: "video_upload_authorization",
            error: "Não autorizado"
          }, 401);
        }

        if (!env.MEDIA) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-upload",
            errorClass: "r2_binding_missing",
            error: "Binding R2 MEDIA não conectado"
          }, 500);
        }

        const renderId = sanitizeRenderId(
          url.searchParams.get("renderId") ||
          request.headers.get("x-ugi-render-id") ||
          ""
        );

        if (!renderId) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-upload",
            errorClass: "render_id_missing",
            error: "renderId ausente ou inválido"
          }, 400);
        }

        const declaredLength = Number(request.headers.get("content-length") || 0);
        if (declaredLength > VIDEO_UPLOAD_MAX_BYTES) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-upload",
            renderId,
            errorClass: "video_too_large",
            maxBytes: VIDEO_UPLOAD_MAX_BYTES,
            declaredBytes: declaredLength
          }, 413);
        }

        const contentType = String(request.headers.get("content-type") || "").toLowerCase();
        if (contentType && !contentType.includes("video/mp4") && !contentType.includes("application/octet-stream")) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-upload",
            renderId,
            errorClass: "invalid_video_content_type",
            contentType
          }, 415);
        }

        const bytes = new Uint8Array(await request.arrayBuffer());

        if (!bytes.length) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-upload",
            renderId,
            errorClass: "empty_video",
            error: "Arquivo vazio"
          }, 400);
        }

        if (bytes.length > VIDEO_UPLOAD_MAX_BYTES) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-upload",
            renderId,
            errorClass: "video_too_large",
            maxBytes: VIDEO_UPLOAD_MAX_BYTES,
            receivedBytes: bytes.length
          }, 413);
        }

        if (!hasMp4FtypSignature(bytes)) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-upload",
            renderId,
            errorClass: "invalid_mp4_signature",
            error: "O arquivo recebido não possui assinatura MP4/ISO-BMFF válida (ftyp)."
          }, 415);
        }

        // R43.1 — cada render pode possuir três masters independentes.
        // Compatibilidade: ausência de platform continua sendo tratada como Instagram/legacy.
        const platformRaw = String(
          url.searchParams.get("platform") ||
          request.headers.get("x-ugi-platform") ||
          "instagram"
        ).trim().toLowerCase();

        const platform = platformRaw === "youtube_shorts" || platformRaw === "youtube-shorts"
          ? "youtube"
          : platformRaw;

        if (!VIDEO_PLATFORMS.includes(platform)) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-upload",
            renderId,
            errorClass: "invalid_video_platform",
            platform: platformRaw,
            allowedPlatforms: VIDEO_PLATFORMS
          }, 400);
        }

        const videoKey = `${VIDEO_PREFIX}${renderId}/${platform}.mp4`;
        const uploadedAt = new Date().toISOString();
        const githubRunId = String(
          url.searchParams.get("githubRunId") ||
          request.headers.get("x-github-run-id") ||
          ""
        ).trim() || null;
        const durationRaw = Number(
          url.searchParams.get("duration") ||
          request.headers.get("x-ugi-video-duration") ||
          0
        );
        const duration = Number.isFinite(durationRaw) && durationRaw > 0
          ? durationRaw
          : null;

        const previous = await loadVideoResult(env, renderId);

        const putResult = await env.MEDIA.put(
          videoKey,
          bytes,
          {
            httpMetadata: {
              contentType: "video/mp4",
              cacheControl: "public,max-age=31536000,immutable"
            },
            customMetadata: {
              renderId,
              source: "github-actions-ffmpeg",
              ...(githubRunId ? { githubRunId } : {})
            }
          }
        );

        const videoUrl = `${url.origin}/media/${encodeURIComponent(videoKey)}`;
        const previousAssets = previous?.assets && typeof previous.assets === "object"
          ? previous.assets
          : {};

        const asset = {
          platform,
          status: "ready",
          ready: true,
          videoKey,
          videoUrl,
          videoBytes: bytes.length,
          contentType: "video/mp4",
          mp4Signature: true,
          duration: duration || VIDEO_PLATFORM_DEFAULT_DURATIONS[platform] || null,
          githubRunId,
          r2Etag: putResult?.etag || null,
          uploadedAt,
          approvalStatus: previousAssets?.[platform]?.approvalStatus || "pending_approval"
        };

        const assets = { ...previousAssets, [platform]: asset };
        const readyPlatforms = VIDEO_PLATFORMS.filter((name) => assets?.[name]?.ready);
        const allPlatformsReady = VIDEO_PLATFORMS.every((name) => assets?.[name]?.ready);

        const primary = assets.instagram || asset;
        const result = {
          ...(previous || {}),
          ok: true,
          version: VERSION,
          route: "/api/video-upload",
          routing: "GITHUB_ACTIONS_TO_WORKER_TO_R2_MULTI_ASSET",
          renderer: "github-actions-ffmpeg",
          costMode: "zero_cost_initial",
          renderId,
          status: allPlatformsReady ? "ready" : "processing",
          ready: allPlatformsReady,
          assets,
          readyPlatforms,
          expectedPlatforms: VIDEO_PLATFORMS,
          allPlatformsReady,

          // Compatibilidade R37/R42: videoUrl/videoKey continuam apontando para Instagram.
          videoKey: primary?.videoKey || null,
          videoUrl: primary?.videoUrl || null,
          videoBytes: primary?.videoBytes || null,
          contentType: "video/mp4",
          mp4Signature: true,
          duration: primary?.duration || null,
          githubRunId,
          uploadedAt
        };

        await saveVideoResult(env, result);

        // R37: se este render nasceu como conteúdo editorial,
        // atualiza automaticamente o rascunho da Central de Aprovação.
        let approvalDraft = null;
        let approvalBridgeError = null;

        try {
          const mappedDraftId = String(
            previous?.approvalDraftId ||
            renderId
          ).trim();

          approvalDraft = await getLocalDraft(env, mappedDraftId);
          if (approvalDraft) {
            approvalDraft.type = approvalDraft.type || "reel";
            approvalDraft.assets = assets;
            approvalDraft.readyPlatforms = readyPlatforms;
            approvalDraft.expectedPlatforms = VIDEO_PLATFORMS;
            approvalDraft.allPlatformsReady = allPlatformsReady;

            // Compatibilidade: campos legados continuam representando Instagram.
            approvalDraft.videoUrl = primary?.videoUrl || null;
            approvalDraft.videoKey = primary?.videoKey || null;
            approvalDraft.videoBytes = primary?.videoBytes || null;
            approvalDraft.videoDuration = primary?.duration || null;
            approvalDraft.renderId = renderId;
            approvalDraft.renderStatus = allPlatformsReady ? "ready" : "processing";
            approvalDraft.normalizationStatus = allPlatformsReady ? "ready" : "processing";
            approvalDraft.qualityStatus =
              approvalDraft.qualityStatus === "needs_review"
                ? "needs_review"
                : allPlatformsReady
                  ? "ready_for_review"
                  : "awaiting_render";
            approvalDraft.workflowStatus =
              allPlatformsReady ? "pending_approval" : "generating";
            approvalDraft.updatedAt = uploadedAt;
            await saveLocalDraft(env, approvalDraft);
            await saveContentEvent(
              env,
              approvalDraft,
              "render_ready",
              { platform, videoKey, videoBytes: bytes.length, githubRunId, readyPlatforms, allPlatformsReady }
            );
          }
        } catch (bridgeError) {
          approvalBridgeError =
            bridgeError?.message || String(bridgeError);
          console.log(
            "R37 approval bridge upload warning:",
            approvalBridgeError
          );
        }

        return json({
          ...result,
          platform,
          approvalDraftId: approvalDraft?.id || null,
          approvalReady: Boolean(approvalDraft) && allPlatformsReady,
          approvalBridgeError
        }, 201);
      }

      // Callback de falha/estado chamado pelo GitHub Actions.
      if (request.method === "POST" && path === "/api/video-status") {
        if (!isGithubVideoUploadAuthorized(request, env)) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-status",
            errorClass: "video_status_authorization",
            error: "Não autorizado"
          }, 401);
        }

        if (!env.MEDIA) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-status",
            errorClass: "r2_binding_missing",
            error: "Binding R2 MEDIA não conectado"
          }, 500);
        }

        const body = await request.json().catch(() => ({}));
        const renderId = sanitizeRenderId(body.renderId || body.render_id || "");
        if (!renderId) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-status",
            errorClass: "render_id_missing",
            error: "renderId ausente ou inválido"
          }, 400);
        }

        const previous = await loadVideoResult(env, renderId);
        const status = ["queued", "processing", "failed"].includes(String(body.status || ""))
          ? String(body.status)
          : "failed";
        const updatedAt = new Date().toISOString();
        const result = {
          ...(previous || {}),
          ok: status !== "failed",
          version: VERSION,
          route: "/api/video-status",
          routing: "GITHUB_ACTIONS_TO_WORKER_STATUS",
          renderer: "github-actions-ffmpeg",
          costMode: "zero_cost_initial",
          renderId,
          status,
          ready: false,
          videoUrl: previous?.videoUrl || null,
          videoKey: previous?.videoKey || null,
          githubRunId: String(body.githubRunId || body.github_run_id || previous?.githubRunId || "").trim() || null,
          errorClass: status === "failed"
            ? String(body.errorClass || body.error_class || "github_workflow_failed").slice(0, 120)
            : null,
          githubError: status === "failed"
            ? String(body.githubError || body.github_error || "O workflow falhou antes de entregar um MP4 válido.").slice(0, 1000)
            : null,
          updatedAt
        };

        await saveVideoResult(env, result);

        const mappedDraftId = String(
          previous?.approvalDraftId ||
          renderId
        ).trim();

        const approvalDraft = await getLocalDraft(env, mappedDraftId);
        if (approvalDraft) {
          approvalDraft.renderStatus =
            status === "failed" ? "failed" : status;
          approvalDraft.workflowStatus =
            status === "failed" ? "generation_failed" : "generating";
          approvalDraft.qualityStatus =
            status === "failed" ? "needs_review" : approvalDraft.qualityStatus;
          approvalDraft.generationError =
            status === "failed" ? result.githubError : null;
          approvalDraft.updatedAt = updatedAt;
          await saveLocalDraft(env, approvalDraft);
          await saveContentEvent(
            env,
            approvalDraft,
            status === "failed" ? "render_failed" : "render_status",
            { status, githubRunId: result.githubRunId || null }
          );
        }

        return json(result);
      }

      // R44.5.2 — callback semântico de sucesso chamado pelo GitHub Actions.
      if (request.method === "POST" && path === "/api/video-semantic-result") {
        if (!isGithubVideoUploadAuthorized(request, env)) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-semantic-result",
            errorClass: "video_semantic_authorization",
            error: "Não autorizado"
          }, 401);
        }

        if (!env.MEDIA) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-semantic-result",
            errorClass: "r2_binding_missing",
            error: "Binding R2 MEDIA não conectado"
          }, 500);
        }

        const body = await request.json().catch(() => ({}));
        const renderId = sanitizeRenderId(body.renderId || body.render_id || "");
        if (!renderId) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-semantic-result",
            errorClass: "render_id_missing",
            error: "renderId ausente ou inválido"
          }, 400);
        }

        const previous = await loadVideoResult(env, renderId);
        if (!previous) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-semantic-result",
            renderId,
            errorClass: "render_not_found",
            error: "Render não encontrado"
          }, 404);
        }

        const semanticValidation =
          body.semanticValidation && typeof body.semanticValidation === "object"
            ? body.semanticValidation
            : {};

        const copyLockValidation =
          body.copyLockValidation && typeof body.copyLockValidation === "object"
            ? body.copyLockValidation
            : { required: previous?.copyLock?.enabled === true, pass: previous?.copyLock?.enabled !== true };

        const legacyContentLeakDetected = body.legacyContentLeakDetected === true;
        const semanticPass =
          semanticValidation.pass === true &&
          legacyContentLeakDetected !== true &&
          (previous?.copyLock?.enabled !== true || copyLockValidation.pass === true);

        const updatedAt = new Date().toISOString();
        const nextResult = {
          ...previous,
          version: VERSION,
          semanticValidationAvailable: true,
          semanticValidation: {
            ...semanticValidation,
            pass: semanticPass,
            receivedAt: updatedAt
          },
          copyLockValidation,
          legacyContentLeakDetected,
          semanticEvidence: body.semanticEvidence || null,
          mediaProviders: body.mediaProviders || null,
          finalCta: body.finalCta || null,
          updatedAt
        };

        await saveVideoResult(env, nextResult);

        const mappedDraftId = String(previous.approvalDraftId || renderId).trim();
        const draft = await getLocalDraft(env, mappedDraftId);
        if (draft) {
          draft.semanticValidationRequired = draft.semanticValidationRequired === true || draft.copyLock?.enabled === true;
          draft.semanticValidationAvailable = true;
          draft.semanticValidation = nextResult.semanticValidation;
          draft.copyLockValidation = copyLockValidation;
          draft.legacyContentLeakDetected = legacyContentLeakDetected;
          draft.semanticEvidence = nextResult.semanticEvidence;
          draft.mediaProviders = nextResult.mediaProviders;
          draft.finalCta = nextResult.finalCta;
          draft.qualityStatus = semanticPass
            ? (draft.renderStatus === "ready" ? "ready_for_review" : draft.qualityStatus)
            : "needs_review";
          draft.updatedAt = updatedAt;
          await saveLocalDraft(env, draft);
          await saveContentEvent(env, draft, "video_semantic_validation", {
            pass: semanticPass,
            legacyContentLeakDetected,
            copyLockPass: copyLockValidation?.pass === true
          });
        }

        return json({
          ok: true,
          version: VERSION,
          route: "/api/video-semantic-result",
          renderId,
          semanticValidationAvailable: true,
          semanticPass,
          legacyContentLeakDetected,
          copyLockValidation,
          publicationTriggered: false,
          bufferMutationPerformed: false
        });
      }

      // Resultado individual. Usado pela Lola UGI depois que o job foi enfileirado.
      if (request.method === "GET" && path.startsWith("/api/video-result/")) {
        if (
          !isLolaUGIAuthorized(request, env) &&
          !isAdminAuthorized(request, env)
        ) {
          return json({ ok: false, error: "Não autorizado" }, 401);
        }

        if (!env.MEDIA) {
          return json({
            ok: false,
            version: VERSION,
            errorClass: "r2_binding_missing",
            error: "Binding R2 MEDIA não conectado"
          }, 500);
        }

        const renderId = sanitizeRenderId(
          decodeURIComponent(path.slice("/api/video-result/".length))
        );

        if (!renderId) {
          return json({
            ok: false,
            version: VERSION,
            errorClass: "render_id_invalid",
            error: "renderId inválido"
          }, 400);
        }

        const result = await loadVideoResult(env, renderId);

        if (!result) {
          return json({
            ok: true,
            version: VERSION,
            route: `/api/video-result/${renderId}`,
            renderId,
            status: "processing",
            ready: false,
            videoUrl: null,
            videoKey: null,
            note: "O renderer ainda não entregou o MP4 ao R2 ou o resultado ainda não foi registrado."
          }, 200);
        }

        return json({ ...result, ready: result.status === "ready" });
      }

      // Último resultado concluído, útil para diagnóstico operacional.
      if (request.method === "GET" && path === "/api/video-results/latest") {
        if (
          !isLolaUGIAuthorized(request, env) &&
          !isAdminAuthorized(request, env)
        ) {
          return json({ ok: false, error: "Não autorizado" }, 401);
        }

        if (!env.MEDIA) {
          return json({
            ok: false,
            version: VERSION,
            errorClass: "r2_binding_missing",
            error: "Binding R2 MEDIA não conectado"
          }, 500);
        }

        const result = await loadLatestVideoResult(env);
        return json({
          ok: true,
          version: VERSION,
          route: "/api/video-results/latest",
          found: Boolean(result),
          result: result || null
        });
      }

      // ========================================================
      // R44.4.11 — DYNAMIC VIDEO SCENES / FAIL-CLOSED
      const normalizeDynamicVideoScenes = (rawScenes) => {
        const platforms = ["instagram", "tiktok", "youtube"];
        const allowedRoles = new Set(["hook", "pain", "consequence", "turn", "result", "cta"]);

        if (!Array.isArray(rawScenes) || rawScenes.length < 4 || rawScenes.length > 10) {
          throw new Error("dynamic_video_scenes_required");
        }

        const normalizeMap = (value, field, index) => {
          if (!value || typeof value !== "object") {
            throw new Error(`invalid_${field}_scene_${index}`);
          }

          const out = {};
          for (const platform of platforms) {
            const text = String(value[platform] || "").trim();
            if (!text) {
              throw new Error(`missing_${field}_${platform}_scene_${index}`);
            }
            out[platform] = text;
          }
          return out;
        };

        const normalized = rawScenes.map((scene, offset) => {
          const index = offset + 1;
          const role = String(scene?.role || "").trim();
          const visualIntent = String(
            scene?.visual_intent ||
            scene?.visualIntent ||
            ""
          ).trim();
          const pexelsQuery = String(
            scene?.pexels_query ||
            scene?.pexelsQuery ||
            visualIntent
          ).trim();

          if (!allowedRoles.has(role)) {
            throw new Error(`invalid_role_scene_${index}`);
          }

          if (!visualIntent || !pexelsQuery) {
            throw new Error(`invalid_dynamic_scene_${index}`);
          }

          return {
            role,
            visual_intent: visualIntent,
            pexels_query: pexelsQuery,
            overlay: normalizeMap(scene?.overlay, "overlay", index),
            support: normalizeMap(scene?.support, "support", index),
            narration: normalizeMap(scene?.narration, "narration", index)
          };
        });

        if (
          normalized.length === 6 &&
          normalized.map((scene) => scene.role).join(">") !==
            "hook>pain>consequence>turn>result>cta"
        ) {
          throw new Error("invalid_six_scene_story_order");
        }

        return normalized;
      };

      // R25 — GITHUB ZERO-COST VIDEO RENDERER
      // ========================================================

      if (request.method === "POST" && path === "/api/video-render") {
        if (
          !isLolaUGIAuthorized(request, env) &&
          !isAdminAuthorized(request, env)
        ) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-render",
            routing: "LOLA_TO_GITHUB_ACTIONS_FFMPEG",
            renderer: "github-actions-ffmpeg",
            githubAccepted: false,
            githubStatus: null,
            errorClass: "worker_authorization",
            error: "Não autorizado",
            authDiagnostic: buildSafeAuthDiagnostic(request, env)
          });
        }

        const body = await request.json().catch(() => ({}));
        const renderId = createRenderId();

        const requestedContentId = String(
          body.content_id ||
          body.contentId ||
          ""
        ).trim();

        const requestedDraftId = String(
          body.draftId ||
          body.draft_id ||
          body.id ||
          ""
        ).trim();

        let existingDraft = null;

        if (requestedDraftId) {
          existingDraft = await getLocalDraft(env, requestedDraftId);
        }

        if (!existingDraft && requestedContentId) {
          existingDraft = await findLocalDraftByContentId(env, requestedContentId);
        }

        // Legacy migration: drafts antigos criados pelo /api/command podiam ter
        // contentId=id. Quando draftId explícito + content_id determinístico são
        // fornecidos, preservamos o id editorial e corrigimos somente a metadata.
        if (existingDraft && requestedContentId) {
          existingDraft = normalizeContentMetadata({
            ...existingDraft,
            contentId: requestedContentId,
            experimentId: String(
              body.experiment_id ||
              body.experimentId ||
              existingDraft.experimentId ||
              ""
            ).trim() || null,
            variant: String(
              body.variant ||
              existingDraft.variant ||
              ""
            ).trim() || null,
            commercialIntent: String(
              body.commercial_intent ||
              body.commercialIntent ||
              existingDraft.commercialIntent ||
              ""
            ).trim() || null
          });
        }

        const approvalDraftId = existingDraft?.id || renderId;

        const resolvedContentId =
          requestedContentId ||
          existingDraft?.contentId ||
          renderId;

        const resolvedExperimentId = String(
          body.experiment_id ||
          body.experimentId ||
          body.experiment ||
          existingDraft?.experimentId ||
          renderId
        ).trim();

        const resolvedVariant = String(
          body.variant ||
          existingDraft?.variant ||
          "A"
        ).trim();

        const resolvedCommercialIntent = String(
          body.commercial_intent ||
          body.commercialIntent ||
          body.intent ||
          existingDraft?.commercialIntent ||
          "atracao_com_potencial_de_conversao"
        ).trim();

        const resolvedCommercialOffer =
          body.commercial_offer === true ||
          body.commercialOffer === true ||
          existingDraft?.commercialOffer === true;

        const resolvedCommerce = normalizeUGICommerce(
          { ...body, commercial_offer: resolvedCommercialOffer },
          existingDraft?.commerce || null
        );

        const resolvedCopyLock = normalizeUGICopyLock(
          body,
          "reel",
          existingDraft?.copyLock || null
        );

        const resolvedEditorialMode = String(
          body.editorial_mode || body.editorialMode ||
          existingDraft?.editorialMode || "standard"
        ).trim() || "standard";

        const title = String(
          body.title ||
          body.topic ||
          existingDraft?.title ||
          existingDraft?.topic ||
          "Sua empresa cresceu. A gestão precisa acompanhar."
        ).trim();

        const duration = clamp(
          Number(
            body.duration ||
            body.videoDuration ||
            body.requestedVideoDuration ||
            8
          ),
          4,
          40
        );

        let dynamicScenes;

        try {
          dynamicScenes = normalizeDynamicVideoScenes(
            body.scenes ||
            body.video_scenes ||
            body.videoScenes ||
            null
          );
        } catch (error) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-render",
            routing: "LOLA_TO_GITHUB_ACTIONS_FFMPEG",
            renderer: "github-actions-ffmpeg",
            githubAccepted: false,
            githubStatus: null,
            renderId,
            approvalDraftId,
            existingDraftReused: Boolean(existingDraft),
            contentId: resolvedContentId,
            experimentId: resolvedExperimentId,
            variant: resolvedVariant,
            commercialIntent: resolvedCommercialIntent,
            errorClass: "dynamic_video_scenes_missing_or_invalid",
            error: String(error?.message || error || "dynamic_video_scenes_required"),
            publicationTriggered: false,
            mutationPerformed: false,
            note:
              "R44.4.11 FAIL-CLOSED: o GitHub não é acionado sem cenas dinâmicas válidas."
          });
        }

        const scenesPayload = JSON.stringify({
          version: "R44.5.2",
          content_id: resolvedContentId,
          experiment_id: resolvedExperimentId,
          variant: resolvedVariant,
          title,
          cta: String(body.cta || existingDraft?.cta || "Conheça a UGI.").trim(),
          editorial_mode: resolvedEditorialMode,
          commercial_offer: resolvedCommercialOffer,
          commerce: resolvedCommerce,
          copy_lock: resolvedCopyLock,
          scenes: dynamicScenes
        });

        const missing = [];

        if (!env.GITHUB_VIDEO_TOKEN) missing.push("GITHUB_VIDEO_TOKEN");
        if (!env.GITHUB_VIDEO_OWNER) missing.push("GITHUB_VIDEO_OWNER");
        if (!env.GITHUB_VIDEO_REPO) missing.push("GITHUB_VIDEO_REPO");
        if (!env.GITHUB_VIDEO_WORKFLOW) missing.push("GITHUB_VIDEO_WORKFLOW");

        if (missing.length) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-render",
            routing: "LOLA_TO_GITHUB_ACTIONS_FFMPEG",
            renderer: "github-actions-ffmpeg",
            githubAccepted: false,
            githubStatus: null,
            errorClass: "worker_configuration",
            error:
              `Configuração ausente no Worker: ${missing.join(", ")}`
          });
        }

        const owner = String(env.GITHUB_VIDEO_OWNER).trim();
        const repo = String(env.GITHUB_VIDEO_REPO).trim();
        const workflow = String(env.GITHUB_VIDEO_WORKFLOW).trim();

        const githubUrl =
          `https://api.github.com/repos/${encodeURIComponent(owner)}` +
          `/${encodeURIComponent(repo)}/actions/workflows/` +
          `${encodeURIComponent(workflow)}/dispatches`;

        const githubResponse = await fetch(
          githubUrl,
          {
            method: "POST",
            headers: {
              "Accept": "application/vnd.github+json",
              "Authorization": `Bearer ${env.GITHUB_VIDEO_TOKEN}`,
              "X-GitHub-Api-Version": "2022-11-28",
              "User-Agent": "UGI-Lola-Video-Renderer"
            },
            body: JSON.stringify({
              ref: "main",
              inputs: {
                title,
                duration: String(duration),
                render_id: renderId,
                content_id: resolvedContentId,
                experiment_id: resolvedExperimentId,
                variant: resolvedVariant,
                commercial_intent: resolvedCommercialIntent,
                scenes_json: scenesPayload
              }
            })
          }
        );

        if (githubResponse.status !== 204) {
          const raw = await githubResponse.text();

          let githubError = raw;

          try {
            const parsed = JSON.parse(raw);
            githubError =
              parsed?.message ||
              parsed?.error ||
              raw;
          } catch {}

          return json({
            ok: false,
            version: VERSION,
            route: "/api/video-render",
            routing: "LOLA_TO_GITHUB_ACTIONS_FFMPEG",
            renderer: "github-actions-ffmpeg",
            costMode: "zero_cost_initial",
            renderId,
            githubAccepted: false,
            githubStatus: githubResponse.status,
            repository: `${owner}/${repo}`,
            workflow,
            ref: "main",
            title,
            duration,
            status: "dispatch_failed",
            errorClass:
              githubResponse.status === 401
                ? "github_authentication"
                : githubResponse.status === 403
                  ? "github_permission"
                  : githubResponse.status === 404
                    ? "github_repository_or_workflow_not_found"
                    : githubResponse.status === 422
                      ? "github_validation"
                      : "github_dispatch_error",
            githubError: String(githubError || "").slice(0, 1000),
            requestedAt: new Date().toISOString(),
            note:
              "A Action recebeu diagnóstico em HTTP 200 para evitar ClientResponseError no cliente."
          });
        }

        const requestedAt = new Date().toISOString();
        const queuedResult = {
          ok: true,
          version: VERSION,
          route: "/api/video-render",
          routing: "LOLA_TO_GITHUB_ACTIONS_FFMPEG",
          renderer: "github-actions-ffmpeg",
          costMode: "zero_cost_initial",
          renderId,
          githubAccepted: true,
          githubStatus: 204,
          repository: `${owner}/${repo}`,
          workflow,
          ref: "main",
          title,
          duration,
          status: "queued",
          ready: false,
          assets: {},
          readyPlatforms: [],
          expectedPlatforms: VIDEO_PLATFORMS,
          allPlatformsReady: false,
          videoUrl: null,
          videoKey: null,
          approvalDraftId,
          existingDraftReused: Boolean(existingDraft),
          contentId: resolvedContentId,
          experimentId: resolvedExperimentId,
          variant: resolvedVariant,
          commercialIntent: resolvedCommercialIntent,
          commercialOffer: resolvedCommercialOffer,
          editorialMode: resolvedEditorialMode,
          commerce: resolvedCommerce,
          copyLock: resolvedCopyLock,
          exactCopy: resolvedCopyLock,
          semanticValidationRequired: resolvedCopyLock?.enabled === true,
          semanticValidationAvailable: false,
          semanticValidation: null,
          copyLockValidation: null,
          legacyContentLeakDetected: false,
          sceneSource: "dynamic",
          sceneCount: dynamicScenes.length,
          sceneRoles: dynamicScenes.map((scene) => scene.role),
          legacyHardcodedScenesDisabled: true,
          requestedAt,
          statusUrl: `${url.origin}/api/video-result/${encodeURIComponent(renderId)}`,
          note: existingDraft
            ? "O GitHub aceitou o job e o render foi associado ao draft editorial existente, sem criar duplicidade."
            : "O GitHub aceitou o job. O workflow produzirá o MP4 e o enviará automaticamente ao R2 pelo Worker."
        };

        let approvalBridgeOk = false;
        let approvalBridgeError = null;

        if (env.MEDIA) {
          await saveVideoResult(env, queuedResult);

          try {
            let approvalDraft = null;

            if (existingDraft) {
              approvalDraft = normalizeContentMetadata({
                ...existingDraft,
                contentId: resolvedContentId,
                renderId,
                type: existingDraft.type || "reel",
                topic: title,
                title,
                text: String(
                  body.caption ||
                  body.text ||
                  existingDraft.text ||
                  title
                ).trim(),
                objective: String(
                  body.objective ||
                  existingDraft.objective ||
                  ""
                ).trim() || null,
                audience: String(
                  body.audience ||
                  existingDraft.audience ||
                  ""
                ).trim() || null,
                hook: String(
                  body.hook ||
                  existingDraft.hook ||
                  ""
                ).trim() || null,
                angle: String(
                  body.angle ||
                  existingDraft.angle ||
                  ""
                ).trim() || null,
                cta: String(
                  body.cta ||
                  existingDraft.cta ||
                  "Conheça a UGI."
                ).trim(),
                experimentId: resolvedExperimentId || null,
                variant: resolvedVariant || null,
                commercialIntent: resolvedCommercialIntent || null,
                commercialOffer: resolvedCommercialOffer,
                editorialMode: resolvedEditorialMode,
                commerce: resolvedCommerce,
                copyLock: resolvedCopyLock,
                exactCopy: resolvedCopyLock,
                semanticValidationRequired: resolvedCopyLock?.enabled === true,
                semanticValidationAvailable: false,
                semanticValidation: null,
                copyLockValidation: null,
                legacyContentLeakDetected: false,
                status: "draft",
                workflowStatus: "generating",
                renderStatus: "processing",
                qualityStatus: "awaiting_render",
                renderer: "github-actions-ffmpeg",
                requestedVideoDuration: duration,
                assets: {},
                readyPlatforms: [],
                expectedPlatforms: VIDEO_PLATFORMS,
                allPlatformsReady: false,
                videoUrl: null,
                videoKey: null,
                generationError: null,
                updatedAt: requestedAt
              });
            } else {
              approvalDraft = normalizeContentMetadata({
                id: approvalDraftId,
                contentId: resolvedContentId,
                renderId,
                type: "reel",
                topic: title,
                title,
                text: String(
                  body.caption ||
                  body.text ||
                  title
                ).trim(),
                objective: String(body.objective || "").trim() || null,
                audience: String(body.audience || "").trim() || null,
                hook: String(body.hook || "").trim() || null,
                angle: String(body.angle || "").trim() || null,
                cta: String(body.cta || "Conheça a UGI.").trim(),
                experimentId: resolvedExperimentId || null,
                variant: resolvedVariant || null,
                commercialIntent: resolvedCommercialIntent || null,
                commercialOffer: resolvedCommercialOffer,
                editorialMode: resolvedEditorialMode,
                commerce: resolvedCommerce,
                copyLock: resolvedCopyLock,
                exactCopy: resolvedCopyLock,
                semanticValidationRequired: resolvedCopyLock?.enabled === true,
                semanticValidationAvailable: false,
                semanticValidation: null,
                copyLockValidation: null,
                legacyContentLeakDetected: false,
                status: "draft",
                workflowStatus: "generating",
                renderStatus: "processing",
                qualityStatus: "awaiting_render",
                renderer: "github-actions-ffmpeg",
                requestedVideoDuration: duration,
                assets: {},
                readyPlatforms: [],
                expectedPlatforms: VIDEO_PLATFORMS,
                allPlatformsReady: false,
                videoUrl: null,
                videoKey: null,
                createdAt: requestedAt,
                updatedAt: requestedAt
              });
            }

            await saveLocalDraft(env, approvalDraft);
            await saveContentEvent(
              env,
              approvalDraft,
              existingDraft ? "render_requeued_existing_draft" : "render_queued",
              {
                renderId,
                duration,
                existingDraftReused: Boolean(existingDraft)
              }
            );

            approvalBridgeOk = true;
          } catch (bridgeError) {
            approvalBridgeError =
              bridgeError?.message || String(bridgeError);
            console.log(
              "R37 approval bridge queue warning:",
              approvalBridgeError
            );
          }
        }

        return json({
          ...queuedResult,
          centralApproval: approvalBridgeOk,
          approvalDraftId: approvalBridgeOk ? approvalDraftId : null,
          existingDraftReused: Boolean(existingDraft),
          approvalBridgeError
        });
      }

      // R21: diagnóstico audiovisual direto, sem renderer de imagem.
      if (request.method === "POST" && path === "/api/video-test") {
        try {
          const body = await request.json().catch(() => ({}));
          const command = {
            id: body.id || `r21-video-test-${Date.now()}`,
            type: "reel",
            topic: body.topic || "Sua empresa cresceu. A gestão precisa acompanhar.",
            objective: body.objective || "Validar tecnicamente o pipeline audiovisual real da UGI.",
            keyMessage: body.keyMessage || "Sua empresa cresceu. A gestão precisa acompanhar.",
            cta: body.cta || "Sua empresa cresceu. A gestão precisa acompanhar. Conheça a UGI.",
            instructions: body.instructions || "Gerar exclusivamente vídeo vertical 9:16 humano, profissional, contemporâneo e realista. Não gerar carrossel nem imagem estática.",
            requestedVideoDuration: Number(body.requestedVideoDuration || body.videoDuration || 8),
            music: { requested: false },
            experiment: null,
            createdAt: new Date().toISOString()
          };

          const draft = await generateVideoDraft(env, command, url.origin);

          return json({
            ok: Boolean(draft?.videoUrl),
            version: VERSION,
            diagnosticRoute: "/api/video-test",
            routing: "DIRECT_TO_generateVideoDraft",
            imageRendererBypassed: true,
            renderStatus: draft?.renderStatus || null,
            videoUrl: draft?.videoUrl || null,
            videoKey: draft?.videoKey || null,
            videoProvider: draft?.videoProvider || null,
            videoProviderOrder: draft?.videoProviderOrder || VIDEO_PROVIDER_ORDER,
            videoDuration: draft?.videoDuration ?? null,
            requestedVideoDuration: draft?.requestedVideoDuration ?? null,
            normalizationStatus: draft?.normalizationStatus || null,
            videoAttempts: draft?.videoAttempts || [],
            authDiagnostic: draft?.authDiagnostic || null,
            generationError: draft?.generationError || null,
            qualityStatus: draft?.qualityStatus || null,
            qualityIssues: draft?.qualityIssues || [],
            semanticAudit: draft?.semanticAudit || null
          }, draft?.videoUrl ? 200 : 502);
        } catch (error) {
          return json({
            ok: false,
            version: VERSION,
            diagnosticRoute: "/api/video-test",
            routing: "DIRECT_TO_generateVideoDraft",
            imageRendererBypassed: true,
            error: error?.message || String(error)
          }, 500);
        }
      }


      // ========================================================
      // R44.5.4 — MATERIAL STORE + PRODUCT CATALOG + COMMERCE
      // ========================================================

      if (request.method === "POST" && path === "/api/materials") {
        if (!isCommerceAdminAuthorized(request, env)) {
          return json({ ok: false, version: VERSION, errorClass: "material_authorization", error: "Não autorizado" }, 401);
        }
        if (!env.MEDIA) return json({ ok: false, errorClass: "r2_binding_missing", error: "Binding R2 MEDIA não conectado" }, 500);
        const body = await request.json().catch(() => null);
        if (!body) return json({ ok: false, errorClass: "invalid_json", error: "JSON inválido" }, 400);
        const material = normalizeMaterialRecord(body);
        if (!material.title || !material.theme || !material.problem || !material.solution) {
          return json({ ok: false, errorClass: "material_required_fields_missing", required: ["title","theme","problem","solution"] }, 400);
        }
        await putJsonR2(env, `${MATERIAL_PREFIX}${material.materialId}.json`, material);
        return json({ ok: true, version: VERSION, route: "/api/materials", material }, 201);
      }

      if (request.method === "GET" && path === "/api/materials") {
        if (!isCommerceAdminAuthorized(request, env)) return json({ ok: false, error: "Não autorizado" }, 401);
        const materials = await listJsonPrefix(env, MATERIAL_PREFIX, 100);
        return json({ ok: true, version: VERSION, count: materials.length, materials });
      }

      if (request.method === "GET" && path.startsWith("/api/materials/") && !path.endsWith("/asset")) {
        if (!isCommerceAdminAuthorized(request, env)) return json({ ok: false, error: "Não autorizado" }, 401);
        const materialId = sanitizeCommerceId(decodeURIComponent(path.slice("/api/materials/".length)));
        const material = materialId ? await getJsonR2(env, `${MATERIAL_PREFIX}${materialId}.json`) : null;
        return material ? json({ ok: true, version: VERSION, material }) : json({ ok: false, errorClass: "material_not_found" }, 404);
      }

      if (request.method === "POST" && path.startsWith("/api/materials/") && path.endsWith("/asset")) {
        if (!isCommerceAdminAuthorized(request, env)) return json({ ok: false, error: "Não autorizado" }, 401);
        if (!env.MEDIA) return json({ ok: false, errorClass: "r2_binding_missing" }, 500);
        const rawId = path.slice("/api/materials/".length, -"/asset".length);
        const materialId = sanitizeCommerceId(decodeURIComponent(rawId));
        const material = materialId ? await getJsonR2(env, `${MATERIAL_PREFIX}${materialId}.json`) : null;
        if (!material) return json({ ok: false, errorClass: "material_not_found" }, 404);
        const declared = Number(request.headers.get("content-length") || 0);
        if (declared > MATERIAL_ASSET_MAX_BYTES) return json({ ok: false, errorClass: "material_asset_too_large", maxBytes: MATERIAL_ASSET_MAX_BYTES }, 413);
        const bytes = new Uint8Array(await request.arrayBuffer());
        if (!bytes.length || bytes.length > MATERIAL_ASSET_MAX_BYTES) return json({ ok: false, errorClass: "invalid_material_asset" }, 400);
        const contentType = String(request.headers.get("content-type") || "application/octet-stream").toLowerCase();
        const ext = contentType.includes("pdf") ? "pdf" : contentType.includes("zip") ? "zip" : "bin";
        const assetKey = `${MATERIAL_ASSET_PREFIX}${materialId}/v${String(material.version || "1").replace(/[^a-zA-Z0-9._-]/g, "-")}.${ext}`;
        await env.MEDIA.put(assetKey, bytes, { httpMetadata: { contentType, cacheControl: "private,no-store" }, customMetadata: { materialId } });
        const now = new Date().toISOString();
        const updated = { ...material, fileKey: assetKey, materialKey: assetKey, mimeType: contentType, size: bytes.length, assetReady: true, updatedAt: now };
        await putJsonR2(env, `${MATERIAL_PREFIX}${materialId}.json`, updated);
        return json({ ok: true, version: VERSION, materialId, fileKey: assetKey, mimeType: contentType, size: bytes.length, assetReady: true });
      }

      if (request.method === "POST" && path === "/api/products") {
        if (!isCommerceAdminAuthorized(request, env)) return json({ ok: false, error: "Não autorizado" }, 401);
        const body = await request.json().catch(() => null);
        if (!body) return json({ ok: false, errorClass: "invalid_json" }, 400);
        const product = normalizeProductRecord(body);
        if (!product.title || !product.materialId || !Number.isFinite(product.price) || product.price <= 0) {
          return json({ ok: false, errorClass: "product_required_fields_missing", required: ["title","materialId","price"] }, 400);
        }
        const material = await getJsonR2(env, `${MATERIAL_PREFIX}${product.materialId}.json`);
        if (!material) return json({ ok: false, errorClass: "material_not_found" }, 409);
        await putJsonR2(env, `${PRODUCT_PREFIX}${product.productId}.json`, product);
        return json({ ok: true, version: VERSION, product }, 201);
      }

      if (request.method === "GET" && path === "/api/products") {
        if (!isCommerceAdminAuthorized(request, env)) return json({ ok: false, error: "Não autorizado" }, 401);
        const products = await listJsonPrefix(env, PRODUCT_PREFIX, 100);
        return json({ ok: true, version: VERSION, count: products.length, products });
      }

      if (request.method === "GET" && path.startsWith("/api/products/")) {
        if (!isCommerceAdminAuthorized(request, env)) return json({ ok: false, error: "Não autorizado" }, 401);
        const productId = sanitizeCommerceId(decodeURIComponent(path.slice("/api/products/".length)));
        const product = productId ? await getJsonR2(env, `${PRODUCT_PREFIX}${productId}.json`) : null;
        return product ? json({ ok: true, version: VERSION, product }) : json({ ok: false, errorClass: "product_not_found" }, 404);
      }

      if (request.method === "POST" && path === "/api/commerce/checkout") {
        if (!isCommerceAdminAuthorized(request, env)) return json({ ok: false, errorClass: "commerce_authorization", error: "Não autorizado" }, 401);
        const body = await request.json().catch(() => null);
        if (!body) return json({ ok: false, errorClass: "invalid_json" }, 400);
        const productId = sanitizeCommerceId(body.productId || body.product_id || "");
        const product = productId ? await getJsonR2(env, `${PRODUCT_PREFIX}${productId}.json`) : null;
        if (!product) return json({ ok: false, errorClass: "product_not_found" }, 404);
        const material = await getJsonR2(env, `${MATERIAL_PREFIX}${product.materialId}.json`);
        if (!material?.assetReady || material?.qualityStatus !== "PASS" || material?.deliveryEnabled !== true) {
          return json({ ok: false, errorClass: "material_not_sellable", materialId: product.materialId, assetReady: material?.assetReady === true, qualityStatus: material?.qualityStatus || null, deliveryEnabled: material?.deliveryEnabled === true }, 409);
        }
        const provider = resolveCommerceProvider(env, body.provider);
        if (!provider) return json({ ok: false, errorClass: "provider_auth_missing", providers: commerceProviderStatus(env) }, 409);
        const checkout = await createProviderCheckout(env, provider, product, material, body, url.origin);
        await putJsonR2(env, `${CHECKOUT_PREFIX}${checkout.checkoutId}.json`, checkout);
        await putJsonR2(env, `${ORDER_PREFIX}${checkout.referenceId}.json`, { ...checkout, orderStatus: "awaiting_payment", paymentStatus: "pending", fulfilledAt: null });
        return json({ ok: true, version: VERSION, route: "/api/commerce/checkout", checkout }, 201);
      }

      if (request.method === "GET" && path.startsWith("/api/commerce/checkout/")) {
        if (!isCommerceAdminAuthorized(request, env)) return json({ ok: false, error: "Não autorizado" }, 401);
        const checkoutId = sanitizeCommerceId(decodeURIComponent(path.slice("/api/commerce/checkout/".length)));
        const checkout = checkoutId ? await getJsonR2(env, `${CHECKOUT_PREFIX}${checkoutId}.json`) : null;
        return checkout ? json({ ok: true, version: VERSION, checkout }) : json({ ok: false, errorClass: "checkout_not_found" }, 404);
      }

      if (request.method === "GET" && path.startsWith("/api/commerce/order/")) {
        if (!isCommerceAdminAuthorized(request, env)) return json({ ok: false, error: "Não autorizado" }, 401);
        const referenceId = sanitizeCommerceId(decodeURIComponent(path.slice("/api/commerce/order/".length)));
        const order = referenceId ? await getJsonR2(env, `${ORDER_PREFIX}${referenceId}.json`) : null;
        return order ? json({ ok: true, version: VERSION, order }) : json({ ok: false, errorClass: "order_not_found" }, 404);
      }

      if (request.method === "POST" && path === "/api/commerce/webhook/asaas") {
        if (!env.ASAAS_WEBHOOK_TOKEN) return json({ ok: false, errorClass: "asaas_webhook_token_missing" }, 503);
        const receivedToken = request.headers.get("asaas-access-token") || "";
        if (receivedToken !== env.ASAAS_WEBHOOK_TOKEN) return json({ ok: false, errorClass: "invalid_webhook_signature" }, 401);
        const body = await request.json().catch(() => null);
        if (!body) return json({ ok: false, errorClass: "invalid_json" }, 400);
        const normalized = normalizeAsaasWebhook(body);
        if (!normalized.referenceId) return json({ ok: true, ignored: true, reason: "reference_not_found" }, 202);
        const order = await getJsonR2(env, `${ORDER_PREFIX}${normalized.referenceId}.json`);
        if (!order) return json({ ok: true, ignored: true, reason: "order_not_found" }, 202);
        const now = new Date().toISOString();
        const next = { ...order, providerEvent: normalized.event, providerPaymentId: normalized.paymentId, paymentStatus: normalized.paid ? "paid" : normalized.status || "pending", paidAt: normalized.paid ? (order.paidAt || now) : order.paidAt || null, updatedAt: now };
        if (normalized.paid && !next.fulfilledAt) {
          const fulfillment = await fulfillPaidOrder(env, next, url.origin);
          Object.assign(next, fulfillment.orderPatch);
        }
        await putJsonR2(env, `${ORDER_PREFIX}${normalized.referenceId}.json`, next);
        return json({ ok: true, version: VERSION, referenceId: normalized.referenceId, paymentStatus: next.paymentStatus, fulfillmentReady: Boolean(next.fulfilledAt), publicationTriggered: false, bufferMutationPerformed: false });
      }

      if (request.method === "GET" && path.startsWith("/api/material-delivery/")) {
        if (!env.MEDIA) return new Response("Storage unavailable", { status: 503 });
        const token = sanitizeDeliveryToken(decodeURIComponent(path.slice("/api/material-delivery/".length)));
        const grant = token ? await getJsonR2(env, `${DELIVERY_PREFIX}${token}.json`) : null;
        if (!grant?.fileKey) return new Response("Link inválido", { status: 404 });
        if (Date.parse(grant.expiresAt || "") <= Date.now()) return new Response("Link expirado", { status: 410 });
        const object = await env.MEDIA.get(grant.fileKey);
        if (!object) return new Response("Material não encontrado", { status: 404 });
        const headers = new Headers();
        headers.set("Content-Type", object.httpMetadata?.contentType || grant.mimeType || "application/octet-stream");
        headers.set("Cache-Control", "private,no-store");
        headers.set("Content-Disposition", `attachment; filename="${String(grant.fileName || "material-ugi").replace(/[\"\\]/g, "-")}"`);
        return new Response(object.body, { status: 200, headers });
      }

      if (path === "/health" || path === "/api/health") {
        return json({
          ok: true,
          service: "Lola Operacional UGI",
          version: VERSION,
          status: "online",
          multimedia: true,
          capabilities: {
            post: true,
            carousel: true,
            carouselExactText: true,
            carouselNoAITextRendering: true,
            carouselComposer: "R19 sequential two-pass Browser Run with adaptive 429 backoff",
            semanticValidation: true,
          editorialSelfRepair: true,
          visualBackgroundGeneration: true,
          exactTextOverlay: true,
          terminalStyleRemoved: true,
          browserRunRenderer: true,
          browserRunRequiredForCarousel: true,
          photoPerCarouselSlide: true,
          automaticImageFallbackDisabled: true,
          beatlyMusicMetadataReady: true,
          beatlyCatalogRotation: true,
          beatlyBusinessRelevancePolicy: true,
          semanticGateSelfHealing: true,
            video: true,
            reel: true,
            videoNormalization: true,
            videoProcessor: "Cloudflare Media Transformations binding",
            musicMetadata: true,
            musicMixingAutomatic: false,
            instagramLibraryMusicAutomatic: false,
            musicMultiplatformPolicy: true,
            musicContextFirst: true,
            musicExplicitFilter: true,
            musicPerPlatformRights: true,
            musicFallbackAutomatic: true,
            browser429Backoff: true,
            browserTwoPassRecovery: true,
            realVideoMimeValidation: true,
            videoStaticImageFallbackDisabled: true,
            videoProvider: VIDEO_MODEL,
            videoFallbackProviders: [VIDEO_FALLBACK_MODEL, VIDEO_FALLBACK_MODEL_2],
            videoProviderCascade: true,
            directVideoDiagnostic: "/api/video-test",
            videoRoutingLocked: true,
            videoAuthDiagnostic: true,
            videoGatewayId: "default",
            videoUnifiedBilling: true,
            zeroCostGithubRenderer: true,
            dynamicVideoScenes: true,
            dynamicVideoScenesRequired: true,
            commerceBridge: true,
            commerceHardGate: true,
            materialStore: true,
            productCatalog: true,
            commerceAdapter: true,
            commerceWebhookFailClosed: true,
            commerceFulfillment: true,
            materialDeliveryTokenized: true,
            copyLock: true,
            carouselCopyLock: true,
            videoCopyLock: true,
            semanticSuccessCallback: true,
            semanticSuccessCallbackRoute: "/api/video-semantic-result",
            legacyHardcodedScenesDisabled: true,
            videoSceneInput: "workflow_dispatch.inputs.scenes_json",
            githubVideoRenderRoute: "/api/video-render",
            githubVideoUploadRoute: "/api/video-upload",
            githubVideoStatusRoute: "/api/video-status",
            githubVideoResultRoute: "/api/video-result/{renderId}",
            githubVideoLatestRoute: "/api/video-results/latest",
            githubR2AutomaticDelivery: true,
            videoMultiAsset: true,
            videoPlatforms: VIDEO_PLATFORMS,
            videoIndependentPlatformAssets: true,
            centralMultiAssetApproval: true,
            platformApprovalIndependent: true,
            platformApprovalPublishesAutomatically: false,
            platformApprovalRoute: "/api/platform-approval",
            multiPlatformPublishing: true,
            platformPublishRoute: "/api/platform-publish",
            platformPublicationStatusRoute: "/api/platform-publication-status",
            carouselSlideRecoveryRoute: "/api/carousel-slide-recovery",
            carouselSlideRecoveryInPlace: true,
            bufferChannelsRoute: "/api/buffer/channels",
            approvalSeparatedFromPublishing: true,
            operationalAuthFix: true,
            r2AssetValidationFix: true,
            publicationAssetValidation: "R2 binding first, public HEAD fallback",
            operationalAuthRoutes: [
              "/api/platform-approval",
              "/api/platform-publish",
              "/api/platform-publication-status"
            ],
            supportedPublishModes: ["shareNow", "customScheduled", "addToQueue"],
            bufferChannelOverrides: {
              instagram: Boolean(env.BUFFER_CHANNEL_INSTAGRAM || IG),
              tiktok: Boolean(env.BUFFER_CHANNEL_TIKTOK),
              youtube: Boolean(env.BUFFER_CHANNEL_YOUTUBE)
            },
            githubActionHttp200Compatibility: true,
            videoImageFallbackDisabled: true,
            videoGateway: "workers-ai-direct"
          },
          bindings: {
            AI: Boolean(env.AI),
            IMAGES: Boolean(env.IMAGES),
            MEDIA_R2: Boolean(env.MEDIA),
            VIDEO: Boolean(env.VIDEO),
            LOLA_AUTH_KEY: Boolean(env.LOLA_AUTH_KEY),
            LOLA_COMMAND_KEY: Boolean(env.LOLA_COMMAND_KEY),
            BUFFER_API_KEY: Boolean(env.BUFFER_API_KEY),
          BROWSER: Boolean(env.BROWSER),
            MUSIC_CATALOG_JSON: Boolean(env.MUSIC_CATALOG_JSON),
            GITHUB_VIDEO_TOKEN: Boolean(env.GITHUB_VIDEO_TOKEN),
            GITHUB_VIDEO_OWNER: Boolean(env.GITHUB_VIDEO_OWNER),
            GITHUB_VIDEO_REPO: Boolean(env.GITHUB_VIDEO_REPO),
            GITHUB_VIDEO_WORKFLOW: Boolean(env.GITHUB_VIDEO_WORKFLOW),
            GITHUB_VIDEO_UPLOAD_KEY: Boolean(env.GITHUB_VIDEO_UPLOAD_KEY),
            ASAAS_API_KEY: Boolean(env.ASAAS_API_KEY),
            ASAAS_WEBHOOK_TOKEN: Boolean(env.ASAAS_WEBHOOK_TOKEN),
            PAGBANK_TOKEN: Boolean(env.PAGBANK_TOKEN)
          },
          endpoints: {
            central: "/approve",
        approvalMvp: true,
        contentLifecycleTracking: true,
        approvalArchive: true,
        videoToApprovalBridge: true,
            health: "/api/health",
            command: "POST /api/command",
            commands: "GET /api/commands",
            drafts: "GET /api/drafts",
            draftLookup: "GET /api/draft-lookup?content_id={content_id}",
            musicCatalog: "POST /api/music/catalog",
            musicCatalogStatus: "GET /api/music/catalog/status",
            musicPolicyStatus: "GET /api/music/policy/status",
            videoRender: "POST /api/video-render",
            videoUpload: "POST /api/video-upload",
            videoStatus: "POST /api/video-status",
            videoSemanticResult: "POST /api/video-semantic-result",
            videoResult: "GET /api/video-result/{renderId}",
            videoLatest: "GET /api/video-results/latest",
            materials: "GET|POST /api/materials",
            material: "GET /api/materials/{materialId}",
            materialAsset: "POST /api/materials/{materialId}/asset",
            products: "GET|POST /api/products",
            product: "GET /api/products/{productId}",
            commerceCheckout: "POST /api/commerce/checkout",
            commerceCheckoutGet: "GET /api/commerce/checkout/{checkoutId}",
            commerceOrder: "GET /api/commerce/order/{referenceId}",
            asaasWebhook: "POST /api/commerce/webhook/asaas",
            materialDelivery: "GET /api/material-delivery/{token}"
          },
          timestamp: new Date().toISOString()
        });
      }

      // ========================================================
      // COMMAND
      // ========================================================

      if (path === "/api/command" && request.method === "POST") {
        if (!isLolaUGIAuthorized(request, env)) {
          return json({ ok: false, error: "Comando não autorizado" }, 401);
        }

        const body = await readBody(request);

        if (!body) {
          return json({ ok: false, error: "JSON inválido" }, 400);
        }

        const validation = validateCommand(body);

        if (validation) {
          return json({ ok: false, error: validation }, 400);
        }

        const command = createCommand(body);
        await saveCommand(env, command);

        let proposal = null;
        let generationWarning = null;

        if (body.generate_now !== false) {
          if (!env.AI || !env.MEDIA) {
            command.status = "received";
            command.generationStatus = "bindings_missing";
            await saveCommand(env, command);

            return json(
              {
                ok: true,
                version: VERSION,
                message:
                  "Comando salvo. AI ou R2 MEDIA não estão conectados.",
                command,
                proposal: null
              },
              202
            );
          }

          try {
            proposal = await generateFromCommand(
              env,
              command,
              url.origin
            );

            command.status = "generated";
            command.generationStatus =
              proposal?.qualityStatus === "needs_review"
                ? "generated_needs_review"
                : "generated";
            command.generatedDraftId = proposal?.id || null;
            command.updatedAt = new Date().toISOString();

            await saveCommand(env, command);
          } catch (error) {
            generationWarning = error?.message || String(error);

            command.status = "received";
            command.generationStatus = "generation_failed";
            command.lastGenerationError = generationWarning;
            command.updatedAt = new Date().toISOString();

            await saveCommand(env, command);
          }
        }

        return json(
          {
            ok: true,
            version: VERSION,
            message: proposal
              ? "Comando recebido e proposta criada pela Lola Operacional."
              : generationWarning
                ? "Comando salvo. A geração automática encontrou um problema, mas o comando não foi perdido."
                : "Comando recebido e salvo.",
            command,
            proposal,
            warning: generationWarning
          },
          202
        );
      }

      // ========================================================
      // BEATLY MUSIC CATALOG
      // ========================================================

      // R14.2: endpoint seguro para confirmar se o catálogo está disponível.
      // Não expõe títulos, artistas, IDs ou qualquer conteúdo do catálogo.
      if (
        path === "/api/music/catalog/status" &&
        request.method === "GET"
      ) {
        const catalog = await loadBeatlyCatalog(env);

        return json({
          ok: true,
          version: VERSION,
          provider: "ugi_music_engine",
          configured: catalog.length > 0,
          source: env.MUSIC_CATALOG_JSON
            ? "MUSIC_CATALOG_JSON"
            : env.MEDIA
              ? "R2_or_empty"
              : "none",
          tracksAvailable: catalog.length,
          cacheLimit: MUSIC_CACHE_LIMIT,
          fallbackAttempts: MUSIC_FALLBACK_ATTEMPTS,
          directVariableMode: Boolean(env.MUSIC_CATALOG_JSON),
          externalProviderConfigured: Boolean(env.MUSIC_PROVIDER_URL),
          externalProviderAuthenticated: Boolean(env.MUSIC_PROVIDER_TOKEN),
          instagramAudioIdsFabricated: false,
          syncRequired: false,
          policy: musicPolicySummary()
        });
      }

      if (
        path === "/api/music/policy/status" &&
        request.method === "GET"
      ) {
        return json({
          ok: true,
          version: VERSION,
          mode: "multiplatform_context_first",
          maxOperationalTracks: MUSIC_CACHE_LIMIT,
          fallbackAttempts: MUSIC_FALLBACK_ATTEMPTS,
          priorities: [
            "context_relevance",
            "UGI_professional_fit",
            "explicit_safety",
            "commercial_platform_eligibility",
            "modernity",
            "trend"
          ],
          platforms: MUSIC_PLATFORM_POLICY,
          note:
            "Nenhum ID de áudio é fabricado. Áudio de biblioteca nativa só é usado quando a plataforma/fonte autorizada fornecer identificação e elegibilidade reais."
        });
      }

      if (
        path === "/api/music/catalog" &&
        request.method === "POST"
      ) {
        if (
          !isAdminAuthorized(request, env) &&
          !isLolaUGIAuthorized(request, env)
        ) {
          return json(
            { ok: false, error: "Não autorizado" },
            401
          );
        }

        const body = await readBody(request);
        const tracks =
          Array.isArray(body)
            ? body
            : Array.isArray(body?.tracks)
              ? body.tracks
              : null;

        if (!tracks) {
          return json(
            {
              ok: false,
              error:
                "Envie um array de faixas ou { tracks: [...] }"
            },
            400
          );
        }

        if (!env.MEDIA) {
          return json(
            {
              ok: false,
              error: "R2 MEDIA não conectado"
            },
            500
          );
        }

        const sanitized =
          tracks
            .filter(Boolean)
            .slice(0, 1000)
            .map((track, index) => ({
              id:
                String(
                  track.id ||
                  track.audioId ||
                  `beatly-${index + 1}`
                ),
              title:
                String(track.title || "").trim(),
              artist:
                String(track.artist || "").trim(),
              audioId:
                String(
                  track.audioId ||
                  track.id ||
                  ""
                ).trim(),
              source: "beatly",
              genre:
                String(track.genre || "").trim(),
              moods:
                Array.isArray(track.moods)
                  ? track.moods.slice(0, 12)
                  : [],
              tags:
                Array.isArray(track.tags)
                  ? track.tags.slice(0, 20)
                  : [],
              description:
                String(
                  track.description || ""
                ).trim(),
              trendScore:
                Number(track.trendScore || 0) || 0,
              businessRelevant:
                track.businessRelevant !== false,
              professional:
                track.professional !== false,
              modern:
                track.modern !== false,
              explicit:
                track.explicit === true,
              licensed:
                track.licensed !== false,
              active:
                track.active !== false,
              startSeconds:
                Number(track.startSeconds || 0) || 0
            }))
            .filter(track => track.title);

        await env.MEDIA.put(
          BEATLY_CATALOG_KEY,
          JSON.stringify(
            {
              provider: "beatly",
              updatedAt: new Date().toISOString(),
              count: sanitized.length,
              tracks: sanitized
            },
            null,
            2
          ),
          {
            httpMetadata: {
              contentType: "application/json"
            }
          }
        );

        return json({
          ok: true,
          version: VERSION,
          provider: "beatly",
          tracksSaved: sanitized.length,
          policy: musicPolicySummary()
        });
      }

      // ========================================================
      // COMMANDS
      // ========================================================

      if (path === "/api/commands" && request.method === "GET") {
        if (
          !isAdminAuthorized(request, env) &&
          !isLolaUGIAuthorized(request, env)
        ) {
          return json({ ok: false, error: "Não autorizado" }, 401);
        }

        return json({
          ok: true,
          version: VERSION,
          commands: await listCommands(env)
        });
      }


      // ========================================================
      // R44.4.7 — COMPACT DRAFT LOOKUP BY CONTENT_ID — READ ONLY
      // ========================================================

      if (
        path === "/api/draft-lookup" &&
        request.method === "GET"
      ) {
        if (
          !isAdminAuthorized(request, env) &&
          !isLolaUGIAuthorized(request, env)
        ) {
          return json({ ok: false, error: "Não autorizado" }, 401);
        }

        const contentId = String(
          url.searchParams.get("content_id") || ""
        ).trim();

        if (!contentId) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/draft-lookup",
            error: "content_id_required",
            publicationTriggered: false,
            mutationPerformed: false
          }, 400);
        }

        // Consulta diretamente o MESMO armazenamento R2 usado por /api/drafts,
        // porém não serializa a coleção inteira e não filtra apenas status=draft.
        // Isso permite localizar também conteúdo que já avançou de estado.
        let cursor = undefined;
        let draft = null;
        let scanned = 0;
        const maxScanned = 1000;

        do {
          const page = await env.MEDIA.list({
            prefix: DRAFT_PREFIX,
            limit: DRAFT_LIMIT,
            ...(cursor ? { cursor } : {})
          });

          for (const object of page.objects || []) {
            if (!object.key.endsWith(".json")) continue;
            if (scanned >= maxScanned) break;
            scanned += 1;

            try {
              const stored = await env.MEDIA.get(object.key);
              if (!stored) continue;

              const candidate = normalizeContentMetadata(
                await stored.json()
              );

              const candidateContentId = String(
                candidate?.contentId ||
                candidate?.content_id ||
                candidate?.metadata?.contentId ||
                candidate?.metadata?.content_id ||
                ""
              ).trim();

              if (candidateContentId === contentId) {
                draft = candidate;
                break;
              }
            } catch (error) {
              console.log(
                "R44.4.7 draft lookup read error:",
                object.key,
                error
              );
            }
          }

          if (draft || scanned >= maxScanned) break;

          cursor = page.truncated
            ? page.cursor
            : undefined;
        } while (cursor);

        if (!draft) {
          return json({
            ok: true,
            version: VERSION,
            route: "/api/draft-lookup",
            content_id: contentId,
            found: false,
            draftId: null,
            renderId: null,
            status: null,
            workflowStatus: null,
            createdAt: null,
            updatedAt: null,
            publicationTriggered: false,
            mutationPerformed: false
          });
        }

        return json({
          ok: true,
          version: VERSION,
          route: "/api/draft-lookup",
          content_id: contentId,
          found: true,
          draftId:
            draft.id ||
            draft.draftId ||
            draft.draft_id ||
            null,
          renderId:
            draft.renderId ||
            draft.render_id ||
            null,
          status:
            draft.status ||
            null,
          workflowStatus:
            draft.workflowStatus ||
            draft.workflow_status ||
            null,
          createdAt:
            draft.createdAt ||
            draft.created_at ||
            null,
          updatedAt:
            draft.updatedAt ||
            draft.updated_at ||
            null,
          publicationTriggered: false,
          mutationPerformed: false
        });
      }

      // ========================================================
      // DRAFTS
      // ========================================================

      if (path === "/api/drafts" && request.method === "GET") {
        if (
          !isAdminAuthorized(request, env) &&
          !isLolaUGIAuthorized(request, env)
        ) {
          return json({ ok: false, error: "Não autorizado" }, 401);
        }

        return json({
          ok: true,
          version: VERSION,
          drafts: await listLocalDrafts(env)
        });
      }

      // ========================================================
      // R44.4 — BUFFER CHANNELS DIAGNOSTIC
      // ========================================================

      if (path === "/api/buffer/channels" && request.method === "GET") {
        if (
          !isAdminAuthorized(request, env) &&
          !isLolaUGIAuthorized(request, env)
        ) {
          return json({ ok: false, error: "Não autorizado" }, 401);
        }

        try {
          const discovered = await discoverBufferChannels(env);

          return json({
            ok: true,
            version: VERSION,
            organization: discovered.organization,
            channels: discovered.channels,
            note:
              "Use os IDs retornados em BUFFER_CHANNEL_INSTAGRAM, BUFFER_CHANNEL_TIKTOK e BUFFER_CHANNEL_YOUTUBE se houver múltiplos canais da mesma rede."
          });
        } catch (error) {
          return json({
            ok: false,
            version: VERSION,
            errorClass: "buffer_channel_discovery_failed",
            error: error?.message || String(error)
          }, 400);
        }
      }


      // ========================================================
      // R44.4.6 — CAROUSEL SINGLE-SLIDE RECOVERY
      // ========================================================

      if (
        path === "/api/carousel-slide-recovery" &&
        request.method === "POST"
      ) {
        if (
          !isAdminAuthorized(request, env) &&
          !isLolaUGIAuthorized(request, env)
        ) {
          return json({ ok: false, error: "Não autorizado" }, 401);
        }

        if (!env.MEDIA || !env.BROWSER) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/carousel-slide-recovery",
            errorClass: "required_binding_missing",
            error: "Bindings MEDIA e BROWSER são obrigatórios para recovery."
          }, 500);
        }

        const body = await readBody(request);
        const id = String(body?.id || body?.draftId || "").trim();
        const slideNumber = Number(body?.slideNumber || body?.slide || 0);
        const maxAttempts = clamp(
          Number(body?.maxAttempts || 3),
          1,
          3
        );

        if (!id) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/carousel-slide-recovery",
            error: "id/draftId ausente"
          }, 400);
        }

        if (!Number.isInteger(slideNumber) || slideNumber < 1) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/carousel-slide-recovery",
            error: "slideNumber inválido"
          }, 400);
        }

        const draft = await getLocalDraft(env, id);

        if (!draft) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/carousel-slide-recovery",
            draftId: id,
            error: "Rascunho não encontrado"
          }, 404);
        }

        if (String(draft.type || "").toLowerCase() !== "carousel") {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/carousel-slide-recovery",
            draftId: id,
            error: "Recovery disponível somente para drafts de carrossel."
          }, 409);
        }

        const slides = Array.isArray(draft.slides) ? draft.slides : [];
        const slide = slides.find(
          item => Number(item?.number) === slideNumber
        );

        if (!slide) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/carousel-slide-recovery",
            draftId: id,
            slideNumber,
            error: `Slide ${slideNumber} não existe no draft.`
          }, 404);
        }

        let command = null;

        if (draft.commandId) {
          try {
            command = await getLocalCommand(env, draft.commandId);
          } catch {}
        }

        if (!command) {
          command = {
            id: draft.commandId || `recovery-${draft.id}`,
            type: "carousel",
            topic: draft.area || draft.topic || "",
            objective: draft.angle || "",
            keyMessage: draft.topic || "",
            cta: "",
            slides: slides.length,
            experiment: draft.experiment || "",
            requestedBy: "Lola Recovery"
          };
        }

        const origin = url.origin;
        const expectedKey =
          `${CAROUSEL_PREFIX}${draft.id}-slide-${slideNumber}.png`;

        const alreadyStored = await env.MEDIA.head(expectedKey);

        const attempts = [];
        let rendered = null;

        if (alreadyStored) {
          rendered = {
            key: expectedKey,
            url: `${origin}/media/${expectedKey}`,
            renderer: "r19-browser-photo-editorial-png",
            reused: true
          };
          attempts.push({
            attempt: 0,
            ok: true,
            reusedExistingAsset: true,
            error: null
          });
        } else {
          for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
              rendered = await renderCarouselSlideExact(
                env,
                command,
                slide,
                draft.id,
                origin
              );

              attempts.push({
                attempt,
                ok: true,
                reusedExistingAsset: false,
                error: null
              });
              break;
            } catch (error) {
              const message = error?.message || String(error);
              attempts.push({
                attempt,
                ok: false,
                reusedExistingAsset: false,
                error: message
              });

              if (attempt < maxAttempts) {
                const delayMs =
                  attempt === 1
                    ? 15000
                    : 30000;
                await sleep(delayMs);
              }
            }
          }
        }

        const imageUrls = [];
        const imageKeys = [];
        const existingSlides = [];
        const missingSlides = [];

        for (const item of slides) {
          const number = Number(item?.number);
          const key =
            `${CAROUSEL_PREFIX}${draft.id}-slide-${number}.png`;
          const stored = await env.MEDIA.head(key);

          if (stored) {
            existingSlides.push(number);
            imageKeys.push(key);
            imageUrls.push(`${origin}/media/${key}`);
          } else {
            missingSlides.push(number);
          }
        }

        const ready =
          slides.length > 0 &&
          missingSlides.length === 0 &&
          imageUrls.length === slides.length;

        const previousErrors = Array.isArray(draft.renderErrors)
          ? draft.renderErrors
          : [];

        const filteredErrors = previousErrors.filter(
          value =>
            !String(value || "").startsWith(`Slide ${slideNumber}:`)
        );

        const lastFailure =
          attempts.length &&
          attempts[attempts.length - 1]?.ok !== true
            ? attempts[attempts.length - 1]?.error
            : null;

        const renderErrors = lastFailure
          ? [
              ...filteredErrors,
              `Slide ${slideNumber}: ${lastFailure}`
            ]
          : filteredErrors;

        const semanticPass =
          draft.carouselAudit?.semanticPass !== false;

        const nextDraft = {
          ...draft,
          imageUrls,
          imageKeys,
          imageUrl: imageUrls[0] || null,
          imageKey: imageKeys[0] || null,
          renderErrors,
          renderStatus: ready ? "ready" : "partial",
          generationStatus:
            ready ? "generated" : "generated_needs_review",
          qualityStatus:
            ready && semanticPass
              ? "ready_for_review"
              : "needs_review",
          workflowStatus:
            ready ? "pending_approval" : "partial",
          approvalStatus:
            draft.approvalStatus || "pending_approval",
          publicationTriggered: false,
          recovery: {
            ...(draft.recovery || {}),
            lastSlideNumber: slideNumber,
            lastRecoveryAt: new Date().toISOString(),
            attempts,
            existingSlides,
            missingSlides
          }
        };

        const saved = await saveLocalDraft(env, nextDraft);

        await saveContentEvent(
          env,
          saved,
          rendered
            ? "carousel_slide_recovered"
            : "carousel_slide_recovery_failed",
          {
            slideNumber,
            attempts,
            existingSlides,
            missingSlides,
            renderStatus: saved.renderStatus,
            qualityStatus: saved.qualityStatus
          }
        );

        return json({
          ok: Boolean(rendered),
          version: VERSION,
          route: "/api/carousel-slide-recovery",
          draftId: saved.id,
          commandId: saved.commandId || null,
          contentId: saved.contentId || null,
          slideNumber,
          rendered: Boolean(rendered),
          reusedExistingAsset: Boolean(rendered?.reused),
          slideUrl: rendered?.url || null,
          slideKey: rendered?.key || null,
          attempts,
          existingSlides,
          missingSlides,
          totalExpectedSlides: slides.length,
          totalExistingSlides: existingSlides.length,
          renderStatus: saved.renderStatus,
          generationStatus: saved.generationStatus,
          qualityStatus: saved.qualityStatus,
          workflowStatus: saved.workflowStatus,
          approvalStatus: saved.approvalStatus || "pending_approval",
          publicationTriggered: false,
          imageUrls: saved.imageUrls || [],
          imageKeys: saved.imageKeys || [],
          renderErrors: saved.renderErrors || [],
          note: rendered
            ? "Recovery aplicado no draft existente. Nenhum novo draft foi criado."
            : "Recovery não concluiu o slide. O draft existente foi preservado."
        }, rendered ? 200 : 502);
      }

      // ========================================================
      // R44.4 — PLATFORM PUBLISH / SCHEDULE
      // ========================================================

      if (path === "/api/platform-publish" && request.method === "POST") {
        if (
          !isAdminAuthorized(request, env) &&
          !isLolaUGIAuthorized(request, env)
        ) {
          return json({ ok: false, error: "Não autorizado" }, 401);
        }

        const body = await readBody(request);

        if (!body?.id) {
          return json({ ok: false, error: "id ausente" }, 400);
        }

        const platform =
          normalizeApprovalPlatform(body.platform);

        if (!platform) {
          return json({
            ok: false,
            error: "platform inválida",
            allowedPlatforms: VIDEO_PLATFORMS
          }, 400);
        }

        const mode =
          normalizePublishMode(body.mode);

        if (!mode) {
          return json({
            ok: false,
            error: "mode inválido",
            allowedModes: [
              "shareNow",
              "customScheduled",
              "addToQueue"
            ]
          }, 400);
        }

        let dueAt = null;

        if (mode === "customScheduled") {
          const parsed =
            new Date(body.dueAt || "");

          if (
            !body.dueAt ||
            Number.isNaN(parsed.getTime())
          ) {
            return json({
              ok: false,
              error:
                "dueAt ISO 8601 válido é obrigatório para customScheduled."
            }, 400);
          }

          if (
            parsed.getTime() <= Date.now() + 60_000
          ) {
            return json({
              ok: false,
              error:
                "O agendamento precisa estar pelo menos 1 minuto no futuro."
            }, 400);
          }

          dueAt = parsed.toISOString();
        }

        const draft =
          await getLocalDraft(env, body.id);

        if (!draft) {
          return json({
            ok: false,
            error: "Rascunho não encontrado"
          }, 404);
        }

        const commerceReasons = commerceGateReasons(draft);
        const semanticReasons = semanticGateReasons(draft);
        const publicationGateReasons = [...commerceReasons, ...semanticReasons];

        if (publicationGateReasons.length) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/platform-publish",
            errorClass: "commerce_or_semantic_gate_blocked",
            error: "Publicação bloqueada por hard gate Commerce/Semantic.",
            reasons: publicationGateReasons,
            publicationTriggered: false,
            bufferMutationPerformed: false
          }, 409);
        }

        if (!hasMultiPlatformAssets(draft)) {
          return json({
            ok: false,
            error:
              "Este conteúdo não possui assets multi-plataforma."
          }, 409);
        }

        const asset =
          draft.assets?.[platform];

        if (!asset?.ready || !asset?.videoUrl) {
          return json({
            ok: false,
            error:
              `Asset ${platform} ainda não está pronto.`
          }, 409);
        }

        if (
          normalizeAssetApprovalStatus(
            asset.approvalStatus
          ) !== "approved"
        ) {
          return json({
            ok: false,
            error:
              `Asset ${platform} precisa estar aprovado antes da publicação.`
          }, 409);
        }

        const currentPublication =
          asset.publication || {};

        if (
          currentPublication.bufferPostId &&
          !["error", "cancelled"].includes(
            String(
              currentPublication.status || ""
            ).toLowerCase()
          )
        ) {
          return json({
            ok: false,
            error:
              `Asset ${platform} já possui publicação Buffer ativa.`,
            publication:
              currentPublication
          }, 409);
        }

        const requestedAt =
          new Date().toISOString();

        try {
          const created =
            await createBufferPlatformVideoPost(
              draft,
              platform,
              mode,
              dueAt,
              env
            );

          const post =
            created.post;

          const publication = {
            status:
              publicationStateFromBufferPost(
                post
              ),
            bufferStatus:
              post.status || null,
            bufferPostId:
              post.id || null,
            channelId:
              created.channel?.id || null,
            channelService:
              post.channelService ||
              created.channel?.service ||
              platform,
            channelSource:
              created.channel?.source || null,
            mode,
            dueAt:
              post.dueAt || dueAt || null,
            sentAt:
              post.sentAt || null,
            externalLink:
              post.externalLink || null,
            sharedNow:
              Boolean(post.sharedNow),
            requestedAt,
            updatedAt:
              new Date().toISOString(),
            error:
              post?.error?.message || null,
            bufferError:
              post?.error || null,
            bufferDiagnostics:
              created.bufferDiagnostics || null
          };

          draft.assets = {
            ...draft.assets,
            [platform]: {
              ...asset,
              publication
            }
          };

          draft.updatedAt =
            publication.updatedAt;

          const saved =
            await saveLocalDraft(
              env,
              draft
            );

          await syncPlatformApprovalToVideoResult(
            env,
            draft.renderId || draft.id,
            saved.assets
          );

          await saveContentEvent(
            env,
            saved,
            mode === "shareNow"
              ? "platform_publish_requested"
              : "platform_scheduled",
            {
              platform,
              bufferPostId:
                publication.bufferPostId,
              bufferStatus:
                publication.bufferStatus,
              publicationStatus:
                publication.status,
              dueAt:
                publication.dueAt,
              externalLink:
                publication.externalLink
            }
          );

          return json({
            ok: true,
            version: VERSION,
            route:
              "/api/platform-publish",
            platform,
            mode,
            publication,
            post,
            assetValidation: created.assetValidation || null,
            publicationTriggered: true,
            otherPlatformsUnaffected: true
          });
        } catch (error) {
          const failedAt =
            new Date().toISOString();

          draft.assets = {
            ...draft.assets,
            [platform]: {
              ...asset,
              publication: {
                ...currentPublication,
                status: "error",
                mode,
                dueAt,
                requestedAt,
                updatedAt: failedAt,
                error:
                  error?.message ||
                  String(error),
                bufferDiagnostics:
                  error?.bufferDiagnostics || null,
                bufferPayload:
                  error?.bufferPayload || null
              }
            }
          };

          const saved =
            await saveLocalDraft(
              env,
              draft
            );

          await syncPlatformApprovalToVideoResult(
            env,
            draft.renderId || draft.id,
            saved.assets
          );

          await saveContentEvent(
            env,
            saved,
            "platform_publish_error",
            {
              platform,
              mode,
              error:
                error?.message ||
                String(error)
            }
          );

          return json({
            ok: false,
            version: VERSION,
            route:
              "/api/platform-publish",
            platform,
            mode,
            errorClass:
              "platform_publish_failed",
            error:
              error?.message ||
              String(error),
            bufferDiagnostics:
              error?.bufferDiagnostics || null,
            bufferPayload:
              error?.bufferPayload || null,
            otherPlatformsUnaffected: true
          }, 400);
        }
      }

      // ========================================================
      // R44.4.3 — PLATFORM PUBLICATION ELIGIBILITY (READ-ONLY)
      // ========================================================

      if (
        path.startsWith("/api/platform-publication-eligibility/") &&
        request.method === "GET"
      ) {
        if (
          !isAdminAuthorized(request, env) &&
          !isLolaUGIAuthorized(request, env)
        ) {
          return json({ ok: false, error: "Não autorizado" }, 401);
        }

        const id = String(
          decodeURIComponent(
            path.slice("/api/platform-publication-eligibility/".length)
          ) || ""
        ).trim();

        if (!id) {
          return json({
            ok: false,
            version: VERSION,
            route: "/api/platform-publication-eligibility/{id}",
            error: "id ausente"
          }, 400);
        }

        const draft = await getLocalDraft(env, id);

        if (!draft) {
          return json({
            ok: false,
            version: VERSION,
            route: `/api/platform-publication-eligibility/${id}`,
            draftId: id,
            error: "Rascunho não encontrado"
          }, 404);
        }

        const platformStates = {};

        for (const platform of VIDEO_PLATFORMS) {
          const asset = draft.assets?.[platform] || null;
          const approvalStatus = normalizeAssetApprovalStatus(
            asset?.approvalStatus
          );
          const ready = asset?.ready === true && Boolean(asset?.videoUrl);
          const publication = asset?.publication || null;
          const activeBufferPublication = Boolean(
            publication?.bufferPostId &&
            !["error", "cancelled"].includes(
              String(publication?.status || "").toLowerCase()
            )
          );

          const reasons = [
            ...commerceGateReasons(draft),
            ...semanticGateReasons(draft)
          ];
          if (!asset) reasons.push("asset_missing");
          else if (!ready) reasons.push("asset_not_ready");
          if (approvalStatus !== "approved") {
            reasons.push(
              approvalStatus === "rejected"
                ? "rejected"
                : "pending_approval"
            );
          }
          if (activeBufferPublication) reasons.push("buffer_publication_already_active");

          platformStates[platform] = {
            platform,
            assetExists: Boolean(asset),
            ready,
            approvalStatus,
            eligible: reasons.length === 0,
            reasons,
            bufferPostId: publication?.bufferPostId || null,
            publicationStatus: publication?.status || null
          };
        }

        const eligiblePlatforms = VIDEO_PLATFORMS.filter(
          (platform) => platformStates[platform]?.eligible === true
        );
        const ineligiblePlatforms = VIDEO_PLATFORMS.filter(
          (platform) => platformStates[platform]?.eligible !== true
        );

        return json({
          ok: true,
          version: VERSION,
          route: `/api/platform-publication-eligibility/${id}`,
          draftId: draft.id || id,
          renderId: draft.renderId || draft.id || id,
          workflowStatus: draft.workflowStatus || null,
          platformStates,
          eligiblePlatforms,
          ineligiblePlatforms,
          anyEligible: eligiblePlatforms.length > 0,
          allEligible: eligiblePlatforms.length === VIDEO_PLATFORMS.length,
          publicationTriggered: false,
          bufferMutationPerformed: false,
          note: "Consulta read-only. Nenhuma publicação, agendamento ou criação de post no Buffer foi executada."
        });
      }

      // ========================================================
      // R44.4 — PLATFORM PUBLICATION STATUS
      // ========================================================

      if (
        path === "/api/platform-publication-status" &&
        request.method === "GET"
      ) {
        if (
          !isAdminAuthorized(request, env) &&
          !isLolaUGIAuthorized(request, env)
        ) {
          return json({ ok: false, error: "Não autorizado" }, 401);
        }

        const id =
          String(
            url.searchParams.get("id") || ""
          ).trim();

        const platform =
          normalizeApprovalPlatform(
            url.searchParams.get("platform")
          );

        if (!id || !platform) {
          return json({
            ok: false,
            error:
              "id e platform são obrigatórios."
          }, 400);
        }

        const draft =
          await getLocalDraft(env, id);

        if (!draft) {
          return json({
            ok: false,
            error:
              "Rascunho não encontrado."
          }, 404);
        }

        const asset =
          draft.assets?.[platform];

        const bufferPostId =
          asset?.publication?.bufferPostId;

        if (!bufferPostId) {
          return json({
            ok: false,
            error:
              `Asset ${platform} ainda não possui bufferPostId.`
          }, 409);
        }

        try {
          const statusResult =
            await getBufferPostStatus(
              bufferPostId,
              env
            );

          const post = statusResult.post;

          const publication = {
            ...(asset.publication || {}),
            status:
              publicationStateFromBufferPost(
                post
              ),
            bufferStatus:
              post.status || null,
            dueAt:
              post.dueAt || null,
            sentAt:
              post.sentAt || null,
            externalLink:
              post.externalLink || null,
            sharedNow:
              Boolean(post.sharedNow),
            updatedAt:
              new Date().toISOString(),
            error:
              post?.error?.message ||
              asset?.publication?.error ||
              null,
            bufferError:
              post?.error || null,
            bufferDiagnostics:
              statusResult.bufferDiagnostics || null
          };

          draft.assets = {
            ...draft.assets,
            [platform]: {
              ...asset,
              publication
            }
          };

          draft.updatedAt =
            publication.updatedAt;

          const saved =
            await saveLocalDraft(
              env,
              draft
            );

          await syncPlatformApprovalToVideoResult(
            env,
            draft.renderId || draft.id,
            saved.assets
          );

          await saveContentEvent(
            env,
            saved,
            "platform_publication_status_checked",
            {
              platform,
              bufferPostId,
              bufferStatus:
                publication.bufferStatus,
              publicationStatus:
                publication.status,
              sentAt:
                publication.sentAt,
              externalLink:
                publication.externalLink
            }
          );

          return json({
            ok: true,
            version: VERSION,
            route:
              "/api/platform-publication-status",
            platform,
            publication,
            post,
            bufferDiagnostics:
              statusResult.bufferDiagnostics || null
          });
        } catch (error) {
          return json({
            ok: false,
            version: VERSION,
            route:
              "/api/platform-publication-status",
            platform,
            errorClass:
              "buffer_status_check_failed",
            error:
              error?.message ||
              String(error),
            bufferDiagnostics:
              error?.bufferDiagnostics || null,
            bufferPayload:
              error?.bufferPayload || null
          }, 400);
        }
      }

      // ========================================================
      // APIs ADMIN
      // ========================================================

      const LOLA_OPERATIONAL_ROUTES = [
        "/api/platform-approval",
        "/api/platform-publish",
        "/api/platform-publication-status",
        "/api/carousel-slide-recovery"
      ];

      const isLolaOperationalRoute =
        LOLA_OPERATIONAL_ROUTES.includes(path);

      if (
        path.startsWith("/api/") &&
        !isAdminAuthorized(request, env) &&
        !(
          isLolaOperationalRoute &&
          isLolaUGIAuthorized(request, env)
        )
      ) {
        return json(
          {
            ok: false,
            error: "Não autorizado"
          },
          401
        );
      }

      // ========================================================
      // PROPOSE
      // ========================================================

      if (path === "/api/propose" && request.method === "POST") {
        if (!env.AI || !env.MEDIA) {
          return json(
            {
              ok: false,
              error: "Bindings AI ou MEDIA (R2) não conectados"
            },
            500
          );
        }

        const history = await loadHistory(env);
        const brief = chooseBrief(history);

        const proposal = await generateStandardProposal(
          env,
          brief,
          url.origin
        );

        return json({
          ok: true,
          version: VERSION,
          proposal
        });
      }

      // ========================================================
      // ADJUST
      // ========================================================

      if (path === "/api/adjust" && request.method === "POST") {
        const body = await readBody(request);

        if (!body?.id || !String(body?.text || "").trim()) {
          return json({ ok: false, error: "Dados incompletos" }, 400);
        }

        const draft = await getLocalDraft(env, body.id);

        if (!draft) {
          return json({ ok: false, error: "Rascunho não encontrado" }, 404);
        }

        draft.text = String(body.text).trim();
        draft.updatedAt = new Date().toISOString();
        draft.qualityStatus = "manually_adjusted";
        draft.workflowStatus = "pending_approval";

        const savedDraft = await saveLocalDraft(env, draft);
        await saveContentEvent(
          env,
          savedDraft,
          "manual_adjustment"
        );

        return json({ ok: true, draft: savedDraft });
      }

      // ========================================================
      // DISCARD
      // ========================================================

      if (path === "/api/discard" && request.method === "POST") {
        const body = await readBody(request);

        if (!body?.id) {
          return json({ ok: false, error: "id ausente" }, 400);
        }

        const draft = await getLocalDraft(env, body.id);

        if (!draft) {
          return json({ ok: true });
        }

        await archiveApprovalRecord(
          env,
          draft,
          "rejected",
          { rejectedAt: new Date().toISOString() }
        );
        await saveContentEvent(env, draft, "rejected");

        await deleteDraftMedia(env, draft);
        await env.MEDIA.delete(`${DRAFT_PREFIX}${body.id}.json`);

        return json({ ok: true, archived: true });
      }

      // ========================================================
      // R43.3 — PLATFORM APPROVAL (SEM PUBLICAÇÃO AUTOMÁTICA)
      // ========================================================

      if (path === "/api/platform-approval" && request.method === "POST") {
        const body = await readBody(request);

        if (!body?.id) {
          return json({ ok: false, error: "id ausente" }, 400);
        }

        const platform = normalizeApprovalPlatform(body.platform);
        if (!platform) {
          return json({
            ok: false,
            error: "platform inválida",
            allowedPlatforms: VIDEO_PLATFORMS
          }, 400);
        }

        const decision = String(body.decision || "").trim().toLowerCase();
        if (!["approved", "rejected"].includes(decision)) {
          return json({
            ok: false,
            error: "decision deve ser approved ou rejected"
          }, 400);
        }

        const draft = await getLocalDraft(env, body.id);
        if (!draft) {
          return json({ ok: false, error: "Rascunho não encontrado" }, 404);
        }

        if (!hasMultiPlatformAssets(draft)) {
          return json({
            ok: false,
            error: "Este conteúdo não possui assets multi-plataforma."
          }, 409);
        }

        const currentAsset = draft.assets?.[platform];
        if (!currentAsset) {
          return json({
            ok: false,
            error: `Asset ${platform} ainda não existe.`
          }, 409);
        }

        if (currentAsset.ready !== true || !currentAsset.videoUrl) {
          return json({
            ok: false,
            error: `Asset ${platform} ainda não está pronto para revisão.`
          }, 409);
        }

        if (
          currentAsset?.publication?.bufferPostId &&
          !["error", "cancelled"].includes(
            String(
              currentAsset?.publication?.status || ""
            ).toLowerCase()
          )
        ) {
          return json({
            ok: false,
            error:
              `A decisão de ${platform} não pode ser alterada porque a publicação já foi enviada ao Buffer.`,
            publication:
              currentAsset.publication
          }, 409);
        }

        const decidedAt = new Date().toISOString();

        draft.assets = {
          ...draft.assets,
          [platform]: {
            ...currentAsset,
            approvalStatus: decision,
            approvalDecisionAt: decidedAt
          }
        };

        const summary = approvalSummaryFromAssets(draft.assets);

        // O rascunho permanece salvo na Central. Aprovação não publica.
        draft.status = "draft";
        draft.workflowStatus = summary.workflowStatus;
        draft.approvalSummary = summary;
        draft.updatedAt = decidedAt;

        const savedDraft = await saveLocalDraft(env, draft);

        await syncPlatformApprovalToVideoResult(
          env,
          draft.renderId || draft.id,
          savedDraft.assets
        );

        await saveContentEvent(
          env,
          savedDraft,
          decision === "approved"
            ? "platform_approved"
            : "platform_rejected",
          {
            platform,
            decision,
            approvalWorkflowStatus: summary.workflowStatus,
            approvedCount: summary.approvedCount,
            rejectedCount: summary.rejectedCount,
            pendingCount: summary.pendingCount
          }
        );

        return json({
          ok: true,
          version: VERSION,
          route: "/api/platform-approval",
          renderId: draft.renderId || draft.id,
          draftId: draft.id,
          platform,
          decision,
          asset: savedDraft.assets?.[platform] || null,
          approvalSummary: summary,
          workflowStatus: summary.workflowStatus,
          publicationTriggered: false,
          note:
            "Decisão registrada na Central. Nenhuma publicação automática foi executada."
        });
      }

      // ========================================================
      // APPROVE LEGADO
      // ========================================================

      if (path === "/api/approve" && request.method === "POST") {
        const body = await readBody(request);

        if (!body?.id) {
          return json({ ok: false, error: "id ausente" }, 400);
        }

        const draft = await getLocalDraft(env, body.id);

        if (!draft) {
          return json({ ok: false, error: "Rascunho não encontrado" }, 404);
        }

        if (hasMultiPlatformAssets(draft)) {
          return json(
            {
              ok: false,
              error:
                "Conteúdo multi-asset deve ser revisado por plataforma na Central R43.3.",
              route: "/api/platform-approval",
              platforms: VIDEO_PLATFORMS
            },
            409
          );
        }

        if (draft.renderStatus !== "ready") {
          return json(
            {
              ok: false,
              error: "O conteúdo ainda não está completamente renderizado."
            },
            409
          );
        }

        let result;

        if (draft.type === "carousel") {
          if (
            !Array.isArray(draft.imageUrls) ||
            draft.imageUrls.length < 2
          ) {
            return json(
              {
                ok: false,
                error: "Carrossel sem imagens suficientes."
              },
              409
            );
          }

          result = await bufferCreateCarousel(draft, env);
        } else if (draft.type === "reel" || draft.type === "video") {
          if (!draft.videoUrl) {
            return json(
              {
                ok: false,
                error: "Vídeo ainda não disponível."
              },
              409
            );
          }

          result = await bufferCreateVideo(draft, env);
        } else {
          if (!draft.imageUrl) {
            return json(
              {
                ok: false,
                error: "Imagem ainda não disponível."
              },
              409
            );
          }

          result = await bufferCreatePost(draft, env);
        }

        const created = result?.data?.createPost;

        if (!created?.post) {
          throw new Error(
            created?.message ||
            firstGraphQLError(result) ||
            "O Buffer não criou a publicação."
          );
        }

        draft.status = created.post.status || "scheduled";
        draft.workflowStatus = draft.status;
        draft.bufferPostId = created.post.id;
        draft.dueAt = created.post.dueAt || null;
        draft.approvedAt = new Date().toISOString();
        draft.updatedAt = draft.approvedAt;

        await archiveApprovalRecord(
          env,
          draft,
          draft.status,
          {
            bufferPostId: draft.bufferPostId,
            dueAt: draft.dueAt
          }
        );
        await saveContentEvent(
          env,
          draft,
          "approved_to_buffer",
          {
            bufferPostId: draft.bufferPostId,
            dueAt: draft.dueAt
          }
        );

        await env.MEDIA.delete(`${DRAFT_PREFIX}${draft.id}.json`);

        return json({
          ok: true,
          post: created.post,
          draft,
          musicNotice:
            draft.music?.requested
              ? "A faixa foi mantida como metadata. Esta versão não anexa automaticamente música da biblioteca do Instagram."
              : null
        });
      }

      // ========================================================
      // HOME
      // ========================================================

      return json({
        ok: true,
        version: VERSION,
        message: "Lola Operacional UGI ativa",
        multimedia: true,
        post: true,
        carousel: true,
        carouselExactText: true,
            carouselNoAITextRendering: true,
        video: true,
        mediaTransformations: Boolean(env.VIDEO),
        imagesBinding: Boolean(env.IMAGES),
        carouselRenderer: "r19-browser-photo-editorial-png",
        semanticValidation: true,
          editorialSelfRepair: true,
          visualBackgroundGeneration: true,
          exactTextOverlay: true,
          terminalStyleRemoved: true,
          browserRunRenderer: true,
          browserRunRequiredForCarousel: true,
          photoPerCarouselSlide: true,
          automaticImageFallbackDisabled: true,
          beatlyMusicMetadataReady: true,
        beatlyCatalogRotation: true,
        beatlyBusinessRelevancePolicy: true,
        semanticGateSelfHealing: true,
        musicMetadata: true,
        musicMixingAutomatic: false,
        central: "/approve",
        health: "/api/health",
        command: "POST /api/command",
        commands: "GET /api/commands",
        drafts: "GET /api/drafts",
        musicCatalogStatus: "GET /api/music/catalog/status",
            musicPolicyStatus: "GET /api/music/policy/status",
        buffer: "somente na aprovação"
      });
    } catch (error) {
      // R37.2 — Actions do ChatGPT tratam respostas HTTP não-2xx como
      // ClientResponseError antes de exibir o corpo. Para /api/video-render,
      // devolvemos diagnóstico em HTTP 200 para tornar o erro observável.
      if (
        request.method === "POST" &&
        new URL(request.url).pathname === "/api/video-render"
      ) {
        return json(
          {
            ok: false,
            version: VERSION,
            route: "/api/video-render",
            errorClass: "video_render_unexpected_exception",
            error: error?.message || String(error),
            stack: String(error?.stack || "").slice(0, 2000),
            diagnosticHttpStatus: 200,
            note:
              "Erro inesperado capturado em HTTP 200 para evitar ClientResponseError e permitir diagnóstico."
          },
          200
        );
      }

      return json(
        {
          ok: false,
          version: VERSION,
          error: error?.message || String(error)
        },
        500
      );
    }
  }
};

// ============================================================
// AUTH
// ============================================================

function isAdminAuthorized(request, env) {
  const expected = env.LOLA_AUTH_KEY;

  if (!expected) return false;

  // Compatibilidade existente: header administrativo customizado.
  if (request.headers.get("x-lola-key") === expected) {
    return true;
  }

  // R44.4.12: GPT Actions usa uma única configuração de autenticação
  // por Action e pode transmitir a API key como Authorization: Bearer.
  // Aceitar o MESMO LOLA_AUTH_KEY como Bearer evita exigir troca de
  // nomes de secrets ou alterações no GitHub.
  const authorization = request.headers.get("authorization") || "";

  if (authorization.startsWith("Bearer ")) {
    return authorization.slice(7).trim() === expected;
  }

  return false;
}

function buildSafeAuthDiagnostic(request, env) {
  const authorization = request.headers.get("authorization") || "";
  const bearer = authorization.startsWith("Bearer ")
    ? authorization.slice(7).trim()
    : "";

  const xLolaKey = request.headers.get("x-lola-key") || "";
  const xCommandKey = request.headers.get("x-lola-command-key") || "";

  return {
    authorizationPresent: Boolean(authorization),
    bearerPresent: Boolean(bearer),
    xLolaKeyPresent: Boolean(xLolaKey),
    xLolaCommandKeyPresent: Boolean(xCommandKey),
    lolaAuthKeyConfigured: Boolean(env.LOLA_AUTH_KEY),
    lolaCommandKeyConfigured: Boolean(env.LOLA_COMMAND_KEY),
    bearerMatchesLolaAuthKey:
      Boolean(bearer) &&
      Boolean(env.LOLA_AUTH_KEY) &&
      bearer === env.LOLA_AUTH_KEY,
    bearerMatchesLolaCommandKey:
      Boolean(bearer) &&
      Boolean(env.LOLA_COMMAND_KEY) &&
      bearer === env.LOLA_COMMAND_KEY,
    xLolaKeyMatches:
      Boolean(xLolaKey) &&
      Boolean(env.LOLA_AUTH_KEY) &&
      xLolaKey === env.LOLA_AUTH_KEY,
    xLolaCommandKeyMatches:
      Boolean(xCommandKey) &&
      Boolean(env.LOLA_COMMAND_KEY) &&
      xCommandKey === env.LOLA_COMMAND_KEY
  };
}

function isLolaUGIAuthorized(request, env) {
  const expected = env.LOLA_COMMAND_KEY;

  if (!expected) return false;

  const custom = request.headers.get("x-lola-command-key");

  if (custom === expected) return true;

  const authorization = request.headers.get("authorization") || "";

  if (authorization.startsWith("Bearer ")) {
    return authorization.slice(7).trim() === expected;
  }

  return false;
}

function isGithubVideoUploadAuthorized(request, env) {
  const expected = env.GITHUB_VIDEO_UPLOAD_KEY;
  if (!expected) return false;

  const custom = request.headers.get("x-ugi-video-upload-key");
  if (custom && custom === expected) return true;

  const authorization = request.headers.get("authorization") || "";
  if (authorization.startsWith("Bearer ")) {
    return authorization.slice(7).trim() === expected;
  }

  return false;
}

function sanitizeRenderId(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  return /^[a-zA-Z0-9][a-zA-Z0-9._-]{5,119}$/.test(raw) ? raw : "";
}

function createRenderId() {
  const stamp = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14);
  const random = crypto.randomUUID().replace(/-/g, "").slice(0, 12);
  return `ugi-${stamp}-${random}`;
}

function hasMp4FtypSignature(bytes) {
  if (!bytes || bytes.length < 12) return false;
  // ISO Base Media File Format: bytes 4..7 devem conter a box `ftyp`.
  return (
    bytes[4] === 0x66 &&
    bytes[5] === 0x74 &&
    bytes[6] === 0x79 &&
    bytes[7] === 0x70
  );
}

async function saveVideoResult(env, result) {
  if (!env.MEDIA || !result?.renderId) return;

  const payload = JSON.stringify(result, null, 2);
  const metadata = { httpMetadata: { contentType: "application/json" } };

  await Promise.all([
    env.MEDIA.put(`${VIDEO_RESULT_PREFIX}${result.renderId}.json`, payload, metadata),
    result.status === "ready"
      ? env.MEDIA.put(VIDEO_RESULT_LATEST_KEY, payload, metadata)
      : Promise.resolve()
  ]);
}

async function loadVideoResult(env, renderId) {
  const object = await env.MEDIA.get(`${VIDEO_RESULT_PREFIX}${renderId}.json`);
  if (!object) return null;
  try {
    return JSON.parse(await object.text());
  } catch {
    return null;
  }
}

async function loadLatestVideoResult(env) {
  const object = await env.MEDIA.get(VIDEO_RESULT_LATEST_KEY);
  if (!object) return null;
  try {
    return JSON.parse(await object.text());
  } catch {
    return null;
  }
}

// ============================================================
// R44.5.2 — COMMERCE + COPY LOCK + SEMANTIC BRIDGE
// ============================================================


function isCommerceAdminAuthorized(request, env) {
  return isAdminAuthorized(request, env) || isLolaUGIAuthorized(request, env);
}

function sanitizeCommerceId(value) {
  const raw = String(value || "").trim();
  if (!raw || raw.length > 160) return "";
  return /^[a-zA-Z0-9._:-]+$/.test(raw) ? raw : "";
}

function sanitizeDeliveryToken(value) {
  const raw = String(value || "").trim();
  return /^[a-f0-9-]{20,80}$/i.test(raw) ? raw : "";
}

function newCommerceId(prefix) {
  return `${prefix}-${crypto.randomUUID()}`;
}

async function putJsonR2(env, key, value) {
  if (!env.MEDIA) throw new Error("r2_binding_missing");
  await env.MEDIA.put(key, JSON.stringify(value, null, 2), { httpMetadata: { contentType: "application/json", cacheControl: "no-store" } });
}

async function getJsonR2(env, key) {
  if (!env.MEDIA) return null;
  const obj = await env.MEDIA.get(key);
  if (!obj) return null;
  try { return JSON.parse(await obj.text()); } catch { return null; }
}

async function listJsonPrefix(env, prefix, limit = 100) {
  if (!env.MEDIA) return [];
  const listed = await env.MEDIA.list({ prefix, limit: Math.max(1, Math.min(Number(limit) || 100, 1000)) });
  const rows = [];
  for (const item of listed.objects || []) {
    if (!item.key.endsWith(".json")) continue;
    const value = await getJsonR2(env, item.key);
    if (value) rows.push(value);
  }
  return rows;
}

function normalizeMaterialRecord(body = {}) {
  const now = new Date().toISOString();
  const materialId = sanitizeCommerceId(body.materialId || body.material_id || "") || newCommerceId("mat");
  return {
    materialId,
    title: String(body.title || "").trim(),
    theme: String(body.theme || "").trim(),
    problem: String(body.problem || "").trim(),
    solution: String(body.solution || "").trim(),
    description: String(body.description || "").trim() || null,
    version: String(body.version || "1.0").trim(),
    status: String(body.status || "draft").trim(),
    qualityStatus: String(body.qualityStatus || body.quality_status || "NOT_RUN").trim().toUpperCase(),
    qualityGates: body.qualityGates && typeof body.qualityGates === "object" ? body.qualityGates : null,
    reuseWindowDays: Number.isFinite(Number(body.reuseWindowDays)) ? Number(body.reuseWindowDays) : 30,
    fileKey: String(body.fileKey || body.materialKey || "").trim() || null,
    materialKey: String(body.materialKey || body.fileKey || "").trim() || null,
    fileUrl: String(body.fileUrl || body.materialUrl || "").trim() || null,
    checksum: String(body.checksum || "").trim() || null,
    mimeType: String(body.mimeType || "").trim() || null,
    size: Number.isFinite(Number(body.size)) ? Number(body.size) : null,
    assetReady: body.assetReady === true,
    deliveryEnabled: body.deliveryEnabled === true,
    createdAt: String(body.createdAt || now),
    updatedAt: now,
    lastUsedAt: body.lastUsedAt || null
  };
}

function normalizeProductRecord(body = {}) {
  const now = new Date().toISOString();
  const productId = sanitizeCommerceId(body.productId || body.product_id || "") || newCommerceId("prod");
  return {
    productId,
    materialId: sanitizeCommerceId(body.materialId || body.material_id || ""),
    title: String(body.title || "").trim(),
    theme: String(body.theme || "").trim() || null,
    description: String(body.description || "").trim() || null,
    price: Number(body.price),
    currency: String(body.currency || "BRL").trim().toUpperCase(),
    commercialIntent: String(body.commercialIntent || body.commercial_intent || "direct_low_ticket_conversion").trim(),
    commercialOffer: body.commercialOffer !== false,
    status: String(body.status || "active").trim(),
    provider: String(body.provider || "").trim() || null,
    createdAt: String(body.createdAt || now),
    updatedAt: now,
    lastUsedAt: body.lastUsedAt || null
  };
}

function commerceProviderStatus(env) {
  return {
    asaas: { apiKey: Boolean(env.ASAAS_API_KEY), webhookToken: Boolean(env.ASAAS_WEBHOOK_TOKEN) },
    pagbank: { token: Boolean(env.PAGBANK_TOKEN), webhookVerificationImplemented: false }
  };
}

function resolveCommerceProvider(env, requested = null) {
  const name = String(requested || "").trim().toLowerCase();
  if ((!name || name === "asaas") && env.ASAAS_API_KEY) return "asaas";
  if (name === "pagbank" && env.PAGBANK_TOKEN) return "pagbank";
  if (!name && env.PAGBANK_TOKEN) return "pagbank";
  return null;
}

async function createProviderCheckout(env, provider, product, material, body, origin) {
  const referenceId = sanitizeCommerceId(body.referenceId || body.reference_id || "") || newCommerceId("ord");
  const providerPayload = body.providerPayload && typeof body.providerPayload === "object" ? { ...body.providerPayload } : null;
  if (!providerPayload) throw new Error("provider_payload_required");
  const now = new Date().toISOString();
  let endpoint = "";
  let headers = { "Content-Type": "application/json" };
  let payload = providerPayload;

  if (provider === "asaas") {
    endpoint = `${String(env.ASAAS_API_BASE || "https://api.asaas.com/v3").replace(/\/$/, "")}/checkouts`;
    headers.access_token = env.ASAAS_API_KEY;
    payload.externalReference = payload.externalReference || referenceId;
  } else if (provider === "pagbank") {
    endpoint = `${String(env.PAGBANK_API_BASE || "https://api.pagseguro.com").replace(/\/$/, "")}/checkouts`;
    headers.Authorization = `Bearer ${env.PAGBANK_TOKEN}`;
    headers["x-idempotency-key"] = referenceId;
    payload.reference_id = payload.reference_id || referenceId;
    payload.notification_urls = payload.notification_urls || [`${origin}/api/commerce/webhook/pagbank`];
    payload.payment_notification_urls = payload.payment_notification_urls || [`${origin}/api/commerce/webhook/pagbank`];
  } else {
    throw new Error("unsupported_provider");
  }

  const response = await fetch(endpoint, { method: "POST", headers, body: JSON.stringify(payload) });
  const raw = await response.text();
  let data = null;
  try { data = JSON.parse(raw); } catch { data = { raw: raw.slice(0, 2000) }; }
  if (!response.ok) {
    const error = new Error(`provider_checkout_failed_${response.status}`);
    error.providerResponse = data;
    throw error;
  }

  const providerId = String(data?.id || data?.checkoutId || data?.checkout_id || "").trim();
  const checkoutUrl = String(data?.url || data?.checkoutUrl || data?.checkout_url || data?.link || data?.paymentLink || "").trim();
  if (!providerId || !checkoutUrl) {
    const error = new Error("provider_checkout_response_incomplete");
    error.providerResponse = data;
    throw error;
  }
  const checkoutId = sanitizeCommerceId(providerId) || newCommerceId("chk");
  return {
    checkoutId,
    providerCheckoutId: providerId,
    checkoutUrl,
    referenceId,
    provider,
    productId: product.productId,
    materialId: material.materialId,
    amount: product.price,
    currency: product.currency || "BRL",
    status: "created",
    paymentStatus: "pending",
    fulfillmentReady: false,
    createdAt: now,
    updatedAt: now,
    providerResponse: data
  };
}

function normalizeAsaasWebhook(body = {}) {
  const payment = body.payment && typeof body.payment === "object" ? body.payment : {};
  const checkout = body.checkout && typeof body.checkout === "object" ? body.checkout : {};
  const status = String(payment.status || body.status || "").trim().toUpperCase();
  const event = String(body.event || "").trim().toUpperCase();
  const paidStatuses = new Set(["RECEIVED", "CONFIRMED", "RECEIVED_IN_CASH"]);
  const paidEvents = new Set(["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED", "PAYMENT_RECEIVED_IN_CASH"]);
  return {
    event,
    status: status.toLowerCase() || null,
    paid: paidStatuses.has(status) || paidEvents.has(event),
    paymentId: String(payment.id || body.paymentId || "").trim() || null,
    referenceId: sanitizeCommerceId(payment.externalReference || checkout.externalReference || body.externalReference || "")
  };
}

async function fulfillPaidOrder(env, order, origin) {
  const material = await getJsonR2(env, `${MATERIAL_PREFIX}${order.materialId}.json`);
  if (!material?.assetReady || !material?.fileKey || material?.qualityStatus !== "PASS" || material?.deliveryEnabled !== true) {
    return { orderPatch: { fulfillmentStatus: "blocked", fulfillmentError: "material_not_ready", fulfillmentReady: false } };
  }
  const token = crypto.randomUUID();
  const now = new Date();
  const expiresAt = new Date(now.getTime() + DELIVERY_TOKEN_TTL_MS).toISOString();
  const grant = {
    token,
    referenceId: order.referenceId,
    productId: order.productId,
    materialId: order.materialId,
    fileKey: material.fileKey,
    mimeType: material.mimeType || "application/octet-stream",
    fileName: `${String(material.title || "material-ugi").replace(/[^a-zA-Z0-9._-]+/g, "-")}.${String(material.mimeType || "").includes("pdf") ? "pdf" : "bin"}`,
    createdAt: now.toISOString(),
    expiresAt
  };
  await putJsonR2(env, `${DELIVERY_PREFIX}${token}.json`, grant);
  return { orderPatch: { fulfillmentStatus: "fulfilled", fulfillmentReady: true, fulfilledAt: now.toISOString(), deliveryUrl: `${origin}/api/material-delivery/${token}`, deliveryExpiresAt: expiresAt } };
}

function normalizeUGICommerce(body = {}, existing = null) {
  const source = body?.commerce && typeof body.commerce === "object"
    ? body.commerce
    : {};

  const prior = existing && typeof existing === "object" ? existing : {};

  const productId = String(
    source.product_id || source.productId ||
    body.product_id || body.productId ||
    prior.productId || prior.product_id || ""
  ).trim() || null;

  const priceId = String(
    source.price_id || source.priceId ||
    body.price_id || body.priceId ||
    prior.priceId || prior.price_id || ""
  ).trim() || null;

  const paymentLink = String(
    source.payment_link || source.paymentLink || source.checkout_url || source.checkoutUrl ||
    body.payment_link || body.paymentLink || body.checkout_url || body.checkoutUrl ||
    prior.paymentLink || prior.payment_link || prior.checkoutUrl || ""
  ).trim() || null;

  const materialId = String(
    source.material_id || source.materialId ||
    body.material_id || body.materialId ||
    prior.materialId || prior.material_id || ""
  ).trim() || null;

  const materialUrl = String(
    source.material_url || source.materialUrl ||
    body.material_url || body.materialUrl ||
    prior.materialUrl || prior.material_url || ""
  ).trim() || null;

  const fulfillmentReady =
    source.fulfillment_ready === true || source.fulfillmentReady === true ||
    body.fulfillment_ready === true || body.fulfillmentReady === true ||
    prior.fulfillmentReady === true;

  const required =
    source.required === true || body.commercial_offer === true ||
    body.commercialOffer === true || prior.required === true;

  return {
    required,
    productId,
    priceId,
    paymentLink,
    materialId,
    materialUrl,
    fulfillmentReady,
    provider: String(source.provider || prior.provider || "").trim() || null,
    currency: String(source.currency || prior.currency || "BRL").trim() || "BRL",
    price: Number.isFinite(Number(source.price ?? prior.price))
      ? Number(source.price ?? prior.price)
      : null
  };
}

function normalizeUGICopyLock(body = {}, type = null, existing = null) {
  const raw = body?.copy_lock ?? body?.copyLock ?? body?.exact_copy ?? body?.exactCopy ?? null;
  const prior = existing && typeof existing === "object" ? existing : {};

  if (raw === null || raw === undefined || raw === false) {
    return {
      ...prior,
      enabled: prior.enabled === true
    };
  }

  if (raw === true) {
    return {
      ...prior,
      enabled: true,
      mode: prior.mode || "exact"
    };
  }

  if (typeof raw === "string") {
    return {
      ...prior,
      enabled: true,
      mode: "exact",
      caption: raw
    };
  }

  if (typeof raw !== "object") {
    return { ...prior, enabled: false };
  }

  const slides = Array.isArray(raw.slides)
    ? raw.slides.map((slide, index) => ({
        number: index + 1,
        headline: sanitizeSlideText(slide?.headline || ""),
        body: sanitizeSlideText(slide?.body || "")
      }))
    : (Array.isArray(prior.slides) ? prior.slides : null);

  const videoScenes = Array.isArray(raw.video_scenes || raw.videoScenes || raw.scenes)
    ? (raw.video_scenes || raw.videoScenes || raw.scenes)
    : (Array.isArray(prior.videoScenes) ? prior.videoScenes : null);

  return {
    enabled: raw.enabled !== false,
    mode: String(raw.mode || prior.mode || "exact").trim() || "exact",
    type: String(raw.type || type || prior.type || "").trim() || null,
    caption: String(raw.caption || prior.caption || "").trim() || null,
    cta: String(raw.cta || prior.cta || "").trim() || null,
    slides,
    videoScenes,
    strict: raw.strict !== false
  };
}

function applyCarouselCopyLock(command, pkg) {
  const lock = command?.copyLock;
  if (!lock?.enabled) return pkg;

  const next = {
    ...pkg,
    caption: lock.caption || pkg.caption,
    slides: Array.isArray(pkg.slides) ? pkg.slides.map((slide) => ({ ...slide })) : []
  };

  if (Array.isArray(lock.slides) && lock.slides.length) {
    if (lock.slides.length !== command.slides) {
      throw new Error(
        `COPY_LOCK_INVALID: slides locked=${lock.slides.length}; expected=${command.slides}`
      );
    }

    next.slides = lock.slides.map((slide, index) => ({
      number: index + 1,
      headline: sanitizeSlideText(slide.headline || ""),
      body: sanitizeSlideText(slide.body || "")
    }));
  }

  if (lock.cta && next.slides.length) {
    next.slides[next.slides.length - 1].body = sanitizeSlideText(lock.cta);
  }

  return next;
}

function validateCarouselCopyLock(command, pkg) {
  const lock = command?.copyLock;
  if (!lock?.enabled) {
    return { required: false, pass: true, mismatches: [] };
  }

  const mismatches = [];

  if (lock.caption && String(pkg?.caption || "").trim() !== String(lock.caption).trim()) {
    mismatches.push("caption_mismatch");
  }

  if (Array.isArray(lock.slides)) {
    if (!Array.isArray(pkg?.slides) || pkg.slides.length !== lock.slides.length) {
      mismatches.push("slide_count_mismatch");
    } else {
      lock.slides.forEach((expected, index) => {
        const actual = pkg.slides[index] || {};
        if (sanitizeSlideText(actual.headline || "") !== sanitizeSlideText(expected.headline || "")) {
          mismatches.push(`slide_${index + 1}_headline_mismatch`);
        }
        if (sanitizeSlideText(actual.body || "") !== sanitizeSlideText(expected.body || "")) {
          mismatches.push(`slide_${index + 1}_body_mismatch`);
        }
      });
    }
  }

  if (lock.cta && pkg?.slides?.length) {
    const actualCTA = sanitizeSlideText(pkg.slides[pkg.slides.length - 1]?.body || "");
    if (actualCTA !== sanitizeSlideText(lock.cta)) {
      mismatches.push("cta_mismatch");
    }
  }

  return {
    required: true,
    pass: mismatches.length === 0,
    mode: lock.mode || "exact",
    mismatches
  };
}

function commerceGateReasons(draft) {
  const commerce = normalizeUGICommerce({}, draft?.commerce || null);
  const required = draft?.commercialOffer === true || commerce.required === true;
  if (!required) return [];

  const reasons = [];
  if (!commerce.productId) reasons.push("commerce_product_id_missing");
  if (!commerce.priceId) reasons.push("commerce_price_id_missing");
  if (!commerce.paymentLink) reasons.push("commerce_payment_link_missing");
  if (!commerce.materialId) reasons.push("commerce_material_id_missing");
  if (!commerce.materialUrl) reasons.push("commerce_material_url_missing");
  if (commerce.fulfillmentReady !== true) reasons.push("commerce_fulfillment_not_ready");
  return reasons;
}

function semanticGateReasons(draft) {
  const strict = draft?.semanticValidationRequired === true || draft?.copyLock?.enabled === true;
  if (!strict) return [];

  const reasons = [];
  if (draft?.semanticValidationAvailable !== true) {
    reasons.push("semantic_validation_unavailable");
  } else if (draft?.semanticValidation?.pass !== true) {
    reasons.push("semantic_validation_failed");
  }
  if (draft?.legacyContentLeakDetected === true) {
    reasons.push("legacy_content_leak_detected");
  }
  if (draft?.copyLock?.enabled === true && draft?.copyLockValidation?.pass !== true) {
    reasons.push("copy_lock_failed");
  }
  return reasons;
}

// ============================================================
// COMMAND HUB
// ============================================================

function validateCommand(body) {
  const allowed = ["carousel", "post", "reel", "video"];

  const type = String(body?.type || "").trim().toLowerCase();

  if (!allowed.includes(type)) {
    return "type deve ser 'post', 'carousel', 'reel' ou 'video'";
  }

  if (!String(body?.topic || "").trim()) {
    return "topic é obrigatório";
  }

  return null;
}

function createCommand(body) {
  const id = crypto.randomUUID();

  const type = String(body.type).trim().toLowerCase();

  const musicInput =
    body.music && typeof body.music === "object"
      ? body.music
      : {};

  const commandTextForMusic = normalizeText([
    body.topic,
    body.objective,
    body.key_message,
    body.keyMessage,
    body.instructions,
    body.cta
  ].filter(Boolean).join(" "));

  const musicRequestedByText =
    /\b(musica|trilha|audio|beatly|som)\b/.test(commandTextForMusic);

  const beatlyRequestedByText =
    /\bbeatly\b/.test(commandTextForMusic);

  return {
    id,
    version: VERSION,

    source: String(body.source || "lola-chatgpt"),

    type,

    contentId: String(
      body.content_id ||
      body.contentId ||
      ""
    ).trim() || null,

    experimentId: String(
      body.experiment_id ||
      body.experimentId ||
      body.experiment ||
      ""
    ).trim() || null,

    variant: String(
      body.variant ||
      ""
    ).trim() || null,

    commercialIntent: String(
      body.commercial_intent ||
      body.commercialIntent ||
      ""
    ).trim() || null,

    topic: String(body.topic).trim(),

    objective: String(
      body.objective || "organic_growth"
    ).trim(),

    audience: String(
      body.audience ||
      "gestores, líderes, coordenadores, empreendedores e profissionais responsáveis por equipes"
    ).trim(),

    hook: String(body.hook || "").trim(),

    keyMessage: String(
      body.key_message ||
      body.keyMessage ||
      ""
    ).trim(),

    instructions: String(body.instructions || "").trim(),

    cta: String(body.cta || "salvar e compartilhar").trim(),

    slides:
      type === "carousel"
        ? clamp(Number(body.slides || 7), 4, 10)
        : 1,

    requestedVideoDuration:
      type === "reel" || type === "video"
        ? clamp(
            Number(body.duration || body.video_duration || 8),
            4,
            40
          )
        : null,

    // Veo 3.1 Fast aceita 4s, 6s ou 8s por geração.
    // Nunca declaramos como duração real algo maior que o arquivo produzido.
    videoDuration:
      type === "reel" || type === "video"
        ? resolveVeoDurationSeconds(
            Number(body.duration || body.video_duration || 8)
          )
        : null,

    music: {
      requested: Boolean(
        musicInput.title ||
        musicInput.track ||
        body.music_title ||
        musicRequestedByText
      ),

      title: String(
        musicInput.title ||
        musicInput.track ||
        body.music_title ||
        ""
      ).trim(),

      artist: String(
        musicInput.artist ||
        body.music_artist ||
        ""
      ).trim(),

      audioId: String(
        musicInput.audio_id ||
        musicInput.audioId ||
        body.instagram_audio_id ||
        ""
      ).trim(),

      source: String(
        musicInput.source ||
        (
          beatlyRequestedByText
            ? "beatly"
            : (
                musicInput.title ||
                body.music_title ||
                musicRequestedByText
                  ? "beatly"
                  : ""
              )
        )
      ).trim(),

      startSeconds:
        Number(
          musicInput.start_seconds ||
          musicInput.startSeconds ||
          0
        ) || 0,

      status:
        musicInput.title ||
        body.music_title ||
        musicRequestedByText
          ? "requested"
          : "none",

      policy: {
        provider: "beatly",
        currentAndModern: true,
        businessRelevant: true,
        professionalTone: true,
        avoidExplicit: true,
        avoidAggressiveOrDistracting: true,
        avoidRandomTrendWithoutContext: true,
        rotationWithoutRepeat: true,
        restartAfterCatalogExhausted: true
      }
    },

    commercialOffer: body.commercial_offer === true,

    editorialMode: String(
      body.editorial_mode || body.editorialMode || "standard"
    ).trim() || "standard",

    copyLock: normalizeUGICopyLock(body, type),

    commerce: normalizeUGICommerce(body),

    campaign: String(
      body.campaign || "UGI Organic Growth"
    ).trim(),

    experiment: String(body.experiment || "").trim(),

    requestedBy: String(body.requested_by || "Lola").trim(),

    status: "received",

    generationStatus: "pending",

    createdAt: new Date().toISOString()
  };
}

async function saveCommand(env, command) {
  await env.MEDIA.put(
    `${COMMAND_PREFIX}${command.id}.json`,
    JSON.stringify(command),
    {
      httpMetadata: {
        contentType: "application/json"
      }
    }
  );
}


async function getLocalCommand(env, id) {
  if (!env.MEDIA || !id) return null;

  const object = await env.MEDIA.get(
    `${COMMAND_PREFIX}${id}.json`
  );

  if (!object) return null;

  try {
    return await object.json();
  } catch {
    return null;
  }
}

async function listCommands(env) {
  const result = await env.MEDIA.list({
    prefix: COMMAND_PREFIX,
    limit: COMMAND_LIMIT
  });

  const commands = [];

  for (const item of result.objects) {
    if (!item.key.endsWith(".json")) continue;

    try {
      const object = await env.MEDIA.get(item.key);

      if (!object) continue;

      commands.push(await object.json());
    } catch {}
  }

  commands.sort((a, b) =>
    String(b.createdAt || "").localeCompare(
      String(a.createdAt || "")
    )
  );

  return commands;
}

// ============================================================
// COMMAND -> GERAÇÃO
// ============================================================

async function generateFromCommand(env, command, origin) {
  if (command.type === "carousel") {
    return generateCarousel(env, command, origin);
  }

  if (command.type === "reel" || command.type === "video") {
    return generateVideoDraft(env, command, origin);
  }

  const brief = {
    id: `command-${command.id}`,
    area: command.topic,
    angle: command.objective,
    hashtags: ["#Gestao", "#Lideranca", BRAND_HASHTAG],
    instruction:
      [command.keyMessage, command.instructions]
        .filter(Boolean)
        .join(" ") ||
      `Desenvolva uma orientação prática sobre ${command.topic}.`,
    cta: command.cta
  };

  return generateStandardProposal(
    env,
    brief,
    origin,
    command
  );
}

// ============================================================
// CARROSSEL — TEXTO EXATO + IMAGES BINDING
// ============================================================

async function generateCarousel(env, command, origin) {
  let packageResult = null;
  let audit = null;
  let lastError = null;
  let fallbackUsed = false;
  let semanticRepairExhausted = false;

  // R14: gera e autocorrige antes de desistir.
  // O gate determinístico é duro; o gate semântico tenta reparo,
  // mas não impede a renderização indefinidamente quando a estrutura está correta.
  for (
    let generationAttempt = 0;
    generationAttempt < FULL_GENERATION_ATTEMPTS;
    generationAttempt++
  ) {
    let result = null;

    for (
      let attempt = 0;
      attempt < CAROUSEL_ATTEMPTS;
      attempt++
    ) {
      try {
        result = await aiCarouselJSON(
          env,
          command,
          generationAttempt * 10 + attempt
        );

        if (
          result &&
          Array.isArray(result.slides) &&
          result.slides.length >= 4
        ) {
          break;
        }
      } catch (error) {
        lastError = error;
      }
    }

    if (
      !result ||
      !Array.isArray(result.slides) ||
      result.slides.length < 4
    ) {
      fallbackUsed = true;
      result = deterministicCarouselFallback(command);
    }

    try {
      result = await repairCarouselText(env, command, result);
      packageResult = await normalizeCarouselPackage(
        env,
        command,
        result
      );
      audit = await auditCarouselPackage(
        env,
        command,
        packageResult
      );

      for (
        let repairAttempt = 0;
        repairAttempt < CAROUSEL_PACKAGE_REPAIRS && !audit.pass;
        repairAttempt++
      ) {
        packageResult = await repairCarouselPackage(
          env,
          command,
          packageResult,
          audit,
          generationAttempt * 10 + repairAttempt
        );

        packageResult = await normalizeCarouselPackage(
          env,
          command,
          packageResult
        );

        audit = await auditCarouselPackage(
          env,
          command,
          packageResult
        );
      }

      if (audit?.pass) break;

      // Se só a semântica ainda discorda, geramos uma nova proposta
      // completa antes de aceitar uma revisão humana.
      if (audit?.hardPass && !audit?.semanticPass) {
        semanticRepairExhausted = true;
      }
    } catch (error) {
      lastError = error;
    }
  }

  // Fallback final existe apenas para garantir estrutura.
  // Nunca volta ao renderer visual antigo.
  if (!packageResult) {
    fallbackUsed = true;
    packageResult = await normalizeCarouselPackage(
      env,
      command,
      deterministicCarouselFallback(command)
    );

    audit = await auditCarouselPackage(
      env,
      command,
      packageResult,
      { skipAI: true }
    );
  }

  // R19 FINAL CLOSURE:
  // Antes de bloquear por requisito objetivo, repara deterministicamente
  // os elementos que vieram literalmente do briefing.
  if (!audit?.hardPass) {
    const hardIssues = Array.isArray(audit?.hardIssues)
      ? audit.hardIssues
      : [];

    let deterministicRepairApplied = false;

    if (
      hardIssues.includes("capa explícita não foi preservada") &&
      hasExplicitCarouselCover(command) &&
      Array.isArray(packageResult?.slides) &&
      packageResult.slides[0]
    ) {
      packageResult.slides[0].headline = sanitizeSlideText(
        resolveRequiredCover(command)
      );
      deterministicRepairApplied = true;
    }

    if (
      hardIssues.includes("fechamento não preservou o CTA do briefing") &&
      Array.isArray(packageResult?.slides) &&
      packageResult.slides.length
    ) {
      packageResult.slides[
        packageResult.slides.length - 1
      ].body = sanitizeSlideText(
        resolveRequiredCarouselCTA(command)
      );
      deterministicRepairApplied = true;
    }

    if (deterministicRepairApplied) {
      packageResult = await normalizeCarouselPackage(
        env,
        command,
        packageResult
      );

      // A normalização pode tentar ajustar a capa novamente.
      // Por isso, a literalidade exigida é reaplicada no último instante.
      if (
        hasExplicitCarouselCover(command) &&
        packageResult?.slides?.[0]
      ) {
        packageResult.slides[0].headline = sanitizeSlideText(
          resolveRequiredCover(command)
        );
      }

      if (
        packageResult?.slides?.length &&
        resolveRequiredCarouselCTA(command)
      ) {
        packageResult.slides[
          packageResult.slides.length - 1
        ].body = sanitizeSlideText(
          resolveRequiredCarouselCTA(command)
        );
      }

      audit = await auditCarouselPackage(
        env,
        command,
        packageResult,
        { skipAI: true }
      );
    }
  }

  // R44.5.2: copy-lock é aplicado por último, depois de qualquer geração/rewrite.
  // Assim nenhum modelo pode substituir a copy aprovada.
  if (command?.copyLock?.enabled) {
    packageResult = applyCarouselCopyLock(command, packageResult);
    const copyLockValidation = validateCarouselCopyLock(command, packageResult);
    if (!copyLockValidation.pass) {
      throw new Error(
        `COPY_LOCK_FAILED: ${copyLockValidation.mismatches.join(" | ")}`
      );
    }
    audit = await auditCarouselPackage(
      env,
      command,
      packageResult,
      { skipAI: true }
    );
  }

  // Somente requisitos objetivos realmente irrecuperáveis bloqueiam.
  if (!audit?.hardPass) {
    throw new Error(
      `Carrossel bloqueado por requisito objetivo após autorreparo: ${
        (audit?.hardIssues || audit?.issues || ["erro editorial"])
          .join(" | ")
      }`
    );
  }

  // Se a única pendência for opinião semântica da auditoria,
  // renderizamos para revisão humana em vez de perder o teste visual.
  const semanticAdvisory =
    !audit.semanticPass
      ? (audit.semanticIssues || [])
      : [];

  const slides = packageResult.slides;
  const caption = packageResult.caption;
  const hashtags = carouselHashtags(command);
  const finalText = `${caption}\n\n${hashtags.join(" ")}`;

  const id = crypto.randomUUID();
  const imageUrls = [];
  const imageKeys = [];
  const renderErrors = [];
  const compositor = "r19-browser-photo-editorial-png";

  // R19: duas passagens. Cards já concluídos não são refeitos.
  // Em caso de 429, os cards pendentes aguardam cooldown e entram numa segunda passagem.
  let pendingSlides = [...slides];
  const renderedByNumber = new Map();

  for (let pass = 0; pass < CAROUSEL_RENDER_PASSES && pendingSlides.length; pass++) {
    if (pass > 0) {
      await sleep(CAROUSEL_FAILED_PASS_COOLDOWN_MS);
    }

    const nextPending = [];

    for (let index = 0; index < pendingSlides.length; index++) {
      const slide = pendingSlides[index];

      try {
        if (index > 0 || pass > 0) {
          await sleep(CAROUSEL_SLIDE_SPACING_MS);
        }

        const rendered = await renderCarouselSlideExact(
          env,
          command,
          slide,
          id,
          origin
        );

        renderedByNumber.set(slide.number, rendered);
      } catch (error) {
        nextPending.push(slide);

        if (pass === CAROUSEL_RENDER_PASSES - 1) {
          renderErrors.push(
            `Slide ${slide.number}: ${error?.message || "erro"}`
          );
        }
      }
    }

    pendingSlides = nextPending;
  }

  for (const slide of slides) {
    const rendered = renderedByNumber.get(slide.number);
    if (!rendered) continue;
    imageUrls.push(rendered.url);
    imageKeys.push(rendered.key);
  }

  const ready =
    imageUrls.length === slides.length &&
    renderErrors.length === 0;

  const music =
    await resolveMusicForDraft(
      env,
      command,
      "carousel"
    );

  const draft = {
    id,
    version: VERSION,
    type: "carousel",
    commandId: command.id,
    contentId: command.contentId || id,
    experimentId: command.experimentId || command.experiment || null,
    variant: command.variant || null,
    commercialIntent: command.commercialIntent || null,
    commercialOffer: command.commercialOffer === true,
    editorialMode: command.editorialMode || "standard",
    copyLock: command.copyLock || { enabled: false },
    exactCopy: command.copyLock || { enabled: false },
    copyLockValidation: validateCarouselCopyLock(command, packageResult),
    semanticValidationRequired: command.copyLock?.enabled === true,
    semanticValidationAvailable: true,
    semanticValidation: {
      pass: audit?.hardPass === true && validateCarouselCopyLock(command, packageResult).pass === true,
      source: "worker_carousel_deterministic_qa",
      hardPass: audit?.hardPass === true,
      semanticPass: audit?.semanticPass === true
    },
    legacyContentLeakDetected: false,
    commerce: command.commerce || normalizeUGICommerce({}),
    topic: cleanTopic(
      packageResult.topic || command.topic
    ),
    area: command.topic,
    angle: command.objective,
    slides,
    text: finalText,
    captionWords: wordCount(caption),
    hashtags,
    imageUrls,
    imageKeys,
    imageUrl: imageUrls[0] || null,
    imageKey: imageKeys[0] || null,
    status: "draft",
    renderStatus: ready ? "ready" : "partial",
    qualityStatus:
      ready && audit.semanticPass
        ? "ready_for_review"
        : "needs_review",
    qualityIssues: [
      ...semanticAdvisory,
      ...renderErrors
    ],
    carouselAudit: audit,
    renderer: compositor,
    renderErrors,
    generationFallback: fallbackUsed,
    semanticRepairExhausted,
    generationError:
      fallbackUsed
        ? lastError?.message ||
          "fallback editorial estrutural utilizado"
        : null,
    music,
    source: "command-hub",
    experiment: command.experiment,
    createdAt: new Date().toISOString()
  };

  await saveLocalDraft(env, draft);

  await saveHistory(env, {
    briefId: `command-${command.id}`,
    topic: draft.topic,
    area: command.topic,
    angle: command.objective,
    type: "carousel",
    createdAt: draft.createdAt
  });

  return draft;
}

async function normalizeCarouselPackage(env, command, value) {
  const fallback = deterministicCarouselFallback(command);
  const requiredCTA = resolveRequiredCarouselCTA(command);

  let rawSlides = Array.isArray(value?.slides)
    ? value.slides.slice(0, command.slides)
    : [];

  while (rawSlides.length < command.slides) {
    const source =
      fallback.slides[rawSlides.length] ||
      fallback.slides[fallback.slides.length - 1];

    rawSlides.push(source);
  }

  let slides = rawSlides.map((slide, index) => ({
    number: index + 1,
    headline: sanitizeSlideText(
      slide?.headline ||
      editorialHeadlineFor(index + 1, command.slides, command)
    ),
    body: sanitizeSlideText(slide?.body || "")
  }));

  slides = slides.map((slide, index) => ({
    ...slide,
    headline: isGenericCarouselHeadline(slide.headline)
      ? editorialHeadlineFor(index + 1, command.slides, command)
      : slide.headline,
    body: enforceSlideBodyDensity(
      slide.body,
      index + 1,
      command.slides
    )
  }));

  // R12: comando simples não precisa trazer uma capa pronta.
  // Se houver uma capa explícita no briefing, ela é preservada.
  // Caso contrário, a própria Lola cria uma headline curta.
  const coverHeadline = await ensureCarouselCoverHeadline(
    env,
    command,
    slides[0]?.headline
  );

  slides[0].headline = sanitizeSlideText(coverHeadline);

  if (!slides[0].body) {
    slides[0].body = sanitizeSlideText(
      command.keyMessage ||
      command.objective ||
      fallback.slides[0].body
    );
  }

  slides[0].body = enforceSlideBodyDensity(
    slides[0].body,
    1,
    command.slides
  );

  // Cards internos nunca podem cair em títulos estruturais.
  for (let i = 1; i < slides.length - 1; i++) {
    if (
      isGenericCarouselHeadline(slides[i].headline) ||
      wordCount(slides[i].headline) > 9
    ) {
      slides[i].headline =
        editorialHeadlineFor(i + 1, command.slides, command);
    }

    slides[i].body = enforceSlideBodyDensity(
      slides[i].body,
      i + 1,
      command.slides
    );
  }

  // Último card: fechamento real, nunca "Parte 7".
  const lastIndex = command.slides - 1;

  slides[lastIndex].headline =
    sanitizeSlideText(resolveClosingHeadline(command));

  slides[lastIndex].body =
    enforceSlideBodyDensity(
      sanitizeSlideText(requiredCTA),
      command.slides,
      command.slides
    );

  const caption = await ensureCarouselCaption(
    env,
    command,
    cleanCaption(value?.caption || "")
  );

  return {
    topic: cleanTopic(value?.topic || command.topic),
    caption,
    slides
  };
}

async function ensureCarouselCoverHeadline(
  env,
  command,
  existingHeadline
) {
  const explicit = extractExplicitCarouselCover(command);

  if (explicit) {
    return explicit;
  }

  const existing = sanitizeSlideText(existingHeadline || "");

  if (
    existing &&
    !isGenericCarouselHeadline(existing) &&
    wordCount(existing) <= CAROUSEL_COVER_MAX_WORDS &&
    !looksLikeBriefDump(existing)
  ) {
    return existing;
  }

  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const result = await env.AI.run(
        TXT,
        {
          messages: [
            {
              role: "system",
              content: [
                "Você cria headlines de capa para carrosséis da Uma Gestão Inteligente.",
                "Escreva uma única headline curta e forte em português brasileiro.",
                `Use no máximo ${CAROUSEL_COVER_MAX_WORDS} palavras.`,
                "Não use dois-pontos.",
                "Não use aspas.",
                "Não use Tema, Parte, Slide, Card ou Insight.",
                "Não prometa resultados absolutos.",
                "A headline deve traduzir o problema gerencial do briefing em linguagem natural.",
                "Retorne somente a headline."
              ].join(" ")
            },
            {
              role: "user",
              content: [
                `Tema: ${command.topic || ""}`,
                `Objetivo: ${command.objective || ""}`,
                command.keyMessage
                  ? `Mensagem: ${command.keyMessage}`
                  : "",
                command.instructions
                  ? `Contexto: ${command.instructions}`
                  : ""
              ].filter(Boolean).join("\n")
            }
          ],
          max_tokens: 80,
          temperature: 0.28,}
      );

      const headline =
        sanitizeSlideText(result?.response || "");

      if (
        headline &&
        !isGenericCarouselHeadline(headline) &&
        wordCount(headline) <= CAROUSEL_COVER_MAX_WORDS &&
        !looksLikeBriefDump(headline)
      ) {
        return headline;
      }
    } catch {}
  }

  return deterministicCoverHeadline(command);
}

function extractExplicitCarouselCover(command) {
  const source = [
    command.hook,
    command.keyMessage,
    command.instructions
  ].filter(Boolean).join("\n");

  const patterns = [
    /capa[^“”"\n]{0,80}[“"]([^”"\n]{4,120})[”"]/i,
    /(?:^|\n)\s*1[.)-]?\s*(?:\*\*)?capa(?:\*\*)?\s*:\s*[“"]?([^\n”"]{4,120})/i,
    /capa\s*:\s*[“"]?([^\n”"]{4,120})/i
  ];

  for (const rx of patterns) {
    const match = source.match(rx);

    if (match?.[1]) {
      const value = stripTrailingBriefText(match[1]);

      if (
        value &&
        wordCount(value) <= 14 &&
        !isGenericCarouselHeadline(value)
      ) {
        return value;
      }
    }
  }

  return "";
}

function deterministicCoverHeadline(command) {
  const text = normalizeText([
    command.topic,
    command.objective,
    command.keyMessage,
    command.instructions
  ].join(" "));

  if (/centraliz|deleg|autonom|gargal/.test(text)) {
    return "Sua equipe decide sem depender de você?";
  }

  if (/decis|prioriz/.test(text)) {
    return "Toda decisão precisa chegar até você?";
  }

  if (/process|retrabal|padron/.test(text)) {
    return "Onde o retrabalho começa na sua operação?";
  }

  if (/reun|comunic|alinh/.test(text)) {
    return "Sua reunião resolve ou só ocupa a agenda?";
  }

  if (/tempo|produt|foco/.test(text)) {
    return "Quem está protegendo seu tempo estratégico?";
  }

  if (/lider|equipe/.test(text)) {
    return "Sua liderança cria autonomia ou dependência?";
  }

  return "O que está travando sua gestão hoje?";
}

function looksLikeBriefDump(value) {
  const text = normalizeText(value || "");

  return (
    /objetivo|direcao|regras|estrutura|area|angulo/.test(text) ||
    text.split(" ").length > 14
  );
}

function enforceSlideBodyDensity(value, number, total) {
  const text = sanitizeSlideText(value || "");

  const maxWords =
    number === 1
      ? 18
      : number === total
        ? 28
        : CAROUSEL_BODY_MAX_WORDS;

  const words = text.split(/\s+/).filter(Boolean);

  if (words.length <= maxWords) {
    return text;
  }

  let shortened =
    words.slice(0, maxWords).join(" ");

  shortened = shortened
    .replace(/[,:;–—-]+\s*$/, "")
    .trim();

  if (!/[.!?]$/.test(shortened)) {
    shortened += ".";
  }

  return shortened;
}

function hasExplicitCarouselCover(command) {
  const instructions = String(command.instructions || "");
  const keyMessage = String(command.keyMessage || "");
  const source = `${instructions}\n${keyMessage}`;

  const explicitPattern =
    /(?:capa|headline\s+(?:da\s+)?capa|primeiro\s+card|card\s+1)[^“”"\n]{0,100}[“"]([^”"\n]{4,160})[”"]|(?:^|\n)\s*1[.)-]?\s*(?:\*\*)?capa(?:\*\*)?\s*:/i;

  if (explicitPattern.test(source)) return true;

  const hook = sanitizeSlideText(command.hook || "");
  return Boolean(hook && !isGenericCarouselHeadline(hook));
}

function resolveRequiredCover(command) {
  // Usa primeiro o mesmo extrator empregado por ensureCarouselCoverHeadline,
  // eliminando divergência entre "capa exigida" e "capa aplicada".
  const explicit = extractExplicitCarouselCover(command);
  if (explicit) return explicit;

  const instructions = String(command.instructions || "");
  const keyMessage = String(command.keyMessage || "");
  const source = `${instructions}\n${keyMessage}`;

  const patterns = [
    /capa[^“”"\n]{0,80}[“"]([^”"\n]{4,120})[”"]/i,
    /(?:^|\n)\s*1[.)-]?\s*(?:\*\*)?capa(?:\*\*)?\s*:\s*[“"]?([^\n”"]{4,120})/i,
    /capa\s*:\s*[“"]?([^\n”"]{4,120})/i
  ];

  for (const rx of patterns) {
    const match = source.match(rx);
    if (match?.[1]) return stripTrailingBriefText(match[1]);
  }

  const hook = sanitizeSlideText(command.hook || "");
  if (hook && !isGenericCarouselHeadline(hook)) {
    return stripTrailingBriefText(hook);
  }

  return stripTrailingBriefText(
    cleanTopic(command.topic || "Uma gestão que não depende de uma pessoa")
  );
}

function stripTrailingBriefText(value) {
  return String(value || "")
    .replace(/\*\*/g, "")
    .replace(/\s+(?:objetivo|direção|regras|estrutura)\s*:.*$/i, "")
    .trim();
}

function isGenericCTA(value) {
  const t = normalizeText(value || "");
  return !t || [
    "salvar e compartilhar",
    "salve e compartilhe",
    "salvar",
    "compartilhar",
    "saiba mais",
    "comente abaixo"
  ].includes(t);
}

function resolveRequiredCarouselCTA(command) {
  const cta = sanitizeSlideText(command.cta || "");
  if (cta && !isGenericCTA(cta)) return cta;

  const text = normalizeText([
    command.topic,
    command.objective,
    command.keyMessage,
    command.instructions
  ].join(" "));

  if (/centraliz|deleg|autonom|gargal|decis/.test(text)) {
    return "Revise as decisões que chegaram até você na última semana: quais a sua equipe já poderia decidir sem pedir autorização?";
  }
  if (/reun|comunic|alinh/.test(text)) {
    return "Qual ajuste simples você pode fazer na próxima reunião para aumentar clareza e reduzir dependência?";
  }
  if (/process|retrabal|padron/.test(text)) {
    return "Qual etapa do seu processo hoje mais precisa de um responsável e de um critério claro de conclusão?";
  }
  return "Qual decisão de gestão você pode transformar em um critério mais claro ainda esta semana?";
}

function resolveClosingHeadline(command) {
  const text = normalizeText([
    command.topic,
    command.objective,
    command.instructions
  ].join(" "));

  if (/centraliz|deleg|autonom|gargal|decis/.test(text)) {
    return "O que ainda precisa passar por você?";
  }
  if (/process|retrabal|padron/.test(text)) {
    return "Qual etapa precisa ficar mais clara?";
  }
  if (/reun|comunic|alinh/.test(text)) {
    return "O que você mudará na próxima reunião?";
  }
  return "Leve isso para a prática";
}

async function ensureCarouselCaption(env, command, currentCaption) {
  let caption = cleanCaption(currentCaption);
  if (isValidCarouselCaption(caption)) return caption;

  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const result = await env.AI.run(
        TXT,
        {
          messages: [
            {
              role: "system",
              content: [
                "Você é editora-chefe da Uma Gestão Inteligente.",
                "Escreva somente a legenda final em português brasileiro.",
                `A legenda deve ter entre ${CAROUSEL_MIN_WORDS} e ${CAROUSEL_MAX_WORDS} palavras, sem contar hashtags.`,
                "Use de 3 a 5 parágrafos curtos.",
                "A legenda deve complementar o carrossel, e não repetir slide por slide.",
                "Comece com um problema observável de gestão.",
                "Explique por que isso acontece e ensine uma aplicação prática.",
                "Finalize com uma pergunta útil ou CTA discreto.",
                "Não use hashtags dentro da legenda.",
                "Não invente valores financeiros, percentuais, estatísticas ou políticas universais.",
                "Evite clichês, promessas absolutas e linguagem genérica de IA."
              ].join(" ")
            },
            {
              role: "user",
              content: [
                `Tema: ${command.topic}`,
                `Objetivo: ${command.objective}`,
                command.keyMessage ? `Mensagem central: ${command.keyMessage}` : "",
                command.instructions ? `Instruções do briefing: ${command.instructions}` : "",
                `CTA desejado: ${resolveRequiredCarouselCTA(command)}`,
                caption ? `Legenda atual a corrigir: ${caption}` : "Crie a legenda do zero.",
                "Retorne somente a legenda final."
              ].filter(Boolean).join("\n")
            }
          ],
          max_tokens: 900,
          temperature: 0.22,
          repetition_penalty: 1.12,
          frequency_penalty: 0.35,}
      );

      caption = cleanCaption(result?.response || "");
      if (isValidCarouselCaption(caption)) return caption;
    } catch {}
  }

  return buildCarouselFallbackCaption(command);
}

function isValidCarouselCaption(caption) {
  const count = wordCount(caption);
  if (count < CAROUSEL_MIN_WORDS || count > CAROUSEL_MAX_WORDS) return false;
  if (/#\w+/.test(caption)) return false;
  if (MONEY_OR_PERCENT_PATTERN.test(caption)) return false;
  if (hasExactDuplicateParagraph(caption)) return false;
  return paragraphList(caption).length >= 3;
}

function buildCarouselFallbackCaption(command) {
  const topic = String(command.topic || "gestão").trim();
  const objective = String(
    command.objective || "reduzir dependência do gestor e melhorar a clareza das decisões"
  ).trim();
  const cta = resolveRequiredCarouselCTA(command);

  let caption = [
    `Quando um tema como ${topic} aparece na rotina, o problema raramente está apenas na quantidade de trabalho. Muitas vezes existe uma concentração de decisões, critérios pouco explícitos ou responsabilidades que ainda não ficaram claras para a equipe.`,
    `O efeito é previsível: questões simples sobem para o gestor, as pessoas esperam autorização e o trabalho perde velocidade. Além de consumir atenção, esse padrão reduz a oportunidade de a equipe desenvolver julgamento e assumir responsabilidade sobre decisões compatíveis com seu papel.`,
    `Uma forma prática de avançar em ${objective} é separar três situações: o que a equipe pode decidir sozinha, o que pode decidir e comunicar depois e o que realmente precisa de aprovação prévia por envolver risco ou impacto relevante. O critério deve ser compreensível antes de a dúvida aparecer.`,
    `Comece observando as decisões que chegaram até você nos últimos dias e transforme os casos repetitivos em acordos claros. Autonomia não significa ausência de controle; significa colocar o controle no critério certo, em vez de concentrá-lo em uma pessoa.`,
    cta
  ].join("\n\n");

  const words = caption.split(/\s+/).filter(Boolean);
  if (words.length > CAROUSEL_MAX_WORDS) {
    caption = words.slice(0, CAROUSEL_MAX_WORDS - 12).join(" ") + `\n\n${cta}`;
  }

  return cleanCaption(caption);
}

function carouselHashtags(command) {
  const text = normalizeText([
    command.topic,
    command.objective,
    command.keyMessage
  ].join(" "));

  let tags;
  if (/deleg|autonom|centraliz|gargal/.test(text)) {
    tags = ["#Delegacao", "#AutonomiaNaGestao"];
  } else if (/decis/.test(text)) {
    tags = ["#TomadaDeDecisao", "#DecisaoGerencial"];
  } else if (/process|retrabal|padron/.test(text)) {
    tags = ["#GestaoDeProcessos", "#Padronizacao"];
  } else if (/reun|comunic|alinh/.test(text)) {
    tags = ["#ComunicacaoNaGestao", "#ReunioesProdutivas"];
  } else if (/lider|equipe/.test(text)) {
    tags = ["#Lideranca", "#GestaoDeEquipe"];
  } else {
    tags = ["#Gestao", "#Lideranca"];
  }

  return [...tags, BRAND_HASHTAG];
}

function validateCarouselPackageProgrammatically(command, pkg) {
  const issues = [];
  const slides = Array.isArray(pkg?.slides) ? pkg.slides : [];
  const requiredCover = resolveRequiredCover(command);
  const requiredCTA = resolveRequiredCarouselCTA(command);

  if (slides.length !== command.slides) {
    issues.push(`quantidade de slides: ${slides.length}/${command.slides}`);
  }

  if (!slides[0]?.headline) {
    issues.push("capa sem headline");
  } else if (
    hasExplicitCarouselCover(command) &&
    normalizeText(slides[0].headline) !== normalizeText(requiredCover)
  ) {
    issues.push("capa explícita não foi preservada");
  }

  if (slides.some(slide => isGenericCarouselHeadline(slide?.headline))) {
    issues.push("título genérico Parte/Slide/Card/Insight");
  }

  for (let i = 0; i < slides.length; i++) {
    const slide = slides[i];
    const bodyWords = wordCount(slide?.body || "");
    const headlineWords = wordCount(slide?.headline || "");

    if (!slide?.body) issues.push(`slide ${i + 1} sem conteúdo`);

    if (i === 0) {
      if (headlineWords > CAROUSEL_COVER_MAX_WORDS) issues.push("capa longa demais");
      if (bodyWords > 18) issues.push("capa com texto demais");
    } else if (i === slides.length - 1) {
      if (bodyWords > 34) issues.push("CTA final denso demais");
    } else if (bodyWords > CAROUSEL_BODY_MAX_WORDS) {
      issues.push(`slide ${i + 1} denso demais`);
    }

    if (MONEY_OR_PERCENT_PATTERN.test(`${slide?.headline || ""} ${slide?.body || ""}`)) {
      issues.push(`slide ${i + 1} contém valor/percentual não permitido`);
    }
  }

  const captionWords = wordCount(pkg?.caption || "");
  if (captionWords < CAROUSEL_MIN_WORDS || captionWords > CAROUSEL_MAX_WORDS) {
    issues.push(`legenda com ${captionWords} palavras; obrigatório ${CAROUSEL_MIN_WORDS}-${CAROUSEL_MAX_WORDS}`);
  }
  if (/#\w+/.test(pkg?.caption || "")) {
    issues.push("hashtags dentro da legenda antes do bloco final");
  }
  if (MONEY_OR_PERCENT_PATTERN.test(pkg?.caption || "")) {
    issues.push("legenda contém valor financeiro ou percentual não solicitado");
  }

  const lastBody = slides[slides.length - 1]?.body || "";
  if (requiredCTA && normalizeText(lastBody) !== normalizeText(requiredCTA)) {
    issues.push("fechamento não preservou o CTA do briefing");
  }

  return [...new Set(issues)];
}

async function auditCarouselPackage(env, command, pkg, options = {}) {
  const hardIssues = validateCarouselPackageProgrammatically(command, pkg);
  const semanticIssues = [];
  let semantic = {
    pass: true,
    reason: "controles determinísticos aprovados"
  };

  if (!hardIssues.length && !options.skipAI) {
    try {
      const result = await aiJSON(
        env,
        [
          {
            role: "system",
            content: [
              "Você é auditora editorial da Uma Gestão Inteligente.",
              "Seu trabalho é detectar DESVIO REAL de briefing, e não punir paráfrases válidas.",
              "A sequência deve avançar logicamente e cada card deve ter função distinta.",
              "Se o briefing NÃO trouxer uma capa literal ou gancho explícito, NÃO exija que a headline seja igual ao tema.",
              "Nessa situação, aprove a capa quando ela representar claramente tema + objetivo de forma interessante.",
              "Se houver capa/gancho explícito, aí sim cobre preservação literal.",
              "O último card deve fechar coerentemente com a ação/pergunta definida.",
              "A legenda deve complementar o carrossel e ensinar aplicação prática.",
              "Reprove apenas por desvio relevante, contradição, clichê vazio, regra universal inventada ou conteúdo que não entrega o objetivo.",
              "Não reescreva nada."
            ].join(" ")
          },
          {
            role: "user",
            content: JSON.stringify({
              topic: command.topic,
              objective: command.objective,
              explicitCover: hasExplicitCarouselCover(command),
              requiredCover: hasExplicitCarouselCover(command)
                ? resolveRequiredCover(command)
                : null,
              hook: command.hook,
              keyMessage: command.keyMessage,
              instructions: command.instructions,
              cta: command.cta,
              package: pkg
            })
          }
        ],
        randomSeed(),
        0.03,
        carouselAuditSchema()
      );

      semantic = result || semantic;

      if (!semantic.pass) {
        semanticIssues.push(
          `semântica: ${semantic.reason || "briefing precisa de ajuste"}`
        );
      }
    } catch (error) {
      semantic = {
        pass: true,
        reason:
          `auditoria semântica indisponível; controles determinísticos aprovados: ${error?.message || error}`
      };
    }
  }

  const hardPass = hardIssues.length === 0;
  const semanticPass = semanticIssues.length === 0;

  return {
    pass: hardPass && semanticPass,
    hardPass,
    semanticPass,
    issues: [...new Set([...hardIssues, ...semanticIssues])],
    hardIssues: [...new Set(hardIssues)],
    semanticIssues: [...new Set(semanticIssues)],
    semantic
  };
}

function carouselAuditSchema() {
  return {
    type: "object",
    properties: {
      pass: { type: "boolean" },
      reason: { type: "string" }
    },
    required: ["pass", "reason"],
    additionalProperties: false
  };
}

async function repairCarouselPackage(env, command, pkg, audit, attempt) {
  const result = await aiJSON(
    env,
    [
      {
        role: "system",
        content: [
          "Você é editora-chefe da Uma Gestão Inteligente.",
          "Reescreva o pacote somente para corrigir os problemas apontados pela auditoria.",
          `Mantenha exatamente ${command.slides} slides.`,
          `A legenda deve ter obrigatoriamente ${CAROUSEL_MIN_WORDS}-${CAROUSEL_MAX_WORDS} palavras, sem hashtags.`,
          "Não use títulos como Parte, Slide, Card ou Insight.",
          hasExplicitCarouselCover(command)
            ? "Preserve literalmente a capa/gancho explícito do briefing."
            : "Crie uma capa curta e forte que represente tema + objetivo; não copie o tema mecanicamente.",
          "Preserve o fechamento/CTA exigido.",
          "Cada card deve ter uma função diferente e avançar a narrativa.",
          "Não invente valores financeiros, percentuais, estatísticas ou regras universais.",
          "Use português brasileiro natural, consultivo e específico.",
          "Retorne somente JSON válido."
        ].join(" ")
      },
      {
        role: "user",
        content: JSON.stringify({
          requiredCover: resolveRequiredCover(command),
          requiredCTA: resolveRequiredCarouselCTA(command),
          topic: command.topic,
          objective: command.objective,
          keyMessage: command.keyMessage,
          instructions: command.instructions,
          problems: audit.issues,
          current: pkg
        })
      }
    ],
    randomSeed() + attempt,
    0.12,
    carouselSchema()
  );

  return result || pkg;
}

async function aiCarouselJSON(
  env,
  command,
  attempt = 0
) {
  const seed = randomSeed() + attempt;

  return aiJSON(
    env,
    [
      {
        role: "system",
        content: [
          "Você é estrategista editorial da Uma Gestão Inteligente.",
          "Crie um carrossel de Instagram em português brasileiro correto.",
          "Público: gestores, líderes e empreendedores.",
          "Conteúdo prático, específico, útil e compartilhável.",
          "Voz de consultoria madura: direta, humana e sem frases de efeito vazias.",
          "Evite motivação genérica e clichês de IA.",
          "Não invente estatísticas, valores financeiros, percentuais ou regras universais.",
          "Cada slide deve acrescentar uma informação nova e fazer a narrativa avançar.",
          "O primeiro slide é a capa: headline de 3 a 8 palavras e body de no máximo 18 palavras.",
          "Slides intermediários: headline de 2 a 7 palavras e body preferencialmente entre 18 e 40 palavras.",
          "O último slide precisa concluir com uma ação clara ou pergunta curta.",
          "Evite repetir a mesma ideia com palavras diferentes.",
          "Use ortografia portuguesa correta.",
          "Jamais invente palavras.",
          "Não use erros deliberados de escrita.",
          "Não inclua hashtags na legenda.",
          `A legenda deve ter obrigatoriamente entre ${CAROUSEL_MIN_WORDS} e ${CAROUSEL_MAX_WORDS} palavras e complementar os cards, não apenas repetir o conteúdo.`,
          "Se o briefing trouxer uma capa/gancho explícito, preserve esse texto no primeiro headline.",
          "Se o briefing trouxer um CTA/pergunta final explícito, preserve-o no último card."
        ].join(" ")
      },
      {
        role: "user",
        content: [
          `Tema: ${command.topic}`,
          `Objetivo: ${command.objective}`,
          `Público: ${command.audience}`,
          `Quantidade EXATA de slides: ${command.slides}`,
          command.hook ? `Gancho: ${command.hook}` : "",
          command.keyMessage
            ? `Mensagem central: ${command.keyMessage}`
            : "",
          command.instructions
            ? `Instruções: ${command.instructions}`
            : "",
          `CTA: ${command.cta}`,
          "Retorne JSON contendo topic, caption e slides.",
          "Cada slide deve conter headline e body.",
          `O array slides deve ter exatamente ${command.slides} itens.`
        ]
          .filter(Boolean)
          .join("\n")
      }
    ],
    0.28,
    carouselSchema()
  );
}

async function repairCarouselText(
  env,
  command,
  carousel
) {
  try {
    const result = await aiJSON(
      env,
      [
        {
          role: "system",
          content: [
            "Você é revisora editorial brasileira.",
            "Corrija exclusivamente ortografia, gramática, clareza, concisão e naturalidade.",
            "Elimine palavras inexistentes, letras trocadas e capitalização errada.",
            "Mantenha a quantidade exata de slides.",
            "Mantenha a ordem lógica.",
            "Nunca use títulos genéricos como Parte 1, Parte 7, Slide 1, Card 2 ou Insight 03.",
            "A capa deve ter uma promessa, tensão ou pergunta específica que funcione sozinha no feed.",
            "O último slide deve ter um título de ação ou reflexão, nunca Parte N.",
            "Cada slide deve comunicar uma ideia principal e evitar blocos densos.",
            "Não acrescente estatísticas.",
            "Não use hashtags.",
            `A legenda precisa ter ${CAROUSEL_MIN_WORDS}-${CAROUSEL_MAX_WORDS} palavras.`,
            `O primeiro headline deve ser exatamente: ${resolveRequiredCover(command)}`,
            `O último body deve ser exatamente: ${resolveRequiredCarouselCTA(command)}`,
            "Retorne somente JSON."
          ].join(" ")
        },
        {
          role: "user",
          content: JSON.stringify({
            topic: carousel.topic,
            caption: carousel.caption,
            slides: carousel.slides,
            requiredSlides: command.slides
          })
        }
      ],
      randomSeed(),
      0.08,
      carouselSchema()
    );

    if (
      result &&
      Array.isArray(result.slides) &&
      result.slides.length === command.slides
    ) {
      return result;
    }
  } catch {}

  return carousel;
}

function carouselSchema() {
  return {
    type: "object",

    properties: {
      topic: {
        type: "string"
      },

      caption: {
        type: "string"
      },

      slides: {
        type: "array",

        items: {
          type: "object",

          properties: {
            headline: {
              type: "string"
            },

            body: {
              type: "string"
            }
          },

          required: ["headline", "body"],

          additionalProperties: false
        }
      }
    },

    required: ["topic", "caption", "slides"],

    additionalProperties: false
  };
}

function isGenericCarouselHeadline(value) {
  const t = normalizeText(value || "");
  return /^(parte|slide|card|insight)\s*\d*$/i.test(t) ||
    /^(parte|slide|card|insight)\s+\d+/i.test(t);
}

function editorialHeadlineFor(number, total, command) {
  if (number === 1) {
    return cleanTopic(command.topic || "Uma decisão que muda a gestão");
  }
  if (number === total) return "Leve isso para a prática";

  const map = [
    "O sinal que merece atenção",
    "O impacto na rotina",
    "O que está por trás disso",
    "Uma mudança simples",
    "Defina quem decide o quê",
    "Transforme clareza em autonomia",
    "Acompanhe sem centralizar",
    "Faça o acordo funcionar"
  ];
  return map[Math.max(0, Math.min(map.length - 1, number - 2))];
}

function limitCarouselBody(value, number, total) {
  let text = sanitizeSlideText(value);
  const max = number === 1 ? 150 : number === total ? 190 : 230;
  if (text.length <= max) return text;
  const cut = text.slice(0, max);
  const end = Math.max(cut.lastIndexOf(". "), cut.lastIndexOf("; "), cut.lastIndexOf(", "));
  return (end > 90 ? cut.slice(0, end + 1) : cut.replace(/\s+\S*$/, "").trim() + "...").trim();
}

// ------------------------------------------------------------
// RENDER DO CARROSSEL — PNG DETERMINÍSTICO
// ------------------------------------------------------------
//
// Motivo da mudança no R8:
// O erro Cloudflare Images 9412 significa que uma transformação recebeu
// conteúdo que não foi reconhecido como imagem válida. O R7 usava um SVG
// dinâmico como camada de texto dentro do pipeline do Images binding.
// Para eliminar essa dependência e garantir texto 100% legível, o R8
// rasteriza o carrossel diretamente em PNG dentro do Worker.
//
// O binding IMAGES continua conectado e pode ser usado futuramente para
// otimizações, overlays raster e outras transformações, mas NÃO é mais
// necessário para escrever texto nos cards.
// ------------------------------------------------------------

async function renderCarouselSlideExact(
  env,
  command,
  slide,
  draftId,
  origin
) {
  if (!env.BROWSER) {
    throw new Error(
      "R13 exige o binding BROWSER (Cloudflare Browser Run) para renderizar o carrossel com tipografia editorial."
    );
  }

  const background =
    await generateCarouselVisualBackground(
      env,
      command,
      slide,
      0
    );

  const html =
    buildCarouselBrowserHtml(
      command,
      slide,
      background.base64
    );

  let screenshotResponse = null;
  let browserLastError = null;

  for (let browserAttempt = 0; browserAttempt < BROWSER_RENDER_ATTEMPTS; browserAttempt++) {
    try {
      screenshotResponse =
        await env.BROWSER.quickAction(
          "screenshot",
          {
            html,
            selector: "#card",
            viewport: {
              width: 1080,
              height: 1350,
              deviceScaleFactor: 1
            },
            screenshotOptions: {
              omitBackground: false
            }
          }
        );

      if (screenshotResponse?.ok) {
        break;
      }

      const status = Number(screenshotResponse?.status || 0);

      if (status !== 429) {
        throw new Error(
          `Browser Run retornou HTTP ${status || "desconhecido"}`
        );
      }

      const retryAfterHeader =
        screenshotResponse?.headers?.get?.("retry-after");
      const retryAfterSeconds =
        Number(retryAfterHeader || 0);

      const jitterMs = Math.floor(Math.random() * 1200);
      const delayMs =
        retryAfterSeconds > 0
          ? Math.min(retryAfterSeconds * 1000 + jitterMs, BROWSER_MAX_BACKOFF_MS)
          : Math.min(
              BROWSER_BASE_BACKOFF_MS * (2 ** browserAttempt) + jitterMs,
              BROWSER_MAX_BACKOFF_MS
            );

      browserLastError =
        `HTTP 429; nova tentativa em ${delayMs}ms`;

      await sleep(delayMs);
    } catch (error) {
      browserLastError =
        error?.message || String(error);

      if (browserAttempt >= BROWSER_RENDER_ATTEMPTS - 1) break;

      await sleep(
        Math.min(BROWSER_BASE_BACKOFF_MS * (2 ** browserAttempt), BROWSER_MAX_BACKOFF_MS)
      );
    }
  }

  if (!screenshotResponse?.ok) {
    throw new Error(
      `Browser Run falhou no slide ${slide.number} após backoff: ${
        browserLastError ||
        `HTTP ${screenshotResponse?.status || "desconhecido"}`
      }`
    );
  }

  const bytes =
    new Uint8Array(
      await screenshotResponse.arrayBuffer()
    );

  if (!bytes || bytes.length < 5000) {
    throw new Error(
      `Browser Run não produziu PNG válido no slide ${slide.number}.`
    );
  }

  const key =
    `${CAROUSEL_PREFIX}${draftId}-slide-${slide.number}.png`;

  await env.MEDIA.put(
    key,
    bytes,
    {
      httpMetadata: {
        contentType: "image/png",
        cacheControl:
          "public,max-age=31536000,immutable"
      }
    }
  );

  const stored =
    await env.MEDIA.head(key);

  if (!stored) {
    throw new Error(
      `Slide ${slide.number} não foi confirmado no R2.`
    );
  }

  return {
    key,
    url: `${origin}/media/${key}`,
    renderer: "r19-browser-photo-editorial-png"
  };
}

async function generateCarouselVisualBackground(
  env,
  command,
  slide,
  attempt = 0
) {
  if (!env.AI) {
    throw new Error("Binding AI ausente para imagem do carrossel");
  }

  const prompt =
    buildCarouselVisualPrompt(
      command,
      slide
    );

  const result =
    await env.AI.run(
      IMG,
      {
        prompt,
        steps: CAROUSEL_VISUAL_STEPS,}
    );

  if (!result?.image) {
    throw new Error(
      `Imagem de fundo não gerada para o slide ${slide.number}`
    );
  }

  return {
    base64: result.image,
    bytes: carouselBase64ToBytes(result.image)
  };
}

function buildCarouselBrowserHtml(
  command,
  slide,
  backgroundBase64
) {
  const isCover = slide.number === 1;
  const isLast = slide.number === command.slides;

  const headline =
    escapeHtml(
      sanitizeSlideText(slide.headline)
    );

  const body =
    escapeHtml(
      sanitizeSlideText(slide.body)
    );

  const photoData =
    `data:image/jpeg;base64,${backgroundBase64}`;

  const eyebrow =
    isCover
      ? "UMA GESTÃO INTELIGENTE"
      : editorialEyebrowForSlide(slide.number);

  // Três composições para evitar repetição visual:
  // capa editorial, painel inferior e painel lateral.
  const layout =
    isCover
      ? "cover"
      : isLast
        ? "closing"
        : (
            slide.number % 2 === 0
              ? "bottom"
              : "side"
          );

  return `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, initial-scale=1">
<style>
  *{box-sizing:border-box}
  html,body{
    margin:0;
    width:1080px;
    height:1350px;
    overflow:hidden;
    background:#06152a;
  }

  #card{
    position:relative;
    width:1080px;
    height:1350px;
    overflow:hidden;
    background:#07182d;
    font-family:Arial, Helvetica, "Open Sans", sans-serif;
    color:#fff;
  }

  .photo{
    position:absolute;
    inset:0;
    background-image:url("${photoData}");
    background-size:cover;
    background-position:center;
    transform:scale(1.01);
  }

  .scrim{
    position:absolute;
    inset:0;
    pointer-events:none;
  }

  .brand{
    position:absolute;
    z-index:5;
    top:72px;
    left:72px;
    display:inline-flex;
    align-items:center;
    min-height:42px;
    padding:0 18px;
    border-radius:999px;
    background:rgba(5,25,47,.78);
    border:1px solid rgba(119,204,255,.35);
    backdrop-filter:blur(10px);
    color:#bfe7ff;
    font-size:20px;
    line-height:1;
    font-weight:700;
    letter-spacing:.08em;
    text-transform:uppercase;
  }

  .copy{
    position:absolute;
    z-index:4;
  }

  h1{
    margin:0;
    font-size:64px;
    line-height:1.02;
    letter-spacing:-.035em;
    font-weight:800;
    text-wrap:balance;
  }

  p{
    margin:28px 0 0;
    font-size:31px;
    line-height:1.30;
    font-weight:400;
    color:#eef7fc;
    text-wrap:pretty;
  }

  .accent{
    width:92px;
    height:8px;
    border-radius:999px;
    background:#24aaff;
    margin-bottom:30px;
  }

  .footer{
    position:absolute;
    z-index:6;
    left:72px;
    right:72px;
    bottom:44px;
    padding-top:20px;
    border-top:1px solid rgba(184,225,249,.32);
    display:flex;
    justify-content:space-between;
    align-items:center;
    font-size:18px;
    letter-spacing:.035em;
    color:#d2e9f7;
    font-weight:600;
  }

  /* CAPA: fotografia forte + gradiente editorial. */
  #card.cover .scrim{
    background:
      linear-gradient(90deg,
        rgba(3,17,34,.97) 0%,
        rgba(3,17,34,.90) 45%,
        rgba(3,17,34,.35) 78%,
        rgba(3,17,34,.06) 100%),
      linear-gradient(0deg,
        rgba(3,17,34,.72) 0%,
        transparent 48%);
  }

  #card.cover .photo{
    background-position:center;
  }

  #card.cover .copy{
    left:72px;
    top:335px;
    width:665px;
  }

  #card.cover h1{
    font-size:72px;
  }

  #card.cover p{
    max-width:620px;
  }

  /* INTERNOS PARES: foto em cima, painel limpo embaixo. */
  #card.bottom .photo{
    height:725px;
  }

  #card.bottom .scrim{
    background:
      linear-gradient(0deg,
        #07182d 0%,
        #07182d 46%,
        rgba(7,24,45,.62) 58%,
        transparent 78%);
  }

  #card.bottom .copy{
    left:72px;
    right:72px;
    top:765px;
  }

  #card.bottom h1{
    font-size:58px;
  }

  #card.bottom p{
    max-width:900px;
  }

  /* INTERNOS ÍMPARES: foto full bleed + coluna escura lateral. */
  #card.side .scrim{
    background:
      linear-gradient(90deg,
        rgba(4,18,35,.96) 0%,
        rgba(4,18,35,.91) 55%,
        rgba(4,18,35,.30) 82%,
        rgba(4,18,35,.05) 100%);
  }

  #card.side .copy{
    left:72px;
    top:310px;
    width:610px;
  }

  #card.side h1{
    font-size:62px;
  }

  /* FECHAMENTO: foto ampla; sem botão genérico e sem
     "salve / aplique / compartilhe". */
  #card.closing .scrim{
    background:
      linear-gradient(0deg,
        rgba(3,17,34,.98) 0%,
        rgba(3,17,34,.88) 50%,
        rgba(3,17,34,.18) 83%,
        rgba(3,17,34,.03) 100%);
  }

  #card.closing .copy{
    left:72px;
    right:72px;
    bottom:190px;
  }

  #card.closing h1{
    font-size:64px;
    max-width:900px;
  }

  #card.closing p{
    max-width:880px;
  }

.platform-stack{
  display:grid;
  gap:14px;
  margin-top:14px;
}

.platform-card{
  background:#071a2f;
  border:1px solid #285071;
  border-radius:14px;
  padding:12px;
}

.platform-head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:8px;
  margin-bottom:10px;
}

.platform-name{
  font-weight:800;
  letter-spacing:.02em;
  color:#fff;
}

.platform-status{
  display:inline-block;
  border-radius:999px;
  padding:5px 9px;
  font-size:11px;
  font-weight:700;
}

.platform-status.pending_approval{
  background:#3b3015;
  color:#ffd27d;
}

.platform-status.approved{
  background:#103d31;
  color:#7ce6b9;
}

.platform-status.rejected{
  background:#4a1d27;
  color:#ff9bad;
}

.platform-meta{
  color:#8faac6;
  font-size:12px;
  margin:8px 0 10px;
}

.platform-actions{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:8px;
}

.platform-actions button{
  width:100%;
}

.approval-summary{
  margin-top:12px;
  padding:11px;
  border-radius:10px;
  background:#0a1e34;
  border:1px solid #284f73;
  color:#c7d9ea;
  font-size:12px;
  line-height:1.5;
}


.publication-box{
  margin-top:10px;
  padding:10px;
  border-radius:10px;
  background:#0b2138;
  border:1px solid #315a7b;
}

.publication-status{
  font-size:12px;
  color:#b8cde0;
  line-height:1.45;
  margin-bottom:8px;
}

.publish-actions{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:8px;
}

.publish-actions .queue{
  grid-column:1 / -1;
}

.purple{
  background:#6d4ad3;
}

.teal{
  background:#087f78;
}

</style>
</head>
<body>
  <main id="card" class="${layout}">
    <div class="photo"></div>
    <div class="scrim"></div>

    <div class="brand">${escapeHtml(eyebrow)}</div>

    <section class="copy">
      <div class="accent"></div>
      <h1>${headline}</h1>
      <p>${body}</p>
    </section>

    <footer class="footer">
      <span>UGI | UMA GESTÃO INTELIGENTE</span>
      <span>${slide.number}/${command.slides}</span>
    </footer>
  </main>
</body>
</html>`;
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function buildCarouselVisualPrompt(
  command,
  slide
) {
  const role =
    visualSceneForCarouselSlide(
      command,
      slide
    );

  return [
    "Premium editorial business photography for a Brazilian management consultancy social media carousel.",
    "Vertical 4:5 composition.",
    role,
    `Concept: ${sanitizeSlideText(slide.headline)}.`,
    `Management situation: ${sanitizeSlideText(slide.body)}.`,
    "Realistic people, natural gestures, candid action, authentic small-business or leadership environment.",
    "Contemporary photography, subtle cinematic light, sophisticated navy and electric-blue visual identity where natural.",
    "Strong photographic composition with clear negative space for an editorial text overlay.",
    "Do not place the main subject in the lower text-safe area.",
    "No posed stock-photo handshake.",
    "No generic boardroom.",
    "No futuristic interface.",
    "No terminal screen.",
    "No neon cyberpunk UI.",
    "NO WRITTEN LANGUAGE ANYWHERE IN THE GENERATED IMAGE.",
    "No words, no letters, no numbers, no logos, no trademarks, no watermarks, no readable screens, no readable documents, no signage.",
    `This is carousel card ${slide.number} of ${command.slides}; compose a UNIQUE scene for this card, not a variation of another card.`,
    "Avoid repeating the same room, camera angle, pose, desk setup or group arrangement used in adjacent cards.",
    "No graphic interface frames, no terminal typography, no code aesthetics, no fake app screen.",
    "Photorealistic, premium, human-centered, visually distinct from every other carousel card."
  ].join(" ");
}

function visualSceneForCarouselSlide(
  command,
  slide
) {
  const text = normalizeText([
    command.topic,
    command.objective,
    slide.headline,
    slide.body
  ].join(" "));

  const n = slide.number;

  if (/centraliz|deleg|autonom|gargal/.test(text)) {
    const scenes = [
      "A busy business owner standing between several team members who are naturally looking to them for decisions, visible operational pressure, candid moment.",
      "A team member pausing mid-task while a manager is occupied elsewhere, showing dependency without melodrama.",
      "A manager being interrupted by two different colleagues during active work, illustrating unnecessary decision bottlenecks.",
      "A leader calmly defining boundaries with one employee beside a real operational workflow, hands and gestures communicating clarity.",
      "Two colleagues making a routine decision together while the manager remains in the background, visualizing responsible autonomy.",
      "A small team independently coordinating work in a real operating environment while the leader observes without intervening.",
      "A manager reviewing completed work with the team from a supportive distance, calm ownership and accountability."
    ];

    return scenes[(n - 1) % scenes.length];
  }

  if (/process|retrabal|padron/.test(text)) {
    const scenes = [
      "A small-business team handling an active workflow with visible but unreadable physical materials, one repeated task creating friction.",
      "Two employees comparing work outputs and noticing an avoidable inconsistency, candid operational setting.",
      "A manager tracing a physical workflow through real objects and handoffs, no readable labels.",
      "A worker correcting a previously completed task while a colleague observes the process.",
      "A leader and employee simplifying a physical sequence of work using objects and spatial arrangement only.",
      "A team performing a clear handoff in a real service or operations environment.",
      "A calm final quality check showing a process now flowing cleanly."
    ];

    return scenes[(n - 1) % scenes.length];
  }

  if (/reun|comunic|alinh/.test(text)) {
    const scenes = [
      "A leader opening a short focused conversation with a small team in a modern workplace, natural eye contact.",
      "Two colleagues listening while one person explains a priority with gestures and no presentation screen.",
      "A meeting becoming distracted by side conversations, subtle tension, candid documentary style.",
      "A leader refocusing a discussion around one clear decision, hands emphasizing the point.",
      "A concise standing alignment conversation near the actual work area, not a boardroom.",
      "Team members leaving a short meeting and immediately acting on aligned responsibilities.",
      "A leader checking in briefly with one colleague after the team has moved into action."
    ];

    return scenes[(n - 1) % scenes.length];
  }

  const genericScenes = [
    "A business leader making a focused decision in an authentic small-company environment.",
    "A manager coaching one employee during real work, candid and practical.",
    "A small team solving an operational problem together with natural body language.",
    "A leader observing a real workflow and identifying the key constraint.",
    "Two colleagues taking ownership of a task while the manager stays out of the center.",
    "A practical review moment focused on quality and accountability.",
    "A confident team moving forward after a clear management decision."
  ];

  return genericScenes[(n - 1) % genericScenes.length];
}

async function composeCarouselPhotoAndText(
  env,
  backgroundBytes,
  overlaySvg
) {
  if (!env.IMAGES) {
    throw new Error(
      "Binding IMAGES ausente para composição visual do carrossel"
    );
  }

  const baseStream =
    new Blob(
      [backgroundBytes],
      { type: "image/jpeg" }
    ).stream();

  const overlayStream =
    new Blob(
      [overlaySvg],
      { type: "image/svg+xml;charset=utf-8" }
    ).stream();

  const result =
    await env.IMAGES
      .input(baseStream)
      .transform({
        width: 864,
        height: 1080,
        fit: "cover",
        gravity: "auto"
      })
      .draw(
        env.IMAGES.input(overlayStream),
        {
          top: 0,
          left: 0,
          opacity: 1
        }
      )
      .output({
        format: "image/png"
      });

  const response =
    result.response();

  if (!response.ok) {
    throw new Error(
      `Images binding retornou HTTP ${response.status}`
    );
  }

  return new Uint8Array(
    await response.arrayBuffer()
  );
}

async function rasterizeSvgToPng(
  env,
  svg
) {
  if (!env.IMAGES) {
    throw new Error("Binding IMAGES ausente");
  }

  const stream =
    new Blob(
      [svg],
      { type: "image/svg+xml;charset=utf-8" }
    ).stream();

  const result =
    await env.IMAGES
      .input(stream)
      .output({
        format: "image/png"
      });

  const response =
    result.response();

  if (!response.ok) {
    throw new Error(
      `Falha ao rasterizar SVG: HTTP ${response.status}`
    );
  }

  return new Uint8Array(
    await response.arrayBuffer()
  );
}

function buildCarouselTextOverlaySvg(
  command,
  slide
) {
  const W = 864;
  const H = 1080;

  const isCover =
    slide.number === 1;

  const isLast =
    slide.number === command.slides;

  const title =
    escapeXml(
      sanitizeSlideText(
        slide.headline
      )
    );

  const body =
    sanitizeSlideText(
      slide.body
    );

  const titleLines =
    wrapSvgText(
      sanitizeSlideText(slide.headline),
      isCover ? 26 : 30,
      isCover ? 4 : 3
    );

  const bodyLines =
    wrapSvgText(
      body,
      isCover ? 36 : 42,
      isCover ? 4 : isLast ? 5 : 6
    );

  const titleSize =
    isCover
      ? (titleLines.length >= 4 ? 58 : 66)
      : 48;

  const bodySize =
    isCover
      ? 31
      : 30;

  const titleY =
    isCover
      ? 300
      : 655;

  const bodyY =
    isCover
      ? 610
      : 820;

  const panelY =
    isCover
      ? 0
      : 565;

  const panelH =
    isCover
      ? H
      : 515;

  const coverGradient =
    isCover
      ? `
        <linearGradient id="shade" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="#06162b" stop-opacity="0.96"/>
          <stop offset="66%" stop-color="#06162b" stop-opacity="0.76"/>
          <stop offset="100%" stop-color="#06162b" stop-opacity="0.18"/>
        </linearGradient>
      `
      : `
        <linearGradient id="shade" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#07182d" stop-opacity="0.93"/>
          <stop offset="100%" stop-color="#07182d" stop-opacity="0.99"/>
        </linearGradient>
      `;

  const eyebrow =
    isCover
      ? "UMA GESTÃO INTELIGENTE"
      : editorialEyebrowForSlide(slide.number);

  const ctaBadge =
    isLast
      ? `
        <rect x="68" y="965" width="410" height="56" rx="28"
          fill="#1997F2" fill-opacity="0.95"/>
        <text x="96" y="1002"
          font-family="Arial, Helvetica, sans-serif"
          font-size="22" font-weight="700"
          fill="#FFFFFF">SALVE PARA REVISAR COM A EQUIPE</text>
      `
      : "";

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
  width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <defs>
    ${coverGradient}
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="9"
        flood-color="#000000" flood-opacity="0.30"/>
    </filter>
  </defs>

  <rect x="0" y="${panelY}" width="${W}" height="${panelH}"
    fill="url(#shade)"/>

  <rect x="0" y="0" width="10" height="${H}"
    fill="#2AA8FF"/>

  <rect x="68" y="${isCover ? 80 : 610}" width="92" height="5"
    rx="2.5" fill="#2AA8FF"/>

  <text x="68" y="${isCover ? 132 : 635}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="20" font-weight="700" letter-spacing="1.2"
    fill="#8FD5FF">${escapeXml(eyebrow)}</text>

  ${svgTextLines(
    titleLines,
    68,
    titleY,
    titleSize,
    isCover ? 1.05 : 1.12,
    "#FFFFFF",
    800
  )}

  ${svgTextLines(
    bodyLines,
    68,
    bodyY,
    bodySize,
    1.34,
    "#D9EAF7",
    400
  )}

  <line x1="68" y1="1038" x2="796" y2="1038"
    stroke="#4384B2" stroke-opacity="0.55" stroke-width="2"/>

  <text x="68" y="1066"
    font-family="Arial, Helvetica, sans-serif"
    font-size="18" font-weight="600"
    fill="#9BC3DE">UGI | UMA GESTÃO INTELIGENTE</text>

  <text x="750" y="1066"
    font-family="Arial, Helvetica, sans-serif"
    font-size="18" font-weight="700"
    fill="#4FC3FF">${slide.number}/${command.slides}</text>

  ${ctaBadge}
</svg>`;
}

function buildCarouselFullFallbackSvg(
  command,
  slide
) {
  const isCover =
    slide.number === 1;

  const isLast =
    slide.number === command.slides;

  const titleLines =
    wrapSvgText(
      sanitizeSlideText(slide.headline),
      isCover ? 26 : 30,
      isCover ? 4 : 3
    );

  const bodyLines =
    wrapSvgText(
      sanitizeSlideText(slide.body),
      isCover ? 36 : 42,
      isCover ? 4 : isLast ? 5 : 6
    );

  const titleSize =
    isCover
      ? (titleLines.length >= 4 ? 58 : 66)
      : 48;

  const bodySize =
    isCover
      ? 31
      : 30;

  const titleY =
    isCover
      ? 300
      : 520;

  const bodyY =
    isCover
      ? 610
      : 690;

  const eyebrow =
    isCover
      ? "UMA GESTÃO INTELIGENTE"
      : editorialEyebrowForSlide(slide.number);

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
  width="864" height="1080" viewBox="0 0 864 1080">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#06162B"/>
      <stop offset="55%" stop-color="#0A3150"/>
      <stop offset="100%" stop-color="#0D5B82"/>
    </linearGradient>
    <radialGradient id="glow" cx="82%" cy="16%" r="42%">
      <stop offset="0%" stop-color="#27B7FF" stop-opacity="0.42"/>
      <stop offset="100%" stop-color="#27B7FF" stop-opacity="0"/>
    </radialGradient>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="9"
        flood-color="#000000" flood-opacity="0.30"/>
    </filter>
  </defs>

  <rect width="864" height="1080" fill="url(#bg)"/>
  <rect width="864" height="1080" fill="url(#glow)"/>
  <circle cx="755" cy="150" r="118" fill="#24AFFF" fill-opacity="0.10"/>
  <circle cx="790" cy="195" r="64" fill="#59DCEB" fill-opacity="0.09"/>

  <rect x="0" y="0" width="10" height="1080" fill="#2AA8FF"/>
  <rect x="68" y="${isCover ? 80 : 350}" width="92" height="5"
    rx="2.5" fill="#2AA8FF"/>

  <text x="68" y="${isCover ? 132 : 395}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="20" font-weight="700" letter-spacing="1.2"
    fill="#8FD5FF">${escapeXml(eyebrow)}</text>

  ${svgTextLines(
    titleLines,
    68,
    titleY,
    titleSize,
    isCover ? 1.05 : 1.12,
    "#FFFFFF",
    800
  )}

  ${svgTextLines(
    bodyLines,
    68,
    bodyY,
    bodySize,
    1.34,
    "#D9EAF7",
    400
  )}

  <line x1="68" y1="1038" x2="796" y2="1038"
    stroke="#4384B2" stroke-opacity="0.55" stroke-width="2"/>

  <text x="68" y="1066"
    font-family="Arial, Helvetica, sans-serif"
    font-size="18" font-weight="600"
    fill="#9BC3DE">UGI | UMA GESTÃO INTELIGENTE</text>

  <text x="750" y="1066"
    font-family="Arial, Helvetica, sans-serif"
    font-size="18" font-weight="700"
    fill="#4FC3FF">${slide.number}/${command.slides}</text>
</svg>`;
}

function editorialEyebrowForSlide(number) {
  const labels = [
    "GESTÃO NA PRÁTICA",
    "SINAL",
    "IMPACTO",
    "CAUSA",
    "MUDANÇA",
    "MÉTODO",
    "PRÓXIMO PASSO"
  ];

  return labels[
    Math.max(
      0,
      Math.min(
        labels.length - 1,
        number - 1
      )
    )
  ];
}

function wrapSvgText(
  text,
  maxChars,
  maxLines
) {
  const words =
    String(text || "")
      .replace(/\s+/g, " ")
      .trim()
      .split(" ")
      .filter(Boolean);

  const lines = [];
  let current = "";

  for (const word of words) {
    const next =
      current
        ? `${current} ${word}`
        : word;

    if (
      next.length <= maxChars ||
      !current
    ) {
      current = next;
    } else {
      lines.push(current);
      current = word;
    }

    if (lines.length >= maxLines) {
      break;
    }
  }

  if (
    current &&
    lines.length < maxLines
  ) {
    lines.push(current);
  }

  if (
    lines.length === maxLines &&
    words.join(" ").length >
      lines.join(" ").length
  ) {
    lines[maxLines - 1] =
      lines[maxLines - 1]
        .replace(/[.,;:!?]+$/, "")
        .replace(/\s+\S*$/, "")
        .trim() + "…";
  }

  return lines;
}

function svgTextLines(
  lines,
  x,
  y,
  fontSize,
  lineHeight,
  fill,
  weight
) {
  const safeLines =
    Array.isArray(lines)
      ? lines
      : [];

  return `
  <text x="${x}" y="${y}"
    font-family="Arial, Helvetica, sans-serif"
    font-size="${fontSize}"
    font-weight="${weight}"
    fill="${fill}"
    filter="url(#softShadow)">
    ${safeLines.map(
      (line, index) =>
        `<tspan x="${x}" dy="${
          index === 0
            ? 0
            : Math.round(fontSize * lineHeight)
        }">${escapeXml(line)}</tspan>`
    ).join("")}
  </text>`;
}

function escapeXml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function carouselBase64ToBytes(value) {
  const binary = atob(value);

  return Uint8Array.from(
    binary,
    char => char.charCodeAt(0)
  );
}

async function buildDeterministicCarouselPng(
  command,
  slide
) {
  const W = 864;
  const H = 1080;

  const rgba = new Uint8Array(W * H * 4);

  const isCover = slide.number === 1;
  const isLast = slide.number === command.slides;
  const template = isCover
    ? "cover"
    : isLast
      ? "cta"
      : slide.number === 4
        ? "focus"
        : slide.number === 6
          ? "method"
          : "editorial";

  // Fundo premium com profundidade, sem aparência de dashboard.
  for (let y = 0; y < H; y++) {
    const t = y / (H - 1);

    for (let x = 0; x < W; x++) {
      const radial = Math.max(
        0,
        1 - Math.hypot(
          x - W * 0.78,
          y - H * 0.18
        ) / 780
      );

      const i = (y * W + x) * 4;

      rgba[i] = Math.round(
        5 + 5 * t + 7 * radial
      );
      rgba[i + 1] = Math.round(
        18 + 18 * t + 18 * radial
      );
      rgba[i + 2] = Math.round(
        35 + 34 * t + 32 * radial
      );
      rgba[i + 3] = 255;
    }
  }

  // Marca lateral muito mais discreta que no R8.
  fillRectRgba(
    rgba,
    W,
    H,
    0,
    0,
    10,
    H,
    44,
    157,
    255,
    255
  );

  // Luz editorial no topo e detalhe geométrico.
  fillRectRgba(
    rgba,
    W,
    H,
    10,
    0,
    W - 10,
    6,
    55,
    190,
    255,
    210
  );

  fillCircleRgba(
    rgba,
    W,
    H,
    748,
    120,
    118,
    31,
    117,
    194,
    28
  );

  fillCircleRgba(
    rgba,
    W,
    H,
    786,
    168,
    66,
    16,
    211,
    220,
    22
  );

  // Eyebrow da marca.
  fillRectRgba(
    rgba,
    W,
    H,
    66,
    70,
    isCover ? 308 : 250,
    38,
    10,
    55,
    92,
    238
  );

  drawBitmapText(
    rgba,
    W,
    H,
    isCover
      ? "UMA GESTÃO INTELIGENTE"
      : "GESTÃO NA PRÁTICA",
    82,
    80,
    2,
    [164, 216, 255, 255]
  );

  // Número editorial grande e sutil.
  const bigNumber = String(slide.number).padStart(2, "0");

  drawBitmapText(
    rgba,
    W,
    H,
    bigNumber,
    730,
    92,
    3,
    [48, 116, 175, 55]
  );

  const headline = cleanForBitmap(
    slide.headline
  );

  const body = cleanForBitmap(
    slide.body
  );

  if (template === "cover") {
    const headlineScale = 7;
    let headlineLines = wrapBitmapText(
      headline,
      675,
      headlineScale
    );

    if (headlineLines.length > 4) {
      headlineLines = wrapBitmapText(
        headline,
        675,
        6
      ).slice(0, 4);
    }

    const actualScale =
      headlineLines.length > 3
        ? 6
        : headlineScale;

    drawBitmapTextLines(
      rgba,
      W,
      H,
      headlineLines,
      66,
      245,
      actualScale,
      [247, 251, 255, 255],
      actualScale * 10 + 8
    );

    const headlineHeight =
      headlineLines.length *
      (actualScale * 10 + 8);

    fillRectRgba(
      rgba,
      W,
      H,
      66,
      255 + headlineHeight,
      112,
      6,
      39,
      169,
      255,
      255
    );

    let bodyLines = wrapBitmapText(
      body,
      650,
      4
    ).slice(0, 6);

    drawBitmapTextLines(
      rgba,
      W,
      H,
      bodyLines,
      66,
      310 + headlineHeight,
      4,
      [208, 226, 241, 255],
      44
    );

    // Faixa de promessa/ação na base da capa.
    fillRoundedRectRgba(
      rgba,
      W,
      H,
      66,
      858,
      670,
      92,
      18,
      23,
      88,
      145,
      220
    );

    drawBitmapText(
      rgba,
      W,
      H,
      "Deslize para aplicar →",
      92,
      890,
      3,
      [230, 244, 255, 255]
    );
  } else if (template === "focus") {
    // Template com caixa de foco central.
    let headlineLines = wrapBitmapText(
      headline,
      670,
      5
    ).slice(0, 3);

    drawBitmapTextLines(
      rgba,
      W,
      H,
      headlineLines,
      66,
      210,
      5,
      [250, 252, 255, 255],
      58
    );

    fillRoundedRectRgba(
      rgba,
      W,
      H,
      66,
      430,
      704,
      388,
      24,
      13,
      47,
      83,
      242
    );

    fillRectRgba(
      rgba,
      W,
      H,
      66,
      430,
      8,
      388,
      38,
      181,
      255,
      255
    );

    let bodyLines = wrapBitmapText(
      body,
      620,
      4
    );

    if (bodyLines.length > 8) {
      bodyLines = wrapBitmapText(
        body,
        620,
        3
      ).slice(0, 10);
    }

    const bodyScale =
      bodyLines.length > 8
        ? 3
        : 4;

    drawBitmapTextLines(
      rgba,
      W,
      H,
      bodyLines,
      102,
      474,
      bodyScale,
      [232, 241, 249, 255],
      bodyScale === 4 ? 46 : 36
    );
  } else if (template === "method") {
    // Template de método/lista: mais respiro para conteúdos estruturados.
    let headlineLines = wrapBitmapText(headline, 670, 5).slice(0, 3);
    drawBitmapTextLines(rgba, W, H, headlineLines, 66, 205, 5,
      [250, 252, 255, 255], 58);

    fillRoundedRectRgba(rgba, W, H, 66, 420, 704, 430, 24,
      10, 39, 70, 235);
    fillRectRgba(rgba, W, H, 66, 420, 8, 430,
      38, 181, 255, 255);

    let bodyLines = wrapBitmapText(body, 610, 3).slice(0, 11);
    drawBitmapTextLines(rgba, W, H, bodyLines, 104, 470, 3,
      [232, 241, 249, 255], 39);
  } else if (template === "cta") {
    // Último card: conclusão e CTA visual forte.
    let headlineLines = wrapBitmapText(
      headline,
      665,
      6
    ).slice(0, 3);

    drawBitmapTextLines(
      rgba,
      W,
      H,
      headlineLines,
      66,
      220,
      6,
      [248, 252, 255, 255],
      70
    );

    let bodyLines = wrapBitmapText(
      body,
      630,
      4
    ).slice(0, 8);

    drawBitmapTextLines(
      rgba,
      W,
      H,
      bodyLines,
      66,
      475,
      4,
      [212, 229, 242, 255],
      46
    );

    fillRoundedRectRgba(
      rgba,
      W,
      H,
      66,
      826,
      704,
      126,
      28,
      26,
      128,
      220,
      255
    );

    drawBitmapText(
      rgba,
      W,
      H,
      "salve | aplique | compartilhe",
      105,
      872,
      3,
      [255, 255, 255, 255]
    );
  } else {
    // Template editorial principal.
    let headlineLines = wrapBitmapText(
      headline,
      670,
      5
    ).slice(0, 3);

    drawBitmapTextLines(
      rgba,
      W,
      H,
      headlineLines,
      66,
      210,
      5,
      [248, 252, 255, 255],
      58
    );

    const headlineHeight =
      headlineLines.length * 58;

    fillRectRgba(
      rgba,
      W,
      H,
      66,
      235 + headlineHeight,
      84,
      5,
      38,
      181,
      255,
      255
    );

    let bodyLines = wrapBitmapText(
      body,
      640,
      4
    );

    if (bodyLines.length > 9) {
      bodyLines = wrapBitmapText(
        body,
        640,
        3
      ).slice(0, 11);
    }

    const bodyScale =
      bodyLines.length > 9
        ? 3
        : 4;

    drawBitmapTextLines(
      rgba,
      W,
      H,
      bodyLines,
      66,
      292 + headlineHeight,
      bodyScale,
      [218, 234, 246, 255],
      bodyScale === 4 ? 46 : 36
    );
  }

  // Rodapé minimalista.
  fillRectRgba(
    rgba,
    W,
    H,
    66,
    1000,
    704,
    2,
    49,
    121,
    178,
    150
  );

  drawBitmapText(
    rgba,
    W,
    H,
    "UGI | UMA GESTAO INTELIGENTE",
    66,
    1020,
    2,
    [143, 184, 215, 255]
  );

  drawBitmapText(
    rgba,
    W,
    H,
    `${slide.number}/${command.slides}`,
    724,
    1020,
    2,
    [64, 188, 255, 255]
  );

  drawProgressBarRgba(
    rgba,
    W,
    H,
    66,
    1058,
    704,
    5,
    slide.number,
    command.slides
  );

  return encodePngRgba(
    W,
    H,
    rgba
  );
}

// ------------------------------------------------------------
// RASTER / PNG
// ------------------------------------------------------------

function fillRectRgba(
  rgba,
  W,
  H,
  x,
  y,
  w,
  h,
  r,
  g,
  b,
  a = 255
) {
  const x0 = Math.max(0, Math.floor(x));
  const y0 = Math.max(0, Math.floor(y));
  const x1 = Math.min(W, Math.floor(x + w));
  const y1 = Math.min(H, Math.floor(y + h));

  const alpha = a / 255;

  for (let yy = y0; yy < y1; yy++) {
    for (let xx = x0; xx < x1; xx++) {
      const i = (yy * W + xx) * 4;

      if (a >= 255) {
        rgba[i] = r;
        rgba[i + 1] = g;
        rgba[i + 2] = b;
        rgba[i + 3] = 255;
      } else {
        rgba[i] = Math.round(r * alpha + rgba[i] * (1 - alpha));
        rgba[i + 1] = Math.round(g * alpha + rgba[i + 1] * (1 - alpha));
        rgba[i + 2] = Math.round(b * alpha + rgba[i + 2] * (1 - alpha));
        rgba[i + 3] = 255;
      }
    }
  }
}


function fillCircleRgba(
  rgba,
  W,
  H,
  cx,
  cy,
  radius,
  r,
  g,
  b,
  a = 255
) {
  const x0 = Math.max(
    0,
    Math.floor(cx - radius)
  );
  const x1 = Math.min(
    W - 1,
    Math.ceil(cx + radius)
  );
  const y0 = Math.max(
    0,
    Math.floor(cy - radius)
  );
  const y1 = Math.min(
    H - 1,
    Math.ceil(cy + radius)
  );

  const rr = radius * radius;

  for (let y = y0; y <= y1; y++) {
    for (let x = x0; x <= x1; x++) {
      const dx = x - cx;
      const dy = y - cy;

      if (dx * dx + dy * dy <= rr) {
        fillRectRgba(
          rgba,
          W,
          H,
          x,
          y,
          1,
          1,
          r,
          g,
          b,
          a
        );
      }
    }
  }
}

function fillRoundedRectRgba(
  rgba,
  W,
  H,
  x,
  y,
  w,
  h,
  radius,
  r,
  g,
  b,
  a = 255
) {
  const rr = Math.max(
    0,
    Math.min(
      radius,
      Math.floor(Math.min(w, h) / 2)
    )
  );

  fillRectRgba(
    rgba,
    W,
    H,
    x + rr,
    y,
    w - 2 * rr,
    h,
    r,
    g,
    b,
    a
  );

  fillRectRgba(
    rgba,
    W,
    H,
    x,
    y + rr,
    w,
    h - 2 * rr,
    r,
    g,
    b,
    a
  );

  for (let yy = 0; yy < rr; yy++) {
    for (let xx = 0; xx < rr; xx++) {
      const dx = rr - xx - 0.5;
      const dy = rr - yy - 0.5;

      if (dx * dx + dy * dy <= rr * rr) {
        const points = [
          [x + xx, y + yy],
          [x + w - 1 - xx, y + yy],
          [x + xx, y + h - 1 - yy],
          [x + w - 1 - xx, y + h - 1 - yy]
        ];

        for (const [px, py] of points) {
          fillRectRgba(
            rgba,
            W,
            H,
            px,
            py,
            1,
            1,
            r,
            g,
            b,
            a
          );
        }
      }
    }
  }
}

function drawProgressBarRgba(
  rgba,
  W,
  H,
  x,
  y,
  width,
  height,
  current,
  total
) {
  fillRoundedRectRgba(
    rgba,
    W,
    H,
    x,
    y,
    width,
    height,
    Math.ceil(height / 2),
    34,
    67,
    98,
    220
  );

  const progress =
    Math.max(0, Math.min(1, current / total));

  fillRoundedRectRgba(
    rgba,
    W,
    H,
    x,
    y,
    Math.max(height, Math.round(width * progress)),
    height,
    Math.ceil(height / 2),
    49,
    177,
    255,
    255
  );
}

function strokeRectRgba(
  rgba,
  W,
  H,
  x,
  y,
  w,
  h,
  thickness,
  r,
  g,
  b,
  a = 255
) {
  fillRectRgba(rgba, W, H, x, y, w, thickness, r, g, b, a);
  fillRectRgba(rgba, W, H, x, y + h - thickness, w, thickness, r, g, b, a);
  fillRectRgba(rgba, W, H, x, y, thickness, h, r, g, b, a);
  fillRectRgba(rgba, W, H, x + w - thickness, y, thickness, h, r, g, b, a);
}

async function encodePngRgba(
  width,
  height,
  rgba
) {
  const stride = width * 4;
  const raw = new Uint8Array((stride + 1) * height);

  for (let y = 0; y < height; y++) {
    const rowStart = y * (stride + 1);
    raw[rowStart] = 0; // filtro PNG "None"
    raw.set(
      rgba.subarray(y * stride, (y + 1) * stride),
      rowStart + 1
    );
  }

  const compressed = await deflateBytes(raw);

  const signature = new Uint8Array([
    137, 80, 78, 71, 13, 10, 26, 10
  ]);

  const ihdr = new Uint8Array(13);
  writeU32BE(ihdr, 0, width);
  writeU32BE(ihdr, 4, height);
  ihdr[8] = 8;  // bit depth
  ihdr[9] = 6;  // RGBA
  ihdr[10] = 0; // compression
  ihdr[11] = 0; // filter
  ihdr[12] = 0; // interlace

  return concatUint8([
    signature,
    pngChunk("IHDR", ihdr),
    pngChunk("IDAT", compressed),
    pngChunk("IEND", new Uint8Array(0))
  ]);
}

async function deflateBytes(bytes) {
  if (typeof CompressionStream === "undefined") {
    throw new Error(
      "CompressionStream não está disponível neste runtime."
    );
  }

  const stream = new Blob([bytes])
    .stream()
    .pipeThrough(
      new CompressionStream("deflate")
    );

  return new Uint8Array(
    await new Response(stream).arrayBuffer()
  );
}

function pngChunk(type, data) {
  const typeBytes = new TextEncoder().encode(type);
  const out = new Uint8Array(12 + data.length);

  writeU32BE(out, 0, data.length);
  out.set(typeBytes, 4);
  out.set(data, 8);

  const crcInput = new Uint8Array(
    typeBytes.length + data.length
  );

  crcInput.set(typeBytes, 0);
  crcInput.set(data, typeBytes.length);

  writeU32BE(
    out,
    8 + data.length,
    crc32(crcInput)
  );

  return out;
}

function writeU32BE(arr, offset, value) {
  const v = value >>> 0;
  arr[offset] = (v >>> 24) & 255;
  arr[offset + 1] = (v >>> 16) & 255;
  arr[offset + 2] = (v >>> 8) & 255;
  arr[offset + 3] = v & 255;
}

function crc32(bytes) {
  let crc = 0xffffffff;

  for (let i = 0; i < bytes.length; i++) {
    crc ^= bytes[i];

    for (let j = 0; j < 8; j++) {
      crc = (crc >>> 1) ^
        (0xedb88320 & -(crc & 1));
    }
  }

  return (crc ^ 0xffffffff) >>> 0;
}

function concatUint8(parts) {
  const length = parts.reduce(
    (sum, part) => sum + part.length,
    0
  );

  const out = new Uint8Array(length);
  let offset = 0;

  for (const part of parts) {
    out.set(part, offset);
    offset += part.length;
  }

  return out;
}

// ------------------------------------------------------------
// FONTE BITMAP 5x7
// ------------------------------------------------------------

const FONT5X7 = {
  " ":["00000","00000","00000","00000","00000","00000","00000"],
  "A":["01110","10001","10001","11111","10001","10001","10001"],
  "B":["11110","10001","10001","11110","10001","10001","11110"],
  "C":["01111","10000","10000","10000","10000","10000","01111"],
  "D":["11110","10001","10001","10001","10001","10001","11110"],
  "E":["11111","10000","10000","11110","10000","10000","11111"],
  "F":["11111","10000","10000","11110","10000","10000","10000"],
  "G":["01111","10000","10000","10111","10001","10001","01111"],
  "H":["10001","10001","10001","11111","10001","10001","10001"],
  "I":["11111","00100","00100","00100","00100","00100","11111"],
  "J":["00111","00010","00010","00010","10010","10010","01100"],
  "K":["10001","10010","10100","11000","10100","10010","10001"],
  "L":["10000","10000","10000","10000","10000","10000","11111"],
  "M":["10001","11011","10101","10101","10001","10001","10001"],
  "N":["10001","11001","10101","10011","10001","10001","10001"],
  "O":["01110","10001","10001","10001","10001","10001","01110"],
  "P":["11110","10001","10001","11110","10000","10000","10000"],
  "Q":["01110","10001","10001","10001","10101","10010","01101"],
  "R":["11110","10001","10001","11110","10100","10010","10001"],
  "S":["01111","10000","10000","01110","00001","00001","11110"],
  "T":["11111","00100","00100","00100","00100","00100","00100"],
  "U":["10001","10001","10001","10001","10001","10001","01110"],
  "V":["10001","10001","10001","10001","10001","01010","00100"],
  "W":["10001","10001","10001","10101","10101","10101","01010"],
  "X":["10001","10001","01010","00100","01010","10001","10001"],
  "Y":["10001","10001","01010","00100","00100","00100","00100"],
  "Z":["11111","00001","00010","00100","01000","10000","11111"],
  "0":["01110","10001","10011","10101","11001","10001","01110"],
  "1":["00100","01100","00100","00100","00100","00100","01110"],
  "2":["01110","10001","00001","00010","00100","01000","11111"],
  "3":["11110","00001","00001","01110","00001","00001","11110"],
  "4":["00010","00110","01010","10010","11111","00010","00010"],
  "5":["11111","10000","10000","11110","00001","00001","11110"],
  "6":["01110","10000","10000","11110","10001","10001","01110"],
  "7":["11111","00001","00010","00100","01000","01000","01000"],
  "8":["01110","10001","10001","01110","10001","10001","01110"],
  "9":["01110","10001","10001","01111","00001","00001","01110"],
  ".":["00000","00000","00000","00000","00000","00110","00110"],
  ",":["00000","00000","00000","00000","00110","00110","00100"],
  ":":["00000","00110","00110","00000","00110","00110","00000"],
  ";":["00000","00110","00110","00000","00110","00110","00100"],
  "!":["00100","00100","00100","00100","00100","00000","00100"],
  "?":["01110","10001","00001","00010","00100","00000","00100"],
  "-":["00000","00000","00000","11111","00000","00000","00000"],
  "/":["00001","00010","00010","00100","01000","01000","10000"],
  "(":["00010","00100","01000","01000","01000","00100","00010"],
  ")":["01000","00100","00010","00010","00010","00100","01000"],
  "%":["11001","11010","00100","01000","10110","00110","00000"],
  "+":["00000","00100","00100","11111","00100","00100","00000"],
  "=":["00000","11111","00000","11111","00000","00000","00000"],
  "#":["01010","11111","01010","01010","11111","01010","00000"],
  "&":["01100","10010","10100","01000","10101","10010","01101"],
  "a":["00000","00000","01110","00001","01111","10001","01111"],
  "b":["10000","10000","10110","11001","10001","10001","11110"],
  "c":["00000","00000","01111","10000","10000","10000","01111"],
  "d":["00001","00001","01101","10011","10001","10001","01111"],
  "e":["00000","00000","01110","10001","11111","10000","01111"],
  "f":["00110","01001","01000","11100","01000","01000","01000"],
  "g":["00000","00000","01111","10001","01111","00001","01110"],
  "h":["10000","10000","10110","11001","10001","10001","10001"],
  "i":["00100","00000","01100","00100","00100","00100","01110"],
  "j":["00010","00000","00110","00010","00010","10010","01100"],
  "k":["10000","10000","10010","10100","11000","10100","10010"],
  "l":["01100","00100","00100","00100","00100","00100","01110"],
  "m":["00000","00000","11010","10101","10101","10101","10101"],
  "n":["00000","00000","10110","11001","10001","10001","10001"],
  "o":["00000","00000","01110","10001","10001","10001","01110"],
  "p":["00000","00000","11110","10001","11110","10000","10000"],
  "q":["00000","00000","01111","10001","01111","00001","00001"],
  "r":["00000","00000","10111","11000","10000","10000","10000"],
  "s":["00000","00000","01111","10000","01110","00001","11110"],
  "t":["01000","01000","11100","01000","01000","01001","00110"],
  "u":["00000","00000","10001","10001","10001","10011","01101"],
  "v":["00000","00000","10001","10001","10001","01010","00100"],
  "w":["00000","00000","10001","10001","10101","10101","01010"],
  "x":["00000","00000","10001","01010","00100","01010","10001"],
  "y":["00000","00000","10001","10001","01111","00001","01110"],
  "z":["00000","00000","11111","00010","00100","01000","11111"],
  "' ":["00000","00000","00000","00000","00000","00000","00000"]
};

function cleanForBitmap(value) {
  return String(value || "")
    .replace(/[“”]/g, '"')
    .replace(/[‘’]/g, "'")
    .replace(/[–—]/g, "-")
    .replace(/…/g, "...")
    .replace(/\s+/g, " ")
    .trim();
}

function glyphInfo(char) {
  const original = String(char || " ");
  const normalized = original.normalize("NFD");
  const base = normalized[0] || " ";
  const marks = normalized.slice(1);

  const fallbackBase =
    FONT5X7[base]
      ? base
      : FONT5X7[base.toUpperCase()]
        ? base.toUpperCase()
        : "?";

  return {
    glyph: FONT5X7[fallbackBase] || FONT5X7["?"],
    acute: marks.includes("\u0301"),
    grave: marks.includes("\u0300"),
    circumflex: marks.includes("\u0302"),
    tilde: marks.includes("\u0303"),
    diaeresis: marks.includes("\u0308"),
    cedilla:
      original === "Ç" ||
      original === "ç"
  };
}

function drawBitmapText(
  rgba,
  W,
  H,
  text,
  x,
  y,
  scale,
  color
) {
  let cursor = x;

  for (const ch of String(text || "")) {
    drawBitmapGlyph(
      rgba,
      W,
      H,
      ch,
      cursor,
      y,
      scale,
      color
    );

    cursor += bitmapCharAdvance(ch, scale);
  }
}

function drawBitmapTextLines(
  rgba,
  W,
  H,
  lines,
  x,
  y,
  scale,
  color,
  lineHeight
) {
  lines.forEach((line, index) => {
    drawBitmapText(
      rgba,
      W,
      H,
      line,
      x,
      y + index * lineHeight,
      scale,
      color
    );
  });
}

function drawBitmapGlyph(
  rgba,
  W,
  H,
  char,
  x,
  y,
  scale,
  color
) {
  const info = glyphInfo(char);
  const glyph = info.glyph;
  const [r, g, b, a] = color;

  for (let row = 0; row < 7; row++) {
    for (let col = 0; col < 5; col++) {
      if (glyph[row][col] === "1") {
        fillRectRgba(
          rgba,
          W,
          H,
          x + col * scale,
          y + row * scale,
          scale,
          scale,
          r,
          g,
          b,
          a
        );
      }
    }
  }

  // Acentos portugueses desenhados deterministicamente.
  if (info.acute) {
    fillRectRgba(rgba, W, H, x + 3 * scale, y - 2 * scale, scale, scale, r, g, b, a);
    fillRectRgba(rgba, W, H, x + 4 * scale, y - 3 * scale, scale, scale, r, g, b, a);
  }

  if (info.grave) {
    fillRectRgba(rgba, W, H, x + scale, y - 3 * scale, scale, scale, r, g, b, a);
    fillRectRgba(rgba, W, H, x + 2 * scale, y - 2 * scale, scale, scale, r, g, b, a);
  }

  if (info.circumflex) {
    fillRectRgba(rgba, W, H, x + scale, y - 2 * scale, scale, scale, r, g, b, a);
    fillRectRgba(rgba, W, H, x + 2 * scale, y - 3 * scale, scale, scale, r, g, b, a);
    fillRectRgba(rgba, W, H, x + 3 * scale, y - 2 * scale, scale, scale, r, g, b, a);
  }

  if (info.tilde) {
    fillRectRgba(rgba, W, H, x + scale, y - 2 * scale, scale, scale, r, g, b, a);
    fillRectRgba(rgba, W, H, x + 2 * scale, y - 3 * scale, scale, scale, r, g, b, a);
    fillRectRgba(rgba, W, H, x + 3 * scale, y - 2 * scale, scale, scale, r, g, b, a);
    fillRectRgba(rgba, W, H, x + 4 * scale, y - 3 * scale, scale, scale, r, g, b, a);
  }

  if (info.diaeresis) {
    fillRectRgba(rgba, W, H, x + scale, y - 2 * scale, scale, scale, r, g, b, a);
    fillRectRgba(rgba, W, H, x + 3 * scale, y - 2 * scale, scale, scale, r, g, b, a);
  }

  if (info.cedilla) {
    fillRectRgba(rgba, W, H, x + 2 * scale, y + 7 * scale, scale, scale, r, g, b, a);
    fillRectRgba(rgba, W, H, x + 3 * scale, y + 8 * scale, scale, scale, r, g, b, a);
  }
}

function bitmapCharAdvance(char, scale) {
  return char === " "
    ? 3 * scale
    : 6 * scale;
}

function measureBitmapText(text, scale) {
  let width = 0;

  for (const ch of String(text || "")) {
    width += bitmapCharAdvance(ch, scale);
  }

  return width;
}

function wrapBitmapText(
  text,
  maxWidth,
  scale
) {
  const words = cleanForBitmap(text)
    .split(/\s+/)
    .filter(Boolean);

  if (!words.length) return [""];

  const lines = [];
  let line = "";

  for (const word of words) {
    const candidate = line
      ? `${line} ${word}`
      : word;

    if (
      measureBitmapText(candidate, scale) <= maxWidth
    ) {
      line = candidate;
      continue;
    }

    if (line) {
      lines.push(line);
      line = "";
    }

    // Palavra muito longa: quebra por caracteres.
    if (
      measureBitmapText(word, scale) > maxWidth
    ) {
      let piece = "";

      for (const ch of word) {
        const next = piece + ch;

        if (
          measureBitmapText(next, scale) > maxWidth &&
          piece
        ) {
          lines.push(piece);
          piece = ch;
        } else {
          piece = next;
        }
      }

      line = piece;
    } else {
      line = word;
    }
  }

  if (line) lines.push(line);

  return lines;
}

function deterministicCarouselFallback(command) {
  const topic = command.topic;

  const cta =
    command.cta ||
    "Salve este conteúdo para aplicar depois.";

  const base = [
    {
      headline: "Clareza antes da cobrança",
      body:
        `Em ${topic}, resultado sustentável começa quando expectativa, responsabilidade e critério de sucesso ficam claros para todos.`
    },
    {
      headline: "Identifique o erro comum",
      body:
        "Observe onde surgem dúvidas, retrabalho ou dependência excessiva do gestor. Esses sinais mostram onde o alinhamento ainda está fraco."
    },
    {
      headline: "Transforme expectativa em critério",
      body:
        "Defina o resultado esperado, quem decide e em quais situações o tema precisa ser escalado. Quanto mais observável o critério, menos ruído."
    },
    {
      headline: "Dê autonomia com limites claros",
      body:
        "Separe o que a equipe decide sozinha, o que decide e comunica e o que realmente exige aprovação."
    },
    {
      headline: "Feche o ciclo",
      body: cta
    },
    {
      headline: "Teste em pequena escala",
      body:
        "Aplique o novo acordo em uma situação real, acompanhe as dúvidas e ajuste o que ainda estiver ambíguo."
    },
    {
      headline: "Gestão melhora com clareza",
      body: cta
    },
    {
      headline: "Menos ruído, mais execução",
      body:
        "Quando critérios ficam claros, a equipe ganha velocidade e o gestor deixa de ser o ponto obrigatório de todas as decisões."
    },
    {
      headline: "Acompanhe sem microgerenciar",
      body:
        "Defina um ponto de controle por resultado, risco ou prazo em vez de pedir atualização a todo momento."
    },
    {
      headline: "Converta aprendizado em rotina",
      body:
        "Se o novo critério funcionou, documente-o e torne a prática repetível para o restante da equipe."
    }
  ];

  return {
    topic,
    caption: buildFallbackCaption(topic, cta),
    slides: base.slice(0, command.slides)
  };
}

// ============================================================
// VÍDEO / REEL — VEO 3.1 FAST + MEDIA TRANSFORMATIONS
// ============================================================

// R26 GITHUB ACTION COMPAT:
// - preserva o renderer zero-cost do R25
// - evita ClientResponseError no GPT Action retornando HTTP 200 com diagnóstico estruturado
// - erros do GitHub ficam em githubAccepted=false + githubStatus + githubError
// - sucesso também retorna HTTP 200, mantendo status lógico "queued"
// - não expõe GITHUB_VIDEO_TOKEN
// R25 GITHUB ZERO-COST BRIDGE:
// - preserva integralmente carrossel 7/7 e arquitetura já validada
// - adiciona POST /api/video-render para disparar o renderer gratuito no GitHub Actions
// - usa GitHub workflow_dispatch no repositório ugi-video-renderer
// - usa GITHUB_VIDEO_TOKEN como Secret do Worker
// - usa GITHUB_VIDEO_OWNER / REPO / WORKFLOW como variáveis do Worker
// - não usa Veo/Runway/Pruna nesta nova rota
// - não expõe token ou segredo nas respostas
// - retorna 202 quando o GitHub aceitar o job
// R24 AI GATEWAY FIX:
// - preserva carrossel 7/7 e toda a arquitetura validada
// - corrige chamadas a modelos third-party pelo AI binding
// - adiciona gateway: { id: "default" } no terceiro argumento de env.AI.run()
// - usa Unified Billing da Cloudflare; não exige RUNWAY/PRUNA/GOOGLE API keys próprias
// - mantém telemetria do R23 para confirmar autenticação e retorno do provedor
// - mantém /api/video-test como rota direta e exclusiva de vídeo
// R23 VIDEO AUTH DIAGNOSTIC:
// - preserva carrossel 7/7, schema, /api/video-test e pipeline audiovisual do R22
// - adiciona telemetria segura de autenticação/credenciais por tentativa
// - nunca expõe valor de segredo/chave
// - registra bindings presentes, gateway inferido, nome do binding e tamanho do segredo
// - distingue erro de autenticação de erro do provedor e erro de mídia
// - mantém mesma cascata Veo -> Runway -> Pruna
// R22 VIDEO EDITORIAL FIX:
// - corrige a função finalizeVideoEditorial ausente no R21
// - preserva integralmente o pipeline de carrossel validado
// - mantém /api/video-test direto para generateVideoDraft
// - aplica auditoria semântica à legenda antes da geração audiovisual
// - garante fallback seguro para caption e videoPrompt
async function finalizeVideoEditorial(env, command, editorial) {
  const base = editorial && typeof editorial === "object"
    ? { ...editorial }
    : {};

  const brief = {
    id: `video-${command?.id || "diagnostic"}`,
    area: String(command?.topic || "gestão").trim(),
    angle: String(
      command?.objective ||
      command?.keyMessage ||
      command?.topic ||
      "conteúdo audiovisual de gestão"
    ).trim(),
    instruction: String(
      command?.instructions ||
      command?.keyMessage ||
      "Criar conteúdo prático, profissional e aderente ao tema."
    ).trim(),
    cta: String(command?.cta || "").trim()
  };

  base.topic = cleanTopic(
    base.topic ||
    command?.topic ||
    "Uma Gestão Inteligente"
  );

  base.caption = cleanCaption(
    base.caption ||
    buildFallbackCaption(
      command?.topic || "Gestão",
      command?.cta || "Conheça a UGI."
    )
  );

  base.videoPrompt = String(
    base.videoPrompt ||
    [
      "Vertical cinematic editorial business video.",
      "A professional manager working with a small team in a realistic modern workplace.",
      "Natural movement, authentic leadership interaction, operational decision making.",
      "Subtle camera movement, realistic lighting, premium business aesthetic.",
      "No readable text, no logos, no watermarks."
    ].join(" ")
  ).trim();

  let audit = await semanticAudit(
    env,
    brief,
    base.caption,
    randomSeed()
  );

  for (
    let attempt = 0;
    attempt < MAX_SEMANTIC_REWRITES && !audit?.pass;
    attempt++
  ) {
    try {
      base.caption = cleanCaption(
        await semanticRewrite(
          env,
          brief,
          base.caption,
          audit,
          randomSeed()
        )
      );

      audit = await semanticAudit(
        env,
        brief,
        base.caption,
        randomSeed()
      );
    } catch (error) {
      audit = {
        ...(audit || {}),
        pass: false,
        reason:
          audit?.reason ||
          `Reparo semântico do vídeo indisponível: ${error?.message || error}`
      };
      break;
    }
  }

  base.semanticAudit = audit || {
    pass: false,
    aligned: false,
    specific: false,
    inventedRules: false,
    genericLanguage: false,
    reason: "Auditoria semântica do vídeo não concluída."
  };

  return base;
}


function describeVideoAuthEnvironment(env) {
  const candidates = [
    "AI",
    "AI_GATEWAY",
    "CLOUDFLARE_AI_GATEWAY",
    "CLOUDFLARE_API_TOKEN",
    "CF_API_TOKEN",
    "RUNWAY_API_KEY",
    "PRUNA_API_KEY",
    "GOOGLE_API_KEY",
    "VEO_API_KEY"
  ];

  const bindings = {};

  for (const name of candidates) {
    const value = env?.[name];

    if (typeof value === "string") {
      bindings[name] = {
        present: value.length > 0,
        type: "secret_or_text",
        length: value.length
      };
    } else if (value) {
      bindings[name] = {
        present: true,
        type: typeof value
      };
    } else {
      bindings[name] = {
        present: false,
        type: "absent"
      };
    }
  }

  return {
    aiBindingPresent: Boolean(env?.AI),
    videoBindingPresent: Boolean(env?.VIDEO),
    mediaBindingPresent: Boolean(env?.MEDIA),
    gatewayBindingsDetected: Object.entries(bindings)
      .filter(([name, value]) =>
        value.present &&
        /(GATEWAY|TOKEN|API_KEY)/.test(name)
      )
      .map(([name]) => name),
    bindings
  };
}

function classifyVideoError(errorMessage) {
  const message = String(errorMessage || "");

  if (/2021:\s*Invalid User Credentials/i.test(message)) {
    return "authentication_invalid_credentials";
  }

  if (/401|unauthorized|authentication/i.test(message)) {
    return "authentication_error";
  }

  if (/403|forbidden/i.test(message)) {
    return "authorization_error";
  }

  if (/429|rate limit|too many requests/i.test(message)) {
    return "rate_limit";
  }

  if (/result\.video|não retornou.*video/i.test(message)) {
    return "provider_no_video_result";
  }

  if (/MP4|content-type|Saída rejeitada/i.test(message)) {
    return "media_validation_error";
  }

  return "provider_or_runtime_error";
}

async function generateVideoDraft(
  env,
  command,
  origin
) {
  let editorial = await createVideoEditorial(
    env,
    command
  );

  editorial = await finalizeVideoEditorial(
    env,
    command,
    editorial
  );

  const id = crypto.randomUUID();
  const authDiagnostic = describeVideoAuthEnvironment(env);

  const requestedDuration = Number(
    command.requestedVideoDuration ||
    command.videoDuration ||
    8
  );

  let videoUrl = null;
  let videoKey = null;
  let chosenProvider = null;
  let actualClipDuration = null;
  let renderStatus = "video_generation_failed";
  let normalizationStatus = env.VIDEO ? "pending" : "binding_missing";
  let generationError = null;
  const videoAttempts = [];

  // R20: cascade estritamente audiovisual.
  // Nenhum modelo de imagem participa desta função.
  for (const provider of VIDEO_PROVIDER_ORDER) {
    if (videoUrl) break;

    const providerDuration = resolveProviderVideoDuration(
      provider,
      requestedDuration
    );

    for (let attempt = 0; attempt < VIDEO_ATTEMPTS; attempt++) {
      const telemetry = {
        provider,
        attempt: attempt + 1,
        requestedDuration,
        providerDuration,
        state: null,
        remoteUrl: null,
        remoteContentType: null,
        remoteBytes: 0,
        mp4Signature: false,
        stored: false,
        authDiagnostic,
        gatewayId: "default",
        gatewayMode: "cloudflare_unified_billing",
        aiGatewayLogId: null,
        errorClass: null,
        error: null
      };

      try {
        const input = buildVideoProviderInput(
          provider,
          editorial.videoPrompt,
          providerDuration
        );

        const result = await env.AI.run(
          provider,
          input,
          {
            gateway: {
              id: "default",
              collectLog: true,
              metadata: {
                source: "lola-ugi",
                module: "video",
                version: VERSION,
                provider
              }
            }
          }
        );

        telemetry.aiGatewayLogId =
          env.AI?.aiGatewayLogId || null;

        telemetry.state = String(
          result?.state || ""
        );

        const remoteVideo = extractGeneratedVideoUrl(result);
        telemetry.remoteUrl = remoteVideo || null;

        const providerState = String(
          result?.state || ""
        ).toLowerCase();

        if (!remoteVideo) {
          throw new Error(
            `Modelo ${provider} não retornou result.video. state=${result?.state || "desconhecido"}`
          );
        }

        if (providerState && providerState !== "completed") {
          throw new Error(
            `Modelo ${provider} retornou state=${result?.state}; esperado Completed.`
          );
        }

        const response = await fetch(remoteVideo, {
          cache: "no-store",
          redirect: "follow",
          headers: {
            "accept": "video/mp4,video/*;q=0.9,*/*;q=0.1"
          }
        });

        if (!response.ok || !response.body) {
          throw new Error(
            `Download do vídeo de ${provider} falhou (HTTP ${response.status}).`
          );
        }

        const contentType = String(
          response.headers.get("content-type") || ""
        ).toLowerCase();

        const rawBytes = new Uint8Array(
          await response.arrayBuffer()
        );

        telemetry.remoteContentType = contentType || "ausente";
        telemetry.remoteBytes = rawBytes.length;
        telemetry.mp4Signature = isLikelyMp4(rawBytes);

        if (!isRealVideoPayload(rawBytes, contentType)) {
          throw new Error(
            `Saída rejeitada de ${provider}: esperado vídeo MP4 real; recebido type=${contentType || "ausente"}, bytes=${rawBytes.length}, mp4=${isLikelyMp4(rawBytes)}.`
          );
        }

        let finalBytes = rawBytes;

        if (env.VIDEO) {
          let rawKey = null;
          try {
            rawKey = `${VIDEO_PREFIX}${Date.now()}-${id}-${safeProviderName(provider)}-raw.mp4`;

            await env.MEDIA.put(
              rawKey,
              rawBytes,
              {
                httpMetadata: {
                  contentType: "video/mp4",
                  cacheControl: "private,max-age=3600"
                }
              }
            );

            const rawObject = await env.MEDIA.get(rawKey);

            if (!rawObject?.body) {
              throw new Error(
                "MP4 bruto não encontrado no R2 para normalização."
              );
            }

            const transformed = env.VIDEO
              .input(rawObject.body)
              .transform({
                width: 720,
                height: 1280,
                fit: "cover"
              })
              .output({
                mode: "video",
                time: "0s",
                duration: `${providerDuration}s`,
                audio: true
              });

            const normalizedResponse = await transformed.response();

            if (!normalizedResponse.ok) {
              throw new Error(
                `Media Transformations HTTP ${normalizedResponse.status}`
              );
            }

            const normalizedType = String(
              normalizedResponse.headers.get("content-type") || ""
            ).toLowerCase();

            const normalizedBytes = new Uint8Array(
              await normalizedResponse.arrayBuffer()
            );

            if (!isRealVideoPayload(normalizedBytes, normalizedType)) {
              throw new Error(
                `Media Transformations não retornou MP4 válido: type=${normalizedType || "ausente"}, bytes=${normalizedBytes.length}.`
              );
            }

            finalBytes = normalizedBytes;
            normalizationStatus = "ready";
          } catch (normalizationError) {
            // Fallback permitido somente para o MP4 bruto já validado.
            normalizationStatus = "fallback_validated_raw_video";
            telemetry.normalizationWarning =
              normalizationError?.message || String(normalizationError);
            finalBytes = rawBytes;
          } finally {
            if (rawKey) {
              try { await env.MEDIA.delete(rawKey); } catch {}
            }
          }
        }

        if (!isLikelyMp4(finalBytes)) {
          throw new Error(
            `Payload final de ${provider} perdeu assinatura MP4 antes do armazenamento.`
          );
        }

        const finalKey =
          `${VIDEO_PREFIX}${Date.now()}-${id}-${safeProviderName(provider)}.mp4`;

        await env.MEDIA.put(
          finalKey,
          finalBytes,
          {
            httpMetadata: {
              contentType: "video/mp4",
              cacheControl: "public,max-age=31536000,immutable"
            }
          }
        );

        const stored = await env.MEDIA.head(finalKey);
        const storedType = String(
          stored?.httpMetadata?.contentType || ""
        ).toLowerCase();

        if (
          !stored ||
          Number(stored.size || 0) < 10000 ||
          storedType !== "video/mp4"
        ) {
          throw new Error(
            `R2 não confirmou MP4 final de ${provider}: type=${storedType || "ausente"}, size=${stored?.size || 0}.`
          );
        }

        telemetry.stored = true;
        telemetry.finalBytes = Number(stored.size || finalBytes.length);
        telemetry.finalContentType = storedType;
        videoAttempts.push(telemetry);

        videoKey = finalKey;
        videoUrl = `${origin}/media/${finalKey}`;
        chosenProvider = provider;
        actualClipDuration = providerDuration;
        renderStatus = "ready";
        generationError = null;
        break;
      } catch (error) {
        telemetry.error = error?.message || String(error);
        telemetry.errorClass = classifyVideoError(telemetry.error);
        generationError = telemetry.error;
        videoAttempts.push(telemetry);

        if (attempt < VIDEO_ATTEMPTS - 1) {
          await sleep(3500 * (attempt + 1));
        }
      }
    }
  }

  const caption = cleanCaption(
    editorial.caption ||
    buildFallbackCaption(
      command.topic,
      command.cta
    )
  );

  const finalText =
    `${caption}\n\n#Gestao #Lideranca ${BRAND_HASHTAG}`;

  const qualityIssues = [];
  qualityIssues.push(...validateCaption(caption));

  if (!editorial.semanticAudit?.pass) {
    qualityIssues.push(
      `semântica: ${editorial.semanticAudit?.reason || "auditoria pendente"}`
    );
  }

  if (!videoUrl) {
    qualityIssues.push(
      `vídeo: nenhum provedor audiovisual retornou MP4 real. Último erro: ${generationError || "não informado"}`
    );
  }

  if (
    videoUrl &&
    requestedDuration > Number(actualClipDuration || 0)
  ) {
    qualityIssues.push(
      `duração: solicitado ${requestedDuration}s; arquivo audiovisual real produzido tem ${actualClipDuration}s. O R20 não fabrica duração.`
    );
  }

  const draft = {
    id,
    version: VERSION,

    type:
      command.type === "video"
        ? "video"
        : "reel",

    commandId: command.id,
    contentId: command.contentId || id,
    experimentId: command.experimentId || command.experiment || null,
    variant: command.variant || null,
    commercialIntent: command.commercialIntent || null,

    topic: cleanTopic(
      editorial.topic ||
      command.topic
    ),

    area: command.topic,
    angle: command.objective,
    text: finalText,
    captionWords: wordCount(caption),
    videoPrompt: editorial.videoPrompt,
    videoUrl,
    videoKey,

    requestedVideoDuration: requestedDuration,
    videoDuration: actualClipDuration,
    generatedClipDuration: actualClipDuration,
    videoProvider: chosenProvider,
    videoProviderOrder: VIDEO_PROVIDER_ORDER,
    videoAttempts,
    authDiagnostic,

    status: "draft",
    renderStatus,
    normalizationStatus,

    qualityStatus:
      videoUrl
        ? "ready_for_review"
        : "needs_review",

    qualityIssues,
    semanticAudit: editorial.semanticAudit || null,
    generationError,

    music: await resolveMusicForDraft(
      env,
      command,
      command.type
    ),

    musicTechnicalNote:
      command.music?.requested
        ? "Música permanece independente do pipeline audiovisual. Nenhuma faixa, ID ou licença é inventada."
        : "",

    source: "command-hub",
    experiment: command.experiment,
    createdAt: new Date().toISOString()
  };

  await saveLocalDraft(env, draft);

  await saveHistory(env, {
    briefId: `command-${command.id}`,
    topic: draft.topic,
    area: command.topic,
    type: draft.type,
    createdAt: draft.createdAt
  });

  return draft;
}

function buildVideoProviderInput(provider, prompt, duration) {
  const cleanPrompt = String(prompt || "").slice(0, 1000);

  if (provider === "google/veo-3.1-fast") {
    return {
      prompt: cleanPrompt,
      aspect_ratio: "9:16",
      duration: `${duration}s`,
      generate_audio: true,
      resolution: "720p"
    };
  }

  if (provider === "runwayml/gen-4.5") {
    return {
      prompt: cleanPrompt,
      duration,
      ratio: "720:1280"
    };
  }

  if (provider === "pruna/p-video") {
    return {
      prompt: cleanPrompt,
      duration,
      resolution: "720p",
      aspect_ratio: "9:16",
      draft: false,
      save_audio: true,
      prompt_upsampling: true
    };
  }

  throw new Error(`Provedor de vídeo não suportado: ${provider}`);
}

function resolveProviderVideoDuration(provider, requested) {
  const n = Number(requested || 8);

  if (provider === "google/veo-3.1-fast") {
    if (n <= 4) return 4;
    if (n <= 6) return 6;
    return 8;
  }

  if (provider === "runwayml/gen-4.5") {
    return clamp(Math.round(n), 2, 10);
  }

  if (provider === "pruna/p-video") {
    return clamp(Math.round(n), 1, 20);
  }

  return 5;
}

function safeProviderName(provider) {
  return String(provider || "video")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60);
}

function isRealVideoPayload(bytes, contentType = "") {
  const type = String(contentType || "").toLowerCase();

  if (!(bytes instanceof Uint8Array) || bytes.length < 10000) {
    return false;
  }

  // Bloqueia explicitamente respostas de imagem, mesmo que tenham extensão enganosa.
  if (
    type.includes("image/") ||
    type.includes("jpeg") ||
    type.includes("png") ||
    type.includes("webp")
  ) {
    return false;
  }

  if (type && !type.includes("video") && !type.includes("mp4")) {
    return false;
  }

  return isLikelyMp4(bytes);
}

async function createVideoEditorial(
  env,
  command
) {
  try {
    return await aiJSON(
      env,
      [
        {
          role: "system",
          content: [
            "Você cria Reels profissionais para a marca Uma Gestão Inteligente.",
            "Público: gestores, líderes e empreendedores.",
            "Crie um Reel curto, sofisticado, realista e útil.",
            "A legenda deve ser em português brasileiro.",
            "videoPrompt deve ser em inglês.",
            "O vídeo deve ser vertical, profissional e mostrar ação real de gestão.",
            "Não mostre texto legível dentro do vídeo.",
            "Não use logos.",
            "Não use ficção científica.",
            "Evite pessoas posando para a câmera."
          ].join(" ")
        },
        {
          role: "user",
          content: [
            `Tema: ${command.topic}`,
            `Objetivo: ${command.objective}`,
            command.keyMessage
              ? `Mensagem central: ${command.keyMessage}`
              : "",
            command.instructions
              ? `Instruções: ${command.instructions}`
              : "",
            `Duração aproximada: ${command.videoDuration} segundos`,
            command.music?.requested
              ? `Referência de ritmo/atmosfera: ${command.music.title} - ${command.music.artist}. Não inclua música comercial dentro do arquivo gerado.`
              : "",
            `CTA: ${command.cta}`,
            "Retorne topic, caption e videoPrompt."
          ]
            .filter(Boolean)
            .join("\n")
        }
      ],
      randomSeed(),
      0.32,
      videoSchema()
    );
  } catch {
    return {
      topic: command.topic,

      caption: buildFallbackCaption(
        command.topic,
        command.cta
      ),

      videoPrompt: [
        "Vertical cinematic editorial business video.",
        "A professional manager working with a small team in a realistic modern workplace.",
        "Natural movement, authentic leadership interaction, operational decision making.",
        "Subtle camera movement, realistic lighting, premium business aesthetic.",
        "No readable text, no logos, no watermarks."
      ].join(" ")
    };
  }
}

function videoSchema() {
  return {
    type: "object",

    properties: {
      topic: {
        type: "string"
      },

      caption: {
        type: "string"
      },

      videoPrompt: {
        type: "string"
      }
    },

    required: [
      "topic",
      "caption",
      "videoPrompt"
    ],

    additionalProperties: false
  };
}

function extractGeneratedVideoUrl(result) {
  return (
    result?.result?.video ||
    result?.video ||
    null
  );
}

function isLikelyMp4(bytes) {
  if (!(bytes instanceof Uint8Array) || bytes.length < 12) {
    return false;
  }

  // MP4/ISO BMFF normally contains the "ftyp" box at offset 4.
  return (
    bytes[4] === 0x66 &&
    bytes[5] === 0x74 &&
    bytes[6] === 0x79 &&
    bytes[7] === 0x70
  );
}

// ============================================================
// MÚSICA
// ============================================================

function normalizeMusic(
  music,
  contentType
) {
  const value =
    music && typeof music === "object"
      ? music
      : {};

  if (!value.requested && !value.title) {
    return {
      requested: false,
      title: "",
      artist: "",
      audioId: "",
      source: "",
      startSeconds: 0,
      status: "none",
      policy: null
    };
  }

  return {
    requested: true,

    title: String(
      value.title || ""
    ).trim(),

    artist: String(
      value.artist || ""
    ).trim(),

    audioId: String(
      value.audioId || ""
    ).trim(),

    source: String(
      value.source || "beatly"
    ).trim(),

    startSeconds:
      Number(value.startSeconds || 0) || 0,

    status:
      contentType === "reel" ||
      contentType === "video"
        ? "metadata_ready_music_attachment_pending"
        : "metadata_only",

    policy:
      value.policy || {
        provider: "beatly",
        currentAndModern: true,
        businessRelevant: true,
        professionalTone: true
      }
  };
}

async function resolveMusicForDraft(
  env,
  command,
  contentType
) {
  const base = normalizeMusic(
    command?.music,
    contentType
  );

  if (!base.requested) return base;

  // Se a Lola recebeu uma música específica, preserva.
  if (base.title) {
    return {
      ...base,
      source: base.source || "beatly",
      selectionMode: "explicit",
      ugiMusicPolicy: musicPolicySummary()
    };
  }

  const catalog = await loadBeatlyCatalog(env);

  if (!catalog.length) {
    return {
      ...base,
      source: "beatly",
      status: "beatly_catalog_pending",
      selectionMode: "catalog_required",
      ugiMusicPolicy: musicPolicySummary(),
      recommendationProfile:
        inferMusicProfile(command)
    };
  }

  const selected =
    await selectBeatlyTrack(
      env,
      command,
      catalog
    );

  if (!selected) {
    return {
      ...base,
      source: "beatly",
      status: "beatly_no_eligible_track",
      selectionMode: "no_eligible_track",
      ugiMusicPolicy: musicPolicySummary(),
      recommendationProfile:
        inferMusicProfile(command)
    };
  }

  return {
    requested: true,
    title: String(selected.title || "").trim(),
    artist: String(selected.artist || "").trim(),
    audioId: String(
      selected.audioId ||
      selected.id ||
      ""
    ).trim(),
    source: "beatly",
    startSeconds:
      Number(selected.startSeconds || 0) || 0,
    status:
      contentType === "reel" ||
      contentType === "video"
        ? "metadata_ready_music_attachment_pending"
        : "metadata_only",
    selectionMode: "automatic_ugi_rotation",
    trendScore:
      Number(selected.trendScore || 0) || null,
    moods: Array.isArray(selected.moods)
      ? selected.moods
      : [],
    ugiMusicPolicy: musicPolicySummary(),
    recommendationProfile:
      inferMusicProfile(command),
    platformEligibility:
      normalizePlatformEligibility(selected),
    platformPolicy:
      MUSIC_PLATFORM_POLICY
  };
}

function normalizePlatformEligibility(track) {
  const raw =
    track?.platformEligibility &&
    typeof track.platformEligibility === "object"
      ? track.platformEligibility
      : {};

  const result = {};

  for (const platform of MUSIC_PLATFORMS) {
    const value = raw[platform];

    result[platform] = {
      eligible:
        value?.eligible === true
          ? true
          : value?.eligible === false
            ? false
            : null,
      verified:
        value?.verified === true,
      audioId:
        String(
          value?.audioId ||
          value?.id ||
          ""
        ).trim() || null,
      reason:
        String(value?.reason || "").trim() || null
    };
  }

  return result;
}

function musicPolicySummary() {
  return {
    engine: "UGI_music_multiplatform",
    provider: "platform_aware",
    contextFirst: true,
    modern: true,
    trendAware: true,
    trendIsSecondary: true,
    businessRelevant: true,
    professional: true,
    nonDistracting: true,
    explicitLyricsBlocked: true,
    randomTrendWithoutContextBlocked: true,
    commercialEligibilityRequired: true,
    platformRightsAreIndependent: true,
    platforms: MUSIC_PLATFORM_POLICY,
    rotationWithoutRepeat: true,
    restartAfterCatalogExhausted: true,
    fallbackAttempts: MUSIC_FALLBACK_ATTEMPTS
  };
}

function inferMusicProfile(command) {
  const text = normalizeText([
    command?.topic,
    command?.objective,
    command?.keyMessage,
    command?.instructions
  ].filter(Boolean).join(" "));

  if (/lider|deleg|autonom|equipe|gest/.test(text)) {
    return {
      mood: ["confident", "modern", "focused", "human"],
      energy: "medium",
      avoid: ["aggressive", "comic", "melodramatic"]
    };
  }

  if (/produt|tempo|process|eficien|operac/.test(text)) {
    return {
      mood: ["focused", "clean", "forward-moving", "modern"],
      energy: "medium",
      avoid: ["chaotic", "heavy", "sleepy"]
    };
  }

  if (/inovac|tecnolog|inteligencia artificial|ia\b/.test(text)) {
    return {
      mood: ["contemporary", "optimistic", "smart", "subtle-electronic"],
      energy: "medium",
      avoid: ["cyberpunk", "gaming", "overly-futuristic"]
    };
  }

  return {
    mood: ["modern", "professional", "warm", "confident"],
    energy: "medium",
    avoid: ["aggressive", "comic", "overly-dramatic"]
  };
}

async function loadBeatlyCatalog(env) {
  let raw = null;

  if (env.MUSIC_CATALOG_JSON) {
    try {
      raw = JSON.parse(
        String(env.MUSIC_CATALOG_JSON)
      );
    } catch {}
  }

  if (!raw && env.MEDIA) {
    try {
      const object =
        await env.MEDIA.get(BEATLY_CATALOG_KEY);

      if (object) raw = await object.json();
    } catch {}
  }

  let list = Array.isArray(raw)
    ? raw
    : Array.isArray(raw?.tracks)
      ? raw.tracks
      : [];

  // Se MUSIC_CATALOG_JSON contém apenas a política editorial (sem tracks),
  // tenta uma fonte musical real configurada. Não fabrica catálogo.
  if (!list.length && env.MUSIC_PROVIDER_URL) {
    try {
      const headers = { "accept": "application/json" };
      if (env.MUSIC_PROVIDER_TOKEN) {
        headers.authorization = `Bearer ${String(env.MUSIC_PROVIDER_TOKEN)}`;
      }
      const res = await fetch(String(env.MUSIC_PROVIDER_URL), { headers });
      if (res.ok) {
        const providerRaw = await res.json();
        list = Array.isArray(providerRaw)
          ? providerRaw
          : Array.isArray(providerRaw?.tracks)
            ? providerRaw.tracks
            : [];
      }
    } catch {}
  }

  list = list.slice(0, MUSIC_CACHE_LIMIT);

  return list
    .filter(Boolean)
    .filter(track => track.active !== false)
    .filter(track => track.explicit !== true)
    .filter(track => track.licensed !== false)
    .filter(track => track.safeForBusiness !== false)
    .filter(track => {
      const safetyText = normalizeText([
        track.title,
        track.artist,
        track.genre,
        track.description,
        ...(Array.isArray(track.tags) ? track.tags : []),
        ...(Array.isArray(track.moods) ? track.moods : [])
      ].filter(Boolean).join(" "));
      return !MUSIC_EXPLICIT_TERMS.some(term =>
        safetyText.includes(normalizeText(term))
      );
    })
    .filter(track => {
      const trend =
        Number(track.trendScore);

      return !Number.isFinite(trend) ||
        trend >= BEATLY_MIN_TREND_SCORE;
    });
}

async function loadBeatlyHistory(env) {
  if (!env.MEDIA) return [];

  try {
    const object =
      await env.MEDIA.get(BEATLY_HISTORY_KEY);

    if (!object) return [];

    const parsed = await object.json();

    return Array.isArray(parsed)
      ? parsed
      : [];
  } catch {
    return [];
  }
}

async function saveBeatlyHistory(
  env,
  history
) {
  if (!env.MEDIA) return;

  await env.MEDIA.put(
    BEATLY_HISTORY_KEY,
    JSON.stringify(
      history.slice(-BEATLY_HISTORY_LIMIT),
      null,
      2
    ),
    {
      httpMetadata: {
        contentType: "application/json"
      }
    }
  );
}

async function selectBeatlyTrack(
  env,
  command,
  catalog
) {
  const history =
    await loadBeatlyHistory(env);

  const usedIds = new Set(
    history
      .map(item => String(item.id || ""))
      .filter(Boolean)
  );

  let pool = catalog.filter(
    track => !usedIds.has(
      String(track.id || track.audioId || "")
    )
  );

  let cycleRestarted = false;

  if (!pool.length) {
    pool = [...catalog];
    cycleRestarted = true;
  }

  const profile =
    inferMusicProfile(command);

  const scored = pool
    .map(track => ({
      track,
      score:
        scoreBeatlyTrack(
          track,
          command,
          profile
        )
    }))
    .sort((a, b) => b.score - a.score);

  const shortlist =
    scored.slice(
      0,
      Math.min(
        BEATLY_RANDOM_TOP_N,
        scored.length
      )
    );

  if (!shortlist.length) return null;

  // Sorteio dentro dos mais adequados:
  // mantém variedade sem sacrificar relevância.
  const chosen =
    shortlist[
      Math.floor(
        Math.random() * shortlist.length
      )
    ].track;

  const chosenId =
    String(
      chosen.id ||
      chosen.audioId ||
      `${chosen.artist || ""}:${chosen.title || ""}`
    );

  const nextHistory =
    cycleRestarted
      ? []
      : history;

  nextHistory.push({
    id: chosenId,
    title: chosen.title || "",
    artist: chosen.artist || "",
    topic: command.topic || "",
    usedAt: new Date().toISOString()
  });

  await saveBeatlyHistory(
    env,
    nextHistory
  );

  return chosen;
}

function scoreBeatlyTrack(
  track,
  command,
  profile
) {
  let score = 0;

  const trend =
    Number(track.trendScore);

  if (Number.isFinite(trend)) {
    score += clamp(trend, 0, 1) * 5;
  } else {
    score += 1.5;
  }

  const tags = normalizeText([
    ...(Array.isArray(track.moods)
      ? track.moods
      : []),
    ...(Array.isArray(track.tags)
      ? track.tags
      : []),
    track.genre,
    track.description,
    track.businessFit
  ].filter(Boolean).join(" "));

  const commandText =
    normalizeText([
      command.topic,
      command.objective,
      command.keyMessage,
      command.instructions
    ].filter(Boolean).join(" "));

  for (const mood of profile.mood || []) {
    if (
      tags.includes(
        normalizeText(mood)
      )
    ) {
      score += 1.2;
    }
  }

  const topicTokens =
    commandText
      .split(/\s+/)
      .filter(token => token.length >= 5)
      .slice(0, 24);

  for (const token of topicTokens) {
    if (tags.includes(token)) {
      score += 0.22;
    }
  }

  if (track.businessRelevant === true) {
    score += 1.4;
  }

  if (track.professional === true) {
    score += 1.2;
  }

  if (track.modern === true) {
    score += 1.0;
  }

  if (track.explicit === true) {
    score -= 100;
  }

  for (const avoid of profile.avoid || []) {
    if (
      tags.includes(
        normalizeText(avoid)
      )
    ) {
      score -= 2;
    }
  }

  return score;
}

// ============================================================
// POST PADRÃO
// ============================================================

async function generateStandardProposal(
  env,
  brief,
  origin,
  command = null
) {
  const history = await loadHistory(env);

  const recentTopics =
    history
      .map(item => item.topic)
      .filter(Boolean)
      .slice(0, 20);

  let best = null;
  let lastError = null;

  for (
    let completeAttempt = 0;
    completeAttempt < FULL_GENERATION_ATTEMPTS;
    completeAttempt++
  ) {
    try {
      const style = pick(STYLES);
      const seed = randomSeed() + completeAttempt;

      let proposal = await createProposal(
        env,
        brief,
        style,
        recentTopics,
        seed
      );

      proposal = normalizeProposal(proposal);

      if (
        topicInvalid(proposal.topic) ||
        isTooSimilar(
          proposal.topic,
          recentTopics
        )
      ) {
        try {
          proposal.topic =
            await repairTopic(
              env,
              brief,
              proposal.topic,
              recentTopics,
              seed + 1
            );
        } catch {
          proposal.topic =
            safeTopicFromBrief(brief);
        }
      }

      if (topicInvalid(proposal.topic)) {
        proposal.topic =
          safeTopicFromBrief(brief);
      }

      let caption =
        cleanCaption(proposal.caption);

      let issues =
        validateCaption(caption);

      for (
        let rewriteAttempt = 0;
        rewriteAttempt <
          CAPTION_REWRITE_ATTEMPTS &&
        issues.length;
        rewriteAttempt++
      ) {
        try {
          caption =
            await rewriteCaption(
              env,
              brief,
              caption,
              issues,
              seed + 20 + rewriteAttempt
            );

          caption =
            cleanCaption(caption);

          issues =
            validateCaption(caption);
        } catch (error) {
          lastError = error;
        }
      }

      let semantic = {
        pass: false,
        aligned: false,
        specific: false,
        inventedRules: false,
        genericLanguage: false,
        reason: "auditoria pendente"
      };

      if (!issues.length) {
        semantic = await semanticAudit(
          env,
          brief,
          caption,
          seed + 70
        );

        for (
          let semanticAttempt = 0;
          semanticAttempt < MAX_SEMANTIC_REWRITES &&
          !semantic.pass;
          semanticAttempt++
        ) {
          try {
            caption = await semanticRewrite(
              env,
              brief,
              caption,
              semantic,
              seed + 80 + semanticAttempt
            );

            caption = cleanCaption(caption);
            issues = validateCaption(caption);

            if (issues.length) {
              break;
            }

            semantic = await semanticAudit(
              env,
              brief,
              caption,
              seed + 90 + semanticAttempt
            );
          } catch (error) {
            lastError = error;
            break;
          }
        }
      }

      const candidate = {
        proposal,
        caption,
        issues,
        semantic,
        style,
        score:
          scoreCaptionCandidate(
            caption,
            issues
          ) +
          (semantic.pass ? 35 : -25)
      };

      if (
        !best ||
        candidate.score > best.score
      ) {
        best = candidate;
      }

      if (issues.length === 0 && semantic.pass) {
        break;
      }
    } catch (error) {
      lastError = error;
    }
  }

  if (!best) {
    const fallbackCaption =
      await resilientFallbackCaption(
        env,
        brief
      );

    best = {
      proposal: {
        topic:
          safeTopicFromBrief(brief),

        caption: fallbackCaption,

        imagePrompt:
          buildFallbackImagePrompt(
            brief
          )
      },

      caption: fallbackCaption,

      issues:
        validateCaption(
          fallbackCaption
        ),

      semantic: {
        pass: false,
        aligned: false,
        specific: false,
        inventedRules:
          MONEY_OR_PERCENT_PATTERN.test(
            fallbackCaption
          ),
        genericLanguage: false,
        reason: "fallback editorial utilizado"
      },

      style: pick(STYLES),

      score: 0
    };
  }

  let caption =
    cleanCaption(best.caption);

  if (wordCount(caption) < 70) {
    try {
      caption =
        await resilientFallbackCaption(
          env,
          brief,
          caption
        );
    } catch {}
  }

  if (!caption) {
    caption =
      buildFallbackCaption(
        brief.angle ||
        brief.area ||
        "gestão",
        brief.cta
      );
  }

  const finalIssues =
    validateCaption(caption);

  let finalSemantic = best.semantic || {
    pass: false,
    aligned: false,
    specific: false,
    inventedRules:
      MONEY_OR_PERCENT_PATTERN.test(caption),
    genericLanguage: false,
    reason: "auditoria semântica ausente"
  };

  if (!finalIssues.length) {
    try {
      finalSemantic = await semanticAudit(
        env,
        brief,
        caption,
        (best.seed || randomSeed()) + 140
      );
    } catch {}
  }

  const qualityStatus =
    finalIssues.length ||
    !finalSemantic.pass
      ? "needs_review"
      : "ready_for_review";

  const finalCaption =
    `${caption}\n\n${brief.hashtags.join(" ")}`;

  const visualPrompt =
    buildImagePrompt(
      best.proposal?.imagePrompt ||
      buildFallbackImagePrompt(brief),
      best.style || pick(STYLES),
      brief
    );

  const image =
    await generateImageResilient(
      env,
      visualPrompt,
      best.seed || randomSeed()
    );

  const id = crypto.randomUUID();

  let imageKey = null;
  let imageUrl = null;
  let renderStatus = "ready";

  if (image?.bytes) {
    imageKey =
      `${IMAGE_PREFIX}${Date.now()}-${id}.jpg`;

    await env.MEDIA.put(
      imageKey,
      image.bytes,
      {
        httpMetadata: {
          contentType: "image/jpeg",
          cacheControl:
            "public,max-age=31536000,immutable"
        }
      }
    );

    const stored =
      await env.MEDIA.head(imageKey);

    if (stored) {
      imageUrl =
        `${origin}/media/${imageKey}`;
    } else {
      imageKey = null;
      renderStatus =
        "image_storage_failed";
    }
  } else {
    renderStatus =
      "image_generation_failed";
  }

  const draft = {
    id,
    version: VERSION,

    type: "post",

    commandId: command?.id || null,

    topic: cleanTopic(
      best.proposal?.topic ||
      safeTopicFromBrief(brief)
    ),

    area: brief.area,

    angle: brief.angle,

    text: finalCaption,

    captionWords: wordCount(caption),

    hashtags: brief.hashtags,

    imageUrl,
    imageKey,

    status: "draft",

    renderStatus,

    qualityStatus,

    qualityIssues: [
      ...finalIssues,
      ...(
        finalSemantic.pass
          ? []
          : [
              `semântica: ${
                finalSemantic.reason ||
                "aderência insuficiente"
              }`
            ]
      )
    ],

    semanticAudit: finalSemantic,

    music: command
      ? await resolveMusicForDraft(
          env,
          command,
          "post"
        )
      : normalizeMusic(null, "post"),

    automaticRetries: {
      proposal: FULL_GENERATION_ATTEMPTS,
      caption:
        CAPTION_REWRITE_ATTEMPTS,
      image: IMAGE_ATTEMPTS
    },

    source:
      command
        ? "command-hub"
        : "automatic",

    experiment:
      command?.experiment || "",

    generationWarning:
      lastError?.message || null,

    createdAt: new Date().toISOString()
  };

  await saveLocalDraft(env, draft);

  await saveHistory(env, {
    briefId: brief.id,
    topic: draft.topic,
    area: brief.area,
    angle: brief.angle,
    qualityStatus,
    createdAt: draft.createdAt
  });

  return draft;
}

// ============================================================
// TEXTO / FALLBACK
// ============================================================

async function resilientFallbackCaption(
  env,
  brief,
  previous = ""
) {
  try {
    const result = await env.AI.run(
      TXT,
      {
        messages: [
          {
            role: "system",

            content: [
              "Você escreve conteúdo prático de gestão para a marca Uma Gestão Inteligente.",
              "Produza apenas uma legenda em português brasileiro.",
              "Use entre 120 e 180 palavras.",
              "Use 4 ou 5 parágrafos curtos.",
              "Explique um problema real de gestão e uma ação concreta.",
              "Não use título.",
              "Não use hashtags.",
              "Não use Markdown.",
              "Evite motivação genérica."
            ].join(" ")
          },

          {
            role: "user",

            content: [
              `Tema: ${brief.area}.`,
              `Recorte: ${brief.angle}.`,
              `Orientação: ${brief.instruction}.`,
              `Fechamento: ${brief.cta}.`,
              previous
                ? `Aproveite apenas o que for útil desta tentativa: ${previous}`
                : ""
            ]
              .filter(Boolean)
              .join("\n")
          }
        ],

        max_tokens: 900,

        temperature: 0.28,}
    );

    const text =
      cleanCaption(
        result?.response || ""
      );

    if (
      text &&
      wordCount(text) >= 70
    ) {
      return text;
    }
  } catch {}

  return buildFallbackCaption(
    brief.angle || brief.area,
    brief.cta
  );
}

function buildFallbackCaption(topic, cta) {
  const subject =
    String(topic || "gestão").trim();

  const close =
    String(
      cta ||
      "Qual mudança você pode testar hoje?"
    ).trim();

  return [
    `Quando ${subject} começa a depender apenas de esforço individual, o problema costuma aparecer em forma de atrasos, retrabalho e decisões que voltam sempre para a mesma pessoa.`,

    `Antes de criar mais uma regra, observe onde a rotina trava. Identifique qual decisão está sem critério, quem depende de autorização e o que não está claro no resultado esperado.`,

    `Depois transforme essa observação em um acordo simples: defina quem é responsável, qual resultado precisa ser entregue e em quais situações a decisão realmente deve subir para o gestor.`,

    `Teste esse critério em uma situação real durante alguns dias. Compare o número de dúvidas, interrupções e retrabalhos antes e depois. Se houver melhora, transforme o acordo em rotina; se não houver, ajuste o critério.`,

    close
  ].join("\n\n");
}

// ============================================================
// IMAGEM PADRÃO
// ============================================================

async function generateImageResilient(
  env,
  prompt,
  baseSeed
) {
  let lastError = null;

  for (
    let attempt = 0;
    attempt < IMAGE_ATTEMPTS;
    attempt++
  ) {
    try {
      const result = await env.AI.run(
        IMG,
        {
          prompt,
          steps: 6,}
      );

      if (result?.image) {
        const bytes =
          base64ToBytes(
            result.image
          );

        if (bytes.length > 1000) {
          return {
            bytes,
            attempt: attempt + 1
          };
        }
      }
    } catch (error) {
      lastError = error;
    }
  }

  return {
    bytes: null,

    error:
      lastError?.message ||
      "Imagem não gerada."
  };
}

function base64ToBytes(base64) {
  return Uint8Array.from(
    atob(base64),
    char => char.charCodeAt(0)
  );
}

// ============================================================
// PROPOSTA
// ============================================================

async function createProposal(
  env,
  brief,
  style,
  recentTopics,
  seed
) {
  return aiJSON(
    env,
    [
      {
        role: "system",

        content: [
          "Você é a estrategista editorial da marca Uma Gestão Inteligente.",
          "Público: gestores, líderes, donos de pequenos negócios e empreendedores.",
          "Escreva em português brasileiro natural.",
          "Tom: consultoria prática, humana, direta e específica.",
          "Não use motivação genérica.",
          "Não descreva fotografia na legenda.",
          "Não use hashtags dentro da legenda.",
          "Não use Markdown.",
          `Legenda preferencial entre ${TARGET_MIN} e ${TARGET_MAX} palavras.`,
          "Use 4 ou 5 parágrafos curtos.",
          "Apresente problema real, causa ou diagnóstico, consequência, método prático e fechamento.",
          "Cada parágrafo deve acrescentar informação nova.",
          "topic deve ter entre 3 e 9 palavras.",
          `Área: ${brief.area}.`,
          `Ângulo: ${brief.angle}.`,
          `Orientação: ${brief.instruction}`,
          `Critério semântico obrigatório: ${semanticCriterionForBrief(brief)}`,
          "Não invente valores financeiros, percentuais, limites numéricos, políticas ou regras universais.",
          "Evite frases promocionais, motivacionais ou clichês típicos de IA.",
          `Fechamento: ${brief.cta}`
        ].join(" ")
      },

      {
        role: "user",

        content: [
          "Crie uma publicação inédita.",
          "Não inclua hashtags.",
          "Não use o topic como primeira frase da legenda.",
          recentTopics.length
            ? `Evite repetir estes temas: ${recentTopics.join(" | ")}`
            : "",
          `Direção visual interna: ${style}.`,
          "imagePrompt deve estar em inglês.",
          "Mostre uma situação profissional concreta.",
          "Retorne topic, caption e imagePrompt."
        ]
          .filter(Boolean)
          .join("\n")
      }
    ],
    0.45,
    postSchema()
  );
}

function postSchema() {
  return {
    type: "object",

    properties: {
      topic: {
        type: "string"
      },

      caption: {
        type: "string"
      },

      imagePrompt: {
        type: "string"
      }
    },

    required: [
      "topic",
      "caption",
      "imagePrompt"
    ],

    additionalProperties: false
  };
}

// ============================================================
// REWRITE
// ============================================================

async function rewriteCaption(
  env,
  brief,
  caption,
  issues,
  seed
) {
  const result = await env.AI.run(
    TXT,
    {
      messages: [
        {
          role: "system",

          content: [
            "Você é editora-chefe da Uma Gestão Inteligente.",
            "Reescreva a legenda inteira.",
            "Entregue somente a legenda final.",
            `Busque entre ${TARGET_MIN} e ${TARGET_MAX} palavras.`,
            "Use 4 ou 5 parágrafos.",
            "Não use título.",
            "Não use Markdown.",
            "Não use hashtags.",
            "Não descreva imagem.",
            "Comece em uma situação real de gestão.",
            "Inclua um método prático.",
            "Evite frases genéricas.",
            `Área: ${brief.area}.`,
            `Ângulo: ${brief.angle}.`,
            `Orientação: ${brief.instruction}`,
            `Critério semântico obrigatório: ${semanticCriterionForBrief(brief)}`,
            "Não invente valores financeiros, percentuais, limites numéricos, políticas ou regras universais.",
            "Evite linguagem promocional, motivacional ou clichês típicos de IA.",
            `Fechamento: ${brief.cta}`
          ].join(" ")
        },

        {
          role: "user",

          content: [
            `Problemas encontrados: ${issues.join(" | ")}`,
            "Legenda anterior:",
            caption,
            "Reescreva integralmente."
          ].join("\n")
        }
      ],

      max_tokens: 1000,

      temperature: 0.24,

      repetition_penalty: 1.1,

      frequency_penalty: 0.35,
    }
  );

  return result?.response || caption;
}

// ============================================================
// REPAIR TOPIC
// ============================================================

async function repairTopic(
  env,
  brief,
  oldTopic,
  recentTopics,
  seed
) {
  const result = await env.AI.run(
    TXT,
    {
      messages: [
        {
          role: "system",

          content:
            "Crie somente um título editorial natural em português brasileiro, com 3 a 9 palavras. Não use dois-pontos, slogan ou metadados."
        },

        {
          role: "user",

          content: [
            `Área: ${brief.area}`,
            `Ângulo: ${brief.angle}`,
            `Título anterior: ${oldTopic}`,
            recentTopics.length
              ? `Evite: ${recentTopics.join(" | ")}`
              : "",
            "Retorne somente o novo título."
          ]
            .filter(Boolean)
            .join("\n")
        }
      ],

      max_tokens: 80,

      temperature: 0.35,
    }
  );

  return cleanTopic(
    result?.response || oldTopic
  );
}

// ============================================================
// AI JSON
// ============================================================

async function aiJSON(
  env,
  messages,
  temperature,
  schema
) {
  let firstError = null;

  try {
    const result = await env.AI.run(
      TXT,
      {
        messages,

        max_tokens: 1800,

        temperature,

        presence_penalty: 0.25,

        frequency_penalty: 0.3,

        repetition_penalty: 1.08,

        response_format: {
          type: "json_schema",

          json_schema: schema
        }
      }
    );

    const parsed =
      parseAIJSON(result);

    if (parsed) return parsed;
  } catch (error) {
    firstError = error;
  }

  try {
    const retry = await env.AI.run(
      TXT,
      {
        messages: [
          ...messages,

          {
            role: "user",

            content:
              "Retorne SOMENTE JSON válido, sem Markdown, comentários ou texto antes/depois."
          }
        ],

        max_tokens: 1800,

        temperature:
          Math.min(
            temperature,
            0.3
          ),}
    );

    const parsed =
      parseAIJSON(retry);

    if (parsed) return parsed;
  } catch (error) {
    throw new Error(
      error?.message ||
      firstError?.message ||
      "Resposta estruturada inválida"
    );
  }

  throw new Error(
    firstError?.message ||
    "Resposta estruturada inválida"
  );
}

function parseAIJSON(result) {
  if (
    result?.response &&
    typeof result.response === "object"
  ) {
    return result.response;
  }

  if (
    typeof result?.response !== "string"
  ) {
    return null;
  }

  const raw =
    result.response
      .trim()
      .replace(/^```json\s*/i, "")
      .replace(/^```\s*/i, "")
      .replace(/```$/i, "")
      .trim();

  try {
    return JSON.parse(raw);
  } catch {
    const start = raw.indexOf("{");
    const end = raw.lastIndexOf("}");

    if (
      start >= 0 &&
      end > start
    ) {
      try {
        return JSON.parse(
          raw.slice(start, end + 1)
        );
      } catch {
        return null;
      }
    }

    return null;
  }
}

// ============================================================
// VALIDATION
// ============================================================

function validateCaption(text) {
  const issues = [];

  const count = wordCount(text);

  const paragraphs =
    paragraphList(text);

  if (count < MIN_WORDS) {
    issues.push(
      `legenda curta: ${count} palavras`
    );
  }

  if (count > MAX_WORDS) {
    issues.push(
      `legenda longa: ${count} palavras`
    );
  }

  if (
    paragraphs.length < 3 ||
    paragraphs.length > 7
  ) {
    issues.push(
      `estrutura: ${paragraphs.length} parágrafos`
    );
  }

  if (
    BANNED_PATTERNS.some(
      rx => rx.test(text)
    )
  ) {
    issues.push("linguagem genérica, proibida ou artificial");
  }

  if (MONEY_OR_PERCENT_PATTERN.test(text)) {
    issues.push(
      "valor financeiro ou percentual inventado"
    );
  }

  if (startsLikeInternalTitle(text)) {
    issues.push(
      "começo em formato de título interno"
    );
  }

  if (/#\w+/u.test(text)) {
    issues.push(
      "hashtags dentro do corpo"
    );
  }

  if (hasExactDuplicateParagraph(text)) {
    issues.push(
      "parágrafos duplicados"
    );
  }

  if (hasStrongRepetition(text)) {
    issues.push(
      "repetição excessiva"
    );
  }

  if (!endsWithUsefulClose(text)) {
    issues.push("fechamento fraco");
  }

  return [...new Set(issues)];
}

function startsLikeInternalTitle(text) {
  const first = paragraphList(text)[0] || "";
  const wc = wordCount(first);

  if (!first) return false;

  return (
    (wc <= 14 && !/[.!?]$/.test(first)) ||
    (wc <= 16 && /:/.test(first)) ||
    /^(o erro|como |por que |a importância|a importancia|os benefícios|os beneficios|consequências|consequencias|métodos|metodos|simplificando|o líder|o lider|desenvolva|descubra|aprenda)/i.test(first)
  );
}

function endsWithUsefulClose(text) {
  const value = String(text || "").trim();

  return (
    /\?$/.test(value) ||
    /(teste|aplique|observe|revise|compare|avalie|defina|experimente)\.?$/i.test(value)
  );
}

function scoreCaptionCandidate(
  caption,
  issues
) {
  let score = 100;

  score -= issues.length * 18;

  const words = wordCount(caption);

  if (
    words >= TARGET_MIN &&
    words <= TARGET_MAX
  ) {
    score += 15;
  }

  const paragraphs =
    paragraphList(caption).length;

  if (
    paragraphs >= 4 &&
    paragraphs <= 5
  ) {
    score += 10;
  }

  return score;
}

function normalizeProposal(value) {
  return {
    topic: cleanTopic(value?.topic),
    caption:
      cleanCaption(value?.caption),
    imagePrompt:
      String(
        value?.imagePrompt || ""
      ).trim()
  };
}

function sanitizeSlideText(text) {
  return String(text || "")
    .replace(
      /[\u0000-\u001F]/g,
      " "
    )
    .replace(/\s+/g, " ")
    .trim();
}

function hasExactDuplicateParagraph(text) {
  const paragraphs =
    paragraphList(text)
      .map(normalizeText)
      .filter(
        value => value.length > 20
      );

  const seen = new Set();

  for (const paragraph of paragraphs) {
    if (seen.has(paragraph)) {
      return true;
    }

    seen.add(paragraph);
  }

  return false;
}

function hasStrongRepetition(text) {
  const paragraphs =
    paragraphList(text)
      .filter(
        paragraph =>
          wordCount(paragraph) >= 10
      );

  for (
    let i = 0;
    i < paragraphs.length;
    i++
  ) {
    for (
      let j = i + 1;
      j < paragraphs.length;
      j++
    ) {
      if (
        similarity(
          paragraphs[i],
          paragraphs[j]
        ) >= 0.76
      ) {
        return true;
      }
    }
  }

  return false;
}

function paragraphList(text) {
  return String(text || "")
    .split(/\n{2,}/)
    .map(item => item.trim())
    .filter(Boolean);
}

// ============================================================
// R44.4 — BUFFER MULTI-PLATFORM PUBLISHING HELPERS
// ============================================================

function bufferChannelEnvKey(platform) {
  return {
    instagram: "BUFFER_CHANNEL_INSTAGRAM",
    tiktok: "BUFFER_CHANNEL_TIKTOK",
    youtube: "BUFFER_CHANNEL_YOUTUBE"
  }[platform] || null;
}

function publicationStateFromBufferPost(post = {}) {
  const raw = String(post?.status || "").trim().toLowerCase();

  if (raw === "sent") return "published";
  if (raw === "error") return "error";
  if (raw === "draft") return "draft_in_buffer";

  // Buffer pode responder "buffer"/scheduled enquanto aguarda envio.
  if (raw) return "scheduled";
  return "submitted";
}

function normalizePublishMode(value) {
  const raw = String(value || "").trim();
  return ["shareNow", "customScheduled", "addToQueue"].includes(raw)
    ? raw
    : null;
}

async function bufferGraphQL(query, env) {
  if (!env.BUFFER_API_KEY) {
    throw new Error("BUFFER_API_KEY ausente.");
  }

  const response = await fetch(
    "https://api.buffer.com",
    {
      method: "POST",
      headers: {
        Authorization: "Bearer " + env.BUFFER_API_KEY,
        "content-type": "application/json",
        accept: "application/json"
      },
      body: JSON.stringify({ query })
    }
  );

  const raw = await response.text();
  let payload = {};

  try {
    payload = raw ? JSON.parse(raw) : {};
  } catch {
    payload = {
      parseError: true,
      raw: String(raw || "").slice(0, 4000)
    };
  }

  const diagnostics = {
    httpStatus: response.status,
    httpOk: response.ok,
    requestId:
      response.headers.get("x-request-id") ||
      response.headers.get("cf-ray") ||
      null,
    rateLimitRemaining:
      response.headers.get("x-ratelimit-remaining") ||
      null,
    graphqlErrors: Array.isArray(payload?.errors)
      ? payload.errors.map(item => ({
          message: item?.message || null,
          path: item?.path || null,
          extensions: item?.extensions || null
        }))
      : []
  };

  if (!response.ok) {
    const error = new Error(
      `Buffer HTTP ${response.status}: ` +
      String(
        payload?.message ||
        payload?.error ||
        diagnostics.graphqlErrors?.[0]?.message ||
        "resposta inválida"
      )
    );
    error.bufferDiagnostics = diagnostics;
    error.bufferPayload = payload;
    throw error;
  }

  if (diagnostics.graphqlErrors.length) {
    const error = new Error(
      diagnostics.graphqlErrors
        .map(item => item?.message || "GraphQL error")
        .join(" | ")
    );
    error.bufferDiagnostics = diagnostics;
    error.bufferPayload = payload;
    throw error;
  }

  return {
    ...payload,
    __bufferDiagnostics: diagnostics
  };
}

async function discoverBufferChannels(env) {
  const accountPayload = await bufferGraphQL(
    `query {
      account {
        organizations {
          id
          name
        }
      }
    }`,
    env
  );

  const organizations =
    accountPayload?.data?.account?.organizations || [];

  if (!organizations.length) {
    throw new Error("Buffer não retornou organizações.");
  }

  const requestedOrgId =
    String(env.BUFFER_ORGANIZATION_ID || "").trim();

  let organization = null;

  if (requestedOrgId) {
    organization =
      organizations.find(
        item => String(item?.id || "") === requestedOrgId
      ) || null;

    if (!organization) {
      throw new Error(
        "BUFFER_ORGANIZATION_ID não pertence à conta Buffer autenticada."
      );
    }
  } else if (organizations.length === 1) {
    organization = organizations[0];
  } else {
    throw new Error(
      "Há mais de uma organização no Buffer. Configure BUFFER_ORGANIZATION_ID."
    );
  }

  const channelsPayload = await bufferGraphQL(
    `query {
      channels(
        input: {
          organizationId: ${JSON.stringify(organization.id)}
        }
      ) {
        id
        name
        displayName
        service
        isQueuePaused
      }
    }`,
    env
  );

  return {
    organization,
    channels: channelsPayload?.data?.channels || []
  };
}

async function resolveBufferChannel(platform, env) {
  const envKey = bufferChannelEnvKey(platform);
  const explicit = envKey
    ? String(env?.[envKey] || "").trim()
    : "";

  if (explicit) {
    return {
      id: explicit,
      service: platform,
      source: envKey
    };
  }

  // Compatibilidade com o canal Instagram legado já validado.
  if (platform === "instagram" && IG) {
    return {
      id: IG,
      service: "instagram",
      source: "legacy_IG_constant"
    };
  }

  const discovered = await discoverBufferChannels(env);
  const candidates =
    discovered.channels.filter(
      item =>
        String(item?.service || "").toLowerCase() === platform
    );

  if (!candidates.length) {
    throw new Error(
      `Nenhum canal ${platform} conectado ao Buffer.`
    );
  }

  if (candidates.length > 1) {
    throw new Error(
      `Mais de um canal ${platform} encontrado. ` +
      `Configure ${envKey} explicitamente.`
    );
  }

  return {
    ...candidates[0],
    source: "buffer_discovery",
    organizationId: discovered.organization.id
  };
}

function cleanYoutubeTitle(draft = {}) {
  const source =
    String(
      draft.topic ||
      draft.title ||
      draft.hook ||
      "Uma Gestão Inteligente"
    ).trim();

  return source.slice(0, 100);
}

function platformMetadataGraphQL(platform, draft = {}) {
  if (platform === "instagram") {
    return `
      metadata: {
        instagram: {
          type: reel
          shouldShareToFeed: true
        }
      }
    `;
  }

  if (platform === "tiktok") {
    return `
      metadata: {
        tiktok: {
          isAiGenerated: false
        }
      }
    `;
  }

  if (platform === "youtube") {
    const title = cleanYoutubeTitle(draft);
    const categoryId =
      String(
        draft.youtubeCategoryId ||
        "27"
      ).trim() || "27";

    return `
      metadata: {
        youtube: {
          title: ${JSON.stringify(title)}
          categoryId: ${JSON.stringify(categoryId)}
          privacy: public
          madeForKids: false
          notifySubscribers: true
          embeddable: true
          isAiGenerated: false
        }
      }
    `;
  }

  return "";
}

async function verifyPublicVideoAsset(asset, env) {
  if (!asset?.videoUrl) {
    throw new Error("Asset sem videoUrl.");
  }

  // R44.4.2:
  // O vídeo já pertence ao nosso R2. A validação interna deve usar o binding
  // MEDIA diretamente, evitando um self-fetch HTTP ao próprio Worker.
  if (asset?.videoKey && env?.MEDIA) {
    const object = await env.MEDIA.head(asset.videoKey);

    if (!object) {
      throw new Error(
        `Asset R2 não encontrado: ${asset.videoKey}`
      );
    }

    const contentType =
      String(
        object.httpMetadata?.contentType ||
        asset.contentType ||
        ""
      ).toLowerCase();

    if (
      contentType &&
      !contentType.includes("video/mp4") &&
      contentType !== "application/octet-stream"
    ) {
      throw new Error(
        `Asset R2 não é MP4: ${contentType}.`
      );
    }

    if (
      Number(object.size || asset.videoBytes || 0) <= 0
    ) {
      throw new Error("Asset R2 possui tamanho inválido.");
    }

    return {
      source: "r2_binding",
      videoKey: asset.videoKey,
      videoBytes: Number(object.size || asset.videoBytes || 0),
      contentType: contentType || "video/mp4"
    };
  }

  // Fallback somente quando não houver videoKey/binding.
  // Usa HEAD simples; não envia Range, pois a rota /media não implementa
  // semântica de byte-range e alguns self-fetches podem divergir do browser.
  const response = await fetch(
    asset.videoUrl,
    {
      method: "HEAD",
      redirect: "follow"
    }
  );

  if (!response.ok) {
    throw new Error(
      `Asset público retornou HTTP ${response.status}.`
    );
  }

  const contentType =
    String(
      response.headers.get("content-type") || ""
    ).toLowerCase();

  if (
    contentType &&
    !contentType.includes("video/mp4") &&
    contentType !== "application/octet-stream"
  ) {
    throw new Error(
      `Asset público não retornou MP4: ${contentType}.`
    );
  }

  return {
    source: "public_head",
    videoKey: asset.videoKey || null,
    videoBytes: Number(
      response.headers.get("content-length") ||
      asset.videoBytes ||
      0
    ),
    contentType: contentType || "video/mp4"
  };
}

async function createBufferPlatformVideoPost(
  draft,
  platform,
  mode,
  dueAt,
  env
) {
  const asset = draft?.assets?.[platform];

  if (!asset?.videoUrl) {
    throw new Error(
      `Asset ${platform} sem videoUrl.`
    );
  }

  const assetValidation = await verifyPublicVideoAsset(asset, env);

  const channel =
    await resolveBufferChannel(platform, env);

  const dueAtGraphQL =
    mode === "customScheduled"
      ? `dueAt: ${JSON.stringify(dueAt)}`
      : "";

  const metadata =
    platformMetadataGraphQL(
      platform,
      draft
    );

  const videoMetadata =
    platform === "youtube"
      ? `metadata: { title: ${JSON.stringify(cleanYoutubeTitle(draft))} }`
      : `metadata: { thumbnailOffset: 1000 }`;

  const query = `
    mutation {
      createPost(
        input: {
          text: ${JSON.stringify(String(draft.text || ""))}
          channelId: ${JSON.stringify(channel.id)}
          schedulingType: automatic
          mode: ${mode}
          ${dueAtGraphQL}
          aiAssisted: true
          assets: [
            {
              video: {
                url: ${JSON.stringify(asset.videoUrl)}
                ${videoMetadata}
              }
            }
          ]
          ${metadata}
        }
      ) {
        __typename
        ... on PostActionSuccess {
          post {
            id
            text
            status
            dueAt
            sentAt
            externalLink
            sharedNow
            shareMode
            channelService
            error {
              message
              rawError
              supportUrl
            }
          }
        }
        ... on MutationError {
          message
        }
      }
    }
  `;

  const result =
    await bufferGraphQL(query, env);

  const created =
    result?.data?.createPost;

  if (!created?.post) {
    const error = new Error(
      created?.message ||
      "Buffer não criou a publicação."
    );
    error.bufferDiagnostics = {
      ...(result?.__bufferDiagnostics || {}),
      responseType: created?.__typename || null,
      mutationMessage: created?.message || null
    };
    error.bufferPayload = result;
    throw error;
  }

  return {
    post: created.post,
    channel,
    assetValidation,
    bufferDiagnostics: {
      ...(result?.__bufferDiagnostics || {}),
      responseType: created?.__typename || null,
      postError: created?.post?.error || null
    }
  };
}

async function getBufferPostStatus(
  postId,
  env
) {
  const query = `
    query {
      post(
        input: {
          id: ${JSON.stringify(postId)}
        }
      ) {
        id
        text
        status
        dueAt
        sentAt
        externalLink
        sharedNow
        shareMode
        channelService
        error {
          message
          rawError
          supportUrl
        }
      }
    }
  `;

  const result =
    await bufferGraphQL(query, env);

  const post = result?.data?.post;

  if (!post?.id) {
    const error = new Error(
      "Buffer não retornou o post solicitado."
    );
    error.bufferDiagnostics = result?.__bufferDiagnostics || null;
    error.bufferPayload = result;
    throw error;
  }

  return {
    post,
    bufferDiagnostics: {
      ...(result?.__bufferDiagnostics || {}),
      postError: post?.error || null
    }
  };
}

// ============================================================
// R43.3 — MULTI-ASSET APPROVAL HELPERS
// ============================================================

function normalizeApprovalPlatform(value) {
  const raw = String(value || "").trim().toLowerCase();
  if (raw === "youtube_shorts" || raw === "youtube-shorts") return "youtube";
  return VIDEO_PLATFORMS.includes(raw) ? raw : null;
}

function normalizeAssetApprovalStatus(value) {
  const status = String(value || "").trim().toLowerCase();
  return ["pending_approval", "approved", "rejected"].includes(status)
    ? status
    : "pending_approval";
}

function approvalSummaryFromAssets(assets = {}) {
  const platformStates = {};

  for (const platform of VIDEO_PLATFORMS) {
    const asset = assets?.[platform] || null;
    platformStates[platform] = asset
      ? normalizeAssetApprovalStatus(asset.approvalStatus)
      : "pending_approval";
  }

  const values = Object.values(platformStates);
  const approvedCount = values.filter(v => v === "approved").length;
  const rejectedCount = values.filter(v => v === "rejected").length;
  const pendingCount = values.filter(v => v === "pending_approval").length;

  let workflowStatus = "pending_approval";

  if (approvedCount === VIDEO_PLATFORMS.length) {
    workflowStatus = "approved";
  } else if (rejectedCount === VIDEO_PLATFORMS.length) {
    workflowStatus = "rejected";
  } else if (approvedCount > 0) {
    workflowStatus = "partially_approved";
  }

  return {
    workflowStatus,
    approvedCount,
    rejectedCount,
    pendingCount,
    platformStates,
    allReviewed: pendingCount === 0
  };
}

function hasMultiPlatformAssets(draft = {}) {
  const assets = draft?.assets;
  if (!assets || typeof assets !== "object") return false;

  return VIDEO_PLATFORMS.some(platform => Boolean(assets?.[platform]));
}

async function syncPlatformApprovalToVideoResult(env, renderId, assets) {
  if (!env.MEDIA || !renderId) return null;

  const previous = await loadVideoResult(env, renderId);
  if (!previous) return null;

  const summary = approvalSummaryFromAssets(assets);
  const next = {
    ...previous,
    assets,
    approvalSummary: summary,
    approvalWorkflowStatus: summary.workflowStatus,
    updatedAt: new Date().toISOString()
  };

  await saveVideoResult(env, next);
  return next;
}

// ============================================================
// R37 — CONTENT LIFECYCLE / APPROVAL MVP
// ============================================================

function normalizeContentMetadata(draft = {}) {
  const now = new Date().toISOString();
  const id = String(draft.id || draft.renderId || "").trim();

  return {
    ...draft,
    id,
    contentId: String(draft.contentId || id || "").trim(),
    experimentId: String(
      draft.experimentId ||
      draft.experiment_id ||
      draft.experiment ||
      ""
    ).trim() || null,
    variant: String(draft.variant || "").trim() || null,
    objective: String(draft.objective || "").trim() || null,
    angle: String(draft.angle || draft.hookAngle || "").trim() || null,
    hook: String(draft.hook || "").trim() || null,
    cta: String(draft.cta || "").trim() || null,
    audience: String(draft.audience || "").trim() || null,
    commercialIntent: String(
      draft.commercialIntent ||
      draft.commercial_intent ||
      draft.intent ||
      ""
    ).trim() || null,
    commercialOffer: draft.commercialOffer === true || draft.commercial_offer === true,
    editorialMode: String(draft.editorialMode || draft.editorial_mode || "standard").trim() || "standard",
    copyLock: normalizeUGICopyLock(draft, draft.type || null, draft.copyLock || null),
    exactCopy: normalizeUGICopyLock(draft, draft.type || null, draft.copyLock || draft.exactCopy || null),
    commerce: normalizeUGICommerce(draft, draft.commerce || null),
    semanticValidationRequired: draft.semanticValidationRequired === true || draft.copyLock?.enabled === true,
    semanticValidationAvailable: draft.semanticValidationAvailable === true,
    semanticValidation: draft.semanticValidation || null,
    copyLockValidation: draft.copyLockValidation || null,
    legacyContentLeakDetected: draft.legacyContentLeakDetected === true,
    workflowStatus: String(
      draft.workflowStatus ||
      (
        draft.status === "draft"
          ? (draft.renderStatus === "ready" ? "pending_approval" : "generating")
          : draft.status || "draft"
      )
    ),
    createdAt: draft.createdAt || now,
    updatedAt: draft.updatedAt || draft.createdAt || now
  };
}

async function saveContentEvent(env, draft, event, extra = {}) {
  if (!env.MEDIA || !draft?.id) return;

  const at = new Date().toISOString();
  const key =
    `${CONTENT_EVENT_PREFIX}${draft.id}/` +
    `${at.replace(/[:.]/g, "-")}-${event}.json`;

  await env.MEDIA.put(
    key,
    JSON.stringify(
      {
        contentId: draft.contentId || draft.id,
        draftId: draft.id,
        experimentId: draft.experimentId || null,
        variant: draft.variant || null,
        type: draft.type || null,
        event,
        at,
        ...extra
      },
      null,
      2
    ),
    { httpMetadata: { contentType: "application/json" } }
  );
}

async function archiveApprovalRecord(env, draft, finalState, extra = {}) {
  if (!env.MEDIA || !draft?.id) return;

  const record = normalizeContentMetadata({
    ...draft,
    workflowStatus: finalState,
    archivedAt: new Date().toISOString(),
    ...extra
  });

  await env.MEDIA.put(
    `${APPROVAL_ARCHIVE_PREFIX}${draft.id}.json`,
    JSON.stringify(record, null, 2),
    { httpMetadata: { contentType: "application/json" } }
  );
}

// ============================================================
// DRAFTS
// ============================================================

async function saveLocalDraft(
  env,
  draft
) {
  const normalized = normalizeContentMetadata({
    ...draft,
    updatedAt: new Date().toISOString()
  });

  await env.MEDIA.put(
    `${DRAFT_PREFIX}${normalized.id}.json`,
    JSON.stringify(normalized),
    {
      httpMetadata: {
        contentType: "application/json"
      }
    }
  );

  return normalized;
}

async function getLocalDraft(
  env,
  id
) {
  const object =
    await env.MEDIA.get(
      `${DRAFT_PREFIX}${id}.json`
    );

  if (!object) return null;

  return normalizeContentMetadata(await object.json());
}


async function findLocalDraftByContentId(
  env,
  contentId
) {
  const target = String(contentId || "").trim();
  if (!target || !env.MEDIA) return null;

  let cursor = undefined;
  let scanned = 0;
  const maxScanned = 1000;

  do {
    const page = await env.MEDIA.list({
      prefix: DRAFT_PREFIX,
      limit: DRAFT_LIMIT,
      ...(cursor ? { cursor } : {})
    });

    for (const object of page.objects || []) {
      if (!object.key.endsWith(".json")) continue;
      if (scanned >= maxScanned) break;
      scanned += 1;

      try {
        const stored = await env.MEDIA.get(object.key);
        if (!stored) continue;

        const draft = normalizeContentMetadata(
          await stored.json()
        );

        const candidate = String(
          draft?.contentId ||
          draft?.content_id ||
          draft?.metadata?.contentId ||
          draft?.metadata?.content_id ||
          ""
        ).trim();

        if (candidate === target) {
          return draft;
        }
      } catch (error) {
        console.log(
          "R44.4.9 findLocalDraftByContentId read error:",
          object.key,
          error
        );
      }
    }

    if (scanned >= maxScanned) break;

    cursor = page.truncated
      ? page.cursor
      : undefined;
  } while (cursor);

  return null;
}

async function listLocalDrafts(env) {
  const result =
    await env.MEDIA.list({
      prefix: DRAFT_PREFIX,
      limit: DRAFT_LIMIT
    });

  const drafts = [];

  for (const object of result.objects) {
    if (!object.key.endsWith(".json")) {
      continue;
    }

    try {
      const stored =
        await env.MEDIA.get(
          object.key
        );

      if (!stored) continue;

      const draft =
        normalizeContentMetadata(await stored.json());

      if (
        draft &&
        draft.status === "draft"
      ) {
        drafts.push(draft);
      }
    } catch (error) {
      console.log(
        "Erro ao ler rascunho:",
        object.key,
        error
      );
    }
  }

  drafts.sort((a, b) =>
    String(b.createdAt || "")
      .localeCompare(
        String(a.createdAt || "")
      )
  );

  return drafts;
}

async function deleteDraftMedia(
  env,
  draft
) {
  const keys = new Set();

  if (draft.imageKey) {
    keys.add(draft.imageKey);
  }

  if (draft.videoKey) {
    keys.add(draft.videoKey);
  }

  if (Array.isArray(draft.imageKeys)) {
    draft.imageKeys.forEach(key => {
      if (key) keys.add(key);
    });
  }

  for (const key of keys) {
    try {
      await env.MEDIA.delete(key);
    } catch {}
  }
}

// ============================================================
// HISTORY
// ============================================================

async function loadHistory(env) {
  try {
    const object =
      await env.MEDIA.get(
        HISTORY_KEY
      );

    if (!object) return [];

    const data =
      await object.json();

    return Array.isArray(data)
      ? data
      : [];
  } catch {
    return [];
  }
}

async function saveHistory(
  env,
  item
) {
  try {
    const history =
      await loadHistory(env);

    history.unshift(item);

    await env.MEDIA.put(
      HISTORY_KEY,
      JSON.stringify(
        history.slice(
          0,
          HISTORY_LIMIT
        )
      ),
      {
        httpMetadata: {
          contentType:
            "application/json"
        }
      }
    );
  } catch (error) {
    console.log(
      "Erro histórico:",
      error
    );
  }
}

// ============================================================
// BUFFER
// ============================================================

async function bufferCreatePost(
  draft,
  env
) {
  return bufferCreateWithAssets(
    draft,
    env,
    [
      {
        image: {
          url: draft.imageUrl
        }
      }
    ],
    "post"
  );
}

async function bufferCreateCarousel(
  draft,
  env
) {
  const assets =
    draft.imageUrls.map(
      url => ({
        image: { url }
      })
    );

  return bufferCreateWithAssets(
    draft,
    env,
    assets,
    "post"
  );
}

async function bufferCreateVideo(
  draft,
  env
) {
  return bufferCreateWithAssets(
    draft,
    env,
    [
      {
        video: {
          url: draft.videoUrl
        }
      }
    ],
    draft.type === "reel"
      ? "reel"
      : "post"
  );
}

async function bufferCreateWithAssets(
  draft,
  env,
  assets,
  instagramType
) {
  const assetGraphQL =
    assets
      .map(asset => {
        if (asset.image) {
          return `
            {
              image: {
                url: ${JSON.stringify(
                  asset.image.url
                )}
              }
            }
          `;
        }

        if (asset.video) {
          return `
            {
              video: {
                url: ${JSON.stringify(
                  asset.video.url
                )}
              }
            }
          `;
        }

        return "";
      })
      .filter(Boolean)
      .join(",");

  const query =
    `mutation {
      createPost(
        input: {
          text: ${JSON.stringify(
            draft.text
          )}

          channelId: "${IG}"

          schedulingType: automatic

          mode: addToQueue

          aiAssisted: true

          assets: [
            ${assetGraphQL}
          ]

          metadata: {
            instagram: {
              type: ${instagramType}
              shouldShareToFeed: true
            }
          }
        }
      ) {
        ... on PostActionSuccess {
          post {
            id
            text
            status
            dueAt
          }
        }

        ... on MutationError {
          message
        }
      }
    }`;

  return bufferData(
    query,
    env
  );
}

async function bufferData(
  query,
  env
) {
  const response = await fetch(
    "https://api.buffer.com",
    {
      method: "POST",

      headers: {
        Authorization:
          "Bearer " +
          env.BUFFER_API_KEY,

        "content-type":
          "application/json",

        accept:
          "application/json"
      },

      body:
        JSON.stringify({ query })
    }
  );

  let data;

  try {
    data = await response.json();
  } catch {
    data = {};
  }

  const graphError =
    Array.isArray(data?.errors)
      ? data.errors[0]
      : null;

  const message =
    graphError?.message || "";

  const rateLimited =
    response.status === 429 ||
    /rate limit/i.test(message) ||
    graphError
      ?.extensions
      ?.code ===
      "RATE_LIMIT_EXCEEDED";

  if (rateLimited) {
    throw new Error(
      "O Buffer está temporariamente limitado. Aguarde e tente novamente."
    );
  }

  if (!response.ok) {
    throw new Error(
      message ||
      `Buffer HTTP ${response.status}`
    );
  }

  if (graphError) {
    throw new Error(
      message || "Erro do Buffer"
    );
  }

  return data;
}

function firstGraphQLError(data) {
  return (
    Array.isArray(data?.errors) &&
    data.errors[0]?.message
  )
    ? data.errors[0].message
    : "";
}

// ============================================================
// IMAGE PROMPT
// ============================================================

function buildImagePrompt(
  imagePrompt,
  style,
  brief
) {
  const aiRule =
    brief.area ===
    "IA aplicada à gestão"
      ? "If AI is relevant, show a human manager using technology as a practical tool while retaining human judgment. No robots, humanoids, glowing brains or science-fiction holograms."
      : "";

  return [
    imagePrompt,
    style,
    "Vertical 4:5 realistic editorial photograph.",
    "Show one clear real-world professional action directly related to the management concept.",
    "Use one to three people whenever possible.",
    "Prefer visible work, operational activity, coaching, decision-making, quality checking, organizing workflow, delegating or solving a concrete business problem.",
    aiRule,
    "Avoid generic corporate posing.",
    "Avoid boardrooms unless necessary.",
    "Avoid readable documents, computer screens, dashboards, posters, whiteboards and presentation boards.",
    "No readable words, letters, numbers, labels, logos, trademarks or watermarks.",
    "Realistic cinematic lighting and believable professional environment."
  ]
    .filter(Boolean)
    .join(" ")
    .slice(0, 2048);
}

function buildFallbackImagePrompt(brief) {
  return (
    `A realistic business manager in a professional workplace actively solving a concrete management problem related to ${brief.area}. Natural body language, visible practical work, authentic environment, no readable text.`
  );
}

// ============================================================
// MEDIA R2
// ============================================================

async function serveMedia(
  request,
  env,
  path
) {
  if (
    request.method !== "GET" &&
    request.method !== "HEAD"
  ) {
    return new Response(
      "Method not allowed",
      {
        status: 405,
        headers: {
          Allow: "GET, HEAD"
        }
      }
    );
  }

  const key =
    decodeURIComponent(
      path.slice("/media/".length)
    );

  const object =
    request.method === "HEAD"
      ? await env.MEDIA.head(key)
      : await env.MEDIA.get(key);

  if (!object) {
    return new Response(
      request.method === "HEAD"
        ? null
        : "Not found",
      {
        status: 404
      }
    );
  }

  const headers = new Headers();

  if (
    typeof object.writeHttpMetadata ===
    "function"
  ) {
    object.writeHttpMetadata(headers);
  }

  headers.set(
    "Content-Type",
    object.httpMetadata?.contentType ||
    "application/octet-stream"
  );

  headers.set(
    "Cache-Control",
    "public,max-age=31536000,immutable"
  );

  headers.set(
    "Content-Disposition",
    "inline"
  );

  headers.set(
    "Access-Control-Allow-Origin",
    "*"
  );

  headers.set(
    "X-Content-Type-Options",
    "nosniff"
  );

  if (
    object.size &&
    !headers.has("Content-Length")
  ) {
    headers.set(
      "Content-Length",
      String(object.size)
    );
  }

  return new Response(
    request.method === "HEAD"
      ? null
      : object.body,
    {
      status: 200,
      headers
    }
  );
}

// ============================================================
// UTILIDADES
// ============================================================

function chooseBrief(history) {
  const recent = new Set(
    history
      .map(item => item.briefId)
      .filter(Boolean)
      .slice(
        0,
        Math.max(
          1,
          BRIEFS.length - 2
        )
      )
  );

  const available =
    BRIEFS.filter(
      item =>
        !recent.has(item.id)
    );

  return pick(
    available.length
      ? available
      : BRIEFS
  );
}

function pick(list) {
  return list[
    Math.floor(
      Math.random() *
      list.length
    )
  ];
}

function randomSeed() {
  return (
    Math.floor(
      Math.random() *
      900000000
    ) +
    10000000
  );
}

function clamp(
  value,
  min,
  max
) {
  const n =
    Number.isFinite(value)
      ? Math.round(value)
      : min;

  return Math.min(
    Math.max(n, min),
    max
  );
}


function resolveVeoDurationSeconds(value) {
  const requested = Number(value);

  // Veo 3.1 Fast suporta 4s, 6s ou 8s.
  // Selecionamos o maior valor suportado que não exceda
  // a duração solicitada, evitando declarar duração real
  // maior do que o clipe efetivamente produzido.
  if (!Number.isFinite(requested)) return 8;
  if (requested <= 4) return 4;
  if (requested < 6) return 4;
  if (requested < 8) return 6;
  return 8;
}

function safeTopicFromBrief(brief) {
  const raw =
    cleanTopic(
      brief.angle ||
      brief.area ||
      "Gestão mais clara na prática"
    );

  const words =
    raw
      .split(/\s+/)
      .filter(Boolean);

  if (
    words.length >= 3 &&
    words.length <= 9
  ) {
    return raw;
  }

  return "Gestão Mais Clara na Prática";
}

function cleanTopic(text) {
  return String(text || "")
    .replace(
      /^(tema|área|area|ângulo|angulo)\s*:\s*/i,
      ""
    )
    .replace(/\s*\|\s*.*/g, "")
    .replace(/["“”]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function cleanCaption(text) {
  return String(text || "")
    .replace(/\*\*/g, "")
    .replace(/^\s*[-•]\s+/gm, "")
    .replace(/^\s*\d+[.)]\s+/gm, "")
    .replace(
      /(^|\s)#[\p{L}\p{N}_]+/gu,
      " "
    )
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/[ \t]{2,}/g, " ")
    .trim();
}

function topicInvalid(topic) {
  const words =
    String(topic || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean);

  return (
    words.length < 3 ||
    words.length > 9 ||
    String(topic || "").length > 80 ||
    /[|]/.test(topic || "")
  );
}

function wordCount(text) {
  const value =
    String(text || "").trim();

  if (!value) return 0;

  return value
    .split(/\s+/)
    .filter(Boolean)
    .length;
}

function normalizeText(text) {
  return String(text || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(
      /[\u0300-\u036f]/g,
      ""
    )
    .replace(
      /[^a-z0-9\s]/g,
      " "
    )
    .replace(/\s+/g, " ")
    .trim();
}

function similarity(a, b) {
  const A = new Set(
    normalizeText(a)
      .split(" ")
      .filter(word => word.length > 3)
  );

  const B = new Set(
    normalizeText(b)
      .split(" ")
      .filter(word => word.length > 3)
  );

  if (!A.size || !B.size) return 0;

  let common = 0;

  for (const word of A) {
    if (B.has(word)) common++;
  }

  return (
    common /
    Math.min(A.size, B.size)
  );
}

function isTooSimilar(
  topic,
  recentTopics
) {
  return recentTopics.some(
    old =>
      similarity(topic, old) >= 0.7
  );
}

async function readBody(request) {
  try {
    return await request.json();
  } catch {
    return null;
  }
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",

    "Access-Control-Allow-Headers":
      "Content-Type, Authorization, x-lola-key, x-lola-command-key, x-ugi-video-upload-key, x-ugi-render-id, x-github-run-id, x-ugi-video-duration",

    "Access-Control-Allow-Methods":
      "GET, POST, OPTIONS"
  };
}

const json = (
  value,
  status = 200
) =>
  new Response(
    JSON.stringify(
      value,
      null,
      2
    ),
    {
      status,

      headers: {
        "content-type":
          "application/json;charset=UTF-8",

        ...corsHeaders()
      }
    }
  );

const html = value =>
  new Response(
    value,
    {
      headers: {
        "content-type":
          "text/html;charset=UTF-8"
      }
    }
  );

// ============================================================
// CENTRAL DE APROVAÇÃO
// ============================================================

const APP = `<!doctype html>
<html lang="pt-BR">

<head>
<meta charset="utf-8">

<meta
  name="viewport"
  content="width=device-width,initial-scale=1"
>

<title>Lola Operacional</title>

<style>

body{
  margin:0;
  font-family:Arial,sans-serif;
  background:#071528;
  color:#fff;
}

main{
  max-width:720px;
  margin:auto;
  padding:22px;
}

h1{
  color:#39a9ff;
  margin-bottom:4px;
}

.sub{
  color:#9fb2c9;
  margin-bottom:8px;
}

.version{
  color:#5f7790;
  font-size:11px;
  margin-bottom:24px;
}

.box,
.card{
  background:#0d223d;
  border:1px solid #183b60;
  border-radius:16px;
  padding:16px;
  margin-bottom:18px;
}

input,
textarea{
  box-sizing:border-box;
  width:100%;
  padding:13px;
  margin-top:9px;
  background:#071528;
  color:#fff;
  border:1px solid #31577b;
  border-radius:10px;
  font-size:16px;
}

textarea{
  min-height:180px;
}

button{
  border:0;
  border-radius:10px;
  padding:14px;
  color:#fff;
  font-weight:bold;
  font-size:15px;
}

button:disabled{
  opacity:.55;
}

.full{
  width:100%;
  margin-top:10px;
}

.blue{
  background:#168cff;
}

.green{
  background:#159766;
}

.orange{
  background:#c77d13;
}

.red{
  background:#993546;
}

.gray{
  background:#485b70;
}

.ai{
  background:linear-gradient(
    90deg,
    #2563eb,
    #7c3aed
  );
}

img,
video{
  width:100%;
  border-radius:12px;
  margin-bottom:12px;
  background:#000;
}

.text{
  white-space:pre-wrap;
  line-height:1.5;
}

.meta{
  color:#8faac6;
  font-size:12px;
  margin-top:8px;
}

.grid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:9px;
  margin-top:10px;
}

.edit{
  display:none;
  margin-top:12px;
}

.notice{
  font-size:13px;
  color:#9fb2c9;
  margin:10px 0 18px;
}

.local{
  color:#55d6a8;
  font-size:12px;
  margin-top:6px;
}

.warning{
  color:#ffbf69;
  background:#2d2415;
  border-radius:8px;
  padding:10px;
  margin-top:10px;
  font-size:12px;
}

.success{
  color:#79e3b9;
  background:#0d3128;
  border-radius:8px;
  padding:10px;
  margin-top:10px;
  font-size:12px;
}

.music{
  background:#151d31;
  border:1px solid #4c4e76;
  border-radius:10px;
  padding:12px;
  margin-top:12px;
  font-size:13px;
}

.carousel-preview{
  display:flex;
  overflow-x:auto;
  gap:10px;
  margin-top:14px;
  padding-bottom:8px;
}

.carousel-preview img{
  width:86%;
  min-width:86%;
  margin:0;
}

.slide-list{
  margin-top:12px;
}

.slide{
  background:#071528;
  border:1px solid #31577b;
  border-radius:10px;
  padding:12px;
  margin-top:8px;
}

.slide b{
  color:#39a9ff;
}

.tracking{
  margin-top:12px;
  padding:11px;
  border-radius:10px;
  background:#091b30;
  border:1px solid #22496e;
  font-size:12px;
  line-height:1.55;
  color:#b9cce0;
}
.tracking b{ color:#66c5ff; }

.badge{
  display:inline-block;
  padding:5px 9px;
  border-radius:999px;
  background:#183b60;
  color:#9fd7ff;
  font-size:11px;
  margin-bottom:8px;
}

</style>
</head>

<body>

<main>

<h1>Lola Operacional</h1>

<div class="sub">
Central de Aprovação — Uma Gestão Inteligente
</div>

<div class="version">
Versão: ${VERSION}
</div>

<div id="login" class="box">

<b>Chave de aprovação</b>

<input
  id="key"
  type="password"
  placeholder="LOLA_AUTH_KEY"
>

<button
  class="full blue"
  onclick="entrar()"
>
ENTRAR
</button>

</div>

<div
  id="app"
  style="display:none"
>

<button
  id="gen"
  class="full ai"
  onclick="propor()"
>
✨ GERAR PROPOSTA AUTOMÁTICA
</button>

<div id="notice" class="notice">
R44.4: Central Multi-Plataforma — aprovar continua separado de publicar. Assets aprovados podem ser publicados agora, agendados ou enviados à fila do Buffer individualmente.
</div>

<p id="status"></p>

<div id="posts"></div>

</div>

</main>

<script>

let K =
  sessionStorage.getItem(
    "lolaKey"
  ) || "";

let loading = false;

const el =
  id =>
    document.getElementById(id);

if (K) load();

function entrar() {
  K =
    el("key")
      .value
      .trim();

  if (!K) return;

  sessionStorage.setItem(
    "lolaKey",
    K
  );

  load();
}

async function api(
  path,
  options = {}
) {
  options.headers =
    Object.assign(
      {
        "x-lola-key": K
      },
      options.headers || {}
    );

  const response =
    await fetch(
      path,
      options
    );

  let data;

  try {
    data =
      await response.json();
  } catch {
    data = {
      ok:false,
      error:
        "Resposta inválida do servidor."
    };
  }

  if (response.status === 401) {
    sessionStorage.removeItem(
      "lolaKey"
    );

    K = "";

    el("login").style.display =
      "block";

    el("app").style.display =
      "none";

    alert(
      "Chave incorreta ou sessão inválida."
    );

    throw Error("Não autorizado");
  }

  return data;
}

async function propor() {
  const btn = el("gen");

  btn.disabled = true;

  btn.textContent =
    "LOLA ESTÁ CRIANDO...";

  try {
    const data =
      await api(
        "/api/propose",
        {
          method: "POST",

          headers:{
            "content-type":
              "application/json"
          },

          body: "{}"
        }
      );

    if (data.ok) {
      alert(
        "Proposta criada!\\n\\nTema: " +
        data.proposal.topic
      );

      await load();
    } else {
      alert(
        data.error ||
        "Erro ao gerar"
      );
    }
  } catch (error) {
    if (
      error.message !==
      "Não autorizado"
    ) {
      alert(
        "Erro: " +
        error.message
      );
    }
  } finally {
    btn.disabled = false;

    btn.textContent =
      "✨ GERAR PROPOSTA AUTOMÁTICA";
  }
}

async function load() {
  if (loading) return;

  loading = true;

  el("login").style.display =
    "none";

  el("app").style.display =
    "block";

  el("status").textContent =
    "Buscando rascunhos...";

  try {
    const data =
      await api(
        "/api/drafts"
      );

    if (!data.ok) {
      el("status").textContent =
        data.error ||
        "Erro ao carregar.";

      return;
    }

    const drafts =
      data.drafts || [];

    el("status").textContent =
      drafts.length +
      " rascunho(s) aguardando aprovação.";

    render(drafts);
  } finally {
    loading = false;
  }
}

function button(
  text,
  className,
  handler
) {
  const btn =
    document.createElement(
      "button"
    );

  btn.textContent = text;
  btn.className = className;
  btn.onclick = handler;

  return btn;
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function render(drafts) {
  const root = el("posts");

  root.innerHTML = "";

  drafts.forEach(draft => {
    const card =
      document.createElement(
        "div"
      );

    card.className = "card";

    const badge =
      document.createElement(
        "div"
      );

    badge.className = "badge";

    badge.textContent =
      String(
        draft.type || "post"
      ).toUpperCase();

    card.append(badge);

    const title =
      document.createElement(
        "h3"
      );

    title.textContent =
      draft.topic || "Sem tema";

    card.append(title);

    if (
      draft.type === "carousel" &&
      Array.isArray(draft.imageUrls)
    ) {
      const preview =
        document.createElement(
          "div"
        );

      preview.className =
        "carousel-preview";

      draft.imageUrls.forEach(url => {
        const img =
          document.createElement(
            "img"
          );

        img.src = url;
        img.loading = "lazy";

        preview.append(img);
      });

      card.append(preview);
    } else if (
      (
        draft.type === "reel" ||
        draft.type === "video"
      ) &&
      draft.assets &&
      typeof draft.assets === "object" &&
      Object.keys(draft.assets).length
    ) {
      const platformStack =
        document.createElement("div");
      platformStack.className = "platform-stack";

      const labels = {
        instagram: "INSTAGRAM REELS",
        tiktok: "TIKTOK",
        youtube: "YOUTUBE SHORTS"
      };

      ["instagram", "tiktok", "youtube"].forEach(platform => {
        const asset = draft.assets?.[platform];
        if (!asset) return;

        const pcard =
          document.createElement("div");
        pcard.className = "platform-card";

        const head =
          document.createElement("div");
        head.className = "platform-head";

        const name =
          document.createElement("div");
        name.className = "platform-name";
        name.textContent =
          labels[platform] || platform.toUpperCase();

        const status =
          document.createElement("div");
        const approvalStatus =
          asset.approvalStatus || "pending_approval";
        status.className =
          "platform-status " + approvalStatus;
        status.textContent =
          approvalStatus === "approved"
            ? "APROVADO"
            : approvalStatus === "rejected"
              ? "REJEITADO"
              : "AGUARDANDO APROVAÇÃO";

        head.append(name, status);
        pcard.append(head);

        if (asset.videoUrl) {
          const video =
            document.createElement("video");
          video.src = asset.videoUrl;
          video.controls = true;
          video.preload = "metadata";
          video.playsInline = true;
          pcard.append(video);
        }

        const pmeta =
          document.createElement("div");
        pmeta.className = "platform-meta";
        pmeta.textContent =
          "Duração: " +
          (asset.duration || "—") +
          "s | Render: " +
          (asset.status || "—");
        pcard.append(pmeta);

        const actions =
          document.createElement("div");
        actions.className = "platform-actions";

        actions.append(
          button(
            approvalStatus === "approved"
              ? "APROVADO ✓"
              : "APROVAR",
            "blue",
            () => decidePlatform(
              draft,
              platform,
              "approved"
            )
          ),
          button(
            approvalStatus === "rejected"
              ? "REJEITADO"
              : "REJEITAR",
            "red",
            () => decidePlatform(
              draft,
              platform,
              "rejected"
            )
          )
        );

        pcard.append(actions);

        const publicationBox =
          document.createElement("div");
        publicationBox.className =
          "publication-box";

        const publicationStatus =
          document.createElement("div");
        publicationStatus.className =
          "publication-status";

        const publication =
          asset.publication || null;

        if (publication) {
          publicationStatus.textContent =
            "Publicação: " +
            (publication.status || "—") +
            (
              publication.dueAt
                ? " | " +
                  new Date(
                    publication.dueAt
                  ).toLocaleString("pt-BR")
                : ""
            ) +
            (
              publication.externalLink
                ? " | Link disponível"
                : ""
            );
        } else if (
          approvalStatus === "approved"
        ) {
          publicationStatus.textContent =
            "Aprovado e liberado para publicação.";
        } else {
          publicationStatus.textContent =
            "A publicação só é liberada após aprovação.";
        }

        publicationBox.append(
          publicationStatus
        );

        if (
          approvalStatus === "approved" &&
          !(
            publication &&
            publication.bufferPostId &&
            !["error", "cancelled"].includes(
              String(
                publication.status || ""
              ).toLowerCase()
            )
          )
        ) {
          const publishActions =
            document.createElement("div");
          publishActions.className =
            "publish-actions";

          publishActions.append(
            button(
              "PUBLICAR AGORA",
              "green",
              () =>
                publishPlatform(
                  draft,
                  platform,
                  "shareNow"
                )
            ),
            button(
              "AGENDAR",
              "purple",
              () =>
                schedulePlatform(
                  draft,
                  platform
                )
            )
          );

          const queueButton =
            button(
              "ENVIAR À FILA BUFFER",
              "teal queue",
              () =>
                publishPlatform(
                  draft,
                  platform,
                  "addToQueue"
                )
            );

          publishActions.append(
            queueButton
          );

          publicationBox.append(
            publishActions
          );
        }

        if (
          publication?.bufferPostId
        ) {
          publicationBox.append(
            button(
              "ATUALIZAR STATUS",
              "gray full",
              () =>
                refreshPublication(
                  draft,
                  platform
                )
            )
          );
        }

        pcard.append(publicationBox);
        platformStack.append(pcard);
      });

      card.append(platformStack);

      const summary =
        document.createElement("div");
      summary.className = "approval-summary";

      const approved =
        ["instagram", "tiktok", "youtube"]
          .filter(p =>
            draft.assets?.[p]?.approvalStatus === "approved"
          ).length;

      const rejected =
        ["instagram", "tiktok", "youtube"]
          .filter(p =>
            draft.assets?.[p]?.approvalStatus === "rejected"
          ).length;

      const pending =
        ["instagram", "tiktok", "youtube"].length -
        approved -
        rejected;

      summary.textContent =
        "Aprovação consolidada: " +
        (draft.workflowStatus || "pending_approval") +
        " | Aprovados: " + approved +
        " | Rejeitados: " + rejected +
        " | Pendentes: " + pending;

      card.append(summary);
    } else if (
      (
        draft.type === "reel" ||
        draft.type === "video"
      ) &&
      draft.videoUrl
    ) {
      const video =
        document.createElement(
          "video"
        );

      video.src = draft.videoUrl;
      video.controls = true;
      video.preload = "metadata";
      video.playsInline = true;

      card.append(video);
    } else if (draft.imageUrl) {
      const img =
        document.createElement(
          "img"
        );

      img.src = draft.imageUrl;
      img.loading = "lazy";

      card.append(img);
    }

    if (
      draft.qualityStatus ===
      "needs_review"
    ) {
      const warning =
        document.createElement(
          "div"
        );

      warning.className = "warning";

      warning.textContent =
        "⚠ A proposta merece revisão antes da aprovação.";

      card.append(warning);
    }

    if (
      draft.renderStatus !== "ready"
    ) {
      const warning =
        document.createElement(
          "div"
        );

      warning.className = "warning";

      warning.textContent =
        "⚠ Renderização: " +
        (
          draft.renderStatus ||
          "pendente"
        );

      card.append(warning);
    }

    if (
      draft.type === "carousel" &&
      draft.renderer
    ) {
      const renderer =
        document.createElement(
          "div"
        );

      renderer.className =
        draft.renderStatus === "ready"
          ? "success"
          : "warning";

      renderer.textContent =
        "Renderer: " +
        draft.renderer;

      card.append(renderer);
    }

    if (
      (
        draft.type === "reel" ||
        draft.type === "video"
      ) &&
      draft.normalizationStatus
    ) {
      const media =
        document.createElement(
          "div"
        );

      media.className =
        draft.normalizationStatus ===
        "ready"
          ? "success"
          : "warning";

      media.textContent =
        "Media Transformations: " +
        draft.normalizationStatus;

      card.append(media);
    }

    if (
      draft.music &&
      draft.music.requested
    ) {
      const music =
        document.createElement(
          "div"
        );

      music.className = "music";

      music.textContent =
        "🎵 Música solicitada: " +
        (
          draft.music.title ||
          "sem título"
        ) +
        (
          draft.music.artist
            ? " — " +
              draft.music.artist
            : ""
        ) +
        " | Status: " +
        draft.music.status;

      card.append(music);
    }

    if (
      draft.type === "carousel" &&
      Array.isArray(draft.slides)
    ) {
      const wrap =
        document.createElement(
          "div"
        );

      wrap.className =
        "slide-list";

      draft.slides.forEach(slide => {
        const box =
          document.createElement(
            "div"
          );

        box.className = "slide";

        const b =
          document.createElement(
            "b"
          );

        b.textContent =
          "Slide " +
          slide.number +
          " — " +
          slide.headline;

        const p =
          document.createElement(
            "div"
          );

        p.style.marginTop = "6px";
        p.textContent = slide.body;

        box.append(b, p);
        wrap.append(box);
      });

      card.append(wrap);
    }

    const text =
      document.createElement(
        "div"
      );

    text.className = "text";
    text.style.marginTop = "14px";
    text.textContent =
      draft.text || "";

    card.append(text);

    const tracking =
      document.createElement("div");
    tracking.className = "tracking";
    tracking.innerHTML =
      "<b>ID:</b> " +
      escapeHtml(draft.contentId || draft.id || "") +
      "<br><b>Fluxo:</b> " +
      escapeHtml(draft.workflowStatus || "draft") +
      "<br><b>Objetivo:</b> " +
      escapeHtml(draft.objective || "não informado") +
      "<br><b>Experimento:</b> " +
      escapeHtml(draft.experimentId || "—") +
      " | <b>Variante:</b> " +
      escapeHtml(draft.variant || "—") +
      "<br><b>Intenção:</b> " +
      escapeHtml(draft.commercialIntent || "não informada") +
      "<br><b>CTA:</b> " +
      escapeHtml(draft.cta || "—");
    card.append(tracking);

    const meta =
      document.createElement(
        "div"
      );

    meta.className = "meta";

    meta.textContent =
      "Tipo: " +
      (
        draft.type || "post"
      ) +
      " | Qualidade: " +
      (
        draft.qualityStatus ||
        "normal"
      ) +
      " | Render: " +
      (
        draft.renderStatus || ""
      );

    card.append(meta);

    const local =
      document.createElement(
        "div"
      );

    local.className = "local";

    local.textContent =
      "✓ Salvo no R2 — ainda não enviado ao Buffer";

    card.append(local);

    const grid =
      document.createElement(
        "div"
      );

    grid.className = "grid";

    const editBox =
      document.createElement(
        "div"
      );

    editBox.className = "edit";

    if (
      draft.renderStatus === "ready" &&
      !(
        draft.assets &&
        typeof draft.assets === "object" &&
        Object.keys(draft.assets).length
      )
    ) {
      grid.append(
        button(
          "APROVAR",
          "blue",
          () => approve(draft)
        )
      );
    }

    grid.append(
      button(
        "AJUSTAR",
        "orange",
        () =>
          editBox.style.display =
            "block"
      ),

      button(
        "DESCARTAR",
        "red",
        () => discard(draft)
      )
    );

    card.append(grid);

    const textarea =
      document.createElement(
        "textarea"
      );

    textarea.value =
      draft.text || "";

    editBox.append(
      textarea,

      button(
        "SALVAR AJUSTE",
        "green",
        () =>
          adjust(
            draft,
            textarea.value
          )
      ),

      button(
        "CANCELAR",
        "gray",
        () =>
          editBox.style.display =
            "none"
      )
    );

    card.append(editBox);

    root.append(card);
  });
}

async function publishPlatform(
  draft,
  platform,
  mode,
  dueAt = null
) {
  const label = {
    instagram: "Instagram Reels",
    tiktok: "TikTok",
    youtube: "YouTube Shorts"
  }[platform] || platform;

  const actionText =
    mode === "shareNow"
      ? "PUBLICAR AGORA"
      : mode === "addToQueue"
        ? "ENVIAR À FILA BUFFER"
        : "AGENDAR";

  if (
    !confirm(
      actionText +
      " somente em " +
      label +
      "?\\n\\nEsta ação enviará o vídeo aprovado ao Buffer. As outras plataformas não serão afetadas."
    )
  ) return;

  const data =
    await api(
      "/api/platform-publish",
      {
        method: "POST",
        headers: {
          "content-type":
            "application/json"
        },
        body:
          JSON.stringify({
            id: draft.id,
            platform,
            mode,
            dueAt
          })
      }
    );

  if (data.ok) {
    alert(
      label +
      ": solicitação enviada ao Buffer.\\n\\nStatus: " +
      (
        data.publication?.status ||
        "submitted"
      ) +
      (
        data.publication?.dueAt
          ? "\\nAgendamento: " +
            new Date(
              data.publication.dueAt
            ).toLocaleString("pt-BR")
          : ""
      )
    );

    await load();
  } else {
    alert(
      data.error ||
      "Erro ao publicar."
    );

    await load();
  }
}

async function schedulePlatform(
  draft,
  platform
) {
  const value =
    prompt(
      "Informe data e hora local para publicação.\\n\\nFormato: AAAA-MM-DD HH:MM\\nExemplo: 2026-08-17 09:00"
    );

  if (!value) return;

  const normalized =
    value.trim().replace(" ", "T");

  const localDate =
    new Date(normalized);

  if (
    Number.isNaN(
      localDate.getTime()
    )
  ) {
    return alert(
      "Data/hora inválida."
    );
  }

  await publishPlatform(
    draft,
    platform,
    "customScheduled",
    localDate.toISOString()
  );
}

async function refreshPublication(
  draft,
  platform
) {
  const data =
    await api(
      "/api/platform-publication-status" +
      "?id=" +
      encodeURIComponent(draft.id) +
      "&platform=" +
      encodeURIComponent(platform)
    );

  if (data.ok) {
    alert(
      "Status atualizado: " +
      (
        data.publication?.status ||
        "—"
      ) +
      (
        data.publication?.externalLink
          ? "\\nPublicado: " +
            data.publication.externalLink
          : ""
      )
    );

    await load();
  } else {
    alert(
      data.error ||
      "Erro ao consultar status."
    );
  }
}

async function decidePlatform(
  draft,
  platform,
  decision
) {
  const label = {
    instagram: "Instagram Reels",
    tiktok: "TikTok",
    youtube: "YouTube Shorts"
  }[platform] || platform;

  const action =
    decision === "approved"
      ? "APROVAR"
      : "REJEITAR";

  if (
    !confirm(
      action +
      " somente a versão " +
      label +
      "?\\n\\nNenhuma publicação automática será executada."
    )
  ) return;

  const data =
    await api(
      "/api/platform-approval",
      {
        method: "POST",
        headers:{
          "content-type":
            "application/json"
        },
        body:
          JSON.stringify({
            id: draft.id,
            platform,
            decision
          })
      }
    );

  if (data.ok) {
    alert(
      label +
      ": " +
      (
        decision === "approved"
          ? "aprovado"
          : "rejeitado"
      ) +
      ".\\n\\nStatus consolidado: " +
      (
        data.workflowStatus ||
        "pending_approval"
      ) +
      "\\n\\nNenhuma publicação automática foi realizada."
    );

    await load();
  } else {
    alert(
      data.error ||
      "Erro ao registrar decisão."
    );
  }
}

async function adjust(
  draft,
  text
) {
  text = text.trim();

  if (!text) {
    return alert(
      "Legenda vazia."
    );
  }

  const data =
    await api(
      "/api/adjust",
      {
        method: "POST",

        headers:{
          "content-type":
            "application/json"
        },

        body:
          JSON.stringify({
            id: draft.id,
            text
          })
      }
    );

  if (data.ok) {
    alert(
      "Ajuste salvo no R2."
    );

    await load();
  } else {
    alert(
      data.error ||
      "Erro ao ajustar"
    );
  }
}

async function approve(draft) {
  let message =
    "Enviar esta publicação ao Buffer e colocar na próxima vaga da fila?";

  if (draft.type === "carousel") {
    message =
      "Enviar este carrossel completo ao Buffer em uma única publicação?";
  }

  if (
    draft.type === "reel" ||
    draft.type === "video"
  ) {
    message =
      "Enviar este vídeo ao Buffer?";
  }

  if (!confirm(message)) return;

  if (
    draft.music &&
    draft.music.requested
  ) {
    alert(
      "A música está registrada no rascunho, mas ainda NÃO será anexada automaticamente. O binding Media Transformations normaliza/extrai áudio, mas não seleciona uma música da biblioteca do Instagram. O Buffer será acionado sem essa faixa."
    );
  }

  const data =
    await api(
      "/api/approve",
      {
        method: "POST",

        headers:{
          "content-type":
            "application/json"
        },

        body:
          JSON.stringify({
            id: draft.id
          })
      }
    );

  if (data.ok) {
    const when =
      data.post?.dueAt
        ? new Date(
            data.post.dueAt
          ).toLocaleString(
            "pt-BR"
          )
        : "próxima vaga";

    alert(
      "Aprovado e enviado ao Buffer!\\n\\nPublicação: " +
      when
    );

    await load();
  } else {
    alert(
      data.error ||
      "Erro ao aprovar"
    );
  }
}

async function discard(draft) {
  if (
    !confirm(
      (
        draft.assets && Object.keys(draft.assets).length
          ? "Descartar TODO este conteúdo e os três masters (Instagram, TikTok e YouTube) definitivamente?"
          : "Descartar este rascunho e todas as mídias relacionadas definitivamente?"
      )
    )
  ) return;

  const data =
    await api(
      "/api/discard",
      {
        method: "POST",

        headers:{
          "content-type":
            "application/json"
        },

        body:
          JSON.stringify({
            id: draft.id
          })
      }
    );

  if (data.ok) {
    alert(
      "Rascunho descartado."
    );

    await load();
  } else {
    alert(
      data.error ||
      "Erro ao descartar"
    );
  }
}

</script>

</body>
</html>`;


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

