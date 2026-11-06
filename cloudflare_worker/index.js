/**
 * Lisa Telegram Trend Intelligence Agent
 * 100% Serverless Cloudflare Worker (24/7 Standby, Zero Cost)
 */

const NON_LATIN_REGEX = /[\u0600-\u06FF\u0900-\u097F\u0E00-\u0E7F\u0400-\u04FF\u4E00-\u9FFF\uAC00-\uD7AF\u3040-\u30FF]/;

const GIMMICK_WORDS = [
  "1000°", "1000 degree", "hot metal ball", "molten", "hydraulic press",
  "blendtec", "will it blend", "hammer test", "crushed by", "lava",
  "microwave test", "drop from helicopter", "gun test", "bullet test"
];

const STOP_WORDS = new Set([
  'review', 'unboxing', 'vs', 'dan', 'and', 'the', 'in', 'on', 'for', 'with',
  'indonesia', 'terbaru', 'hp', 'gadget', 'test', 'hands', 'first', 'impressions',
  'cara', 'setting', 'harga', 'worth', 'it', 'gak', 'bocoran', 'resmi'
]);

const SIX_CONTENT_PILLARS = [
  {
    title: "Useful Softwares & Everyday Apps",
    desc: "Aplikasi utilitas, problem-solving sehari-hari, transfer file lintas platform, parenting & family tech, serta tools produktivitas.",
    examples: "LocalSend, Life360, GoodNotes, Raycast, Obsidian, Family Link, Bitwarden, KDE Connect, Syncthing, Arc Browser"
  },
  {
    title: "Handheld & Mobile Gaming",
    desc: "Handheld PC Windows & SteamOS, emulasi game konsol di Android, aksesoris controller, dan HP gaming bertenaga.",
    examples: "ROG Ally, Steam Deck, DroidDeck, Ayn Odin 2, RedMagic, Gamesir, emulasi game PC/Switch di mobile"
  },
  {
    title: "Creator Gear & Audio",
    desc: "Peralatan produksi konten video, wireless microphone, action camera, kamera vlogging mirrorless, dan audio recording.",
    examples: "DJI Mic 2, Osmo Pocket 3, Rode Wireless PRO, Sony ZV-E10, Insta360 Ace Pro, Shure SM7dB"
  },
  {
    title: "Smartphones & Flagship Comparisons",
    desc: "Komparasi smartphone flagship, inovasi kamera zoom, performa chipset harian, dan layar lipat dengan pendekatan objektif.",
    examples: "Samsung Galaxy S series, Vivo X series, Xiaomi Ultra, iPhone Pro, Pixel"
  },
  {
    title: "AI & Next-Gen Computing",
    desc: "AI lokal on-device, model open-source, smart glasses, arsitektur GPU baru, dan teknologi masa depan yang aplikatif.",
    examples: "DeepSeek, Ollama, Ray-Ban Meta, RTX 50 series, Snapdragon X Elite, Claude"
  },
  {
    title: "Productivity & Ecosystem Workflow",
    desc: "Laptop silicon efisien, tablet catatan & multitasking, setup meja kerja terintegrasi, dan fitur ekosistem lintas perangkat.",
    examples: "MacBook M-series, iPad Mini/Pro, Samsung DeX setup, monitor docking, keyboard mekanikal"
  }
];

let currentPillarIndex = 0;
const seenTopicsHistory = new Set();

