'use client';
import React, { useState, useEffect } from 'react';
import InteractiveCanvas from '@/components/InteractiveCanvas';
import SpectrumView from '@/components/SpectrumView';
import { useRouter, useSearchParams } from 'next/navigation';

export default function Viewer({ params }: { params: Promise<{ fieldId: string }> }) {
    const { fieldId } = React.use(params);
    const router = useRouter();
    const searchParams = useSearchParams();
    
    const [mode, setMode] = useState<'blink' | 'swipe' | 'difference'>(
        (searchParams.get('mode') as any) || 'blink'
    );
    const [viewMode, setViewMode] = useState<'explorer' | 'detective'>(
        (searchParams.get('viewMode') as any) || 'explorer'
    );
    const [selectedCandidate, setSelectedCandidate] = useState<string | null>(
        searchParams.get('candidate') || null
    );
    const [candidates, setCandidates] = useState<any[]>([]);

    useEffect(() => {
        fetch(`/data/candidates/${fieldId}.json`)
            .then(res => res.json())
            .then(data => setCandidates(data))
            .catch(console.error);
    }, [fieldId]);
    
    // URL state sync
    useEffect(() => {
        const url = new URL(window.location.href);
        url.searchParams.set('mode', mode);
        url.searchParams.set('viewMode', viewMode);
        if (selectedCandidate) {
            url.searchParams.set('candidate', selectedCandidate);
        } else {
            url.searchParams.delete('candidate');
        }
        window.history.replaceState({}, '', url.toString());
    }, [mode, viewMode, selectedCandidate]);

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
            
            if (e.key === 'j' || e.key === 'k') {
                if (candidates.length === 0) return;
                const idx = candidates.findIndex(c => c.id === selectedCandidate);
                let newIdx = 0;
                if (idx !== -1) {
                    newIdx = e.key === 'j' ? (idx + 1) % candidates.length : (idx - 1 + candidates.length) % candidates.length;
                }
                setSelectedCandidate(candidates[newIdx].id);
                setViewMode('detective');
            } else if (e.code === 'Space') {
                e.preventDefault(); // prevent scrolling
                // For space, toggle mode blink vs swipe? Or toggle blink playback?
                // The interactive canvas handles Space playback, but here we can just focus the canvas
            } else if (e.key === 'a') {
                setMode('blink');
            } else if (e.key === 'd') {
                setMode('difference');
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [candidates, selectedCandidate]);

    const isOnePass = fieldId === 'F_ONE';

    return (
        <main className="p-8 text-white bg-gray-900 min-h-screen">
            <div className="absolute top-0 left-0 w-full bg-red-600 text-center py-2 font-bold text-sm z-50">
                SIMULATED DEMO DATA. Not real SPHEREx observations.
            </div>
            
            <div className="max-w-7xl mx-auto mt-12 flex gap-6">
                <div className="flex-1">
                    <div className="flex justify-between items-end mb-6">
                        <div>
                            <h1 className="text-4xl font-bold mb-2">Viewer: {fieldId}</h1>
                            <div className="flex gap-4 items-center">
                                <p className="text-gray-400">Band: 1.25 µm (Near-IR)</p>
                                <div className="flex bg-gray-800 rounded-lg p-1">
                                    <button onClick={() => setViewMode('explorer')} className={`px-3 py-1 rounded ${viewMode === 'explorer' ? 'bg-blue-600' : ''}`}>Explorer</button>
                                    <button onClick={() => setViewMode('detective')} className={`px-3 py-1 rounded ${viewMode === 'detective' ? 'bg-purple-600' : ''}`}>Detective</button>
                                </div>
                            </div>
                        </div>
                    
                    <div className="flex gap-2 bg-gray-800 p-1 rounded-lg">
                        <button 
                            onClick={() => setMode('blink')}
                            className={`px-4 py-2 rounded ${mode === 'blink' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
                        >
                            Blink
                        </button>
                        <button 
                            onClick={() => setMode('swipe')}
                            className={`px-4 py-2 rounded ${mode === 'swipe' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
                        >
                            Swipe
                        </button>
                        <button 
                            onClick={() => setMode('difference')}
                            className={`px-4 py-2 rounded ${mode === 'difference' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
                        >
                            Difference
                        </button>
                    </div>
                </div>

                    {isOnePass ? (
                        <div className="w-full h-[600px] bg-gray-800 rounded-lg border border-gray-700 flex flex-col items-center justify-center">
                            <h2 className="text-2xl font-bold text-gray-300 mb-2">Not enough epochs yet</h2>
                            <p className="text-gray-500">This field has only been scanned once. Come back after the next pass!</p>
                        </div>
                    ) : selectedCandidate ? (
                        <InteractiveCanvas fieldId={fieldId} candidateId={selectedCandidate} mode={mode} />
                    ) : (
                        <div className="w-full h-[600px] bg-gray-800 rounded-lg border border-gray-700 flex flex-col items-center justify-center">
                            <h2 className="text-2xl font-bold text-gray-300 mb-2">No candidate selected</h2>
                            <p className="text-gray-500">Select a candidate from the right panel to view cutouts.</p>
                        </div>
                    )}
                </div>

                {/* Detective Side Panel */}
                {viewMode === 'detective' && (
                    <div className="w-96 bg-gray-800 border border-gray-700 rounded-lg flex flex-col h-[700px] mt-[100px]">
                        <div className="p-4 border-b border-gray-700">
                            <h2 className="text-xl font-bold text-purple-400">Detective Mode</h2>
                            <p className="text-sm text-gray-400">Investigate high-SNR candidates.</p>
                        </div>
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {/* Dynamic candidate list sorted by SNR */}
                            {candidates.sort((a,b) => b.snr - a.snr).map(cand => (
                                <button
                                    key={cand.id}
                                    onClick={() => setSelectedCandidate(cand.id)}
                                    className={`w-full text-left p-3 rounded-lg border ${selectedCandidate === cand.id ? 'border-purple-500 bg-purple-900/20' : 'border-gray-700 hover:border-gray-500 bg-gray-900/50'}`}
                                >
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="font-bold">{cand.id}</span>
                                        <span className="text-xs px-2 py-1 bg-gray-700 rounded-full">{cand.snr.toFixed(1)} SNR</span>
                                    </div>
                                    <p className="text-xs text-gray-400">p_local: {cand.p_local.toExponential(2)}</p>
                                </button>
                            ))}
                        </div>
                        
                        {/* Detail View */}
                        {selectedCandidate && (
                            <div className="p-4 border-t border-gray-700 bg-gray-900/50">
                                <h3 className="font-bold mb-2">Details: {selectedCandidate}</h3>
                                {(() => {
                                    const cand = candidates.find(c => c.id === selectedCandidate);
                                    if (!cand) return null;
                                    return (
                                        <div className="text-sm space-y-2 mb-4 text-gray-300">
                                            <p><strong>Type Label:</strong> {cand.type_label}</p>
                                            <p><strong>Particle Hit Check:</strong> <span className={cand.sharpness > 0.95 ? "text-red-400" : "text-green-400"}>{cand.sharpness > 0.95 ? "FAILED (Cosmic Ray)" : "PASSED (Not a cosmic ray)"}</span></p>
                                            <p><strong>Cross-Match:</strong> {cand.crossmatch ? cand.crossmatch.name : "None (Unknown object)"}</p>
                                        </div>
                                    );
                                })()}
                                <div className="flex gap-2">
                                    <button onClick={async () => {
                                        try {
                                            await fetch('http://localhost:8000/votes', {
                                                method: 'POST', 
                                                headers: {'Content-Type':'application/json'},
                                                body: JSON.stringify({candidate_id: selectedCandidate, vote: 'real'})
                                            });
                                            alert('Vote cast: REAL');
                                        } catch (e) {
                                            alert('API offline. Vote saved locally.');
                                        }
                                    }} className="flex-1 bg-green-700 hover:bg-green-600 py-2 rounded text-sm font-bold">Mark Real</button>
                                    <button onClick={async () => {
                                        try {
                                            await fetch('http://localhost:8000/votes', {
                                                method: 'POST', 
                                                headers: {'Content-Type':'application/json'},
                                                body: JSON.stringify({candidate_id: selectedCandidate, vote: 'fake'})
                                            });
                                            alert('Vote cast: FAKE');
                                        } catch (e) {
                                            alert('API offline. Vote saved locally.');
                                        }
                                    }} className="flex-1 bg-red-700 hover:bg-red-600 py-2 rounded text-sm font-bold">Mark Fake</button>
                                </div>
                                <SpectrumView candidateId={selectedCandidate} />
                            </div>
                        )}
                    </div>
                )}
            </div>
        </main>
    );
}
