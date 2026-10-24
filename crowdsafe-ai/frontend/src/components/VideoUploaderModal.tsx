import React, { useState } from 'react';
import { X, UploadCloud, FileVideo, Check, AlertCircle, Sparkles } from 'lucide-react';
import { api } from '../services/api';

interface VideoUploaderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: (newCameraId: string) => void;
  onLoadSampleSuccess: () => void;
}

export const VideoUploaderModal: React.FC<VideoUploaderModalProps> = ({
  isOpen,
  onClose,
  onUploadSuccess,
  onLoadSampleSuccess,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [cameraName, setCameraName] = useState<string>('');
  const [location, setLocation] = useState<string>('');
  const [uploading, setUploading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      setFile(selected);
      if (!cameraName) {
        setCameraName(selected.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      if (!cameraName) {
        setCameraName(selected.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setErrorMsg('Please select a video file.');
      return;
    }

    try {
      setUploading(true);
      setErrorMsg(null);
      const res = await api.uploadVideo(file, cameraName || file.name, location || 'Upload Sector');
      onUploadSuccess(res.camera_id);
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed';
      setErrorMsg(msg);
    } finally {
      setUploading(false);
    }
  };

  const handleInstantSample = async () => {
    try {
      setUploading(true);
      setErrorMsg(null);
      await api.loadSampleVideo();
      onLoadSampleSuccess();
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Load sample failed';
      setErrorMsg(msg);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-dark-850 border border-dark-700 rounded-2xl w-full max-w-lg p-6 shadow-2xl relative">
        <div className="flex items-center justify-between pb-4 border-b border-dark-700">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-dark-800 rounded-lg border border-dark-700 text-emerald-400">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-mono text-base font-bold text-white">Upload Crowd Video</h3>
              <p className="text-xs text-slate-400">Process prerecorded surveillance video with YOLO</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 1-Click Fast Track Option */}
        <div className="mt-4 p-3 bg-cyan-950/30 border border-cyan-800/40 rounded-xl flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <Sparkles className="w-4 h-4 text-cyan-400 shrink-0" />
            <div>
              <span className="text-xs font-mono font-bold text-cyan-200 block">
                No video file ready?
              </span>
              <span className="text-[11px] text-slate-400">
                Load the bundled Intel Pedestrian benchmark crowd video instantly.
              </span>
            </div>
          </div>
          <button
            onClick={handleInstantSample}
            disabled={uploading}
            className="px-3 py-1.5 rounded-lg text-xs font-mono font-bold text-cyan-200 bg-cyan-900/60 hover:bg-cyan-800/80 border border-cyan-700 transition-colors shrink-0"
          >
            Load Sample
          </button>
        </div>

        {/* File Dropzone */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          className={`mt-4 border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
            isDragOver
              ? 'border-emerald-500 bg-emerald-950/20'
              : file
              ? 'border-emerald-600/70 bg-dark-900'
              : 'border-dark-700 bg-dark-900/60 hover:border-slate-500'
          }`}
          onClick={() => document.getElementById('video-input')?.click()}
        >
          <input
            id="video-input"
            type="file"
            accept="video/mp4,video/avi,video/quicktime,video/webm"
            onChange={handleFileChange}
            className="hidden"
          />

          <FileVideo className={`w-10 h-10 mx-auto mb-2 ${file ? 'text-emerald-400' : 'text-slate-500'}`} />

          {file ? (
            <div>
              <p className="text-xs font-mono font-bold text-white truncate max-w-sm mx-auto">
                {file.name}
              </p>
              <p className="text-[11px] text-emerald-400 font-mono mt-1">
                {(file.size / (1024 * 1024)).toFixed(2)} MB • Ready for inference
              </p>
            </div>
          ) : (
            <div>
              <p className="text-xs font-mono text-slate-200 font-semibold">
                Drag and drop your crowd MP4/AVI video here, or click to browse
              </p>
              <p className="text-[11px] text-slate-500 font-mono mt-1">
                Supports MP4, AVI, MOV, WEBM (Max recommended ~100MB)
              </p>
            </div>
          )}
        </div>

        {/* Form Fields */}
        <div className="mt-4 space-y-3">
          <div>
            <label className="block text-xs font-mono text-slate-300 mb-1 uppercase tracking-wider">
              Camera Feed Name:
            </label>
            <input
              type="text"
              placeholder="e.g. South Stairwell Plaza"
              value={cameraName}
              onChange={(e) => setCameraName(e.target.value)}
              className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-300 mb-1 uppercase tracking-wider">
              Location Description:
            </label>
            <input
              type="text"
              placeholder="e.g. Stadium Sector 4 Exit Gate"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>

        {errorMsg && (
          <div className="mt-3 p-2.5 bg-rose-950/60 border border-rose-800 rounded-lg flex items-center space-x-2 text-xs text-rose-300 font-mono">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Footer Actions */}
        <div className="mt-5 pt-4 border-t border-dark-700 flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-mono text-slate-400 hover:text-white bg-dark-800 hover:bg-dark-750 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="px-5 py-2 rounded-lg text-xs font-mono font-bold text-white bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 transition-colors flex items-center space-x-1.5 shadow-lg shadow-emerald-950"
          >
            {uploading ? (
              <span>Processing with YOLO...</span>
            ) : (
              <>
                <UploadCloud className="w-4 h-4" />
                <span>Start Detection</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
