// ───────────────────────────────────────────────────────────────
// NEDERLANDS: vertaalt alle zichtbare tekst van de interface.
// Vaste woorden/labels via een woordenlijst (hele tekst-node), plus
// patronen voor tekst met getallen. Logica-waarden blijven Engels.
// ───────────────────────────────────────────────────────────────
const D: Record<string, string> = {
  // navigatie & algemeen
  'Projects': 'Projecten', 'Agents': 'Agents', 'Channels': 'Kanalen', 'Analytics': 'Statistieken', 'Threads': 'Threads',
  'Finances': 'Financiën', 'War Room': 'Crisiskamer', 'Upgrades': 'Upgrades', 'Achievements': 'Prestaties', 'Settings': 'Instellingen',
  'Company rank': 'Bedrijfsrang', 'XP': 'XP', 'Notifications': 'Meldingen', 'Mark all read': 'Alles gelezen', 'All caught up.': 'Je bent helemaal bij.',
  'Total views': 'Totaal weergaven', 'Balance': 'Saldo', 'Reputation': 'Reputatie', 'Skip 1 day': '1 dag overslaan', 'Resume simulation': 'Simulatie hervatten',
  'Pause simulation': 'Simulatie pauzeren', 'Skipped ahead one day.': 'Een dag vooruitgespoeld.', 'Cancel': 'Annuleren', 'Close': 'Sluiten',
  'DEMO DATA': 'DEMODATA', 'DEMO': 'DEMO', 'INCLUDES DEMO DATA': 'BEVAT DEMODATA', 'LOCAL SIMULATION': 'LOKALE SIMULATIE', 'INTERNAL · SIMULATED': 'INTERN · GESIMULEERD',
  'Start New Video': 'Nieuwe video starten', 'Assign Task': 'Taak geven', 'Hire Agent': 'Agent aannemen', 'Upgrade Office': 'Kantoor upgraden',
  '🎬 Start New Video': '🎬 Nieuwe video starten', '👋 Hire AI Agent': '👋 AI-agent aannemen', '📋 Assign Task': '📋 Taak geven', '📺 Launch New Channel': '📺 Nieuw kanaal starten', '📊 Reports': '📊 Rapporten',
  'CEO Dashboard': 'CEO-dashboard', 'Office Upgrades': 'Kantoor-upgrades', 'Achievements & Missions': 'Prestaties & missies', 'YouTube Channels': 'YouTube-kanalen', 'AI Agents': 'AI-agents',
  // statussen & prioriteit
  'Pending': 'Wachtend', 'Assigned': 'Toegewezen', 'In Progress': 'Bezig', 'Review': 'Controle', 'Approved': 'Goedgekeurd', 'Rejected': 'Afgekeurd', 'Completed': 'Afgerond',
  'Low': 'Laag', 'Medium': 'Normaal', 'High': 'Hoog', 'Critical': 'Kritiek', 'Active': 'Actief', 'Awaiting Approval': 'Wacht op goedkeuring', 'Awaiting Publish': 'Klaar om te publiceren',
  'Published': 'Gepubliceerd', 'Cancelled': 'Gestopt', 'idle': 'vrij', 'working': 'aan het werk', 'meeting': 'in overleg', 'training': 'in training',
  'Idle': 'Vrij', 'Working': 'Aan het werk', 'Meeting': 'In overleg', 'Training': 'In training', 'Investigating': 'Onderzoek loopt', 'Ready': 'Klaar', 'Resolved': 'Opgelost', 'Dismissed': 'Afgewezen',
  // afdelingen & stappen
  'Research': 'Onderzoek', 'Creative': 'Creatief', 'Script': 'Script', 'Voice': 'Stem', 'Production': 'Productie', 'Thumbnail': 'Thumbnail', 'Publishing': 'Publicatie',
  'CEO & Analytics': 'CEO & statistieken', 'Research Department': 'Onderzoeksafdeling', 'Creative Department': 'Creatieve afdeling', 'Script Department': 'Scriptafdeling',
  'Voice Department': 'Stemafdeling', 'Production Department': 'Productieafdeling', 'Thumbnail Department': 'Thumbnailafdeling', 'Publishing Department': 'Publicatieafdeling', 'CEO & Analytics Department': 'CEO & statistiekafdeling',
  'Topic Selection': 'Onderwerp kiezen', 'Titles & Hooks': 'Titels & hooks', 'Scriptwriting': 'Script schrijven', 'Fact Checking': 'Feiten checken', 'Voice-over': 'Voice-over',
  'Video Editing': 'Animatie & montage', 'Quality Control': 'Kwaliteitscheck', 'CEO Approval': 'Goedkeuring niels',
  // rollen
  'Researcher': 'Onderzoeker', 'Niche Analyst': 'Niche-analist', 'Competitor Analyst': 'Concurrentie-analist', 'Topic Finder': 'Onderwerpzoeker', 'Idea Generator': 'Ideeënbedenker',
  'Title Specialist': 'Titelspecialist', 'Hook Specialist': 'Hook-specialist', 'Scriptwriter': 'Scriptschrijver', 'Storytelling Expert': 'Verhaalexpert', 'Fact Checker': 'Feitenchecker',
  'Quality Controller': 'Kwaliteitscontroleur', 'Voice Director': 'Stemregisseur', 'Voice Generator': 'Stemmenmaker', 'Video Editor': 'Animator/editor', 'Visual Researcher': 'Beeldresearcher',
  'Editing Supervisor': 'Montagechef', 'Thumbnail Designer': 'Thumbnailontwerper', 'CTR Specialist': 'CTR-specialist', 'Upload Manager': 'Uploadmanager', 'SEO Specialist': 'SEO-specialist',
  'Social Media Manager': 'Socialemediamanager', 'CEO Agent': 'CEO-agent', 'Financial Manager': 'Financieel manager', 'Performance Analyst': 'Prestatie-analist',
  'Attention to Detail': 'Oog voor detail', 'in meetings': 'in overleg', '⏳ Waiting for you (': '⏳ Wacht op jou (', 'Publish': 'Publiceren', 'Garage Startup': 'Garagebedrijf', 'Growing Studio': 'Groeiende studio', 'DEMO DATA ': 'DEMODATA',
  // crisiskamer
  'Declining Views': 'Dalende weergaven', 'Low CTR': 'Lage CTR', 'Poor Retention': 'Slechte kijkduur', 'Production Delays': 'Productievertraging', 'Falling Revenue': 'Dalende inkomsten',
  'Problem': 'Probleem', 'Scope': 'Bereik', 'Convene War Room': 'Crisiskamer bijeenroepen', 'Approve plan': 'Plan goedkeuren', '✓ Approved by CEO': '✓ Goedgekeurd door niels', 'Dismiss case': 'Zaak sluiten',
  'Hire a CEO Agent, Performance Analyst or Financial Manager first.': 'Neem eerst een CEO-agent, prestatie-analist of financieel manager aan.',
  'No cases yet. Pick a problem above and convene the War Room.': 'Nog geen zaken. Kies hierboven een probleem en roep de crisiskamer bijeen.',
  'Agents are gathering data in the War Room…': 'Agents verzamelen data in de crisiskamer…', 'Approve recommendation?': 'Aanbeveling goedkeuren?',
  'Management agents investigate problems and prepare recommendations. Nothing is executed without your approval.': 'Management-agents onderzoeken problemen en maken aanbevelingen. Niets gebeurt zonder jouw goedkeuring.',
  'War Room convened — analysis in ~6 hours (game time).': 'Crisiskamer bijeengeroepen. Analyse over ~6 uur (speltijd).',
  'The executive crisis room. Management agents investigate declining metrics and bring recommendations for your approval.': 'De crisiskamer. Management-agents onderzoeken dalende cijfers en leggen aanbevelingen aan jou voor.',
  'No active cases. Convene the War Room to investigate a problem.': 'Geen open zaken. Roep de crisiskamer bijeen om een probleem te onderzoeken.', 'Open War Room dashboard': 'Crisiskamer openen',
  // modals
  'Greenlight project': 'Project starten', 'Channel': 'Kanaal', 'Topic': 'Onderwerp', 'Working title': 'Werktitel', 'Priority': 'Prioriteit', 'Deadline (game days)': 'Deadline (speldagen)',
  'The project enters the pipeline at': 'Het project begint bij', 'and flows through all 11 stages. You\'ll be asked to approve it at': 'en gaat door alle 11 stappen. Je keurt het goed bij',
  'and to confirm before': 'en bevestigt vóór', 'Assign': 'Toewijzen', 'Title': 'Titel', 'Description / instructions': 'Beschrijving / instructies', 'Assigned agent': 'Agent',
  'Deadline (days)': 'Deadline (dagen)', 'Link to project': 'Koppel aan project', '— none —': '— geen —', 'Depends on': 'Hangt af van', '— no dependency —': '— niets —',
  'Assign to channel': 'Toewijzen aan kanaal', 'All channels': 'Alle kanalen', 'All desks are taken. Buy an Office Expansion upgrade to hire more agents.': 'Alle bureaus zijn bezet. Koop de upgrade Kantooruitbreiding om meer agents aan te nemen.',
  'Create channel': 'Kanaal maken', 'Channel name': 'Kanaalnaam', 'Logo': 'Logo', 'Color': 'Kleur', 'Niche': 'Niche', 'Target audience': 'Doelgroep', 'Expected RPM (€)': 'Verwachte RPM (€)',
  'Uploads per week': 'Uploads per week', 'This creates a simulated channel. Linking a real YouTube channel requires the YouTube Data API (see Settings).': 'Dit maakt een gesimuleerd kanaal. Een echt YouTube-kanaal koppelen kan via de YouTube Data API (zie Instellingen).',
  "What's the video about?": 'Waar gaat de video over?', 'Ask Research for a suggestion': 'Vraag Onderzoek om een idee', 'e.g. Analyse top 10 competitor videos': 'bv. Analyseer de top 10 IFOLOGY-video\'s',
  'General audience': 'Algemeen publiek', 'e.g. Personal finance explainers': 'bv. 3D What If-shorts', 'e.g. 22–40, US/EU, beginner investors': 'bv. 13-24, wereldwijd', 'e.g. Money Mechanics': 'bv. Driftmark Extra',
  // agent
  'Level': 'Niveau', 'Performance': 'Prestatie', 'Morale': 'Moraal', 'Assign task': 'Taak geven', 'Remove': 'Ontslaan', 'Save instructions': 'Instructies opslaan', 'Share to Threads': 'Delen op Threads',
  'No AI model connected — output is simulated. Add a Claude or OpenAI key in Settings for real results.': 'Geen AI-model gekoppeld, de uitvoer is gesimuleerd. Echte opdrachten lopen via Driftmark HQ.',
  'No tasks yet.': 'Nog geen taken.', 'Agent profile': 'Agentprofiel', 'This agent will leave the company permanently. Their open tasks return to the queue. This cannot be undone.': 'Deze agent verlaat het bedrijf. Open taken gaan terug in de wachtrij. Dit kan niet ongedaan worden.',
  'Remove agent': 'Agent ontslaan', 'Busy with a task': 'Bezig met een taak', 'Instructions (system prompt)': 'Instructies (werkregels)', 'Instructions saved.': 'Instructies opgeslagen.',
  'Channel assignment': 'Kanaal', 'Current task': 'Huidige taak', 'In training.': 'In training.', 'Idle — waiting for work.': 'Vrij, wacht op werk.',
  // afdeling & project
  'Assign department to channel…': 'Afdeling aan kanaal koppelen…', 'Pending CEO approvals': 'Wacht op jouw goedkeuring', 'Nothing waiting for you.': 'Er wacht niets op je.',
  'No active work in this stage.': 'Geen werk in deze stap.', 'Recently delivered': 'Net opgeleverd', 'Assigned tasks': 'Toegewezen taken', 'Team': 'Team', 'Open tasks': 'Open taken', 'Avg quality': 'Gem. kwaliteit',
  'Quality': 'Kwaliteit', 'Cost': 'Kosten', 'Rejections': 'Afkeuringen', 'Tasks': 'Taken', 'CEO approval required': 'Jouw goedkeuring nodig',
  'Review the deliverables below. Approve to move to Publishing, or send it back to a department with feedback.': 'Bekijk het werk hieronder. Keur goed voor publicatie, of stuur het terug met feedback.',
  'Approve': 'Goedkeuren', 'Send back': 'Terugsturen', 'Ready to publish': 'Klaar om te publiceren',
  'Publishing requires your explicit confirmation. YouTube is not connected, so the upload is simulated locally.': 'Publiceren vraagt jouw bevestiging. Claude maakt titel, beschrijving, tags en thumbnail klaar; uploaden doe je zelf in YouTube Studio.',
  'Publish…': 'Publiceren…', 'Views': 'Weergaven', 'Revenue': 'Inkomsten', 'Tasks & deliverables': 'Taken & opleveringen', 'Timeline': 'Tijdlijn', 'Publish this video?': 'Deze video publiceren?',
  'Feedback for the department…': 'Feedback voor de afdeling…', 'CEO requested revisions': 'niels wil aanpassingen', 'Cancel project?': 'Project stoppen?', 'Cancel project': 'Project stoppen',
  '· overdue': '· te laat', 'Created:': 'Gemaakt:', 'Deadline:': 'Deadline:', 'Quality:': 'Kwaliteit:', 'Kind:': 'Soort:', 'Documents': 'Documenten', 'Send': 'Versturen',
  'Approve deliverable': 'Oplevering goedkeuren', 'Request changes': 'Aanpassingen vragen', 'Reassign to…': 'Overdragen aan…', 'Open agent': 'Agent openen', 'Former agent': 'Oud-agent',
  'Leave feedback for the agent…': 'Feedback voor de agent…', 'Deliverable': 'Oplevering', 'Project': 'Project',
  // pagina's
  'Company level': 'Bedrijfsniveau', 'Company reputation': 'Reputatie', 'Daily missions': 'Dagelijkse missies', 'refresh every game day': 'nieuw elke speldag',
  'Hire agent': 'Agent aannemen', 'All': 'Alle', "Open roles you haven't hired yet": 'Open rollen die je nog niet hebt', 'Search agents…': 'Agents zoeken…',
  'Subs': 'Abonnees', 'Videos': "Video's", 'Top videos': "Topvideo's", 'Active agents': 'Actieve agents', 'Active projects': 'Actieve projecten', 'Pending approvals': 'Wacht op goedkeuring',
  'Revenue vs expenses (€ / day)': 'Inkomsten vs. uitgaven (€ per dag)', 'Views per day': 'Weergaven per dag', 'Channel performance (views/day)': 'Kanaalprestaties (weergaven per dag)',
  'Production performance by stage': 'Productie per stap', 'Average quality by stage': 'Gem. kwaliteit per stap', 'CTR & AVD trend (%)': 'CTR & kijkduur (%)', 'CTR (7d)': 'CTR (7 d)', 'AVD (7d)': 'Kijkduur (7 d)',
  'AVD': 'Kijkduur', 'Subscribers': 'Abonnees', 'Expenses': 'Uitgaven', 'Income': 'Inkomsten', 'Profit': 'Winst', 'Break-even': 'Break-even', 'Monthly P&L': 'Maandresultaat',
  'New channel': 'Nieuw kanaal', '💸 Monetized': '💸 Inkomsten aan', 'New video': 'Nieuwe video', 'No projects yet for this channel.': 'Nog geen projecten voor dit kanaal.', '(demo)': '(demo)',
  'Channel profile': 'Kanaalprofiel', 'Edit': 'Bewerken', 'Save': 'Opslaan', 'Uploads / week': 'Uploads per week', 'Agents not assigned to a specific channel work for all channels.': 'Agents zonder vast kanaal werken voor alle kanalen.',
  'Assign a whole department': 'Hele afdeling koppelen', 'Simulated channels. Each has its own niche, audience, schedule, projects and dedicated agents.': 'Gesimuleerde kanalen, elk met eigen niche, publiek, schema, projecten en agents.',
  'New subs': 'Nieuwe abonnees', 'Channel updated.': 'Kanaal bijgewerkt.', 'Upload schedule': 'Uploadschema', 'Assign department': 'Afdeling koppelen',
  'All channels (incl. company overhead)': 'Alle kanalen (incl. vaste kosten)', 'All months': 'Alle maanden',
  'Channel view shows only costs and revenue attributed to this channel; salaries, subscriptions and software are company overhead.': 'Per kanaal zie je alleen de kosten en inkomsten van dat kanaal; salarissen, abonnementen en software zijn vaste kosten.',
  'No expenses in this period.': 'Geen uitgaven in deze periode.', 'Categories': 'Categorieën', 'Video ROI': 'Rendement per video', 'Publish a video to track its ROI.': 'Publiceer een video om het rendement te zien.',
  'Date': 'Datum', 'Category': 'Categorie', 'Note': 'Notitie', 'Amount': 'Bedrag', 'Profit margin': 'Winstmarge', 'Expense breakdown': 'Uitgaven per soort',
  'Ad Revenue': 'Advertentie-inkomsten', 'Salaries': 'Salarissen', 'Freelancers': 'Freelancers', 'AI Subscriptions': 'AI-abonnementen', 'Software': 'Software', 'Hiring': 'Aannemen', 'Rewards': 'Beloningen',
  'Building the office…': 'Kantoor wordt gebouwd…', 'Click a room to open its dashboard · click an employee for their profile · drag to rotate, scroll to zoom': 'Klik op een kamer voor het dashboard · klik op een medewerker voor het profiel · sleep om te draaien, scroll om te zoomen',
  'Production pipeline': 'Productielijn', 'All projects →': 'Alle projecten →', 'No active projects. Start a new video!': 'Geen actieve projecten. Start een nieuwe video!',
  'Live on Threads': 'Live op Threads', 'Open →': 'Openen →', 'Waiting for you': 'Wacht op jou',
  'Empty': 'Leeg', 'No projects yet.': 'Nog geen projecten.', 'Every video moves through the 11-stage production pipeline. Rejected work loops back to the responsible department.': 'Elke video gaat door de productielijn van 11 stappen. Afgekeurd werk gaat terug naar de afdeling die het maakte.',
  'Pipeline board': 'Productiebord', 'All projects': 'Alle projecten', 'Task engine': 'Takenlijst',
  'Integration status': 'Koppelingen', 'API credentials': 'API-sleutels', 'Agent AI provider': 'AI voor agents', 'Local simulation (no API)': 'Lokale simulatie (geen API)',
  'Anthropic API key': 'Anthropic API-sleutel', 'Claude model': 'Claude-model', 'OpenAI API key': 'OpenAI API-sleutel', 'OpenAI model': 'OpenAI-model', 'YouTube Data API key (read-only stats)': 'YouTube Data API-sleutel (alleen stats lezen)',
  'Threads access token': 'Threads-token', 'Voice API key': 'Stem-API-sleutel', 'Supabase anon key': 'Supabase anon-sleutel', 'Save settings': 'Instellingen opslaan', 'YouTube Data API test (read-only)': 'YouTube Data API-test (alleen lezen)',
  'Fetch': 'Ophalen', 'Save data': 'Opslag', 'Export save (keys stripped)': 'Opslag exporteren (zonder sleutels)', 'Import save': 'Opslag importeren', 'Save to Supabase': 'Opslaan in Supabase', 'Load from Supabase': 'Laden uit Supabase',
  'Progress autosaves to this browser. Supabase requires the table in': 'Voortgang wordt in deze browser bewaard. Supabase heeft de tabel nodig uit', 'Danger zone': 'Gevarenzone', 'Reset game': 'Game resetten',
  'Integrations, data and simulation.': 'Koppelingen, data en simulatie.', 'Settings saved locally.': 'Instellingen lokaal opgeslagen.', 'Not a valid save file': 'Geen geldig opslagbestand', 'Import save?': 'Opslag importeren?',
  'Replace progress': 'Voortgang vervangen', 'Saved to Supabase.': 'Opgeslagen in Supabase.', 'Loaded from Supabase.': 'Geladen uit Supabase.', 'No cloud save found.': 'Geen cloudopslag gevonden.',
  'Reset the whole company?': 'Hele bedrijf resetten?', 'All progress, agents, channels and history will be permanently replaced with a fresh demo company. This cannot be undone.': 'Alle voortgang, agents, kanalen en geschiedenis worden vervangen door een nieuwe start. Dit kan niet ongedaan worden.',
  'Reset everything': 'Alles resetten', 'Company reset to demo state.': 'Bedrijf opnieuw gestart.',
  'External publishing (YouTube, Threads) is never performed automatically. Publishing in this game always stays in the local simulation and requires your explicit confirmation.': 'Er wordt nooit automatisch iets op YouTube of Threads gezet. Uploaden doe je altijd zelf; Claude maakt alles klaar.',
  "Keys are stored only in this browser's local storage and sent directly to the provider you choose. Use restricted keys and never share your save file if it contains keys.": 'Sleutels worden alleen in deze browser bewaard en direct naar de gekozen dienst gestuurd. Deel je opslagbestand nooit als er sleutels in staan.',
  'Internal company social network': 'Intern sociaal netwerk', 'Visible to all agents · never posted externally': 'Zichtbaar voor alle agents · je berichten gaan als opdracht naar Claude',
  'Post': 'Plaatsen', 'Share': 'Delen', 'Reply': 'Reageren', 'Reply…': 'Reageer…', 'Most active': 'Meest actief', 'About this feed': 'Over deze feed', 'not connected': 'niet gekoppeld', 'but is': 'maar is',
  'for the real Meta Threads API is prepared in': 'voor de echte Meta Threads-API staat klaar in', 'Feedback loop': 'Feedbacklus', 'Post an update to the whole company…': 'Plaats een bericht voor het hele team…',
  'For you': 'Voor jou', 'Shared with the whole company.': 'Gedeeld met het hele team.', 'Maxed out': 'Maximaal', 'Update': 'Update', 'Report': 'Rapport', 'Question': 'Vraag', 'Win': 'Succes', 'Hand-off': 'Overdracht', 'Alert': 'Waarschuwing',
  'Upgrade': 'Upgraden', 'About': 'Over', 'Approval Memo': 'Goedkeuringsnotitie', 'Upload Package': 'Uploadpakket', 'Task Brief': 'Opdracht', 'Publish (simulation)': 'Publiceren',
  // upgrades & prestaties
  'Render Farm': 'Renderfarm', 'Coffee Bar': 'Koffiebar', 'Office Expansion': 'Kantooruitbreiding', 'Neon Lighting Pack': 'Neonverlichting', 'Glass Meeting Pods': 'Glazen vergaderhokjes', 'Training Lab': 'Trainingslab', 'Sound Studio': 'Geluidsstudio',
  'GPU racks for the edit bay.': 'GPU-rekken voor de montage.', 'Espresso for everyone. Morale stays high.': 'Espresso voor iedereen. Moraal blijft hoog.', 'More desks, more agents.': 'Meer bureaus, meer agents.',
  'Instagrammable office. Boosts reputation.': 'Fotogeniek kantoor. Meer reputatie.', 'Faster reviews, fewer rejections.': 'Snellere controles, minder afkeuringen.', 'VR training stations.': 'VR-trainingsplekken.', 'Acoustic booth for the voice team.': 'Geluidscabine voor het stemteam.',
  '+15% production speed per level': '+15% productiesnelheid per niveau', '+8 morale recovery per level': '+8 moraalherstel per niveau', '+6 agent slots per level': '+6 bureaus per niveau', '+10 reputation': '+10 reputatie',
  '+6 review quality per level': '+6 controlekwaliteit per niveau', '−25% training cost and time per level': '−25% trainingskosten en -tijd per niveau', '+8 voice quality per level': '+8 stemkwaliteit per niveau',
  'First Upload': 'Eerste upload', '100K Views': '100K weergaven', 'Millionaire Views': 'Miljoen weergaven', 'Monetized!': 'Inkomsten aan!', 'First €1,000': 'Eerste €1.000', 'Growing Team': 'Groeiend team',
  'Interior Designer': 'Interieurontwerper', 'Crisis Manager': 'Crisismanager', 'Rising Company': 'Groeiend bedrijf', 'Network Builder': 'Netwerkbouwer', 'Elite Employee': 'Topmedewerker', 'Content Machine': 'Contentmachine', 'Full House': 'Vol huis',
  'Publish your first video.': 'Publiceer je eerste video.', 'Reach 100,000 total views across all channels.': 'Haal 100.000 weergaven over alle kanalen.', 'Reach 1,000,000 total views.': 'Haal 1.000.000 weergaven.',
  'Get your first channel monetized (1,000 subscribers).': 'Zet de inkomsten van je eerste kanaal aan (1.000 abonnees).', 'Earn €1,000 in total ad revenue.': 'Verdien in totaal €1.000 aan advertenties.', 'Hire your first new AI agent.': 'Neem je eerste nieuwe AI-agent aan.',
  'Buy your first office upgrade.': 'Koop je eerste kantoor-upgrade.', 'Resolve your first War Room case.': 'Los je eerste crisiskamer-zaak op.', 'Reach company level 5.': 'Haal bedrijfsniveau 5.', 'Launch a new channel of your own.': 'Start een eigen nieuw kanaal.', 'Train an agent to level 5.': 'Train een agent tot niveau 5.',
  'Post an update on Threads': 'Plaats een bericht op Threads', 'Train an agent': 'Train een agent',
  // adapters
  'Agent reasoning & text deliverables': 'Denkwerk en tekst van agents', 'Agents use the local simulation for text output.': 'Agents gebruiken de lokale simulatie voor tekst.', 'Read channel statistics': 'Kanaalstatistieken lezen',
  'Read-only. Uploading is not implemented; publishing is simulated locally.': 'Alleen lezen. Uploaden doe je zelf in YouTube Studio.', 'Cross-post internal updates': 'Interne berichten doorplaatsen',
  'Adapter interface only. The internal Threads feed is simulated and never posts externally.': 'Alleen de koppeling. De interne Threads-feed plaatst nooit iets extern.', 'Voice generation': 'Stemmen maken',
  'Interface prepared. Voice-over stage outputs simulated metadata.': 'Koppeling klaar. Echte stemmen maakt Claude in ElevenLabs v4.', 'Image generation': 'Beelden maken',
  'Interface prepared. Thumbnail stage outputs simulated variants.': 'Koppeling klaar. Echte thumbnails maakt Claude op opdracht.', 'Video production': 'Videoproductie',
  'Interface prepared. Editing stage outputs simulated renders.': 'Koppeling klaar. Echte animatie gebeurt in Blender op je pc.', 'Cloud saves': 'Cloudopslag', 'Save data is in local browser storage until you configure Supabase.': 'Opslag staat in deze browser tot je Supabase instelt.',
  'Claude / OpenAI models': 'Claude- / OpenAI-modellen',
};

