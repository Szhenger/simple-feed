import React, { useState } from 'react';
import { useFeedStore } from '../store/useFeedStore';

export default function GlobalFeedOverlay() {
  const [isOpen, setIsOpen] = useState(false);
  const { events, unreadCount, markAllRead } = useFeedStore();

  const toggleFeed = () => {
    setIsOpen(!isOpen);
    if (!isOpen) markAllRead();
  };

  return (
    <>
      {/* Floating Action Button for the Inbox */}
      <button 
        onClick={toggleFeed}
        style={{
          position: 'fixed', bottom: '24px', right: '24px', zIndex: 1000,
          background: '#2eaadc', color: '#fff', border: 'none', borderRadius: '50%',
          width: '56px', height: '56px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}
      >
        <span style={{ fontSize: '24px' }}>📥</span>
        {unreadCount > 0 && (
          <span style={{
            position: 'absolute', top: '-4px', right: '-4px', background: '#e03131',
            color: '#fff', fontSize: '12px', fontWeight: 700, width: '24px', height: '24px',
            borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            {unreadCount}
          </span>
        )}
      </button>

      {/* Notion-Style Slide-Out Drawer */}
      <div style={{
        position: 'fixed', top: 0, right: isOpen ? 0 : '-400px', width: '360px', height: '100vh',
        background: '#fcfcfc', borderLeft: '1px solid #e9e9e7', boxShadow: '-4px 0 24px rgba(0,0,0,0.05)',
        transition: 'right 0.3s cubic-bezier(0.16, 1, 0.3, 1)', zIndex: 999, overflowY: 'auto',
        fontFamily: 'Inter, sans-serif'
      }}>
        <div style={{ padding: '24px', borderBottom: '1px solid #e9e9e7', background: '#fff', position: 'sticky', top: 0 }}>
          <h2 style={{ margin: 0, fontSize: '18px', color: '#37352f' }}>Synthesis Feed</h2>
          <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#787774' }}>Real-time agent dispatches.</p>
        </div>

        <div style={{ padding: '16px' }}>
          {events.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#adb5bd', fontSize: '14px', marginTop: '40px' }}>
              No recent dispatches.
            </div>
          ) : (
            events.map(ev => (
              <FeedCard key={ev.id} event={ev} />
            ))
          )}
        </div>
      </div>
    </>
  );
}

// Sub-component for rendering individual dispatches
function FeedCard({ event }: { event: any }) {
  const pillarColors = {
    EDUCATION: { bg: '#e6f4ea', text: '#0b6b43' },
    FINANCE: { bg: '#fef5e7', text: '#b06000' },
    PLANNING: { bg: '#f3f0ff', text: '#5f3dc4' }
  };
  const color = pillarColors[event.pillar as keyof typeof pillarColors] || { bg: '#eee', text: '#333' };

  return (
    <div style={{ background: '#fff', border: '1px solid #e9e9e7', borderRadius: '6px', padding: '16px', marginBottom: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
        <span style={{ fontSize: '11px', fontWeight: 600, padding: '2px 6px', borderRadius: '4px', background: color.bg, color: color.text }}>
          {event.pillar}
        </span>
        <span style={{ fontSize: '11px', color: '#adb5bd' }}>
          {new Date(event.timestamp * 1000).toLocaleTimeString()}
        </span>
      </div>
      <h4 style={{ margin: '0 0 6px 0', fontSize: '14px', color: '#37352f' }}>{event.title}</h4>
      
      {/* If the payload contains AI markdown, render it. Otherwise, render raw JSON keys. */}
      <div style={{ fontSize: '13px', color: '#495057', lineHeight: 1.5 }}>
        {event.payload.markdown ? (
          <div dangerouslySetInnerHTML={{ __html: event.payload.markdown.replace(/\n/g, '<br/>') }} />
        ) : (
          <pre style={{ background: '#f8f9fa', padding: '8px', borderRadius: '4px', overflowX: 'auto', fontSize: '11px' }}>
            {JSON.stringify(event.payload, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
