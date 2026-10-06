'use client';
import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts';

export default function SpectrumView({ candidateId }: { candidateId: string }) {
    const [features, setFeatures] = useState<any[]>([]);
    
    const [spectrumData, setSpectrumData] = useState<any[]>([]);
    const [trackData, setTrackData] = useState<any[]>([]);

    useEffect(() => {
        // Load features
        fetch('/physics/features.json')
            .then(res => res.json())
            .then(setFeatures)
            .catch(console.error);
            
        // Load pipeline JSONs
        Promise.all([
            fetch('/data/spectra.json').then(res => res.json()).catch(() => []),
            fetch('/data/follow_object.json').then(res => res.json()).catch(() => [])
        ]).then(([spectraFiles, followFiles]) => {
            // First we need to map candidateId to a true object id if possible.
            // If candidateId is already an object id like 'comet1', we use it.
            // Otherwise, we might need to find its crossmatch, but for simplicity, we check if candidateId matches any id in follow_object or spectra.
            let obj = spectraFiles.find((s: any) => s.id === candidateId) || followFiles.find((f: any) => f.id === candidateId);
            
            // If not found directly, maybe candidateId is a pipeline candidate ID (e.g. F_COMET_2.2_0).
            // We would need the candidate JSON to crossmatch, but we can also just see if we can fetch the candidate list for its field
            if (!obj) {
                const fieldId = candidateId.split('_').slice(0, 2).join('_'); // e.g. F_COMET
                fetch(`/data/candidates/${fieldId}.json`)
                    .then(res => res.json())
                    .then(cands => {
                        const cand = cands.find((c: any) => c.id === candidateId);
                        if (cand && cand.crossmatch && cand.crossmatch.id) {
                            const crossId = cand.crossmatch.id;
                            obj = spectraFiles.find((s: any) => s.id === crossId) || followFiles.find((f: any) => f.id === crossId);
                            if (obj) {
                                if (obj.spectrum) setSpectrumData(obj.spectrum);
                                if (obj.track) setTrackData(obj.track);
                            }
                        }
                    })
                    .catch(console.error);
            } else {
                if (obj.spectrum) setSpectrumData(obj.spectrum);
                if (obj.track) setTrackData(obj.track);
            }
        });
    }, [candidateId]);

    return (
        <div className="w-full h-64 bg-gray-800 border border-gray-700 rounded-lg p-4 mt-4">
            <h3 className="text-lg font-bold mb-4 text-gray-200">Spectrum Analysis</h3>
            <div className="h-48 w-full">
                {spectrumData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={spectrumData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis dataKey="wave" stroke="#9ca3af" type="number" domain={['dataMin - 0.5', 'dataMax + 0.5']} />
                            <YAxis stroke="#9ca3af" />
                            <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', color: '#fff' }} />
                            <Line type="monotone" dataKey="flux" stroke="#8b5cf6" strokeWidth={2} dot={true} />
                            {features.map(f => (
                                <ReferenceLine key={f.name} x={f.wavelength_um} stroke="#ef4444" strokeDasharray="3 3" label={{ value: f.name, fill: '#ef4444', position: 'insideTopLeft' }} />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="text-gray-500 flex items-center justify-center h-full">No spectrum data available.</div>
                )}
            </div>
            
            {/* Follow an object frame strip */}
            {trackData.length > 0 && (
                <div className="mt-8 pt-4 border-t border-gray-700">
                    <h4 className="text-sm font-bold text-gray-400 mb-2">Follow-an-Object</h4>
                    <div className="flex gap-2 overflow-x-auto">
                        {trackData.map((frame, idx) => (
                            <div key={idx} className="relative w-16 h-16 bg-black border border-gray-600 rounded flex-shrink-0 flex items-center justify-center overflow-hidden" title={`Pass: ${frame.pass}, Band: ${frame.band}, MJD: ${frame.mjd}`}>
                                {frame.image ? (
                                    <img src={frame.image} alt="cutout" className="w-full h-full object-cover" />
                                ) : (
                                    <span className="text-[10px] text-gray-500 text-center px-1">Epoch {idx+1}</span>
                                )}
                                {/* Predicted position marker */}
                                <div className="absolute w-2 h-2 rounded-full border border-red-500 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
