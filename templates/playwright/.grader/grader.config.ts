import { defineConfig } from '@playwright/test';

export default defineConfig({
    testDir: './checks',
    fullyParallel: false,
    retries: 0,
    workers: 1,
    reporter: [
        ['html', { outputFolder: '../grader-report', open: 'never' }],
        ['json', { outputFile: '../grader-results-raw.json' }],
        ['list'],
    ],
});