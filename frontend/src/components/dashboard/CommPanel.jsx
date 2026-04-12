import { useState } from 'react';

export default function CommPanel() {
  const [selectedDevice, setSelectedDevice] = useState('');
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const devices = [
    { id: 'phone-001', name: 'Living Room Camera' },
    { id: 'webcam-002', name: 'Front Door Webcam' },
    { id: 'cctv-003', name: 'Kitchen CCTV' },
  ];
  const handleSend = async () => {
    if (!selectedDevice || !message) return;
    setSending(true);
    setTimeout(() => { setSending(false); setMessage(''); }, 1000);
  };

  return (
    <div id="comm-panel">
      <h2 className="text-base font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Two-Way Communication</h2>
      <div className="glass-card p-6">
        <div className="mb-4">
          <label className="block text-xs font-mono uppercase tracking-wider mb-2" style={{ color: 'var(--text-tertiary)' }}>Target Device</label>
          <select value={selectedDevice} onChange={(e) => setSelectedDevice(e.target.value)}
            className="w-full px-3 py-2.5 rounded-lg text-sm outline-none"
            style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-primary)', color: 'var(--text-primary)' }} id="comm-device-select">
            <option value="">Select a device</option>
            {devices.map(d => (<option key={d.id} value={d.id}>{d.name}</option>))}
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-xs font-mono uppercase tracking-wider mb-2" style={{ color: 'var(--text-tertiary)' }}>Message</label>
          <textarea value={message} onChange={(e) => setMessage(e.target.value)}
            placeholder="Type a message to send through the device speaker..." rows={3}
            className="w-full px-3 py-2.5 rounded-lg text-sm outline-none resize-none"
            style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-primary)', color: 'var(--text-primary)' }} id="comm-message-input" />
        </div>
        <button onClick={handleSend} disabled={!selectedDevice || !message || sending}
          className="w-full py-2.5 rounded-lg text-sm font-semibold cursor-pointer transition-all"
          style={{ background: (selectedDevice && message && !sending) ? 'var(--accent-blue)' : 'var(--bg-surface)',
                   color: (selectedDevice && message && !sending) ? '#ffffff' : 'var(--text-tertiary)', border: 'none' }} id="comm-send-btn">
          {sending ? 'Sending...' : 'Send Message'}
        </button>
      </div>
    </div>
  );
}
