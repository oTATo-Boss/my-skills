import path from "node:path";
export function resolveAgentRoot(): string { return path.resolve(__dirname, "..", "references"); }
