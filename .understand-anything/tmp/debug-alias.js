const path = require('path');
const fs = require('fs');

const root = 'D:/agent开发项目/RAG智能文档检索助手';

// Read actual tsconfig
const tsconfigPath = 'frontend/tsconfig.json';
const tsconfig = JSON.parse(fs.readFileSync(path.join(root, tsconfigPath), 'utf8'));
const tsconfigAliases = tsconfig.compilerOptions.paths;
const tsconfigBaseUrl = tsconfig.compilerOptions.baseUrl;

console.log('tsconfigAliases:', JSON.stringify(tsconfigAliases));
console.log('tsconfigBaseUrl:', tsconfigBaseUrl);

const base = path.resolve(path.dirname(path.join(root, tsconfigPath)), tsconfigBaseUrl || '.').replace(/\\/g, '/');
console.log('Resolved base (from tsconfig):', base);

// Test: what would tryResolve return for this?
function tryResolve(baseDir, importPath) {
    const probes = ['.ts', '.tsx', '.js', '.jsx', '/index.ts', '/index.js', '/index.tsx', '/index.jsx', '.py', '.go', '.rs', '.rb', '.vue'];
    const ext = path.extname(importPath);
    const hasExt = ext !== '';

    if (hasExt) {
        const resolved = path.resolve(baseDir, importPath).replace(/\\/g, '/');
        const relPath = path.relative(root.replace(/\\/g, '/'), resolved).replace(/\\/g, '/');
        return relPath;
    }

    const candidates = [importPath];
    for (const probe of probes) {
        candidates.push(importPath + probe);
    }

    for (const candidate of candidates) {
        try {
            const resolved = path.resolve(baseDir, candidate).replace(/\\/g, '/');
            const relPath = path.relative(root.replace(/\\/g, '/'), resolved).replace(/\\/g, '/');
            return relPath;
        } catch (e) {}
    }
    return null;
}

const result = tryResolve(base, 'src/stores/chat');
console.log('tryResolve(base, "src/stores/chat"):', result);

// Now trace through the actual alias logic
const importPath = '@/stores/chat';
for (const [aliasPat, targets] of Object.entries(tsconfigAliases)) {
    const aliasKey = aliasPat.replace(/\/\*$/, '');
    console.log('aliasKey:', aliasKey, 'targets:', targets);
    if (importPath.startsWith(aliasKey)) {
        const rest = importPath.slice(aliasKey.length);
        console.log('MATCH! rest:', rest);
        for (const target of targets) {
            const resolvedTarget = target.replace(/\*$/, rest);
            console.log('  resolvedTarget:', resolvedTarget);
            const r = tryResolve(base, resolvedTarget);
            console.log('  tryResolve result:', r);
        }
    }
}
