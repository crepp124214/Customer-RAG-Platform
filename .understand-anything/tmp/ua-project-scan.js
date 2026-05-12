const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = process.argv[2];
const OUTPUT_FILE = process.argv[3];

if (!PROJECT_ROOT || !OUTPUT_FILE) {
    console.error('Usage: node ua-project-scan.js <project-root> <output-file>');
    process.exit(1);
}

try {
    fs.accessSync(PROJECT_ROOT);
} catch (e) {
    console.error('Cannot access project root: ' + PROJECT_ROOT);
    process.exit(1);
}

// ========== STEP 1: File Discovery ==========
function discoverFiles() {
    try {
        // git ls-files shows cached files. Filter to only those existing on disk.
        const result = execSync('git -C "' + PROJECT_ROOT + '" ls-files', { encoding: 'utf8' });
        const all = result.split('\n').filter(Boolean).map(f => f.replace(/\\/g, '/'));
        const existing = [];
        const deleted = [];
        for (const f of all) {
            const fullPath = path.join(PROJECT_ROOT, f);
            if (fs.existsSync(fullPath)) {
                existing.push(f);
            } else {
                deleted.push(f);
            }
        }
        console.error('git ls-files total: ' + all.length + ', existing: ' + existing.length + ', deleted: ' + deleted.length);
        return { files: existing, deleted };
    } catch (e) {
        console.error('git ls-files failed, falling back to directory walk: ' + e.message);
        const walked = walkDir(PROJECT_ROOT);
        return { files: walked, deleted: [] };
    }
}

function walkDir(dir) {
    const files = [];
    function walk(current) {
        let entries;
        try {
            entries = fs.readdirSync(current, { withFileTypes: true });
        } catch (e) { return; }
        for (const e of entries) {
            const full = path.join(current, e.name);
            if (e.isDirectory()) {
                if (isExcludedDir(e.name)) continue;
                walk(full);
            } else {
                const rel = path.relative(PROJECT_ROOT, full).replace(/\\/g, '/');
                files.push(rel);
            }
        }
    }
    walk(dir);
    return files;
}

function isExcludedDir(name) {
    const excluded = ['node_modules', '.git', 'vendor', 'venv', '.venv', '__pycache__'];
    return excluded.includes(name);
}

// ========== STEP 2: Exclusion Filtering ==========
function shouldExcludeHardcoded(filePath) {
    const segments = filePath.split('/');
    const fileName = segments[segments.length - 1];

    // Dependency directories
    const depDirs = ['node_modules', '.git', 'vendor', 'venv', '.venv', '__pycache__'];
    for (const seg of segments) {
        if (depDirs.includes(seg)) return true;
    }

    // Build output (full directory segments only)
    const buildDirs = ['dist', 'build', 'out', 'coverage', '.next', '.cache', '.turbo', 'target', 'obj'];
    for (const seg of segments) {
        if (buildDirs.includes(seg)) return true;
    }

    // Lock files
    if (fileName.endsWith('.lock')) return true;
    if (fileName === 'package-lock.json' || fileName === 'yarn.lock' || fileName === 'pnpm-lock.yaml') return true;

    // Binary/asset files
    const binExts = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.mp3', '.mp4', '.pdf', '.zip', '.tar', '.gz'];
    for (const ext of binExts) {
        if (fileName.toLowerCase().endsWith(ext)) return true;
    }

    // Generated files
    if (fileName.endsWith('.min.js') || fileName.endsWith('.min.css') || fileName.endsWith('.map') || fileName.includes('.generated.')) return true;

    // IDE/editor config
    if (segments.includes('.idea') || segments.includes('.vscode')) return true;

    // Misc non-source
    if (fileName === 'LICENSE') return true;
    if (fileName === '.gitignore') return true;
    if (fileName === '.editorconfig') return true;
    if (fileName.startsWith('.prettierrc')) return true;
    if (fileName.startsWith('.eslintrc')) return true;
    if (fileName.endsWith('.log')) return true;

    return false;
}

// ========== STEP 2.5: .understandignore ==========
function readUserIgnorePatterns(projectRoot) {
    let userPatterns = [];
    const userIgnore1 = path.join(projectRoot, '.understand-anything', '.understandignore');
    const userIgnore2 = path.join(projectRoot, '.understandignore');

    for (const p of [userIgnore1, userIgnore2]) {
        try {
            if (fs.existsSync(p)) {
                const content = fs.readFileSync(p, 'utf8');
                const patterns = content.split('\n')
                    .map(l => l.trim())
                    .filter(l => l && !l.startsWith('#'));
                userPatterns = userPatterns.concat(patterns);
            }
        } catch (e) {}
    }

    return userPatterns;
}

