import { contextBridge, shell } from "electron";

// Tiny bridge so the renderer can ask Electron to open a URL externally.
contextBridge.exposeInMainWorld("copilot", {
  openExternal: (url: string) => shell.openExternal(url),
  version: () => "0.1.0",
});
