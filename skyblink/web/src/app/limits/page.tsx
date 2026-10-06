export default function Limits() {
    return (
        <main className="p-12 text-white bg-gray-900 min-h-screen">
            <h1 className="text-4xl font-bold mt-8 mb-4">Limitations & Validation</h1>
            <ul className="list-disc pl-8 mb-8 text-gray-300">
                <li>Shallow Depth: A distant body is very unlikely to be found in single exposures.</li>
                <li>Band-Matching Caveats: Only frames within the precise wavelength tolerance are matched.</li>
                <li>Simulated Data: All results currently shown are based on mock observations.</li>
            </ul>
            <div className="bg-gray-800 p-4 rounded-lg text-yellow-400 font-mono inline-block">
                Results (Efficiency, Recovery Rates, False Positives): Not computed yet
            </div>
        </main>
    );
}