function createIgnoreFilter(projectRoot) {
    const hardcodedPatterns = [
        'node_modules/', '.git/', 'vendor/', 'venv/', '.venv/', '__pycache__/',
        'dist/', 'build/', 'out/', 'coverage/', '.next/', '.cache/', '.turbo/', 'target/', 'obj/',
        '*.lock', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
        '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg', '*.ico', '*.woff', '*.woff2', '*.ttf', '*.eot',
        '*.mp3', '*.mp4', '*.pdf', '*.zip', '*.tar', '*.gz',
        '*.min.js', '*.min.css', '*.map', '*.generated.*',
        '.idea/', '.vscode/',
        'LICENSE', '.gitignore', '.editorconfig', '.prettierrc*', '.eslintrc*', '*.log'
    ];

    const userPatterns = readUserIgnorePatterns(projectRoot);
    if (userPatterns.length === 0) return null;

    const allPatterns = [...hardcodedPatterns, ...userPatterns];

    return function(filePath) {
        let negated = false;
        let matchedExclude = false;

        for (const pattern of allPatterns) {
            const neg = pattern.startsWith('!');
            const realPattern = neg ? pattern.slice(1) : pattern;

            if (matchGitignore(filePath, realPattern)) {
                if (neg) {
                    negated = true;
                } else {
                    matchedExclude = true;
                }
            }
        }

        // Negation wins: if a !pattern matched, include the file
        if (negated) return false;
        return matchedExclude;
    };
}

function matchGitignore(filePath, pattern) {
    // Strip leading / from pattern
    const p = pattern.startsWith('/') ? pattern.slice(1) : pattern;

    // Directory pattern (ends with /)
    if (p.endsWith('/')) {
        const dirPattern = p.slice(0, -1);
        const segments = filePath.split('/');
        if (segments.includes(dirPattern)) return true;
        if (filePath.startsWith(dirPattern + '/') || filePath === dirPattern) return true;
        return false;
    }

    // ** pattern - match across directory boundaries
    if (p.includes('**')) {
        const parts = p.split('**');
        let regexStr = '';
        for (let i = 0; i < parts.length; i++) {
            regexStr += escapeRegex(parts[i]);
            if (i < parts.length - 1) regexStr += '.*';
        }
        try {
            return new RegExp('^' + regexStr + '$').test(filePath);
        } catch (e) {
            // Try matching without anchoring if it's a sub-path pattern
            try {
                return new RegExp(regexStr).test(filePath);
            } catch (e2) {
                return false;
            }
        }
    }

    // Simple glob: * matches anything except /
    const regexStr = escapeRegex(p).replace(/\\\*/g, '[^/]*');
    try {
        return new RegExp('^' + regexStr + '$').test(filePath);
    } catch (e) {
        return false;
    }
}

function escapeRegex(str) {
    return str.replace(/[.+?^${}()|[\]\\]/g, '\\$&');
}

// ========== STEP 3: Language Detection ==========
function detectLanguage(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    const base = path.basename(filePath);

    const extMap = {
        '.ts': 'typescript', '.tsx': 'typescript',
        '.js': 'javascript', '.jsx': 'javascript',
        '.py': 'python',
        '.go': 'go',
        '.rs': 'rust',
        '.java': 'java',
        '.rb': 'ruby',
        '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.h': 'cpp', '.hpp': 'cpp', '.hxx': 'cpp', '.cuh': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.swift': 'swift',
        '.kt': 'kotlin', '.kts': 'kotlin',
        '.php': 'php',
        '.vue': 'vue',
        '.svelte': 'svelte',
        '.sh': 'shell', '.bash': 'shell',
        '.ps1': 'powershell',
        '.bat': 'batch', '.cmd': 'batch',
        '.md': 'markdown', '.rst': 'markdown',
        '.yaml': 'yaml', '.yml': 'yaml',
        '.json': 'json', '.jsonc': 'jsonc',
        '.toml': 'toml',
        '.sql': 'sql',
        '.graphql': 'graphql', '.gql': 'graphql',
        '.proto': 'protobuf',
        '.tf': 'terraform', '.tfvars': 'terraform',
        '.html': 'html', '.htm': 'html',
        '.css': 'css', '.scss': 'css', '.sass': 'css', '.less': 'css',
        '.xml': 'xml',
        '.cfg': 'config', '.ini': 'config', '.env': 'config',
        '.csv': 'csv',
        '.prisma': 'prisma',
        '.mjs': 'javascript', // ES modules
        '.mako': 'mako', // Python template
    };

    if (extMap[ext]) return extMap[ext];

    // Filename-based detection
    if (base === 'Dockerfile' || base.startsWith('Dockerfile.')) return 'dockerfile';
    if (base === 'Makefile') return 'makefile';
    if (base === 'Jenkinsfile') return 'jenkinsfile';
    if (base === '.gitkeep') return 'config';
    if (base.endsWith('.env.example')) return 'config';
    if (ext === '.mako') return 'mako';

    // Fallback
    if (ext) return ext.slice(1).toLowerCase();
    return 'unknown';
}

