export function diatomicVibration(k: number, m1: number, m2: number): number {
    const amu_kg = 1.66053906660e-27;
    const c = 299792458 * 100;
    const mu = (m1 * m2) / (m1 + m2) * amu_kg;
    return (1 / (2 * Math.PI * c)) * Math.sqrt(k / mu);
}

export function wienPeak(t: number): number {
    return 2897.8 / t;
}

export function dimming(d1: number, d2: number): number {
    return Math.pow(d2 / d1, 4);
}

export function parallax(d: number): number {
    return 412530.0 / d;
}