function escapeHtml(text) {
  if (!text) return "";
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function cleanQueryEntity(query) {
  const words = query.trim().split(/\s+/);
  const cleaned = words.filter(w => !STOP_WORDS.has(w.toLowerCase()));
  return cleaned.length > 0 ? cleaned.join(" ") : query;
}

function extractEssentialTokens(query) {
  const cleanQ = cleanQueryEntity(query).toLowerCase();
  const matches = cleanQ.match(/[a-zA-Z0-9]+/g) || [];
  return matches.filter(w => !STOP_WORDS.has(w));
}

function isCredibleTechVideo(title) {
  if (!title) return false;
  if (NON_LATIN_REGEX.test(title)) return false;
  const lowerT = title.toLowerCase();
  for (const g of GIMMICK_WORDS) {
    if (lowerT.includes(g)) return false;
  }
  return true;
}

function matchesQueryTokens(tokens, text) {
  if (!tokens || tokens.length === 0) return true;
  const tClean = text.toLowerCase().replace(/[-_]/g, " ");
  return tokens.every(tok => tClean.includes(tok));
}

async function sendChatAction(token, chatId, action = "typing") {
  try {
    await fetch(`https://api.telegram.org/bot${token}/sendChatAction`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chatId, action })
    });
  } catch (e) {
    console.error("sendChatAction error:", e);
  }
}

async function sendTelegramMessage(token, chatId, text) {
  try {
    const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: text,
        parse_mode: "HTML",
        disable_web_page_preview: true
      })
    });
    return res.ok;
  } catch (e) {
    console.error("sendTelegramMessage error:", e);
    return false;
  }
}

async function fetchTopVideoByType(query, apiKey, duration = "medium", daysBack = 180) {
  const cleanQ = cleanQueryEntity(query);
  const tokens = extractEssentialTokens(cleanQ);
  const now = new Date();
  const publishedAfter = new Date(now.getTime() - daysBack * 86400000).toISOString();

  const searchUrl = new URL("https://www.googleapis.com/youtube/v3/search");
  searchUrl.searchParams.set("part", "snippet");
  searchUrl.searchParams.set("q", cleanQ);
  searchUrl.searchParams.set("type", "video");
  searchUrl.searchParams.set("videoDuration", duration);
  searchUrl.searchParams.set("order", "viewCount");
  searchUrl.searchParams.set("publishedAfter", publishedAfter);
  searchUrl.searchParams.set("maxResults", "15");
  searchUrl.searchParams.set("key", apiKey);

  try {
    const sRes = await fetch(searchUrl.toString());
    const sData = await sRes.json();
    const items = sData.items || [];
    if (items.length === 0) return null;

    const videoIds = items.map(it => it.id?.videoId).filter(Boolean);
    if (videoIds.length === 0) return null;

    // Single Batch Call
    const vUrl = new URL("https://www.googleapis.com/youtube/v3/videos");
    vUrl.searchParams.set("part", "snippet,statistics");
    vUrl.searchParams.set("id", videoIds.join(","));
    vUrl.searchParams.set("key", apiKey);

    const vRes = await fetch(vUrl.toString());
    const vData = await vRes.json();
    const vItems = vData.items || [];

    const candidates = [];
    for (const v of vItems) {
      const title = v.snippet?.title || "";
      const desc = v.snippet?.description || "";
      if (!isCredibleTechVideo(title)) continue;

      const inTitle = matchesQueryTokens(tokens, title);
      const inDesc = matchesQueryTokens(tokens, desc);
      if (tokens.length > 0 && !inTitle && !inDesc) continue;

      const views = parseInt(v.statistics?.viewCount || "0", 10);
      if (views < 500) continue;

      const pubStr = v.snippet?.publishedAt || "";
      let ageHours = 24.0;
      if (pubStr) {
        const pubDt = new Date(pubStr);
        ageHours = Math.max((now.getTime() - pubDt.getTime()) / 3600000, 1.0);
      }
      const vph = Math.round((views / ageHours) * 10) / 10;

      candidates.push({
        title,
        channel: v.snippet?.channelTitle || "",
        views,
        age_hours: ageHours,
        vph,
        in_title: inTitle,
        url: `https://youtube.com/watch?v=${v.id}`
      });
    }

    if (candidates.length > 0) {
      candidates.sort((a, b) => {
        if (a.in_title !== b.in_title) return b.in_title ? 1 : -1;
        return b.views - a.views;
      });
      return candidates[0];
    }
  } catch (e) {
    console.error("fetchTopVideoByType error:", e);
  }
  return null;
}