// ========== STEP 4: File Category Detection ==========
function detectCategory(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    const base = path.basename(filePath);
    const segments = filePath.split('/');

    // Infra (check first - specific patterns take priority)
    if (base === 'Dockerfile' || base.startsWith('Dockerfile.')) return 'infra';
    if (base.startsWith('docker-compose')) return 'infra';
    if (['.tf', '.tfvars'].includes(ext)) return 'infra';
    if (base === 'Makefile') return 'infra';
    if (base === 'Jenkinsfile') return 'infra';
    if (base === 'Procfile') return 'infra';
    if (base === 'Vagrantfile') return 'infra';
    if (filePath.startsWith('.github/workflows/')) return 'infra';
    if (filePath === '.gitlab-ci.yml') return 'infra';
    if (filePath.startsWith('.circleci/')) return 'infra';
    if (base.endsWith('.k8s.yaml') || base.endsWith('.k8s.yml')) return 'infra';
    if (segments.includes('k8s') || segments.includes('kubernetes')) return 'infra';

    // Docs
    if (['.md', '.rst'].includes(ext)) return 'docs';
    if (ext === '.txt' && base !== 'LICENSE') return 'docs';

    // Data/Schema
    if (['.sql', '.graphql', '.gql', '.proto', '.prisma', '.csv'].includes(ext)) return 'data';
    if (base.endsWith('.schema.json')) return 'data';

    // Script
    if (['.sh', '.bash', '.ps1', '.bat', '.cmd'].includes(ext)) return 'script';

    // Markup
    if (['.html', '.htm', '.css', '.scss', '.sass', '.less'].includes(ext)) return 'markup';

    // Config
    if (['.yaml', '.yml', '.json', '.jsonc', '.toml', '.xml', '.cfg', '.ini', '.env'].includes(ext)) return 'config';
    if (base === 'tsconfig.json' || base === 'package.json' || base === 'pyproject.toml' || base === 'Cargo.toml' || base === 'go.mod') return 'config';
    if (base === '.gitkeep') return 'config';
    if (base.endsWith('.env.example')) return 'config';
    if (ext === '.mako') return 'config';

    // Default: code
    return 'code';
}

// ========== STEP 5: Line Counting (using Node.js only, no wc) ==========
function countLines(files) {
    const result = {};
    for (const f of files) {
        try {
            const fullPath = path.join(PROJECT_ROOT, f);
            // Use Buffer to handle encoding issues
            const buf = fs.readFileSync(fullPath);
            // Count newlines
            let count = 0;
            for (let i = 0; i < buf.length; i++) {
                if (buf[i] === 10) count++; // \n
            }
            // If file doesn't end with newline, add 1 for the last line
            if (buf.length > 0 && buf[buf.length - 1] !== 10) count++;
            result[f] = count;
        } catch (e) {
            result[f] = 0;
        }
    }
    return result;
}

