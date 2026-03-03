import { test, expect } from '@playwright/test';
import { existsSync, readdirSync } from 'fs';
import { join } from 'path';

const SRC_DIR = join(__dirname, '../../src');

test.describe('Project Structure Validation', () => {

    test('pages/ directory exists and has .ts files', () => {
        const pagesDir = join(SRC_DIR, 'pages');
        expect(existsSync(pagesDir), 'pages/ directory missing').toBe(true);

        const files = readdirSync(pagesDir).filter(f => f.endsWith('.ts'));
        expect(files.length, 'No Page Object files found in pages/').toBeGreaterThan(0);
    });

    test('tests/ directory exists and has .spec.ts files', () => {
        const testsDir = join(SRC_DIR, 'tests');
        expect(existsSync(testsDir), 'tests/ directory missing').toBe(true);

        const files = readdirSync(testsDir).filter(f => f.endsWith('.spec.ts'));
        expect(files.length, 'No spec files found in tests/').toBeGreaterThan(0);
    });

    test('data/ directory exists and has .json files', () => {
        const dataDir = join(SRC_DIR, 'data');
        expect(existsSync(dataDir), 'data/ directory missing').toBe(true);

        const files = readdirSync(dataDir).filter(f => f.endsWith('.json'));
        expect(files.length, 'No JSON data files found in data/').toBeGreaterThan(0);
    });

});