import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">
      <div className="absolute top-0 w-full bg-red-600 text-center py-2 text-white font-bold text-sm z-50">
        SIMULATED DEMO DATA. Not real SPHEREx observations.
      </div>
      
      <h1 className="text-6xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
        SkyBlink
      </h1>
      
      <p className="text-xl mb-8 text-gray-300 max-w-2xl text-center">
        A billion objects and nobody can look at them all; we built a tool anyone can use to catch the ones that move.
      </p>

      <div className="flex gap-4">
        <Link href="/stories" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors shadow-lg hover:shadow-blue-500/50">
          Try a story
        </Link>
        <Link href="/viewer/F03" className="bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
          Search the sky
        </Link>
      </div>
      
      <div className="mt-16 text-gray-400 text-sm max-w-xl text-center">
        TODO: paste the official SPHEREx data acknowledgement from the IRSA SPHEREx page. <br/> QR2 DOI 10.26131/IRSA652
      </div>
    </main>
  );
}