// ========== STEP 6: Framework Detection ==========
function detectFrameworks(files, projectRoot) {
    const frameworks = new Set();

    // Check package.json
    const pkgJsonPath = files.find(f => f === 'frontend/package.json' || f === 'package.json');
    if (pkgJsonPath) {
        try {
            const pkg = JSON.parse(fs.readFileSync(path.join(projectRoot, pkgJsonPath), 'utf8'));
            const allDeps = { ...(pkg.dependencies || {}), ...(pkg.devDependencies || {}) };
            const depNames = Object.keys(allDeps);

            if (depNames.includes('vue')) frameworks.add('Vue 3');
            if (depNames.includes('element-plus')) frameworks.add('Element Plus');
            if (depNames.includes('pinia')) frameworks.add('Pinia');
            if (depNames.includes('vite')) frameworks.add('Vite');
            if (depNames.includes('vitest')) frameworks.add('Vitest');
            if (depNames.includes('eslint')) frameworks.add('ESLint');
            if (depNames.includes('axios')) frameworks.add('Axios');
            if (depNames.includes('vue-router')) frameworks.add('Vue Router');

            const otherFrameworks = ['react', 'svelte', '@angular/core', 'express', 'fastify', 'koa',
                'next', 'nuxt', 'jest', 'mocha', 'tailwindcss', 'prisma', 'typeorm', 'sequelize',
                'mongoose', 'redux', 'zustand', 'mobx'];
            for (const fw of otherFrameworks) {
                if (depNames.includes(fw)) {
                    frameworks.add(mapFrontendName(fw));
                }
            }
        } catch (e) {
            console.error('Error reading package.json:', e.message);
        }
    }

    // Check tsconfig.json
    if (files.some(f => f.includes('tsconfig.json') && !f.includes('node_modules'))) {
        frameworks.add('TypeScript');
    }

    // Check Python configs
    const requirementsPath = files.find(f => f === 'requirements.txt' || f.endsWith('/requirements.txt'));
    if (requirementsPath) {
        try {
            const content = fs.readFileSync(path.join(projectRoot, requirementsPath), 'utf8');
            const pyFrameworkMap = {
                'django': 'Django', 'djangorestframework': 'Django REST Framework',
                'fastapi': 'FastAPI', 'flask': 'Flask',
                'sqlalchemy': 'SQLAlchemy', 'alembic': 'Alembic',
                'celery': 'Celery', 'pydantic': 'Pydantic',
                'uvicorn': 'Uvicorn', 'gunicorn': 'Gunicorn',
                'aiohttp': 'Aiohttp', 'tornado': 'Tornado',
                'starlette': 'Starlette', 'pytest': 'pytest',
                'hypothesis': 'Hypothesis', 'channels': 'Django Channels',
                'langchain': 'LangChain', 'dashscope': 'DashScope', 'rq': 'RQ'
            };
            for (const [key, name] of Object.entries(pyFrameworkMap)) {
                // Match package name at start of line or after whitespace, with optional version
                const re = new RegExp('(?:^|\\n)\\s*' + key + '(?:[=<>~!]|\\s|$)', 'im');
                if (re.test(content)) {
                    frameworks.add(name);
                }
            }
        } catch (e) {
            console.error('Error reading requirements.txt:', e.message);
        }
    }

    const pyprojectPath = files.find(f => f.endsWith('pyproject.toml'));
    if (pyprojectPath) {
        try {
            const content = fs.readFileSync(path.join(projectRoot, pyprojectPath), 'utf8');
            if (content.includes('[tool.pytest')) frameworks.add('pytest');
            if (content.includes('[tool.django')) frameworks.add('Django');
            const pyFrameworks = ['django', 'fastapi', 'flask', 'sqlalchemy', 'alembic', 'celery', 'pydantic',
                'uvicorn', 'gunicorn', 'aiohttp', 'tornado', 'starlette', 'pytest', 'hypothesis', 'channels',
                'langchain', 'dashscope', 'rq'];
            for (const fw of pyFrameworks) {
                if (content.includes(fw)) {
                    frameworks.add(mapPyName(fw));
                }
            }
        } catch (e) {}
    }

    // Infrastructure tooling
    if (files.some(f => {
        const base = f.split('/').pop();
        return base === 'Dockerfile' || base.startsWith('Dockerfile.');
    })) frameworks.add('Docker');
    if (files.some(f => {
        const base = f.split('/').pop();
        return base.startsWith('docker-compose');
    })) frameworks.add('Docker Compose');
    if (files.some(f => f.endsWith('.tf'))) frameworks.add('Terraform');
    if (files.some(f => f.startsWith('.github/workflows/'))) frameworks.add('GitHub Actions');
    if (files.some(f => f === '.gitlab-ci.yml')) frameworks.add('GitLab CI');
    if (files.some(f => f.endsWith('Jenkinsfile'))) frameworks.add('Jenkins');

    return [...frameworks].sort();
}

function mapFrontendName(name) {
    const map = {
        'react': 'React', 'svelte': 'Svelte', '@angular/core': 'Angular',
        'express': 'Express', 'fastify': 'Fastify', 'koa': 'Koa',
        'next': 'Next.js', 'nuxt': 'Nuxt',
        'jest': 'Jest', 'mocha': 'Mocha', 'tailwindcss': 'Tailwind CSS',
        'prisma': 'Prisma', 'typeorm': 'TypeORM', 'sequelize': 'Sequelize',
        'mongoose': 'Mongoose', 'redux': 'Redux', 'zustand': 'Zustand', 'mobx': 'MobX'
    };
    return map[name] || name;
}

function mapPyName(name) {
    const map = {
        'fastapi': 'FastAPI', 'django': 'Django', 'flask': 'Flask',
        'djangorestframework': 'Django REST Framework', 'sqlalchemy': 'SQLAlchemy',
        'alembic': 'Alembic', 'celery': 'Celery', 'pydantic': 'Pydantic',
        'uvicorn': 'Uvicorn', 'gunicorn': 'Gunicorn', 'aiohttp': 'Aiohttp',
        'tornado': 'Tornado', 'starlette': 'Starlette', 'pytest': 'pytest',
        'hypothesis': 'Hypothesis', 'channels': 'Django Channels',
        'langchain': 'LangChain', 'dashscope': 'DashScope', 'rq': 'RQ'
    };
    return map[name] || name;
}

