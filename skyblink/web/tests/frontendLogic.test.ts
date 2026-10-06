import { expect, test } from 'vitest';
import { encodeViewerState, snapToAvailableBand, applyDivergingColormap } from '../src/utils/frontendLogic';

test('URL state encoding', () => {
    const str = encodeViewerState({ mode: 'blink', viewMode: 'detective', candidate: 'C001' });
    expect(str).toContain('mode=blink');
    expect(str).toContain('viewMode=detective');
    expect(str).toContain('candidate=C001');
});

test('band snapping', () => {
    const bands = [1.25, 2.20, 3.30, 4.27];
    expect(snapToAvailableBand(2.0, bands)).toBe(2.20);
    expect(snapToAvailableBand(4.0, bands)).toBe(4.27);
});

test('diverging colormap', () => {
    expect(applyDivergingColormap(-1.0)).toEqual([255, 0, 0]);
    expect(applyDivergingColormap(1.0)).toEqual([0, 0, 255]);
    expect(applyDivergingColormap(0)).toEqual([0, 0, 0]);
});
