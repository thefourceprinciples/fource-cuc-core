function parseKV(tokens) {
  const args = {};
  tokens.forEach(tok => {
    if (!tok.includes("=")) return;
    const [k, v] = tok.split("=", 2);
    args[k] = v.includes(",") ? v.split(",").map(Number) : (isNaN(Number(v)) ? v : Number(v));
  });
  return args;
}

function runCustomCUC() {
  const src = document.getElementById("cuc_editor").value;
  const outEl = document.getElementById("comp_out");
  const stEl = document.getElementById("comp_status");
  let basins = {}, scores = {}, winner = null, log = "";

  try {
    const lines = src.split("\n");
    lines.forEach((raw, idx) => {
      const line = raw.split("#")[0].trim();
      if (!line) return;
      const [opRaw, ...restParts] = line.split(/\s+/);
      const op = opRaw.toUpperCase();
      const rest = restParts.join(" ");

      if (op === "LOAD") {
        const matches = [...rest.matchAll(/\(\s*([+-]?\d*\.?\d+)\s*,\s*([+-]?\d*\.?\d+)\s*\)/g)];
        if (!matches.length) throw new Error(`Line ${idx + 1}: LOAD needs (A, phi) pairs.`);
        basins = { H0: matches.map(m => ({ A: +m[1], phi: wrap(+m[2]) })) };
        log += `[01] LOAD -> ${basins.H0.length} carriers in H0\n`;
      } else if (op === "COMPOSE") {
        const kv = parseKV(restParts);
        const aOp = kv.A ?? 1.0, pOp = kv.phi ?? 0.0;
        Object.keys(basins).forEach(b => {
          basins[b] = basins[b].map(z => ({ A: z.A * aOp, phi: wrap(z.phi + pOp) }));
        });
        log += `[02] COMPOSE -> A=${aOp}, phi=${pOp}\n`;
      } else if (op === "PROJECT") {
        const kv = parseKV(restParts);
        const [lo, hi] = kv.bounds || [0.1, 1.0];
        Object.keys(basins).forEach(b => {
          basins[b] = basins[b].map(z => ({ A: Math.max(lo, Math.min(hi, z.A)), phi: z.phi }));
        });
        log += `[03] PROJECT -> bounds [${lo}, ${hi}]\n`;
      } else if (op === "BRANCH") {
        const kv = parseKV(restParts);
        const theta = kv.theta ?? 0.35;
        const nextBasins = {};
        let cIdx = 1;
        Object.values(basins).forEach(list => {
          const clusters = [];
          list.forEach(item => {
            let placed = false;
            for (const cl of clusters) {
              if (cl.every(ex => Math.abs(wrap(item.phi - ex.phi)) / Math.PI <= theta)) {
                cl.push(item); placed = true; break;
              }
            }
            if (!placed) clusters.push([item]);
          });
          clusters.forEach(cl => { nextBasins[`H${cIdx++}`] = cl; });
        });
        basins = nextBasins;
        log += `[04] BRANCH -> split into ${Object.keys(basins).length} basins (${Object.keys(basins).join(", ")})\n`;
      } else if (op === "STABILIZE") {
        const kv = parseKV(restParts);
        const steps = kv.steps ?? 10, kappa = kv.kappa ?? 0.45;
        scores = {};
        Object.entries(basins).forEach(([b, list]) => {
          let cur = [...list];
          for (let s = 0; s < steps; s++) {
            const [, psi] = kuramoto(cur.map(z => z.phi));
            cur = cur.map(z => ({ A: z.A, phi: wrap(z.phi - kappa * Math.sin(z.phi - psi)) }));
          }
          basins[b] = cur;
          const [rLock] = kuramoto(cur.map(z => z.phi));
          const meanA = cur.reduce((acc, z) => acc + z.A, 0) / cur.length;
          const cTot = +(meanA * 0.98 * rLock * Math.exp(-2 * (1 - rLock))).toFixed(4);
          scores[b] = { rLock, cTot, eTot: distEnergy(cTot) };
          log += `     ${b} (n=${cur.length}): r=${rLock.toFixed(4)} | C=${cTot} | E=${scores[b].eTot.toFixed(4)}\n`;
        });
      } else if (op === "SELECT") {
        winner = Object.entries(scores).reduce((best, cur) => cur[1].eTot < best[1].eTot ? cur : best)[0];
        log += `[05] SELECT -> Winner: ${winner} (Min Distortion E* = ${scores[winner].eTot.toFixed(4)})\n`;
      } else if (op === "HALT") {
        log += `[06] HALT\n`;
      } else {
        throw new Error(`Line ${idx + 1}: Unknown opcode '${op}'.`);
      }
    });

    // Push compiled state straight onto the live Unit-Circle Canvas above!
    vmBasins = basins;
    vmWinner = winner;
    drawPhasors();
    stEl.innerHTML = `<strong style="color:#22c55e;">Compiled &amp; Executed:</strong> Selected optimal basin <strong>${winner || "N/A"}</strong> (plotted on Unit Circle above).`;
    outEl.textContent = log;
  } catch (err) {
    stEl.innerHTML = `<strong style="color:#ef4444;">Syntax Error:</strong> ${err.message}`;
    outEl.textContent = err.stack || err.message;
  }
}

function loadThreeBasinPreset() {
  document.getElementById("cuc_editor").value = `# 3-Basin Contradiction Split & Min-Distortion Selection
LOAD (0.96, 0.05), (0.94, 0.18), (0.82, 2.15), (0.80, 2.30), (0.55, -1.90), (0.50, -1.75)
COMPOSE A=1.02 phi=0.02
PROJECT bounds=0.1,1.0
BRANCH theta=0.30
STABILIZE steps=15 kappa=0.45
SELECT
HALT`;
  runCustomCUC();
}
