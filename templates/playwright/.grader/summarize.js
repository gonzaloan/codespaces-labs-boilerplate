// Reads grader-results-raw.json (Playwright JSON reporter format)
// Writes grader-results.json (boilerplate standard format)
// Writes grader-report.md (PR comment)

const fs   = require('fs');
const path = require('path');

const ROOT     = process.cwd();
const RAW_FILE = path.join(ROOT, 'grader-results-raw.json');
const OUT_JSON = path.join(ROOT, 'grader-results.json');
const OUT_MD   = path.join(ROOT, 'grader-report.md');

// ---------------------------------------------------------------------------
// Rubric — points per category.
// These values MUST match the per-file point totals configured in GitHub
// Classroom (one autograder test per file, e.g. structure.spec.ts → 6 pts).
// Add or adjust categories to match the specific lab's test files.
// ---------------------------------------------------------------------------

const CATEGORY_POINTS = {
    'Structure': 6,
    'Execution': 17,
    'Quality':   6,
};

const TOTAL_POINTS = Object.values(CATEGORY_POINTS).reduce((a, b) => a + b, 0);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function extractHint(spec) {
    const msg = spec.tests?.[0]?.results?.[0]?.error?.message ?? '';
    if (!msg) return null;

    // Strip ANSI color codes
    const clean = msg.replace(/\x1b\[[0-9;]*m/g, '');
    const lines = clean.split('\n').map(l => l.trim()).filter(l => l.length > 0);

    // Playwright puts the custom expect message on the first line — prefer it
    if (lines[0] && !lines[0].startsWith('expect(') && !lines[0].startsWith('Error:')) {
        return lines[0].slice(0, 400);
    }

    // Fall back: first 3 lines joined
    return lines.slice(0, 3).join(' · ').slice(0, 400) || null;
}

function progressBar(score, total) {
    if (total === 0) return '`░░░░░░░░░░`';
    const filled = Math.round((score / total) * 10);
    return '`' + '█'.repeat(filled) + '░'.repeat(10 - filled) + '`';
}

function statusMessage(pct) {
    if (pct === 100) return 'Perfect score! Excellent work!';
    if (pct >= 80)   return 'Almost there — just a few more to fix!';
    if (pct >= 50)   return 'Good progress, keep going!';
    if (pct >= 20)   return "You've started! Keep building.";
    return 'Time to write some code!';
}

function catIcon(cat) {
    if (cat.score === cat.total) return '✅';
    if (cat.score === 0)         return '❌';
    return '⚠️';
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

function renderAiSection(ai) {
    if (!ai.evaluated) {
        const reason = ai.reason || 'AI Review: not configured.';
        return `\n---\n\n> ${reason}\n\n`;
    }
    const artifactLabel = path.basename(ai.artifact || 'artifact');
    const total = ai.total_score ?? 0;
    const maxS = ai.max_score ?? 0;
    let md = `\n---\n\n### AI Review — ${artifactLabel}   ${total} / ${maxS}\n\n`;
    md += '> *Coaching feedback — not included in your automated score.*\n\n';
    const summary = ai.summary || '';
    if (summary) {
        md += `> **Overall:** ${summary}\n\n`;
    }
    const criteria = ai.criteria || [];
    criteria.forEach((criterion, i) => {
        const openAttr = i === 0 ? ' open' : '';
        md += `<details${openAttr}>\n`;
        md += `<summary><b>${criterion.name}</b> — ${criterion.score} / ${criterion.max}</summary>\n\n`;
        md += `**Strength:** ${criterion.strength || ''}\n\n`;
        md += `**Gap:** ${criterion.gap || ''}\n\n`;
        md += `**Action:** ${criterion.action || ''}\n\n`;
        md += '</details>\n\n';
    });
    return md;
}

// ---------------------------------------------------------------------------
// Read raw results
// ---------------------------------------------------------------------------

let raw;
try {
    raw = JSON.parse(fs.readFileSync(RAW_FILE, 'utf-8'));
} catch (e) {
    console.error('Could not read grader-results-raw.json:', e.message);
    process.exit(1);
}

// ---------------------------------------------------------------------------
// Parse Playwright JSON format: suites[file].suites[describe].specs[]
// ---------------------------------------------------------------------------

const categories = [];

for (const fileSuite of raw.suites ?? []) {
    for (const describeSuite of fileSuite.suites ?? []) {
        const checks = (describeSuite.specs ?? []).map(spec => ({
            name:   spec.title,
            passed: spec.ok,
            hint:   spec.ok ? null : extractHint(spec),
        }));

        const score    = checks.filter(c => c.passed).length;
        const total    = checks.length;
        const maxPts   = CATEGORY_POINTS[describeSuite.title] ?? 0;
        const points   = total > 0 && maxPts > 0
            ? Math.round((score / total) * maxPts * 10) / 10
            : 0;

        categories.push({
            name:      describeSuite.title,
            score,
            total,
            points,
            maxPoints: maxPts,
            checks,
        });
    }
}

const totalPtsEarned = Math.round(categories.reduce((sum, c) => sum + c.points, 0) * 10) / 10;
const durationMs     = raw.stats?.duration ?? 0;
const labName        = path.basename(ROOT);

// ---------------------------------------------------------------------------
// Write grader-results.json
// ---------------------------------------------------------------------------

const results = {
    lab:        labName,
    score:      totalPtsEarned,
    total:      TOTAL_POINTS,
    duration:   durationMs,
    categories,
};

fs.writeFileSync(OUT_JSON, JSON.stringify(results, null, 2));
console.log(`grader-results.json written (${totalPtsEarned}/${TOTAL_POINTS} pts)`);

// ---------------------------------------------------------------------------
// Write grader-report.md
// ---------------------------------------------------------------------------

const pct            = TOTAL_POINTS > 0 ? Math.round((totalPtsEarned / TOTAL_POINTS) * 100) : 0;
const hasStudentCode = detectStudentCode();

let md = '## Lab Grader Results\n\n';
md += `> **Score: ${totalPtsEarned} / ${TOTAL_POINTS} pts (${pct}%)** — ${statusMessage(pct)}\n`;
md += `> ${progressBar(totalPtsEarned, TOTAL_POINTS)}\n\n`;
md += '---\n\n';

// Summary table
md += '### Score Breakdown\n\n';
md += '| | Category | Points | Checks |\n';
md += '|---|---|---|---|\n';
for (const cat of categories) {
    const icon      = catIcon(cat);
    const checksStr = cat.score < cat.total ? `${cat.score}/${cat.total}` : 'all passing';
    md += `| ${icon} | **${cat.name}** | ${cat.points} / ${cat.maxPoints} | ${checksStr} |\n`;
}
md += '\n---\n\n';

if (!hasStudentCode) {
    md += '### Getting Started\n\n';
    md += "*It looks like you haven't added any code yet — here's where to begin:*\n\n";
    md += '1. Read `docs/instructions.md` for the full exercise description\n';
    md += '2. Add your code inside the `src/` directory\n';
    md += '3. Run `npm test` locally to verify before pushing\n\n';
    md += '---\n\n';
}

// Per-category detail sections
md += '### Details\n\n';

for (const cat of categories) {
    const icon      = catIcon(cat);
    const ptsLabel  = `${cat.points} / ${cat.maxPoints} pts`;
    const chkLabel  = `${cat.score}/${cat.total} checks`;
    const failing   = cat.checks.filter(c => !c.passed);

    md += '<details>\n';
    md += `<summary>${icon} <b>${cat.name}</b> — ${ptsLabel} — ${chkLabel}</summary>\n\n`;

    md += '| Check | Status | Hint |\n';
    md += '|---|---|---|\n';
    for (const check of cat.checks) {
        const status = check.passed ? '✅ Pass' : '❌ Fail';
        const hint   = check.hint ?? '';
        md += `| ${check.name} | ${status} | ${hint} |\n`;
    }

    if (failing.length > 0) {
        md += '\n**What to fix:**\n';
        for (const check of failing) {
            const hintText = check.hint ? ` — ${check.hint}` : '';
            md += `- \`${check.name}\`${hintText}\n`;
        }
    }

    md += '\n</details>\n\n';
}

md += '---\n\n';
md += '### Resources\n\n';
md += '- [Playwright Locators](https://playwright.dev/docs/locators)\n';
md += '- [Page Object Model](https://playwright.dev/docs/pom)\n';
md += '- [Assertions reference](https://playwright.dev/docs/test-assertions)\n';
md += '- Lab instructions: `docs/instructions.md`\n';

const aiFile = path.join(ROOT, 'ai-feedback.json');
let ai = { evaluated: false, reason: 'AI Review: not configured — set PORTKEY_API_KEY to enable.' };
if (fs.existsSync(aiFile)) {
    try { ai = JSON.parse(fs.readFileSync(aiFile, 'utf-8')); } catch (_) {}
}
md += renderAiSection(ai);

fs.writeFileSync(OUT_MD, md);
console.log('grader-report.md written');
