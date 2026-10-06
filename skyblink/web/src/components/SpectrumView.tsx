'use client';
import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts';

export default function SpectrumView({ candidateId }: { candidateId: string }) {
    const [features, setFeatures] = useState<any[]>([]);
    
    useEffect(() => {
        fetch('/physics/features.json')
            .then(res => res.json())
            .then(setFeatures)
            .catch(console.error);
    }, []);

    const data = Array.from({ length: 50 }, (_, i) => {
        const wave = 0.75 + (i * 0.1);
        let flux = 100 - (wave - 2.5)**2 * 10;
        // Inject CO2 bump if it's the fictional comet
        if (Math.abs(wave - 4.27) < 0.2) {
            flux += 80;
        }
        return { wave: parseFloat(wave.toFixed(2)), flux };
    });

    return (
        <div className="w-full h-64 bg-gray-800 border border-gray-700 rounded-lg p-4 mt-4">
            <h3 className="text-lg font-bold mb-4 text-gray-200">Spectrum Analysis</h3>
            <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="wave" stroke="#9ca3af" />
                        <YAxis stroke="#9ca3af" />
                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', color: '#fff' }} />
                        <Line type="monotone" dataKey="flux" stroke="#8b5cf6" strokeWidth={2} dot={false} />
                        {features.map(f => (
                            <ReferenceLine key={f.name} x={f.wavelength_um} stroke="#ef4444" strokeDasharray="3 3" label={{ value: f.name, fill: '#ef4444', position: 'insideTopLeft' }} />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
            </div>
            
            {/* Follow an object frame strip */}
            <div className="mt-4 pt-4 border-t border-gray-700">
                <h4 className="text-sm font-bold text-gray-400 mb-2">Follow-an-Object</h4>
                <div className="flex gap-2">
                    {[1, 2, 3, 4].map(frame => (
                        <div key={frame} className="relative w-16 h-16 bg-black border border-gray-600 rounded flex items-center justify-center">
                            <span className="text-xs text-gray-500">Epoch {frame}</span>
                            {/* Predicted position marker */}
                            <div className="absolute w-2 h-2 rounded-full border border-red-500 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
