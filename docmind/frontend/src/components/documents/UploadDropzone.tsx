import { useState, useRef } from 'react';
import { useAppStore } from '@/lib/store';
import { api } from '@/lib/api';
import { UploadCloud, File, X, CheckCircle2, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export function UploadDropzone() {
  const [isOpen, setIsOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { addDocument } = useAppStore();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      const validTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      
      if (!validTypes.includes(selected.type) && !selected.name.endsWith('.txt') && !selected.name.endsWith('.pdf') && !selected.name.endsWith('.docx')) {
        toast.error('Unsupported file type. Please upload PDF, TXT, or DOCX.');
        return;
      }
      setFile(selected);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setIsUploading(true);
    const toastId = toast.loading('Processing document...');
    
    try {
      const doc = await api.uploadDocument(file);
      addDocument(doc);
      toast.success(`Document processed — ${doc.chunk_count} chunks created`, { id: toastId });
      setFile(null);
      setIsOpen(false);
    } catch (e: any) {
      toast.error(`Upload failed: ${e.message}`, { id: toastId });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-lg text-sm font-medium transition-colors"
      >
        <UploadCloud className="w-4 h-4" />
        Upload Document
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden text-slate-800">
        <div className="p-4 border-b border-slate-100 flex justify-between items-center">
          <h2 className="font-semibold text-lg">Upload Document</h2>
          <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6">
          {!file ? (
            <div 
              className="border-2 border-dashed border-slate-200 rounded-xl p-8 flex flex-col items-center justify-center gap-4 cursor-pointer hover:bg-slate-50 hover:border-indigo-300 transition-colors"
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="w-12 h-12 bg-indigo-50 rounded-full flex items-center justify-center text-indigo-600">
                <UploadCloud className="w-6 h-6" />
              </div>
              <div className="text-center">
                <p className="font-medium text-slate-700">Click to upload or drag and drop</p>
                <p className="text-xs text-slate-500 mt-1">PDF, TXT, or DOCX (max 10MB)</p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-6">
              <div className="flex items-center gap-4 p-4 border border-slate-200 rounded-xl bg-slate-50">
                <div className="w-10 h-10 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center shrink-0">
                  <File className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate text-slate-700">{file.name}</p>
                  <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <button 
                  onClick={() => setFile(null)}
                  className="text-slate-400 hover:text-red-500 p-1"
                  disabled={isUploading}
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Strategy</p>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span className="text-sm font-medium capitalize text-slate-700">Title & AI Summarization Chunking</span>
                </div>
                <p className="text-xs text-slate-500 mt-1 ml-6">
                  Intelligently chunks by title and generates summaries for text, tables, and images.
                </p>
              </div>
            </div>
          )}
          
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            className="hidden" 
            accept=".pdf,.txt,.docx"
          />
        </div>
        
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
          <button 
            onClick={() => setIsOpen(false)}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-200 rounded-lg transition-colors"
            disabled={isUploading}
          >
            Cancel
          </button>
          <button 
            onClick={handleUpload}
            disabled={!file || isUploading}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-lg transition-colors"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Processing...
              </>
            ) : (
              'Process Document'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
