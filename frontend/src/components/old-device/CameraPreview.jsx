import { useState, useRef, useEffect } from 'react';

export default function CameraPreview({ isStreaming, onStreamStart, onStreamStop }) {
  const videoRef = useRef(null);
  const [hasPermission, setHasPermission] = useState(null);
  const [error, setError] = useState('');

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: 640, height: 480 },
        audio: false
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setHasPermission(true);
      onStreamStart();
    } catch (err) {
      setError('Camera access denied. Please enable camera permissions.');
      setHasPermission(false);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    onStreamStop();
  };

  useEffect(() => {
    return () => stopCamera();
  }, []);

  return (
    <div className="glass-card overflow-hidden" id="camera-preview-container">
      <div
        className="relative w-full aspect-video flex items-center justify-center"
        style={{ background: 'var(--bg-tertiary)' }}
      >
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
          style={{ display: isStreaming ? 'block' : 'none' }}
        />
        {!isStreaming && (
          <div className="text-center p-6">
            <div className="text-3xl mb-3" style={{ color: 'var(--text-tertiary)' }}>
              [ CAMERA ]
            </div>
            <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
              {error || 'Camera is not active. Tap below to start streaming.'}
            </p>
          </div>
        )}
        {isStreaming && (
          <div
            className="absolute top-3 left-3 flex items-center gap-1.5 px-2 py-1 rounded text-xs font-mono"
            style={{ background: 'rgba(239, 68, 68, 0.9)', color: '#ffffff' }}
          >
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: '#ffffff' }} />
            LIVE
          </div>
        )}
      </div>
      <div className="p-3 flex gap-2">
        {!isStreaming ? (
          <button
            onClick={startCamera}
            className="flex-1 py-2 rounded-lg text-sm font-semibold cursor-pointer transition-all"
            style={{ background: 'var(--accent-blue)', color: '#ffffff' }}
            id="start-stream-btn"
          >
            Start Streaming
          </button>
        ) : (
          <button
            onClick={stopCamera}
            className="flex-1 py-2 rounded-lg text-sm font-semibold cursor-pointer transition-all"
            style={{ background: 'var(--accent-red)', color: '#ffffff' }}
            id="stop-stream-btn"
          >
            Stop Streaming
          </button>
        )}
      </div>
    </div>
  );
}