// ========== STEP 7: Complexity Estimation ==========
function estimateComplexity(totalFiles) {
    if (totalFiles <= 30) return 'small';
    if (totalFiles <= 150) return 'moderate';
    if (totalFiles <= 500) return 'large';
    return 'very-large';
}

// ========== STEP 8: Project Name ==========
function getProjectName(files, projectRoot) {
    // 1. package.json name
    const pkgPath = files.find(f => f === 'frontend/package.json' || f === 'package.json');
    if (pkgPath) {
        try {
            const pkg = JSON.parse(fs.readFileSync(path.join(projectRoot, pkgPath), 'utf8'));
            if (pkg.name) return pkg.name;
        } catch (e) {}
    }

    // 2. Cargo.toml
    const cargoPath = files.find(f => f.endsWith('Cargo.toml'));
    if (cargoPath) {
        try {
            const content = fs.readFileSync(path.join(projectRoot, cargoPath), 'utf8');
            const m = content.match(/\[package\]\s*\n\s*name\s*=\s*"([^"]+)"/);
            if (m) return m[1];
        } catch (e) {}
    }

    // 3. go.mod
    const goModPath = files.find(f => f.endsWith('go.mod'));
    if (goModPath) {
        try {
            const content = fs.readFileSync(path.join(projectRoot, goModPath), 'utf8');
            const m = content.match(/module\s+(\S+)/);
            if (m) {
                const parts = m[1].split('/');
                return parts[parts.length - 1];
            }
        } catch (e) {}
    }

    // 4. pyproject.toml
    const pyprojectPath = files.find(f => f.endsWith('pyproject.toml'));
    if (pyprojectPath) {
        try {
            const content = fs.readFileSync(path.join(projectRoot, pyprojectPath), 'utf8');
            let m = content.match(/\[project\]\s*\n(?:[^\[]*\n)*?name\s*=\s*"([^"]+)"/);
            if (!m) m = content.match(/\[tool\.poetry\]\s*\n(?:[^\[]*\n)*?name\s*=\s*"([^"]+)"/);
            if (m) return m[1];
        } catch (e) {}
    }

    // 5. Directory name
    const parts = projectRoot.replace(/\\/g, '/').split('/').filter(Boolean);
    return parts[parts.length - 1];
}

