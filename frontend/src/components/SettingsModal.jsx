import React, { useState, useEffect } from 'react';
import { X, Key, CheckCircle, Database } from 'lucide-react';
import { api } from '../api/client';

export default function SettingsModal({ onClose, onKeysUpdated }) {
  const [systemStatus, setSystemStatus] = useState(null);
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    async function loadStatus() {
      try {
        const s = await api.getSystemStatus();
        setSystemStatus(s);
      } catch (err) {
        console.error(err);
      }
    }
    loadStatus();
  }, []);

  const handleSaveKeys = async () => {
    try {
      await api.configureKeys(geminiKey, openaiKey);
      setStatusMsg('API Keys updated successfully!');
      const s = await api.getSystemStatus();
      setSystemStatus(s);
      if (onKeysUpdated) onKeysUpdated(s.active_llm_mode);
    } catch (err) {
      setStatusMsg('Error updating keys.');
    }
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(15, 23, 42, 0.6)',
      backdropFilter: 'blur(4px)',
      zIndex: 100,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem'
    }}>
      <div style={{
        background: '#FFFFFF',
        borderRadius: '20px',
        width: '100%',
        maxWidth: '600px',
        padding: '2rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.4rem' }}>System & API Key Settings</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            <X size={22} color="#64748B" />
          </button>
        </div>

        {/* Current Active Mode */}
        {systemStatus && (
          <div style={{ background: '#ECFDF5', border: '1px solid #A7F3D0', padding: '1rem', borderRadius: '10px', marginBottom: '1.5rem' }}>
            <div style={{ fontWeight: 700, color: '#047857', fontSize: '0.9rem', marginBottom: '0.2rem' }}>
              Active AI Intelligence Engine:
            </div>
            <div style={{ fontSize: '1rem', fontWeight: 600, color: '#065F46' }}>
              {systemStatus.active_llm_mode}
            </div>
          </div>
        )}

        <div style={{ display: 'grid', gap: '1.25rem', marginBottom: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem' }}>
              Google Gemini API Key (Optional)
            </label>
            <input
              type="password"
              placeholder="AIzaSy..."
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #CBD5E1' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem' }}>
              OpenAI API Key (Optional)
            </label>
            <input
              type="password"
              placeholder="sk-proj-..."
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #CBD5E1' }}
            />
          </div>
        </div>

        {statusMsg && <div style={{ color: '#10B981', fontWeight: 600, fontSize: '0.85rem', marginBottom: '1rem' }}>{statusMsg}</div>}

        <button className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={handleSaveKeys}>
          Save Configuration
        </button>
      </div>
    </div>
  );
}
