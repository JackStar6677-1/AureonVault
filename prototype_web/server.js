const express = require("express");
const fs = require("node:fs/promises");
const fsSync = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const open = require("open").default;

const app = express();
const PORT = process.env.PORT || 4177;
const ROOT = __dirname;

function normalizePath(inputPath) {
  if (!inputPath) {
    return path.parse(process.cwd()).root;
  }

  return path.normalize(inputPath);
}

function getAvailableDrives() {
  const drives = [];
  for (let code = 65; code <= 90; code += 1) {
    const letter = String.fromCharCode(code);
    const drivePath = `${letter}:\\`;
    if (fsSync.existsSync(drivePath)) {
      drives.push({
        name: `${letter}:`,
        path: drivePath,
        type: "drive",
      });
    }
  }
  return drives;
}

function getQuickAccess() {
  const home = os.homedir();
  const candidates = [
    { name: "Desktop", path: path.join(home, "Desktop") },
    { name: "Documents", path: path.join(home, "Documents") },
    { name: "Downloads", path: path.join(home, "Downloads") },
    { name: "Pictures", path: path.join(home, "Pictures") },
    { name: "Music", path: path.join(home, "Music") },
    { name: "Videos", path: path.join(home, "Videos") },
    { name: "AppData", path: path.join(home, "AppData") },
    { name: "Temp", path: os.tmpdir() },
  ];

  return candidates.filter((item) => fsSync.existsSync(item.path));
}

async function readDirectory(targetPath) {
  const resolved = normalizePath(targetPath);
  const entries = await fs.readdir(resolved, { withFileTypes: true });

  const mapped = await Promise.all(
    entries.map(async (entry) => {
      const fullPath = path.join(resolved, entry.name);
      try {
        const stats = await fs.stat(fullPath);
        return {
          name: entry.name,
          path: fullPath,
          isDirectory: entry.isDirectory(),
          size: stats.size,
          modified: stats.mtimeMs,
          ext: entry.isDirectory() ? "" : path.extname(entry.name).toLowerCase(),
        };
      } catch (error) {
        return {
          name: entry.name,
          path: fullPath,
          isDirectory: entry.isDirectory(),
          size: 0,
          modified: 0,
          ext: entry.isDirectory() ? "" : path.extname(entry.name).toLowerCase(),
          inaccessible: true,
        };
      }
    })
  );

  mapped.sort((a, b) => {
    if (a.isDirectory !== b.isDirectory) {
      return a.isDirectory ? -1 : 1;
    }
    return a.name.localeCompare(b.name, "es", { sensitivity: "base" });
  });

  const stats = await fs.stat(resolved);

  return {
    path: resolved,
    parent: path.dirname(resolved) === resolved ? null : path.dirname(resolved),
    items: mapped,
    meta: {
      modified: stats.mtimeMs,
    },
  };
}

app.use(express.json());
app.use(express.static(path.join(ROOT, "src")));

app.get("/api/drives", async (_req, res) => {
  res.json(getAvailableDrives());
});

app.get("/api/quick-access", async (_req, res) => {
  res.json(getQuickAccess());
});

app.get("/api/read-dir", async (req, res) => {
  try {
    const data = await readDirectory(req.query.path);
    res.json({ ok: true, data });
  } catch (error) {
    res.status(400).json({ ok: false, error: error.message });
  }
});

app.post("/api/open-path", async (req, res) => {
  try {
    const target = req.body.path;
    if (!target) {
      throw new Error("Ruta vacia");
    }
    await open(target);
    res.json({ ok: true });
  } catch (error) {
    res.status(400).json({ ok: false, error: error.message });
  }
});

app.post("/api/reveal-path", async (req, res) => {
  try {
    const target = req.body.path;
    if (!target) {
      throw new Error("Ruta vacia");
    }
    await open(path.dirname(target));
    res.json({ ok: true });
  } catch (error) {
    res.status(400).json({ ok: false, error: error.message });
  }
});

app.listen(PORT, async () => {
  const url = `http://127.0.0.1:${PORT}`;
  console.log(`JackStar File Admin corriendo en ${url}`);
  await open(url);
});
