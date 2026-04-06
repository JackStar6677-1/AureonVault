const state = {
  currentPath: "",
  currentParent: null,
  items: [],
  filteredItems: [],
  selectedItem: null,
};

const drivesList = document.getElementById("drivesList");
const quickAccess = document.getElementById("quickAccess");
const fileList = document.getElementById("fileList");
const detailCard = document.getElementById("detailCard");
const pathInput = document.getElementById("pathInput");
const searchInput = document.getElementById("searchInput");
const backBtn = document.getElementById("backBtn");
const refreshBtn = document.getElementById("refreshBtn");
const currentPathLabel = document.getElementById("currentPathLabel");
const itemCountLabel = document.getElementById("itemCountLabel");
const statusText = document.getElementById("statusText");
const pickFolderBtn = document.getElementById("pickFolderBtn");

const jackstarFS =
  window.jackstarFS ||
  {
    listDrives: async () => {
      const response = await fetch("/api/drives");
      return response.json();
    },
    quickAccess: async () => {
      const response = await fetch("/api/quick-access");
      return response.json();
    },
    readDir: async (targetPath) => {
      const response = await fetch(`/api/read-dir?path=${encodeURIComponent(targetPath || "")}`);
      return response.json();
    },
    openPath: async (targetPath) => {
      const response = await fetch("/api/open-path", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: targetPath }),
      });
      return response.json();
    },
    revealPath: async (targetPath) => {
      const response = await fetch("/api/reveal-path", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: targetPath }),
      });
      return response.json();
    },
    openDialog: async () => ({ canceled: true, filePaths: [] }),
  };

function formatBytes(bytes) {
  if (!bytes) return "--";
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), sizes.length - 1);
  return `${(bytes / 1024 ** i).toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`;
}

function formatDate(value) {
  if (!value) return "--";
  return new Date(value).toLocaleString("es-CL");
}

function iconFor(item) {
  if (item.isDirectory) return "DIR";
  if ([".png", ".jpg", ".jpeg", ".webp", ".gif"].includes(item.ext)) return "IMG";
  if ([".mp4", ".mkv", ".avi"].includes(item.ext)) return "VID";
  if ([".mp3", ".wav", ".flac"].includes(item.ext)) return "AUD";
  if ([".ps1", ".bat", ".cmd", ".js", ".py", ".ts"].includes(item.ext)) return "CMD";
  if ([".zip", ".rar", ".7z"].includes(item.ext)) return "ZIP";
  return "FILE";
}

function setStatus(message) {
  statusText.textContent = message;
}

function renderNavButton(container, item) {
  const button = document.createElement("button");
  button.className = "nav-item";
  button.innerHTML = `<strong>${item.name}</strong><small>${item.path}</small>`;
  button.addEventListener("click", () => loadDirectory(item.path));
  container.appendChild(button);
}

async function renderSidebar() {
  drivesList.innerHTML = "";
  quickAccess.innerHTML = "";

  const [drives, access] = await Promise.all([
    jackstarFS.listDrives(),
    jackstarFS.quickAccess(),
  ]);

  drives.forEach((drive) => renderNavButton(drivesList, drive));
  access.forEach((entry) => renderNavButton(quickAccess, entry));
}

