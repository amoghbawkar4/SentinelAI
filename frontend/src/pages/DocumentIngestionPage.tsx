import { ArrowLeft, FileUp } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function DocumentIngestionPage() {
  return <main className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(6,182,212,0.14),_transparent_55%)] p-4 text-slate-100">
    <section className="w-full max-w-2xl rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-glow backdrop-blur md:p-12">
      <Link to="/choose-workspace" className="inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-slate-100"><ArrowLeft size={16} /> Back to Workspace</Link>
      <div className="mt-10 flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-500/15 text-cyan-400"><FileUp size={28} /></div>
      <h1 className="mt-6 text-3xl font-semibold">Document Ingestion Portal</h1>
      <p className="mt-3 text-slate-400">Secure enterprise document ingestion will be available here.</p>
    </section>
  </main>;
}