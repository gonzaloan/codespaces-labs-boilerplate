// Reads grader-results-raw.json (Playwright JSON reporter format)
// Writes grader-results.json (boilerplate standard format)
// Writes grader-report.md (PR comment)

const fs   = require('fs');
const path = require('path');

const ROOT     = process.cwd();
const RAW_FILE = path.join(ROOT, 'grader-results-raw.json');
const OUT_JSON = path.join(ROOT, 'grader-results.json');
const OUT_MD   = path.join(ROOT, 'grader-report.md');

// --- Read raw results ---

let raw;
try {
    raw = JSON.parse(fs.readFileSync(RAW_FILE, 'utf-8'));
} catch (e) {
    console.error('Could not read grader-results-raw.json:', e.message);
    process.exit(1);
}

// --- Parse Playwright JSON format: suites[file].suites[describe].specs[] ---

const categories = [];

for (const fileSuite of raw.suites ?? []) {
    for (const describeSuite of fileSuite.suites ?? []) {
        const checks = (describeSuite.specs ?? []).map(spec => ({
            name:   spec.title,
            passed: spec.ok,
            hint:   spec.ok ? null : extractHint(spec),
        }));
        categories.push({
            name:  describeSuite.title,
            score: checks.filter(c => c.passed).length,
            total: checks.length,
            checks,
        });
    }
}

const totalScore    = categories.reduce((sum, c) => sum + c.score, 0);
const totalChecks   = categories.reduce((sum, c) => sum + c.total, 0);
const durationMs    = raw.stats?.duration ?? 0;
const labName       = path.basename(ROOT);

// --- Write grader-results.json ---

const results = {
    lab:        labName,
    score:      totalScore,
    total:      totalChecks,
    duration:   durationMs,
    categories,
};

fs.writeFileSync(OUT_JSON, JSON.stringify(results, null, 2));
console.log(`grader-results.json written (${totalScore}/${totalChecks})`);

// --- Write grader-report.md ---

const pct          = totalChecks > 0 ? Math.round((totalScore / totalChecks) * 100) : 0;
const hasStudentCode = detectStudentCode();

let md = '## 🎓 Lab Grader Results\n\n';
md += `> **Score: ${totalScore} / ${totalChecks} checks passed (${pct}%)** — ${statusMessage(pct)}\n`;
md += `> ${progressBar(totalScore, totalChecks)}\n\n`;
md += '---\n\n';

if (!hasStudentCode) {
    md += '### 🚀 Getting Started\n\n';
    md += "*It looks like you haven't added any code yet — here's where to begin:*\n\n";
    md += '1. Read `docs/instructions.md` for the full exercise description\n';
    md += '2. Add your code inside the `src/` directory\n';
    md += '3. Run `npm test` locally to verify before pushing\n\n';
    md += '---\n\n';
}

for (const cat of categories) {
    const summaryIcon = cat.score === cat.total ? '✅' : cat.score === 0 ? '❌' : '⚠️';

    md += '<details>\n';
    md += `<summary>${summaryIcon} ${cat.name} — ${cat.score}/${cat.total} passed</summary>\n\n`;
    md += '| Check | | Hint |\n';
    md += '|---|---|---|\n';

    for (const check of cat.checks) {
        const icon = check.passed ? '✅' : '❌';
        md += `| ${check.name} | ${icon} | ${check.hint ?? ''} |\n`;
    }

    md += '\n</details>\n\n';
}

md += '---\n\n';
md += '### 📚 Resources\n\n';
md += '- [Playwright Locators](https://playwright.dev/docs/locators)\n';
md += '- [Page Object Model](https://playwright.dev/docs/pom)\n';
md += '- [Assertions reference](https://playwright.dev/docs/test-assertions)\n';
md += '- Lab instructions: `docs/instructions.md`\n';

fs.writeFileSync(OUT_MD, md);
console.log('grader-report.md written');

// --- Helpers ---

function extractHint(spec) {
    const msg = spec.tests?.[0]?.results?.[0]?.error?.message ?? '';
    if (!msg) return null;
    const clean = msg
        .replace(/\x1b\[[0-9;]*m/g, '')   // strip ANSI color codes
        .split('\n')
        .map(l => l.trim())
        .filter(l => l.length > 0)
        .slice(0, 3)
        .join(' · ');
    return clean || null;
}

function detectStudentCode() {
    const srcDir = path.join(ROOT, 'src');
    try {
        return hasFiles(srcDir, f => !f.endsWith('.gitkeep'));
    } catch {
        return false;
    }
}

function hasFiles(dir, predicate) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        if (entry.isDirectory()) {
            if (hasFiles(path.join(dir, entry.name), predicate)) return true;
        } else if (predicate(entry.name)) {
            return true;
        }
    }
    return false;
}

function progressBar(passed, total) {
    if (total === 0) return '`░░░░░░░░░░`';
    const filled = Math.round((passed / total) * 10);
    return '`' + '█'.repeat(filled) + '░'.repeat(10 - filled) + '`';
}

function statusMessage(pct) {
    if (pct === 100) return 'Perfect score! Excellent work!';
    if (pct >= 80)   return 'Almost there — just a few more to fix!';
    if (pct >= 50)   return 'Good progress, keep going!';
    if (pct >= 20)   return "You've started! Keep building.";
    return 'Time to write some code!';
}
