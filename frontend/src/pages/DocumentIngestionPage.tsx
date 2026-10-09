import { ArrowLeft, FileText, FileUp, LoaderCircle, ShieldAlert, ShieldCheck, Trash2, UploadCloud } from 'lucide-react';
import { useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';

const ALLOWED_ROLES = ['Employee', 'Manager', 'HR', 'Payroll Administrator', 'Security Analyst', 'SentinelAI Administrator'] as const;
const ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.md', '.csv', '.xlsx'];
const MAX_FILE_SIZE_MB = 10;

type UploadState = 'idle' | 'invalid' | 'uploading' | 'success' | 'error';

function formatBytes(bytes: number) {
  if (bytes === 0) return '0 Bytes';
  const units = ['Bytes', 'KB', 'MB', 'GB'];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / (1024 ** index);
  return `${value.toFixed(value >= 10 || index === 0 ? 0 : 1)} ${units[index]}`;
}

export default function DocumentIngestionPage() {
  const { user } = useAuth();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [validationMessage, setValidationMessage] = useState('');
  const [uploadState, setUploadState] = useState<UploadState>('idle');
  const [statusText, setStatusText] = useState('');
  const [errorText, setErrorText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const selectedRoleSummary = useMemo(() => selectedRoles.join(', ') || 'No roles selected', [selectedRoles]);

  const validateFile = (file: File | null) => {
    if (!file) {
      setValidationMessage('');
      return false;
    }

    const extension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      setValidationMessage('Unsupported file type. Supported types: PDF, DOC, DOCX, TXT, MD, CSV, XLSX.');
      setUploadState('invalid');
      return false;
    }

    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setValidationMessage(`File exceeds the maximum size of ${MAX_FILE_SIZE_MB} MB.`);
      setUploadState('invalid');
      return false;
    }

    setValidationMessage('');
    setUploadState('idle');
    return true;
  };

  const handleFileSelection = (file: File | null) => {
    setErrorText('');
    setStatusText('');
    if (!file) {
      setSelectedFile(null);
      setUploadState('idle');
      return;
    }

    if (validateFile(file)) {
      setSelectedFile(file);
    } else {
      setSelectedFile(null);
    }
  };

  const toggleRole = (role: string) => {
    setSelectedRoles((current) => {
      if (current.includes(role)) return current.filter((item) => item !== role);
      return [...current, role];
    });
    setErrorText('');
    setStatusText('');
  };

  const onSubmit = async () => {
    if (!selectedFile) {
      setErrorText('Please select a document before continuing.');
      setUploadState('error');
      return;
    }

    if (selectedRoles.length === 0) {
      setErrorText('At least one role must be selected for the document access list.');
      setUploadState('error');
      return;
    }

    if (!validateFile(selectedFile)) {
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    selectedRoles.forEach((role) => formData.append('allowed_roles', role));

    setIsSubmitting(true);
    setUploadState('uploading');
    setErrorText('');
    setStatusText('Uploading document...');

    try {
      const response = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setUploadState('success');
      setStatusText(`Document received successfully. Document ID: ${response.data.id}`);
      setSelectedRoles(response.data.allowed_roles ?? selectedRoles);
    } catch (requestError: any) {
      const detail = requestError?.response?.data?.detail || 'Unable to upload the document right now.';
      setUploadState('error');
      setErrorText(typeof detail === 'string' ? detail : 'Unable to upload the document right now.');
      setStatusText('');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-slate-100 md:px-8">
      <div className="mx-auto max-w-5xl">
        <Link to="/choose-workspace" className="inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-slate-100"><ArrowLeft size={16} /> Back to Workspace</Link>

        <section className="mt-8 rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-glow backdrop-blur md:p-10">
          <div className="flex items-center gap-3 text-cyan-400">
            <div className="rounded-2xl bg-cyan-500/10 p-3"><FileUp size={24} /></div>
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.22em] text-slate-400">Secure ingestion</p>
            </div>
          </div>

          <div className="mt-8">
            <h1 className="text-3xl font-semibold text-white">Secure Document Ingestion</h1>
            <p className="mt-2 max-w-2xl text-slate-400">Upload a document to the SentinelAI knowledge base and define who can access it.</p>
          </div>

          <div
            className={`mt-8 rounded-2xl border-2 border-dashed p-8 text-center transition ${dragOver ? 'border-cyan-400 bg-cyan-500/5' : 'border-slate-700 bg-slate-950/40'} ${uploadState === 'invalid' ? 'border-rose-500/50' : ''}`}
            onDragEnter={(event) => { event.preventDefault(); setDragOver(true); }}
            onDragOver={(event) => { event.preventDefault(); setDragOver(true); }}
            onDragLeave={(event) => { event.preventDefault(); setDragOver(false); }}
            onDrop={(event) => { event.preventDefault(); setDragOver(false); const file = event.dataTransfer.files?.[0] ?? null; handleFileSelection(file); }}
          >
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-500/10 text-cyan-400">
              <UploadCloud size={32} />
            </div>
            <p className="mt-5 text-lg font-medium text-white">Drag & drop your file</p>
            <p className="mt-2 text-sm text-slate-400">or</p>
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="mt-4 inline-flex items-center justify-center rounded-xl border border-cyan-500/40 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-300 transition hover:bg-cyan-500/15"
            >
              Browse Files
            </button>
            <input
              ref={inputRef}
              aria-label="Select document"
              type="file"
              accept=".pdf,.doc,.docx,.txt,.md,.csv,.xlsx"
              className="hidden"
              onChange={(event) => handleFileSelection(event.target.files?.[0] ?? null)}
            />
            <p className="mt-4 text-xs text-slate-500">Supported file types: PDF, DOC, DOCX, TXT, MD, CSV, XLSX · Max size: {MAX_FILE_SIZE_MB} MB</p>
          </div>

          {validationMessage && <div className="mt-4 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-200">{validationMessage}</div>}

          {selectedFile && (
            <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="rounded-xl bg-slate-800 p-2 text-cyan-400"><FileText size={20} /></div>
                  <div>
                    <p className="text-base font-medium text-white">{selectedFile.name}</p>
                    <p className="text-xs text-slate-400">{selectedFile.type || 'Document'} · {formatBytes(selectedFile.size)}</p>
                  </div>
                </div>
                <button type="button" onClick={() => { setSelectedFile(null); setValidationMessage(''); setUploadState('idle'); }} className="inline-flex items-center gap-2 rounded-lg border border-slate-700 px-2.5 py-2 text-sm text-slate-300 transition hover:bg-slate-800"><Trash2 size={14} /> Remove</button>
              </div>
            </div>
          )}

          <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-950/50 p-5">
            <h2 className="text-lg font-semibold text-white">Who can access this document?</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {ALLOWED_ROLES.map((role) => (
                <label key={role} className="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/80 px-3 py-2 text-sm text-slate-200">
                  <input aria-label={role} type="checkbox" checked={selectedRoles.includes(role)} onChange={() => toggleRole(role)} className="h-4 w-4 rounded border-slate-600 bg-slate-900 text-cyan-500 focus:ring-cyan-500" />
                  <span>{role}</span>
                </label>
              ))}
            </div>
            <div className="mt-5 rounded-xl border border-slate-800 bg-slate-900/50 p-3">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Access summary</p>
              <p className="mt-2 text-sm text-slate-300">{selectedRoleSummary}</p>
            </div>
          </div>

          <div className="mt-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex-1 text-sm">
              {uploadState === 'success' && <div className="flex items-center gap-2 text-emerald-300"><ShieldCheck size={18} />{statusText}</div>}
              {uploadState === 'uploading' && <div className="flex items-center gap-2 text-cyan-300"><LoaderCircle className="animate-spin" size={18} />{statusText}</div>}
              {uploadState === 'error' && <div className="flex items-center gap-2 text-rose-300"><ShieldAlert size={18} />{errorText}</div>}
            </div>

            <button
              type="button"
              disabled={!selectedFile || selectedRoles.length === 0 || isSubmitting || uploadState === 'invalid'}
              onClick={() => { void onSubmit(); }}
              className="inline-flex items-center justify-center rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
            >
              {isSubmitting ? 'Uploading...' : 'Secure & Ingest'}
            </button>
          </div>
        </section>
      </div>
    </main>
  );
}