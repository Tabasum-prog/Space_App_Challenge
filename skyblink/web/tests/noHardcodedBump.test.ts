import { expect, test } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

function walkDir(dir: string): string[] {
    let results: string[] = [];
    const list = fs.readdirSync(dir);
    list.forEach(file => {
        file = path.join(dir, file);
        const stat = fs.statSync(file);
        if (stat && stat.isDirectory()) { 
            results = results.concat(walkDir(file));
        } else {
            results.push(file);
        }
    });
    return results;
}

test('Frontend does not hardcode the 4.27um comet bump', () => {
    const srcDir = path.resolve(__dirname, '../src');
    const files = walkDir(srcDir);
    
    let foundHardcodedBump = false;
    for (const file of files) {
        if (file.endsWith('.ts') || file.endsWith('.tsx')) {
            const content = fs.readFileSync(file, 'utf8');
            // Check for tell-tale signs of a hardcoded Gaussian or bump for 4.27
            if (content.includes('4.27') && (content.includes('Math.exp') || content.includes('bump'))) {
                foundHardcodedBump = true;
                console.error(`Found hardcoded bump logic in ${file}`);
            }
        }
    }
    
    expect(foundHardcodedBump).toBe(false);
});
