import React, { useState, useEffect } from 'react';
import { X, Ban, ChevronRight } from 'lucide-react';
import { getNotInTool } from '../services/api';

// minimal markdown rendering (headings, bullets, bold) -- source is
// docs/not-in-this-tool.md; no markdown dependency added
function renderMarkdown(md) {
  const blocks = [];
  let list = null;
  const flush = () => {
    if (list) { blocks.push(<ul key={blocks.length} className="list-disc ml-5 space-y-1 mb-3">{list}</ul>); list = null; }
  };
  const inline = (t) => t.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith('**') ? <strong key={i}>{part.slice(2, -2)}</strong> : part);
  md.split('\n').forEach((line) => {
    if (line.startsWith('## ')) { flush(); blocks.push(<h3 key={blocks.length} className="text-base font-bold text-gray-800 mt-4 mb-2">{line.slice(3)}</h3>); }
    else if (line.startsWith('# ')) { flush(); blocks.push(<h2 key={blocks.length} className="text-lg font-bold text-gray-900 mb-2">{line.slice(2)}</h2>); }
    else if (line.startsWith('- ')) { list = list || []; list.push(<li key={list.length}>{inline(line.slice(2))}</li>); }
    else if (line.trim() === '') { flush(); }
    else { flush(); blocks.push(<p key={blocks.length} className="mb-2">{inline(line)}</p>); }
  });
  flush();
  return blocks;
}

// greyed pseudo-levers shown in the taxonomy; clicking opens the panel
export const NOT_IN_TOOL_ENTRIES = [
  'Interest-rate / monetary policy',
  'Active labour market policies (training, PES)',
  'Minimum wages',
  'Distribution-targeted transfers',
];

export function NotInToolTeasers({ onOpen }) {
  return (
    <div className="bg-white rounded-xl shadow-md p-4 mb-3 opacity-90">
      <div className="flex items-center space-x-2 mb-2">
        <Ban className="w-4 h-4 text-gray-400" />
        <span className="font-medium text-gray-500 text-sm">Not in this tool</span>
      </div>
      <div className="space-y-1">
        {NOT_IN_TOOL_ENTRIES.map((e) => (
          <button key={e} onClick={onOpen}
            className="w-full flex items-center justify-between text-left text-sm text-gray-400 hover:text-blue-700 px-2 py-1 rounded hover:bg-blue-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600">
            <span className="line-through decoration-gray-300">{e}</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        ))}
      </div>
      <p className="text-xs text-gray-400 mt-2">Why these are excluded - click any.</p>
    </div>
  );
}

function NotInToolPanel({ open, onClose }) {
  const [markdown, setMarkdown] = useState(null);
  useEffect(() => {
    if (open && markdown === null) {
      getNotInTool().then((d) => setMarkdown(d.markdown))
        .catch(() => setMarkdown('# Unavailable'));
    }
  }, [open, markdown]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4"
         onClick={onClose} role="dialog" aria-modal="true"
         aria-label="What is not in this tool and why">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6"
           onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2 text-gray-900">
            <Ban className="w-5 h-5" />
            <span className="font-bold">What is not in this tool, and why</span>
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

export default NotInToolPanel;
