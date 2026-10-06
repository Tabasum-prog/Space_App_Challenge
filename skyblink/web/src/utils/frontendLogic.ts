export function encodeViewerState(state: any): string {
    const params = new URLSearchParams();
    if (state.mode) params.set('mode', state.mode);
    if (state.viewMode) params.set('viewMode', state.viewMode);
    if (state.candidate) params.set('candidate', state.candidate);
    return params.toString();
}

export function snapToAvailableBand(requested: number, availableBands: number[]): number {
    return availableBands.reduce((prev, curr) => 
        Math.abs(curr - requested) < Math.abs(prev - requested) ? curr : prev
    );
}

export function applyDivergingColormap(value: number): [number, number, number] {
    // -1 to 1 to RGB
    const normalized = Math.max(-1, Math.min(1, value));
    if (normalized < 0) {
        // Red for negative
        return [Math.floor(255 * -normalized), 0, 0];
    } else {
        // Blue for positive
        return [0, 0, Math.floor(255 * normalized)];
    }
}
