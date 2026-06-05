import React, { useState, useEffect } from 'react';
import { AlertTriangle, Lock, X } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

interface SudoModalProps {
  isOpen: boolean;
  actionName: string;
  onConfirm: (password: string) => Promise<void>;
  onCancel: () => void;
}

export const SudoModal: React.FC<SudoModalProps> = ({ isOpen, actionName, onConfirm, onCancel }) => {
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const context = useAuthStore((state) => state.context);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setPassword('');
      setError(null);
      setIsSubmitting(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await onConfirm(password);
      // Let the parent close the modal on success
    } catch (err: any) {
      setError(err.message || "Cryptographic verification failed.");
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-[100]" onClick={onCancel} />
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white rounded-lg shadow-2xl z-[101] border border-red-200 overflow-hidden">
        
        <header className="px-6 py-4 border-b border-gray-100 bg-red-50 flex items-center justify-between">
          <div className="flex items-center gap-2 text-red-700 font-bold tracking-tight">
            <Lock className="w-5 h-5" />
            Step-Up Authentication Required
          </div>
          <button onClick={onCancel} className="text-gray-400 hover:text-gray-600 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </header>

        <form onSubmit={handleSubmit} className="p-6">
          <div className="flex items-start gap-3 p-3 bg-orange-50 border border-orange-100 rounded-md mb-6 text-sm text-orange-800">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 text-orange-600 mt-0.5" />
            <p>
              You are attempting to execute <strong>{actionName}</strong>. This is a highly privileged infrastructure operation. 
              Please re-verify your identity for context <strong>{context?.username}</strong>.
            </p>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cryptographic Passphrase
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-red-500 font-mono text-sm"
              placeholder="Enter your password..."
              required
              autoFocus
            />
            {error && <p className="text-red-600 text-xs mt-2 font-medium">{error}</p>}
          </div>

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              disabled={isSubmitting}
            >
              Abort Operation
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !password}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isSubmitting ? 'Verifying Signature...' : 'Authorize Execution'}
            </button>
          </div>
        </form>
      </div>
    </>
  );
};