const P: [RegExp, (...m: string[]) => string][] = [
  [/^(\d+) working$/, (_, n) => `${n} aan het werk`], [/^(\d+) in meetings$/, (_, n) => `${n} in overleg`], [/^(\d+) idle$/, (_, n) => `${n} vrij`],
  [/^just now$/, () => 'zojuist'], [/^(\d+)h ago$/, (_, n) => `${n} u geleden`], [/^(\d+)d ago$/, (_, n) => `${n} d geleden`],
  [/^(\d+) completed$/, (_, n) => `${n} afgerond`], [/^Task history · (\d+) completed$/, (_, n) => `Takengeschiedenis · ${n} afgerond`],
  [/^Day (\d+)/, (_, n) => `Dag ${n}`], [/^(\d+)d$/, (_, n) => `${n} d`],
  [/^⏳ Waiting for you \((\d+)\)$/, (_, n) => `⏳ Wacht op jou (${n})`], [/^Start (\d+) new videos?$/, (_, n) => `Start ${n} nieuwe video${n === '1' ? '' : "'s"}`],
  [/^Like (\d+) Threads posts$/, (_, n) => `Like ${n} Threads-berichten`], [/^Complete (\d+) tasks company-wide$/, (_, n) => `Rond ${n} taken af`],
  [/^(\d+)\/(\d+) achievements unlocked$/, (_, a, b) => `${a}/${b} prestaties behaald`], [/^Needs (.*)× current income$/, (_, n) => `Vraagt ${n}× de huidige inkomsten`], [/^No revenue yet$/, () => 'Nog geen inkomsten'],
  [/^(\d+)\/(\d+) desks filled · payroll ≈ (.*)\/day$/, (_, a, b, c) => `${a}/${b} bureaus bezet · loonkosten ≈ ${c}/dag`],
  [/^Level (\d+)$/, (_, n) => `Niveau ${n}`], [/^L(\d+)$/, (_, n) => `N${n}`],
];