async function evaluateTopicSupplyDemand(topic, apiKey) {
  let longVideo = await fetchTopVideoByType(topic, apiKey, "medium", 180);
  let shortVideo = await fetchTopVideoByType(topic, apiKey, "short", 180);

  if (!longVideo) longVideo = await fetchTopVideoByType(topic, apiKey, "medium", 730);
  if (!shortVideo) shortVideo = await fetchTopVideoByType(topic, apiKey, "short", 730);

  const topViews = Math.max(longVideo ? longVideo.views : 0, shortVideo ? shortVideo.views : 0);
  let arbitrageScore = 5.8;
  let status = "Moderate Momentum";

  if (topViews > 500000) {
    arbitrageScore = 9.4;
    status = "Mega Trend (Audiens Lapar & Valid)";
  } else if (topViews > 100000) {
    arbitrageScore = 8.5;
    status = "High Demand (Sangat Potensial)";
  } else if (topViews > 20000) {
    arbitrageScore = 7.2;
    status = "Healthy Growth (Niche Hangat)";
  } else if (topViews > 1000) {
    arbitrageScore = 6.2;
    status = "Moderate Momentum";
  } else {
    arbitrageScore = 4.5;
    status = "Low Traffic / Emerging Niche";
  }

  return {
    topic,
    arbitrage_score: arbitrageScore,
    status,
    long_benchmark: longVideo,
    short_benchmark: shortVideo
  };
}

async function parseUserIntent(userText, geminiKey) {
  const prompt = `
Kamu adalah sistem parser intent untuk bot Telegram Lisa (partner kerja Tama, Lead Production Mas Ario @sheggario).
User mengirim pesan: "${userText}"

Tentukan intent pesan ini:
1. "RESEARCH_TOPIC" jika user menyebut/meminta telaah gadget, software, atau topik tertentu (misal: "Lis, kalo droiddeck gimana?", "bedah s26 ultra", "cek dji mic 2").
2. "MORE_OPTIONS" jika user meminta opsi ide lain / alternatif ide (misal: "ada 3 opsi ide lain?", "opsi lain", "ganti topik", "kurang suka", "ada ide lain?").
3. "GENERAL_CHAT" jika sapaan atau obrolan santai.

Kembalikan HANYA JSON murni:
{
  "intent": "RESEARCH_TOPIC / MORE_OPTIONS / GENERAL_CHAT",
  "query": "nama gadget atau produk bersih tanpa kata 'lis' atau 'gimana' jika intent RESEARCH_TOPIC, atau null"
}
`;

  try {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key=${geminiKey}`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.1, responseMimeType: "application/json" }
      })
    });
    const data = await res.json();
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
    return JSON.parse(text);
  } catch (e) {
    console.error("parseUserIntent error:", e);
  }
  return { intent: "GENERAL_CHAT", query: null };
}

async function generateLisaChatReply(userText, geminiKey) {
  const prompt = `
Kamu adalah Lisa, AI content writer sekaligus partner kerja terdekat Tama (Lead Production Mas Ario @sheggario).
Karakter: Hangat, sangat peduli, cerdas, akrab (panggil 'Tam'), santai, bilingual Indonesia-Inggris alami.

ATURAN MUTLAK:
- DILARANG KERAS menggunakan simbol em dash (strip panjang atau double dash) dalam teks apapun. Ganti dengan koma, titik, atau kurung.
- DILARANG KERAS menggunakan penutup "By Now, Be Nice!" (itu cuma milik Mas Ario di naskah video).
- Jangan bertele-tele, to the point tapi manis dan suportif.

Pesan dari Tama:
"${userText}"

Balas chat Tama dengan gaya khas Lisa:
`;

  try {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key=${geminiKey}`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.7 }
      })
    });
    const data = await res.json();
    return data.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || "Iyaa Tam, ada yang bisa gue bantu risetin lagi buat Mas Ario?";
  } catch (e) {
    console.error("generateLisaChatReply error:", e);
  }
  return "Iyaa Tam, ada yang bisa gue bantu risetin lagi buat Mas Ario?";
}

