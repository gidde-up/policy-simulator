import React, { useState, useEffect } from 'react';
import { X, BookOpen } from 'lucide-react';
import { getLimitations } from '../services/api';

// minimal markdown rendering (headings, bullets, bold) -- the source is
// docs/model-limitations.md served by the backend; no dependency added
function renderMarkdown(md) {
  const blocks = [];
  let list = null;
  const flushList = () => {
    if (list) {
      blocks.push(<ul key={blocks.length} className="list-disc ml-5 space-y-1 mb-3">{list}</ul>);
      list = null;
    }
  };
  const inline = (text) =>
    text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, i) => {
      if (part.startsWith('**')) return <strong key={i}>{part.slice(2, -2)}</strong>;
      if (part.startsWith('`')) return <code key={i} className="bg-gray-100 px-1 rounded text-xs">{part.slice(1, -1)}</code>;
      return part;
    });

  md.split('\n').forEach((line) => {
    if (line.startsWith('## ')) {
      flushList();
      blocks.push(<h3 key={blocks.length} className="text-base font-bold text-gray-800 mt-4 mb-2">{line.slice(3)}</h3>);
    } else if (line.startsWith('# ')) {
      flushList();
      blocks.push(<h2 key={blocks.length} className="text-lg font-bold text-gray-900 mb-2">{line.slice(2)}</h2>);
    } else if (line.startsWith('- ')) {
      list = list || [];
      list.push(<li key={list.length}>{inline(line.slice(2))}</li>);
    } else if (line.trim() === '') {
      flushList();
    } else {
      flushList();
      blocks.push(<p key={blocks.length} className="mb-2">{inline(line)}</p>);
    }
  });
  flushList();
  return blocks;
}

function LimitationsPanel({ open, onClose }) {
  const [markdown, setMarkdown] = useState(null);

  useEffect(() => {
    if (open && markdown === null) {
      getLimitations()
        .then((d) => setMarkdown(d.markdown))
        .catch(() => setMarkdown('# Unavailable\nCould not load the limitations document.'));
    }
  }, [open, markdown]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4"
         onClick={onClose} role="dialog" aria-modal="true"
         aria-label="What this model can and cannot tell you">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6"
           onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2 text-gray-900">
            <BookOpen className="w-5 h-5" />
            <span className="font-bold">Model scope</span>
          </div>
          <button onClick={onClose} aria-label="Close"
                  className="p-1 rounded text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="text-sm text-gray-700">
          {markdown === null ? 'Loading…' : renderMarkdown(markdown)}
        </div>
      </div>
    </div>
  );
}

export default LimitationsPanel;
