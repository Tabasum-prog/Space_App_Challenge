export default function Physics() {
    return (
        <main className="p-12 text-white bg-gray-900 min-h-screen">
            <div className="absolute top-0 left-0 w-full bg-red-600 text-center py-2 font-bold text-sm z-50">
                SIMULATED DEMO DATA. Not real SPHEREx observations.
            </div>
            <h1 className="text-4xl font-bold mt-8 mb-4">Physics Lab</h1>
            <div className="grid grid-cols-2 gap-8">
                <div className="bg-gray-800 p-6 rounded-lg">
                    <h2 className="text-2xl font-bold mb-2">P3: Quantum Spectroscopy</h2>
                    <p className="text-gray-400">Vibration calculator and isotope slider (Missing full interactivity)</p>
                </div>
                <div className="bg-gray-800 p-6 rounded-lg">
                    <h2 className="text-2xl font-bold mb-2">P4: Nuclear Mass-Threshold</h2>
                    <p className="text-gray-400">Hydrogen/Deuterium/Lithium burning slider (Missing full interactivity)</p>
                </div>
                <div className="bg-gray-800 p-6 rounded-lg">
                    <h2 className="text-2xl font-bold mb-2">Planet X Detectability</h2>
                    <p className="text-orange-400 font-bold text-sm mb-2">WARNING: Sensitivities are placeholders. Replace from SPHEREx docs.</p>
                    <p className="text-gray-400">Dimming scales as r^-4. (Missing full calculator)</p>
                </div>
                <div className="bg-gray-800 p-6 rounded-lg">
                    <h2 className="text-2xl font-bold mb-2">Parallax & Wien</h2>
                    <p className="text-gray-400">Parallax and Wien Law panels (Missing full graphs)</p>
                </div>
            </div>
        </main>
    );
}