// ========== STEP 9: Import Resolution ==========
function resolveImports(files, fileMap, projectRoot) {
    const importMap = {};

    for (const f of files) {
        importMap[f] = [];
    }

    function tryResolve(baseDir, importPath) {
        const probes = ['.ts', '.tsx', '.js', '.jsx', '/index.ts', '/index.js', '/index.tsx', '/index.jsx', '.py', '.go', '.rs', '.rb', '.vue'];
        const ext = path.extname(importPath);
        const hasExt = ext !== '';

        if (hasExt) {
            const resolved = path.resolve(baseDir, importPath).replace(/\\/g, '/');
            const relPath = path.relative(PROJECT_ROOT.replace(/\\/g, '/'), resolved).replace(/\\/g, '/');
            if (fileMap.has(relPath)) return relPath;
            // Also try the raw relative from root
            if (fileMap.has(importPath)) return importPath;
            return null;
        }

        const candidates = [importPath]; // Try bare path first
        for (const probe of probes) {
            candidates.push(importPath + probe);
        }

        for (const candidate of candidates) {
            try {
                const resolved = path.resolve(baseDir, candidate).replace(/\\/g, '/');
                const relPath = path.relative(PROJECT_ROOT.replace(/\\/g, '/'), resolved).replace(/\\/g, '/');
                if (fileMap.has(relPath)) return relPath;
            } catch (e) {}
        }

        return null;
    }

    // Read tsconfig for path aliases
    let tsconfigAliases = null;
    let tsconfigBaseUrl = null;
    const tsconfigPath = files.find(f => f.includes('tsconfig.json') && !f.includes('node_modules'));
    if (tsconfigPath) {
        try {
            const tsconfig = JSON.parse(fs.readFileSync(path.join(projectRoot, tsconfigPath), 'utf8'));
            if (tsconfig.compilerOptions && tsconfig.compilerOptions.paths) {
                tsconfigAliases = tsconfig.compilerOptions.paths;
                tsconfigBaseUrl = tsconfig.compilerOptions.baseUrl || path.dirname(tsconfigPath);
            }
        } catch (e) {}
    }

    // Read go.mod for module path
    let goModulePath = null;
    const goModPath = files.find(f => f.endsWith('go.mod'));
    if (goModPath) {
        try {
            const content = fs.readFileSync(path.join(projectRoot, goModPath), 'utf8');
            const m = content.match(/module\s+(\S+)/);
            if (m) goModulePath = m[1];
        } catch (e) {}
    }

    // Read composer.json for PHP PSR-4
    let composerAutoload = null;
    const composerPath = files.find(f => f.endsWith('composer.json'));
    if (composerPath) {
        try {
            const composer = JSON.parse(fs.readFileSync(path.join(projectRoot, composerPath), 'utf8'));
            if (composer.autoload && composer.autoload['psr-4']) {
                composerAutoload = composer.autoload['psr-4'];
            }
        } catch (e) {}
    }

    for (const file of files) {
        const category = detectCategory(file);
        if (category !== 'code') continue;

        try {
            const content = fs.readFileSync(path.join(projectRoot, file), 'utf8');
            const lang = detectLanguage(file);
            const baseDir = path.dirname(path.join(projectRoot, file));
            const imports = new Set();

            if (lang === 'typescript' || lang === 'javascript' || lang === 'vue') {
                // Relative imports: import ... from './...' or require('./...')
                const relPattern = /(?:import|require)\s*(?:\(|[{}\w\s,]*from\s*)?['"](\.\.?\/[^'"]+)['"]/g;
                let m;
                while ((m = relPattern.exec(content)) !== null) {
                    const resolved = tryResolve(baseDir, m[1]);
                    if (resolved && resolved !== file) imports.add(resolved);
                }
                // Dynamic imports: import('./...')
                const dynPattern = /import\s*\(\s*['"](\.\.?\/[^'"]+)['"]\s*\)/g;
                while ((m = dynPattern.exec(content)) !== null) {
                    const resolved = tryResolve(baseDir, m[1]);
                    if (resolved && resolved !== file) imports.add(resolved);
                }
                // Path aliases from tsconfig
                if (tsconfigAliases) {
                    const aliasImportPattern = /(?:import|require)\s*(?:\(|[{}\w\s,]*from\s*)?['"]([^'"]+)['"]/g;
                    while ((m = aliasImportPattern.exec(content)) !== null) {
                        const importPath = m[1];
                        if (importPath.startsWith('.')) continue;
                        for (const [aliasDef, targets] of Object.entries(tsconfigAliases)) {
                            // Strip only trailing *, keep the / if present (e.g. @/* -> @/)
                            const aliasKey = aliasDef.replace(/\*$/, '');
                            if (importPath.startsWith(aliasKey) && aliasKey.length > 0) {
                                const rest = importPath.slice(aliasKey.length);
                                for (const target of targets) {
                                    const resolvedTarget = target.replace(/\*$/, rest);
                                    const base = path.resolve(path.dirname(path.join(projectRoot, tsconfigPath)), tsconfigBaseUrl || '.').replace(/\\/g, '/');
                                    const resolved = tryResolve(base, resolvedTarget);
                                    if (resolved && resolved !== file) imports.add(resolved);
                                }
                            }
                        }
                    }
                }
            } else if (lang === 'python') {
                // Relative imports: from .x import y, from ..x import y
                const relPattern = /from\s+(\.\.?[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\s+import/g;
                let m;
                while ((m = relPattern.exec(content)) !== null) {
                    const relImport = m[1];
                    let parts_ = relImport.split('.');
                    let backCount = 0;
                    while (parts_[0] === '') { backCount++; parts_.shift(); }
                    const modulePath = parts_.join('/');
                    let targetDir = baseDir;
                    for (let i = 0; i < backCount; i++) targetDir = path.dirname(targetDir);
                    const candidates = [
                        modulePath.replace(/\./g, '/') + '.py',
                        modulePath.replace(/\./g, '/') + '/__init__.py'
                    ];
                    for (const c of candidates) {
                        const resolved = tryResolve(targetDir, c);
                        if (resolved && resolved !== file) imports.add(resolved);
                    }
                }

                // Absolute imports: from a.b.c import x (capture a.b.c)
                const fromPattern = /(?:^|\n)from\s+([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\s+import/gm;
                while ((m = fromPattern.exec(content)) !== null) {
                    const importPath = m[1];
                    if (importPath.startsWith('.')) continue;
                    const moduleParts = importPath.split('.');
                    for (let len = moduleParts.length; len >= 1; len--) {
                        const modulePath = moduleParts.slice(0, len).join('/');
                        const candidates = [modulePath + '.py', modulePath + '/__init__.py'];
                        let found = false;
                        for (const c of candidates) {
                            if (fileMap.has(c)) {
                                if (c !== file) imports.add(c);
                                found = true;
                            }
                        }
                        if (found) break;
                    }
                }
                // Absolute imports: import a.b.c (capture a.b.c)
                const importPattern = /(?:^|\n)import\s+([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)/gm;
                while ((m = importPattern.exec(content)) !== null) {
                    const importPath = m[1];
                    if (importPath.startsWith('.')) continue;
                    const moduleParts = importPath.split('.');
                    for (let len = moduleParts.length; len >= 1; len--) {
                        const modulePath = moduleParts.slice(0, len).join('/');
                        const candidates = [modulePath + '.py', modulePath + '/__init__.py'];
                        let found = false;
                        for (const c of candidates) {
                            if (fileMap.has(c)) {
                                if (c !== file) imports.add(c);
                                found = true;
                            }
                        }
                        if (found) break;
                    }
                }
            } else if (lang === 'go') {
                if (goModulePath) {
                    const importPattern = /"([^"]+)"/g;
                    const importBlocks = content.match(/import\s*(?:\((.*?)\)|"([^"]+)")/gs);
                    if (importBlocks) {
                        for (const block of importBlocks) {
                            let m;
                            while ((m = importPattern.exec(block)) !== null) {
                                const importPath = m[1];
                                if (importPath.startsWith(goModulePath)) {
                                    const relativePath = importPath.slice(goModulePath.length).replace(/^\//, '');
                                    const candidates = [relativePath, relativePath + '.go', relativePath + '/index.go'];
                                    for (const c of candidates) {
                                        if (fileMap.has(c) && c !== file) imports.add(c);
                                    }
                                }
                            }
                        }
                    }
                }
            } else if (lang === 'rust') {
                const cratePattern = /use\s+crate::(\S+?)\s*;/g;
                let m;
                while ((m = cratePattern.exec(content)) !== null) {
                    const cratePath = m[1].replace(/::/g, '/') + '.rs';
                    const srcTry = tryResolve(path.join(projectRoot, 'src'), cratePath);
                    if (srcTry && srcTry !== file) imports.add(srcTry);
                }
                const superPattern = /use\s+super::(\S+?)\s*;/g;
                while ((m = superPattern.exec(content)) !== null) {
                    const superPath = m[1].replace(/::/g, '/') + '.rs';
                    const resolved = tryResolve(baseDir, '../' + superPath);
                    if (resolved && resolved !== file) imports.add(resolved);
                }
                const modPattern = /mod\s+(\w+)\s*;/g;
                while ((m = modPattern.exec(content)) !== null) {
                    const modName = m[1];
                    const candidates = [modName + '.rs', modName + '/mod.rs'];
                    for (const c of candidates) {
                        const resolved = tryResolve(baseDir, c);
                        if (resolved && resolved !== file) imports.add(resolved);
                    }
                }
            } else if (lang === 'java') {
                const importPattern = /import\s+([a-zA-Z_][\w.]*(?:\.[A-Z][\w]*)+)\s*;/g;
                let m;
                while ((m = importPattern.exec(content)) !== null) {
                    const classPath = m[1];
                    const filePath = classPath.replace(/\./g, '/') + '.java';
                    for (const f of files) {
                        if (f.endsWith('/' + filePath) || f === filePath) {
                            if (f !== file) imports.add(f);
                            break;
                        }
                    }
                }
            } else if (lang === 'kotlin') {
                const importPattern = /import\s+([a-zA-Z_][\w.]*(?:\.[A-Z][\w]*)+)\s*$/gm;
                let m;
                while ((m = importPattern.exec(content)) !== null) {
                    const classPath = m[1];
                    const filePath = classPath.replace(/\./g, '/') + '.kt';
                    for (const f of files) {
                        if (f.endsWith('/' + filePath) || f === filePath) {
                            if (f !== file) imports.add(f);
                            break;
                        }
                    }
                }
            } else if (lang === 'ruby') {
                const relPattern = /require_relative\s+['"]([^'"]+)['"]/g;
                let m;
                while ((m = relPattern.exec(content)) !== null) {
                    const resolved = tryResolve(baseDir, m[1]);
                    if (resolved && resolved !== file) imports.add(resolved);
                }
                const reqPattern = /require\s+['"]([^'"]+)['"]/g;
                while ((m = reqPattern.exec(content)) !== null) {
                    const reqPath = m[1];
                    if (reqPath.startsWith('.')) continue;
                    const candidates = ['lib/' + reqPath + '.rb', 'app/' + reqPath + '.rb', reqPath + '.rb'];
                    for (const c of candidates) {
                        if (fileMap.has(c) && c !== file) {
                            imports.add(c);
                            break;
                        }
                    }
                }
            } else if (lang === 'php') {
                if (composerAutoload) {
                    const usePattern = /use\s+([A-Z][\w\\]+)\s*;/g;
                    let m;
                    while ((m = usePattern.exec(content)) !== null) {
                        const fullClass = m[1];
                        for (const [namespace, dir] of Object.entries(composerAutoload)) {
                            const nsPrefix = namespace.replace(/\\$/, '');
                            if (fullClass.startsWith(nsPrefix)) {
                                const rest = fullClass.slice(nsPrefix.length).replace(/^\\/, '');
                                const filePath = dir.replace(/\/$/, '') + '/' + rest.replace(/\\/g, '/') + '.php';
                                if (fileMap.has(filePath) && filePath !== file) {
                                    imports.add(filePath);
                                    break;
                                }
                            }
                        }
                    }
                }
            } else if (lang === 'cpp' || lang === 'c') {
                const includePattern = /#include\s+["<]([^">]+)[">]/g;
                let m;
                while ((m = includePattern.exec(content)) !== null) {
                    const includePath = m[1];
                    const candidates = [includePath, 'include/' + includePath, 'src/' + includePath];
                    for (const c of candidates) {
                        const resolved = tryResolve(baseDir, c);
                        if (resolved && resolved !== file) imports.add(resolved);
                        if (fileMap.has(c) && c !== file) imports.add(c);
                    }
                }
            }

            importMap[file] = [...imports].sort();
        } catch (e) {
            importMap[file] = [];
        }
    }

    return importMap;
}

// ========== MAIN ==========
function main() {
    // Step 1: Discover files (excluding deleted from working tree)
    const { files: allFiles, deleted: deletedFiles } = discoverFiles();
    console.error('Existing files: ' + allFiles.length + ', deleted from disk: ' + deletedFiles.length);

    // Step 2: Hardcoded exclusion
    let filteredFiles = allFiles.filter(f => !shouldExcludeHardcoded(f));
    const hardcodedRemoved = allFiles.length - filteredFiles.length;
    console.error('After hardcoded exclusion: ' + filteredFiles.length + ' files (removed ' + hardcodedRemoved + ')');

    // Step 2.5: User-configured filtering
    let filteredByIgnore = 0;
    const ignoreFilter = createIgnoreFilter(PROJECT_ROOT);
    if (ignoreFilter) {
        // Apply to original list (allFiles) to correctly handle negation patterns
        const afterFilter = allFiles.filter(f => !ignoreFilter(f));
        filteredByIgnore = filteredFiles.length - afterFilter.length;
        filteredFiles = afterFilter;
        console.error('After .understandignore filter: ' + filteredFiles.length + ' files (delta from hardcoded: ' + filteredByIgnore + ')');
    }

    // Sort files alphabetically
    filteredFiles.sort();

    // Step 3 & 4: Language detection and category detection
    const fileRecords = [];
    const languages = new Set();
    for (const f of filteredFiles) {
        const lang = detectLanguage(f);
        const category = detectCategory(f);
        languages.add(lang);
        fileRecords.push({ path: f, language: lang, category });
    }

    // Step 5: Line counting (using Node.js, no wc)
    const lineCounts = countLines(filteredFiles);
    for (const rec of fileRecords) {
        rec.sizeLines = lineCounts[rec.path] || 0;
    }

    // Step 6: Framework detection
    const frameworks = detectFrameworks(filteredFiles, PROJECT_ROOT);

    // Step 7: Complexity
    const totalFiles = filteredFiles.length;
    const complexity = estimateComplexity(totalFiles);

    // Step 8: Project name
    const name = getProjectName(filteredFiles, PROJECT_ROOT);

    // Step 9: Import resolution
    const fileMap = new Map(filteredFiles.map(f => [f, true]));
    const importMap = resolveImports(filteredFiles, fileMap, PROJECT_ROOT);

    // Step 10: Read description
    let rawDescription = '';
    const pkgPath = filteredFiles.find(f => f === 'frontend/package.json' || f === 'package.json');
    if (pkgPath) {
        try {
            const pkg = JSON.parse(fs.readFileSync(path.join(PROJECT_ROOT, pkgPath), 'utf8'));
            rawDescription = pkg.description || '';
        } catch (e) {}
    }

    // Step 11: Read README head
    let readmeHead = '';
    const readmePath = filteredFiles.find(f => f.toLowerCase().endsWith('readme.md'));
    if (readmePath) {
        try {
            const content = fs.readFileSync(path.join(PROJECT_ROOT, readmePath), 'utf8');
            readmeHead = content.split('\n').slice(0, 10).join('\n');
        } catch (e) {}
    }

    // Build output
    const output = {
        scriptCompleted: true,
        name: name,
        rawDescription: rawDescription,
        readmeHead: readmeHead,
        languages: [...languages].sort(),
        frameworks: frameworks,
        files: fileRecords.map(r => ({
            path: r.path,
            language: r.language,
            sizeLines: r.sizeLines,
            fileCategory: r.category
        })),
        totalFiles: totalFiles,
        filteredByIgnore: Math.max(0, filteredByIgnore),
        estimatedComplexity: complexity,
        importMap: importMap
    };

    // Write output
    fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2), 'utf8');
    console.error('Scan complete. Total: ' + totalFiles + ' files. Output: ' + OUTPUT_FILE);
}

main();
