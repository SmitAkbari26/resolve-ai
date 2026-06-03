import React, { useState, useEffect, useRef } from 'react';
import { knowledgeApi } from '../services/api';
import {
  Upload,
  RefreshCw,
  Trash2,
  Database,
  FileText,
  AlertCircle,
  CheckCircle2,
  BookOpen,
} from 'lucide-react';

interface KnowledgeDocument {
  id: string;
  title: string;
  document_type: string;
  source_path: string;
  uploaded_by: string | null;
  status: string;
  chunk_count: number;
  created_at: string;
}

interface KnowledgeStats {
  total_vector_chunks: number;
  total_documents: number;
  collection_name: string;
  upload_directory: string;
}

const ACCEPTED_TYPES =
  '.pdf,.md,.docx,.txt,.json,application/pdf,text/plain,text/markdown,application/vnd.openxmlformats-officedocument.wordprocessingml.document';

export const KnowledgeBase: React.FC = () => {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [stats, setStats] = useState<KnowledgeStats | null>(null);
  const [title, setTitle] = useState('');
  const [documentType, setDocumentType] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [docs, kbStats] = await Promise.all([
        knowledgeApi.listDocuments(),
        knowledgeApi.getStats(),
      ]);
      setDocuments(Array.isArray(docs) ? docs : []);
      setStats(kbStats);
    } catch {
      setError('Failed to load knowledge base. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setError('Please choose a file to upload.');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await knowledgeApi.uploadDocument(
        file,
        title.trim() || undefined,
        documentType.trim() || undefined,
        'admin'
      );
      setSuccess(
        result.message ||
          `Indexed ${result.chunks_ingested} chunks from "${result.document.title}".`
      );
      setTitle('');
      setDocumentType('');
      if (fileInputRef.current) fileInputRef.current.value = '';
      await loadData();
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data
              ?.detail
          : null;
      setError(msg || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string, docTitle: string) => {
    if (!confirm(`Delete "${docTitle}" and remove it from RAG search?`)) return;
    setError(null);
    try {
      await knowledgeApi.deleteDocument(id);
      setSuccess(`Removed "${docTitle}" from knowledge base.`);
      await loadData();
    } catch {
      setError('Failed to delete document.');
    }
  };

  const handleReingest = async (id: string) => {
    setError(null);
    try {
      const result = await knowledgeApi.reingestDocument(id);
      setSuccess(result.message || 'Document re-indexed.');
      await loadData();
    } catch {
      setError('Re-index failed.');
    }
  };

  const handleIngestDatasets = async () => {
    setUploading(true);
    setError(null);
    try {
      const result = await knowledgeApi.ingestDatasets();
      setSuccess(`Datasets folder: ${result.chunks_ingested} chunks ingested.`);
      await loadData();
    } catch {
      setError('Failed to ingest datasets folder.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <BookOpen className="w-7 h-7 text-emerald-400" />
            Knowledge Base (RAG)
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Upload documents to index them for AI support answers. PDF, MD, DOCX, TXT, JSON.
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-sm text-slate-300 border border-slate-700"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
            <div className="flex items-center gap-2 text-slate-400 text-xs uppercase tracking-wider mb-2">
              <Database className="w-4 h-4" />
              Vector chunks
            </div>
            <p className="text-2xl font-bold text-emerald-400">{stats.total_vector_chunks}</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
            <div className="flex items-center gap-2 text-slate-400 text-xs uppercase tracking-wider mb-2">
              <FileText className="w-4 h-4" />
              Uploaded docs
            </div>
            <p className="text-2xl font-bold text-indigo-400">{stats.total_documents}</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
            <p className="text-slate-400 text-xs uppercase tracking-wider mb-2">Collection</p>
            <p className="text-sm font-mono text-slate-300 truncate">{stats.collection_name}</p>
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 bg-rose-900/20 border border-rose-700 text-rose-300 px-4 py-3 rounded-xl text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}
      {success && (
        <div className="flex items-center gap-2 bg-emerald-900/20 border border-emerald-700 text-emerald-300 px-4 py-3 rounded-xl text-sm">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          {success}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <form
          onSubmit={handleUpload}
          className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4"
        >
          <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
            <Upload className="w-5 h-5 text-indigo-400" />
            Upload & index
          </h2>

          <div>
            <label className="block text-xs text-slate-400 mb-1">File</label>
            <input
              ref={fileInputRef}
              type="file"
              accept={ACCEPTED_TYPES}
              className="w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-indigo-600 file:text-white hover:file:bg-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1">Title (optional)</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Weight Gain Product Guide"
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-slate-200 text-sm"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1">Type (optional)</label>
            <input
              type="text"
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              placeholder="e.g. product, policy"
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2 text-slate-200 text-sm"
            />
          </div>

          <button
            type="submit"
            disabled={uploading}
            className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-medium py-3 rounded-xl"
          >
            <Upload className="w-4 h-4" />
            {uploading ? 'Uploading & indexing…' : 'Upload to RAG'}
          </button>

          <button
            type="button"
            onClick={handleIngestDatasets}
            disabled={uploading}
            className="w-full text-sm text-slate-400 hover:text-slate-200 underline"
          >
            Or re-ingest static datasets/ folder
          </button>
        </form>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 overflow-hidden flex flex-col">
          <h2 className="text-lg font-semibold text-slate-100 mb-4">Indexed documents</h2>
          <div className="flex-1 overflow-y-auto max-h-[420px] space-y-3">
            {documents.length === 0 ? (
              <p className="text-slate-500 text-sm">No uploads yet. Add your first file.</p>
            ) : (
              documents.map((doc) => (
                <div
                  key={doc.id}
                  className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col gap-2"
                >
                  <div className="flex justify-between items-start gap-2">
                    <div>
                      <p className="font-medium text-slate-200">{doc.title}</p>
                      <p className="text-md text-slate-500 mt-0.5">
                        {doc.document_type} · {doc.chunk_count} chunks · {doc.status}
                      </p>
                    </div>
                    <div className="flex gap-1 shrink-0">
                      <button
                        type="button"
                        onClick={() => handleReingest(doc.id)}
                        title="Re-index"
                        className="p-2 text-slate-400 hover:text-indigo-400"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(doc.id, doc.title)}
                        className="p-2 text-slate-400 hover:text-rose-400"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <p className="text-[14px] font-mono text-slate-600 truncate">{doc.id}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