const ATTRS = ['placeholder', 'title', 'aria-label'];
function tr(s: string): string | null {
  const t = s.trim(); if (!t) return null;
  const d = D[t];
  if (d !== undefined) return d === t ? null : s.replace(t, d);
  for (const [re, f] of P) { const m = t.match(re); if (m) { const out = t.replace(re, f as (...a: string[]) => string); return out === t ? null : s.replace(t, out); } }
  return null;
}
function walk(n: Node) {
  if (n.nodeType === 3) { const r = tr(n.nodeValue || ''); if (r !== null && r !== n.nodeValue) n.nodeValue = r; return; }
  if (n.nodeType !== 1) return;
  const el = n as Element;
  if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE' || el.tagName === 'TEXTAREA') return;
  for (const a of ATTRS) { const v = el.getAttribute(a); if (v) { const r = tr(v); if (r !== null && r !== v) el.setAttribute(a, r); } }
  n.childNodes.forEach(walk);
}
export function startDutch(root: HTMLElement) {
  document.documentElement.lang = 'nl';
  walk(root);
  new MutationObserver((ms) => {
    for (const m of ms) {
      if (m.type === 'characterData') walk(m.target);
      else if (m.type === 'attributes') walk(m.target);
      else m.addedNodes.forEach(walk);
    }
  }).observe(root, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ATTRS });
}