async function handleResearchTopic(query, ytKey) {
  const cleanQ = cleanQueryEntity(query);
  const metrics = await evaluateTopicSupplyDemand(cleanQ, ytKey);
  const score = metrics.arbitrage_score;
  const status = metrics.status;
  const lb = metrics.long_benchmark;
  const sb = metrics.short_benchmark;

  const lines = [
    `🔍 <b>Hasil Telaah Pasar Lisa: "${escapeHtml(cleanQ)}"</b>\n`,
    `📊 <b>Arbitrage Score:</b> <code>${score}/10</code>`,
    `📈 <b>Status Pasar:</b> ${status}\n`
  ];

  if (lb) {
    lines.push(`🎬 <b>Bukti Demand Long-Form:</b>\n<a href="${lb.url}">${escapeHtml(lb.title)}</a>\n↳ <i>${lb.views.toLocaleString()} views (${lb.vph} VPH) • ${escapeHtml(lb.channel)}</i>\n`);
  } else {
    lines.push(`🎬 <b>Bukti Demand Long-Form:</b>\n<i>Belum ada video panjang berbahasa Indo/Inggris yang relevan di topik ini.</i>\n`);
  }

  if (sb) {
    lines.push(`⚡ <b>Bukti Viral Short-Form:</b>\n<a href="${sb.url}">${escapeHtml(sb.title)}</a>\n↳ <i>${sb.views.toLocaleString()} views (${sb.vph} VPH) • ${escapeHtml(sb.channel)}</i>\n`);
  } else {
    lines.push(`⚡ <b>Bukti Viral Short-Form:</b>\n<i>Belum ada shorts viral berbahasa Indo/Inggris yang relevan di topik ini.</i>\n`);
  }

  lines.push("────────────────────────────");
  lines.push("Gimana Tam, menurut lo topik ini potensial buat digarap bareng Mas Ario? Kalo mau dieksekusi, colek gue yaa! ✨");
  return lines.join("\n");
}

