import { ArrowRight, FileUp, MessageSquare, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function ChooseWorkspacePage() {
  return <main className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.18),_transparent_55%)] p-4 text-slate-100">
    <section className="w-full max-w-4xl rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glow backdrop-blur md:p-10">
      <div className="flex items-center gap-3 text-blue-400"><div className="rounded-2xl bg-blue-500/20 p-3"><ShieldCheck size={24} /></div><span className="text-sm font-medium uppercase tracking-[0.2em]">SentinelAI</span></div>
      <div className="mt-8 max-w-xl"><h1 className="text-3xl font-semibold">Choose a Workspace</h1><p className="mt-2 text-slate-400">Select where you&apos;d like to continue.</p></div>
      <div className="mt-8 grid gap-4 md:grid-cols-2">
        <Link to="/employee" className="group rounded-2xl border border-slate-700 bg-slate-950/60 p-6 transition hover:border-blue-500/50 hover:bg-slate-800">
          <MessageSquare className="text-blue-400" size={26} />
          <div className="mt-8 flex items-start justify-between gap-4"><div><h2 className="font-medium">SentinelAI Assistant</h2><p className="mt-2 text-sm text-slate-400">Ask secure workplace questions.</p></div><ArrowRight className="shrink-0 text-slate-500 transition group-hover:translate-x-1 group-hover:text-blue-400" size={20} /></div>
        </Link>
        <Link to="/document-ingestion" className="group rounded-2xl border border-slate-700 bg-slate-950/60 p-6 transition hover:border-cyan-500/50 hover:bg-slate-800">
          <FileUp className="text-cyan-400" size={26} />
          <div className="mt-8 flex items-start justify-between gap-4"><div><h2 className="font-medium">Document Ingestion Portal</h2><p className="mt-2 text-sm text-slate-400">Securely upload and index enterprise documents.</p></div><ArrowRight className="shrink-0 text-slate-500 transition group-hover:translate-x-1 group-hover:text-cyan-400" size={20} /></div>
        </Link>
      </div>
    </section>
  </main>;
}