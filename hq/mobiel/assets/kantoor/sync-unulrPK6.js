import { u as b, b as A, d as w, e as O } from "./kantoor-mobiel-D8nsu0GD.js";
const x = [
  [/thumbnail|banner|branding/i, "thumbnail_designer"],
  [/titel|beschrijving|tags/i, "seo_specialist"],
  [/stem|voice/i, "voice_generator"],
  [/animeer|render|montage/i, "video_editor"],
  [/cast|sets|personage|bouw/i, "visual_researcher"],
  [/short/i, "social_media_manager"],
  [/script|schrijf|verloop/i, "scriptwriter"],
  [/idee|bedenk/i, "idea_generator"],
  [/analyse|kijkers|weergaven|groei/i, "performance_analyst"],
  [/hq|werkwijze|koppel/i, "ceo_agent"]
], E = (i) => {
  var s;
  return ((s = x.find(([n]) => n.test(i))) == null ? void 0 : s[1]) ?? "researcher";
}, q = { working: "working", blocked: "meeting", review_ready: "meeting", done: "idle" }, R = {
  Idee: "research",
  Verloop: "topic",
  Script: "script",
  Stemmen: "voice",
  Cast: "editing",
  Sets: "editing",
  Animatie: "editing",
  Render: "editing",
  Montage: "qc",
  "Upload-tekst": "thumbnail",
  Shorts: "approval",
  Online: "publishing"
}, y = ["research", "topic", "titles", "script", "factcheck", "voice", "editing", "thumbnail", "qc", "approval", "publishing"];
let m = "", o = null;
function P() {
  try {
    if (o = o ?? new AudioContext(), o.state !== "running") return;
    const i = o.createOscillator(), s = o.createGain();
    i.frequency.value = 880, s.gain.setValueAtTime(0.06, o.currentTime), s.gain.exponentialRampToValueAtTime(1e-4, o.currentTime + 0.35), i.connect(s).connect(o.destination), i.start(), i.stop(o.currentTime + 0.35);
  } catch {
  }
}
typeof window < "u" && window.addEventListener("pointerdown", () => {
  try {
    o = o ?? new AudioContext(), o.resume();
  } catch {
  }
}, { once: !0 });
function M(i) {
  var k;
  const s = b.getState(), n = A(), _ = JSON.stringify(i.activity.map((e) => [e.id, e.state, e.doing])), g = m ? JSON.parse(m) : null, d = [];
  if (g)
    for (const e of i.activity) {
      const t = g.find((r) => r[0] === e.id);
      t ? t[1] !== e.state ? d.push(e.state === "blocked" ? `⏳ ${e.title} wacht op jou` : e.state === "review_ready" ? `👀 ${e.title} is klaar voor controle` : e.state === "done" ? `✅ ${e.title} is klaar` : `▶️ ${e.title} is weer aan het werk`) : t[2] !== e.doing && e.doing && d.push(`📌 ${e.title}: ${e.doing}`) : d.push(`🆕 Nieuw aan het werk: ${e.title}`);
    }
  m = _;
  const h = i.activity.map((e) => {
    const t = s.agents.find((l) => l.id === e.id), r = E(e.title), p = t ?? w(r, 0, { name: e.title });
    return { ...p, id: e.id, name: e.title, role: r, department: w(r, 0).department, state: q[e.state] ?? "idle", currentTaskId: e.state === "done" ? null : `task_${e.id}`, personality: e.doing ?? "", instructions: `Echte thread in het project. Laatst actief ${e.last}.`, avatar: { ...p.avatar, initials: e.title.split(" ").slice(0, 2).map((l) => {
      var c;
      return ((c = l[0]) == null ? void 0 : c.toUpperCase()) ?? "";
    }).join("") } };
  }), v = i.activity.map((e) => ({
    id: `task_${e.id}`,
    title: e.doing || e.title,
    description: `${e.title} · laatst actief ${e.last}`,
    agentId: e.id,
    projectId: null,
    stage: null,
    kind: "manual",
    priority: e.state === "blocked" ? "High" : "Medium",
    status: e.state === "done" ? "Completed" : e.state === "working" ? "In Progress" : "Review",
    progress: e.state === "done" ? 100 : e.state === "working" ? 50 : 90,
    createdTick: n,
    deadlineTick: n + 24,
    dependencies: [],
    comments: [],
    documents: [],
    result: null,
    quality: null,
    revision: 0
  })), $ = i.videos.map((e) => {
    const t = e.steps.find((c) => !c.done), r = t ? R[t.label] ?? "editing" : "publishing", p = y.indexOf(r), l = e.status === "Online" ? "Published" : e.status === "Klaar" ? "Awaiting Publish" : "Active";
    return {
      id: `real_v${e.nr}`,
      title: e.title,
      topic: e.werktitel,
      channelId: "ch_history",
      stage: r,
      status: l,
      createdTick: 0,
      deadlineTick: n + 168,
      priority: e.status === "In productie" ? "High" : "Medium",
      taskIds: [],
      stageQuality: Object.fromEntries(y.slice(0, Math.max(0, p)).map((c) => [c, 80])),
      rejections: 0,
      cost: 0,
      history: e.notes.map((c) => ({ tick: n, text: c }))
    };
  }), f = s.projects.filter((e) => !e.id.startsWith("real_") && !e.history.some((t) => t.text.includes("(demo)"))), T = i.activity.filter((e) => e.doing).map((e) => {
    var t;
    return { id: `post_${e.id}`, authorId: e.id, department: (t = h.find((r) => r.id === e.id)) == null ? void 0 : t.department, kind: e.state === "blocked" ? "question" : e.state === "done" ? "celebration" : "update", content: e.doing, tick: n, likes: [], comments: [] };
  }), I = s.posts.filter((e) => e.authorId === "player"), a = i.youtube, j = (k = a == null ? void 0 : a.videos) != null && k.length ? a.videos.map((e, t) => ({ id: `ytv_${t}`, projectId: "real", channelId: e.type === "short" ? "ch_science" : "ch_history", title: e.title, publishedTick: n, quality: 0, ctr: 0, avd: 0, views: e.views ?? 0, revenue: 0, likes: 0 })) : i.videos.filter((e) => e.status === "Online").map((e) => ({ id: `real_vid${e.nr}`, projectId: `real_v${e.nr}`, channelId: "ch_history", title: e.title, publishedTick: n, quality: 0, ctr: 0, avd: e.nr === 1 ? 26.3 : 0, views: e.nr === 1 ? 48 : 0, revenue: 0, likes: 0 })), u = (i.costs ?? []).filter((e) => typeof e.bedrag == "number").map((e, t) => ({ id: `cost_${t}`, day: Math.floor(n / 24), channelId: null, category: "AI Subscriptions", amount: -e.bedrag, note: `${e.wat}${e.notitie ? ` · ${e.notitie}` : ""} (${e.datum})` })), S = a == null ? void 0 : a.subscribers;
  u.unshift({ id: "spelgeld", day: 0, channelId: null, category: "Rewards", amount: 1e6, note: "Startkapitaal spelgeld (niet echt)" }), b.setState({
    videos: j,
    ledger: u,
    stats: [],
    company: { ...s.company, name: "Driftmark", balance: -u.reduce((e, t) => e - t.amount, 0) },
    channels: s.channels.map((e) => e.id === "ch_history" ? { ...e, isDemo: !1, subscribers: S ?? e.subscribers, views: (a == null ? void 0 : a.views) ?? e.views } : { ...e, isDemo: !1 }),
    tick: n,
    agents: h,
    tasks: [...v, ...s.tasks.filter((e) => !e.id.startsWith("task_") && f.some((t) => t.id === e.projectId))],
    projects: [...$, ...f],
    posts: [...I, ...T],
    demoMode: !1,
    notifications: [...d.map((e) => ({ id: O("n"), tick: n, text: e, kind: "info", read: !1 })), ...s.notifications].slice(0, 60)
  }), d.length && (d.slice(0, 3).forEach((e) => s.toast(e, "info")), P());
}
export {
  M as applyReal
};
