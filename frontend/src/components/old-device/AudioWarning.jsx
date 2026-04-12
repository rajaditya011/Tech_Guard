import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

export default function AudioWarning() {
  const { user } = useAuth();
  const [hasWarning, setHasWarning] = useState(false);
  const [warningMessage, setWarningMessage] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!user?.id) return;
    const API_URL = import.meta.env.VITE_API_URL || '';
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = API_URL ? API_URL.replace('http', 'ws') + `/ws/old-device/${user.id}` : `${wsProtocol}//${window.location.host}/ws/old-device/${user.id}`;
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'incoming_message' || data.type === 'warning_broadcast') {
          setWarningMessage(data.content || 'Incoming audio alert.');
          setHasWarning(true);
        }
      } catch (e) {}
    };
    return () => ws.close();
  }, [user]);

  const playWarning = () => {
    if (!warningMessage) return;
    setIsPlaying(true);
    const utterance = new SpeechSynthesisUtterance(warningMessage);
    utterance.onend = () => setIsPlaying(false);
    speechSynthesis.speak(utterance);
  };

  const dismissWarning = () => { setHasWarning(false); setWarningMessage(''); };

  if (!hasWarning) {
    return (
      <div className="glass-card p-4" id="audio-warning-panel">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono uppercase tracking-wider" style={{ color: 'var(--text-tertiary)' }}>Audio Channel</span>
          <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>Listening for messages...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-4" style={{ borderColor: 'var(--accent-amber)', borderWidth: '1px' }} id="audio-warning-active">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-mono uppercase tracking-wider" style={{ color: 'var(--accent-amber)' }}>Incoming Message</span>
        <button onClick={dismissWarning} className="text-xs cursor-pointer bg-transparent border-none" style={{ color: 'var(--text-tertiary)' }}>Dismiss</button>
      </div>
      <p className="text-sm mb-3" style={{ color: 'var(--text-primary)' }}>{warningMessage}</p>
      <button onClick={playWarning} disabled={isPlaying} className="w-full py-2 rounded-lg text-sm font-semibold cursor-pointer"
        style={{ background: isPlaying ? 'var(--bg-surface)' : 'var(--accent-amber)', color: isPlaying ? 'var(--text-secondary)' : '#ffffff' }}>
        {isPlaying ? 'Playing...' : 'Play Audio'}
      </button>
    </div>
  );
}