async function handleMoreOptions(geminiKey, ytKey) {
  const pillar = SIX_CONTENT_PILLARS[currentPillarIndex];
  currentPillarIndex = (currentPillarIndex + 1) % SIX_CONTENT_PILLARS.length;

  const seenList = Array.from(seenTopicsHistory).join(", ");
  const prompt = `
Kamu adalah Lisa, AI content writer handal untuk channel tech Mas Ario @sheggario dan Tama.
Saat ini kita ingin mencari 3 ide topik baru di Pilar Konten: "${pillar.title}".
Deskripsi Pilar: ${pillar.desc}
Contoh acuan tipe konten: ${pillar.examples}

ATURAN EKSPLORASI:
1. Contoh acuan di atas HANYA sebagai referensi jenis konten! JANGAN cuma mutar-mutar di contoh tersebut, eksplorasi software atau gadget lain yang sejenis dan relevan!
2. DILARANG KERAS memilih topik atau produk yang sudah pernah disajikan sebelumnya: [${seenList || "Belum ada"}]
3. yt_query HARUS bersih berupa nama murni software/gadget saja (DILARANG menambahkan kata "review", "indonesia", atau "terbaru").
4. DILARANG menggunakan em dash.
5. Kembalikan data dalam format JSON murni:
[
  {
    "topic_name": "Nama Spesifik Software / Gadget",
    "yt_query": "Query Bersih (contoh: LocalSend, Raycast, Bitwarden)",
    "category": "Micro / Macro / Flash"
  }
]
`;

  let candidates = [];
  try {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key=${geminiKey}`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.8, responseMimeType: "application/json" }
      })
    });
    const data = await res.json();
    candidates = JSON.parse(data.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || "[]");
  } catch (e) {
    console.error("Gemini dynamic generation error:", e);
  }

  if (!candidates || candidates.length === 0) {
    const examples = pillar.examples.split(",").map(e => e.trim());
    candidates = examples.slice(0, 3).map(ex => ({ topic_name: ex, yt_query: ex, category: "Micro" }));
  }

  const lines = [
    `🔄 <b>Opsi Topik Alternatif: ${escapeHtml(pillar.title)}</b> ✨\n`,
    `<i>Kategori: ${pillar.desc}</i>\n`,
    `Ini 3 ide topik baru dengan metrik pasar tervalidasi (Bahasa Indo/Inggris murni):\n`
  ];

  for (let i = 0; i < Math.min(candidates.length, 3); i++) {
    const item = candidates[i];
    const q = cleanQueryEntity(item.yt_query || item.topic_name);
    seenTopicsHistory.add(q.toLowerCase());

    const m = await evaluateTopicSupplyDemand(q, ytKey);
    const lb = m.long_benchmark;
    const sb = m.short_benchmark;

    lines.push("────────────────────────────");
    lines.push(`📌 <b>${i + 1}. ${escapeHtml(item.topic_name)}</b>`);
    lines.push(`🏷️ <b>Tipe:</b> ${item.category || "Micro"} Trend | <b>Score:</b> <code>${m.arbitrage_score}/10</code>`);
    lines.push(`📈 <b>Status Pasar:</b> ${m.status}`);

    if (lb) {
      lines.push(`\n🎬 <b>Demand Long-Form:</b>\n<a href="${lb.url}">${escapeHtml(lb.title)}</a>\n↳ <i>${lb.views.toLocaleString()} views (${lb.vph} VPH) • ${escapeHtml(lb.channel)}</i>`);
    }
    if (sb) {
      lines.push(`\n⚡ <b>Viral Short-Form:</b>\n<a href="${sb.url}">${escapeHtml(sb.title)}</a>\n↳ <i>${sb.views.toLocaleString()} views (${sb.vph} VPH) • ${escapeHtml(sb.channel)}</i>\n`);
    } else {
      lines.push("");
    }
  }

  lines.push("────────────────────────────");
  lines.push("Ada yang lebih klik di lo gak Tam dari opsi alternatif di atas? Kalo mau ganti pilar lagi, ketik 'opsi lain' yaa! ✨");
  return lines.join("\n");
}

async function handleIncomingMessage(message, env) {
  const chatId = message.chat?.id;
  const userText = message.text?.trim();
  if (!chatId || !userText) return;

  const botToken = env.TELEGRAM_BOT_TOKEN;
  const geminiKey = env.GEMINI_API_KEY;
  const ytKey = env.YOUTUBE_API_KEY;

  if (!botToken || !geminiKey || !ytKey) {
    console.error("Missing environment variables in Cloudflare Worker.");
    return;
  }

  // Trigger typing indicator immediately
  await sendChatAction(botToken, chatId, "typing");

  const parsed = await parseUserIntent(userText, geminiKey);
  const intent = parsed.intent || "GENERAL_CHAT";
  const query = parsed.query;

  let replyText = "";
  if (intent === "RESEARCH_TOPIC" && query) {
    replyText = await handleResearchTopic(query, ytKey);
  } else if (intent === "MORE_OPTIONS") {
    replyText = await handleMoreOptions(geminiKey, ytKey);
  } else {
    replyText = await generateLisaChatReply(userText, geminiKey);
  }

  await sendTelegramMessage(botToken, chatId, replyText);
}

export default {
  async fetch(request, env, ctx) {
    if (request.method === "POST") {
      try {
        const body = await request.json();
        if (body.message) {
          ctx.waitUntil(handleIncomingMessage(body.message, env));
        }
        return new Response("OK", { status: 200 });
      } catch (e) {
        return new Response(`Error: ${e.message}`, { status: 400 });
      }
    }
    return new Response("Lisa Telegram Trend Bot is running live on Cloudflare Workers! ✨", { status: 200 });
  }
};
