import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const PORT = 9222;
const SCREENSHOT_DIR = path.resolve("docs/screenshots");

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForCdp() {
  for (let i = 0; i < 30; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      if (res.ok) return await res.json();
    } catch {
      // ignore
    }
    await sleep(300);
  }
  throw new Error("Chrome CDP did not become ready in time.");
}

class CdpClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.id = 0;
    this.callbacks = new Map();
  }

  async connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = () => resolve();
      this.ws.onerror = (err) => reject(err);
      this.ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && this.callbacks.has(msg.id)) {
          const { resolve, reject } = this.callbacks.get(msg.id);
          this.callbacks.delete(msg.id);
          if (msg.error) reject(new Error(msg.error.message));
          else resolve(msg.result);
        }
      };
    });
  }

  async send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolve, reject) => {
      this.callbacks.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

async function run() {
  console.log("Launching Chrome...");
  const chromeProc = spawn(
    CHROME_PATH,
    [
      "--headless=new",
      `--remote-debugging-port=${PORT}`,
      "--no-first-run",
      "--no-default-browser-check",
      "--disable-gpu",
      "--hide-scrollbars",
      "--window-size=1440,900",
      "about:blank",
    ],
    { stdio: "ignore" }
  );

  try {
    const versionInfo = await waitForCdp();
    console.log("Connected to Chrome:", versionInfo.Browser);

    const targetsRes = await fetch(`http://127.0.0.1:${PORT}/json/list`);
    const targets = await targetsRes.json();
    const pageTarget = targets.find((t) => t.type === "page") || targets[0];
    if (!pageTarget) throw new Error("No page target found");

    const client = new CdpClient(pageTarget.webSocketDebuggerUrl);
    await client.connect();

    await client.send("Page.enable");
    await client.send("DOM.enable");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1440,
      height: 900,
      deviceScaleFactor: 2,
      mobile: false,
    });

    // 1. Capture Login Page
    console.log("Capturing Login...");
    await client.send("Page.navigate", { url: "http://localhost:3000/login" });
    await sleep(2500);
    let ss = await client.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(SCREENSHOT_DIR, "login.png"), Buffer.from(ss.data, "base64"));

    // Authenticate
    console.log("Authenticating for demo user...");
    const authRes = await fetch("http://localhost:8000/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        username: "aayush.sharma@skillgraph.dev",
        password: "SkillGraph2026!",
      }),
    });
    const authData = await authRes.json();
    const token = authData.access_token;
    const userObj = { id: authData.user_id, name: authData.name, role: authData.role };

    await client.send("Runtime.evaluate", {
      expression: `
        localStorage.setItem("skillgraph_token", ${JSON.stringify(token)});
        localStorage.setItem("skillgraph_user", ${JSON.stringify(JSON.stringify(userObj))});
      `,
    });

    // Dashboard
    console.log("Capturing dashboard.png...");
    await client.send("Page.navigate", { url: "http://localhost:3000/dashboard" });
    await sleep(3500);
    let data = await client.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(SCREENSHOT_DIR, "dashboard.png"), Buffer.from(data.data, "base64"));

    // Skill Graph
    console.log("Capturing skill_graph.png...");
    await client.send("Page.navigate", { url: "http://localhost:3000/skill-graph" });
    await sleep(4000);
    data = await client.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(SCREENSHOT_DIR, "skill_graph.png"), Buffer.from(data.data, "base64"));

    // Role Matching
    console.log("Capturing role_matching.png...");
    await client.send("Page.navigate", { url: "http://localhost:3000/roles" });
    await sleep(3500);
    data = await client.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(SCREENSHOT_DIR, "role_matching.png"), Buffer.from(data.data, "base64"));

    // Gap Analysis
    console.log("Capturing gap_analysis.png...");
    await client.send("Page.navigate", { url: "http://localhost:3000/gaps" });
    await sleep(3500);
    data = await client.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(SCREENSHOT_DIR, "gap_analysis.png"), Buffer.from(data.data, "base64"));

    // Career Simulator (interactive simulation state)
    console.log("Capturing career_simulator.png with simulated delta...");
    await client.send("Page.navigate", { url: "http://localhost:3000/career-simulator" });
    await sleep(2500);
    await client.send("Runtime.evaluate", {
      expression: `
        (() => {
          const buttons = document.querySelectorAll("div.flex.flex-wrap button");
          buttons.forEach((btn, i) => { if (i < 4) btn.click(); });
          setTimeout(() => {
            const simBtn = Array.from(document.querySelectorAll("button")).find(b => b.textContent.includes("Run simulation"));
            if (simBtn) simBtn.click();
          }, 300);
        })();
      `,
    });
    await sleep(2500);
    data = await client.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(SCREENSHOT_DIR, "career_simulator.png"), Buffer.from(data.data, "base64"));

    // AI Analyst (with active analysis populated)
    console.log("Capturing ai_analyst.png with active analysis...");
    await client.send("Page.navigate", { url: "http://localhost:3000/ai-analyst" });
    await sleep(2500);
    await client.send("Runtime.evaluate", {
      expression: `
        (() => {
          const sampleBtn = Array.from(document.querySelectorAll("button")).find(b => b.textContent.includes("Why am I not ready"));
          if (sampleBtn) sampleBtn.click();
        })();
      `,
    });
    await sleep(3000);
    data = await client.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(SCREENSHOT_DIR, "ai_analyst.png"), Buffer.from(data.data, "base64"));

    // Assessments
    console.log("Capturing assessments.png...");
    await client.send("Page.navigate", { url: "http://localhost:3000/assessments" });
    await sleep(3500);
    data = await client.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(SCREENSHOT_DIR, "assessments.png"), Buffer.from(data.data, "base64"));

    // Evidence Locker
    console.log("Capturing evidence_locker.png...");
    await client.send("Page.navigate", { url: "http://localhost:3000/evidence" });
    await sleep(3500);
    data = await client.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(SCREENSHOT_DIR, "evidence_locker.png"), Buffer.from(data.data, "base64"));

    // Learning Paths
    console.log("Capturing learning_paths.png...");
    await client.send("Page.navigate", { url: "http://localhost:3000/learning" });
    await sleep(3500);
    data = await client.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(SCREENSHOT_DIR, "learning_paths.png"), Buffer.from(data.data, "base64"));

    await client.close();
    console.log("All screenshots captured and saved!");
  } finally {
    chromeProc.kill("SIGKILL");
  }
}

run().catch((err) => {
  console.error("Screenshot capture failed:", err);
  process.exit(1);
});