function renderDetails(item) {
  if (!item) {
    detailCard.innerHTML = `<p class="detail-empty">Selecciona un archivo o carpeta para ver detalle.</p>`;
    return;
  }

  detailCard.innerHTML = `
    <div class="detail-top">
      <div class="detail-icon">${iconFor(item)}</div>
      <div>
        <div class="detail-name">${item.name}</div>
        <div class="detail-path">${item.path}</div>
      </div>
    </div>

    <div class="detail-grid">
      <div class="detail-item">
        <span>Tipo</span>
        <strong>${item.isDirectory ? "Carpeta" : item.ext || "Archivo"}</strong>
      </div>
      <div class="detail-item">
        <span>Tamano</span>
        <strong>${item.isDirectory ? "--" : formatBytes(item.size)}</strong>
      </div>
      <div class="detail-item">
        <span>Ultima modificacion</span>
        <strong>${formatDate(item.modified)}</strong>
      </div>
    </div>

    <div class="detail-actions">
      <button class="action-button" data-action="open">Abrir</button>
      <button class="action-button" data-action="reveal">Mostrar en carpeta</button>
      ${item.isDirectory ? '<button class="action-button" data-action="enter">Entrar</button>' : ""}
    </div>
  `;

  detailCard.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      const action = button.dataset.action;
      if (action === "open") {
        if (item.isDirectory) {
          await loadDirectory(item.path);
        } else {
          await jackstarFS.openPath(item.path);
        }
      }
      if (action === "reveal") {
        await jackstarFS.revealPath(item.path);
      }
      if (action === "enter" && item.isDirectory) {
        await loadDirectory(item.path);
      }
    });
  });
}

function renderFileList() {
  fileList.innerHTML = "";
  const items = state.filteredItems;
  itemCountLabel.textContent = String(items.length);

  if (!items.length) {
    fileList.innerHTML = `<div class="empty-state">No hay elementos que coincidan con el filtro actual.</div>`;
    return;
  }

  items.forEach((item) => {
    const row = document.createElement("div");
    row.className = "file-row";
    if (state.selectedItem?.path === item.path) {
      row.classList.add("active");
    }

    row.innerHTML = `
      <div class="file-name">
        <div class="file-icon">${iconFor(item)}</div>
        <div class="file-label">${item.name}</div>
      </div>
      <div class="file-meta">${item.isDirectory ? "Carpeta" : item.ext || "Archivo"}</div>
      <div class="file-meta">${item.isDirectory ? "--" : formatBytes(item.size)}</div>
      <div class="file-meta">${formatDate(item.modified)}</div>
    `;

    row.addEventListener("click", () => {
      state.selectedItem = item;
      renderDetails(item);
      renderFileList();
    });

    row.addEventListener("dblclick", async () => {
      if (item.isDirectory) {
        await loadDirectory(item.path);
      } else {
        await jackstarFS.openPath(item.path);
      }
    });

    fileList.appendChild(row);
  });
}

function applyFilter() {
  const query = searchInput.value.trim().toLowerCase();
  state.filteredItems = state.items.filter((item) => item.name.toLowerCase().includes(query));
  renderFileList();
}

async function loadDirectory(targetPath) {
  setStatus("Listando...");
  const response = await jackstarFS.readDir(targetPath);
  if (!response.ok) {
    setStatus("Error de acceso");
    detailCard.innerHTML = `<div class="empty-state">No se pudo abrir la ruta.<br><br>${response.error}</div>`;
    return;
  }

  state.currentPath = response.data.path;
  state.currentParent = response.data.parent;
  state.items = response.data.items;
  state.selectedItem = null;
  currentPathLabel.textContent = response.data.path;
  pathInput.value = response.data.path;
  renderDetails(null);
  applyFilter();
  setStatus("Carpeta cargada");
}

backBtn.addEventListener("click", async () => {
  if (state.currentParent) {
    await loadDirectory(state.currentParent);
  }
});

refreshBtn.addEventListener("click", async () => {
  if (state.currentPath) {
    await loadDirectory(state.currentPath);
  }
});

pathInput.addEventListener("keydown", async (event) => {
  if (event.key === "Enter") {
    await loadDirectory(pathInput.value.trim());
  }
});

searchInput.addEventListener("input", applyFilter);

pickFolderBtn.addEventListener("click", async () => {
  if (!window.jackstarFS) {
    return;
  }

  const result = await jackstarFS.openDialog();
  if (!result.canceled && result.filePaths.length) {
    await loadDirectory(result.filePaths[0]);
  }
});

async function boot() {
  await renderSidebar();
  const drives = await jackstarFS.listDrives();
  const initialPath = drives[0]?.path || "C:\\";
  await loadDirectory(initialPath);
}

boot();
