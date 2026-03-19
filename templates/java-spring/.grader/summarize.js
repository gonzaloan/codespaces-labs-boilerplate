// Reads Surefire XML reports from .grader/target/surefire-reports/
// Writes grader-results.json (boilerplate standard format)
// Writes grader-report.md (PR comment)

const fs   = require('fs');
const path = require('path');

const ROOT          = process.cwd();
const REPORTS_DIR   = path.join(__dirname, 'target', 'surefire-reports');
const OUT_JSON      = path.join(ROOT, 'grader-results.json');
const OUT_MD        = path.join(ROOT, 'grader-report.md');

// --- Parse Surefire XML files ---

const categories = [];

if (!fs.existsSync(REPORTS_DIR)) {
    console.error('No surefire-reports directory found. Did the grader run?');
    process.exit(1);
}

const xmlFiles = fs.readdirSync(REPORTS_DIR).filter(f => f.endsWith('.xml'));

for (const file of xmlFiles) {
    const content = fs.readFileSync(path.join(REPORTS_DIR, file), 'utf-8');

    const suiteMatch = content.match(/<testsuite[^>]+name="([^"]+)"[^>]*>/);
    if (!suiteMatch) continue;
    const suiteName = suiteMatch[1].replace(/.*\./, ''); // "grader.StructureTest.java" → "StructureTest.java"

    const checks = [];
    const testcaseRegex = /<testcase[^>]+\bname="([^"]+)"[^>]*>([\s\S]*?)<\/testcase>|<testcase[^>]+\bname="([^"]+)"[^>]*\/>/g;
    let match;

    while ((match = testcaseRegex.exec(content)) !== null) {
        const name    = match[1] ?? match[3];
        const body    = match[2] ?? '';
        const failed  = /<failure|<error/.test(body);
        const hint    = failed ? extractHint(body) : null;
        checks.push({ name, passed: !failed, hint });
    }

    if (checks.length > 0) {
        categories.push({
            name:  formatCategoryName(suiteName),
            score: checks.filter(c => c.passed).length,
            total: checks.length,
            checks,
        });
    }
}

const totalScore  = categories.reduce((sum, c) => sum + c.score, 0);
const totalChecks = categories.reduce((sum, c) => sum + c.total, 0);
const labName     = path.basename(ROOT);

// --- Write grader-results.json ---

const results = {
    lab:        labName,
    score:      totalScore,
    total:      totalChecks,
    duration:   0,
    categories,
};

fs.writeFileSync(OUT_JSON, JSON.stringify(results, null, 2));
console.log(`grader-results.json written (${totalScore}/${totalChecks})`);

// --- Write grader-report.md ---

const pct            = totalChecks > 0 ? Math.round((totalScore / totalChecks) * 100) : 0;
const hasStudentCode = detectStudentCode();

let md = '## 🎓 Lab Grader Results\n\n';
md += `> **Score: ${totalScore} / ${totalChecks} checks passed (${pct}%)** — ${statusMessage(pct)}\n`;
md += `> ${progressBar(totalScore, totalChecks)}\n\n`;
md += '---\n\n';

if (!hasStudentCode) {
    md += '### Getting Started\n\n';
    md += "*It looks like you haven't added any code yet — here's where to begin:*\n\n";
    md += '1. Read `docs/instructions.md` for the full exercise description\n';
    md += '2. Add your code inside `src/main/java/`\n';
    md += '3. Run `mvn test` locally to verify before pushing\n\n';
    md += '---\n\n';
}

for (const cat of categories) {
    const summaryIcon = cat.score === cat.total ? '✅' : cat.score === 0 ? '❌' : '⚠️  ';

    md += '<details>\n';
    md += `<summary>${summaryIcon} ${cat.name} — ${cat.score}/${cat.total} passed</summary>\n\n`;
    md += '| Check | | Hint |\n';
    md += '|---|---|---|\n';

    for (const check of cat.checks) {
        const icon = check.passed ? '✅' : '❌';
        md += `| ${formatCheckName(check.name)} | ${icon} | ${check.hint ?? ''} |\n`;
    }

    md += '\n</details>\n\n';
}

md += '---\n\n';
md += '### Resources\n\n';
md += '- [Spring Boot Reference](https://docs.spring.io/spring-boot/docs/current/reference/html/)\n';
md += '- [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/)\n';
md += '- Lab instructions: `docs/instructions.md`\n';

const aiFile = path.join(ROOT, 'ai-feedback.json');
let ai = { evaluated: false, reason: 'AI Review: not configured — set PORTKEY_API_KEY to enable.' };
if (fs.existsSync(aiFile)) {
    try { ai = JSON.parse(fs.readFileSync(aiFile, 'utf-8')); } catch (_) {}
}
md += renderAiSection(ai);

fs.writeFileSync(OUT_MD, md);
console.log('grader-report.md written');

// --- Helpers ---

function extractHint(body) {
    const msg = body.match(/<failure[^>]*message="([^"]*)"/) ??
        body.match(/<error[^>]*message="([^"]*)"/) ??
        body.match(/<failure[^>]*>([\s\S]*?)<\/failure>/) ??
        body.match(/<error[^>]*>([\s\S]*?)<\/error>/);
    if (!msg?.[1]) return null;
    return msg[1].replace(/\s+/g, ' ').trim().slice(0, 120) || null;
}

function formatCategoryName(className) {
    // "StructureTest.java" → "Structure"
    return className.replace(/Test$/, '');
}

function formatCheckName(methodName) {
    // "testSrcHasJavaFiles" → "src has Java files"
    return methodName
        .replace(/^test/, '')
        .replace(/([A-Z])/g, ' $1')
        .trim()
        .toLowerCase();
}

function detectStudentCode() {
    const srcDir = path.join(ROOT, 'src', 'main', 'java');
    try {
        return hasFiles(srcDir, f => f.endsWith('.java'));
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