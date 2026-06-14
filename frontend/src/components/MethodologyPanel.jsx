import React, { useState, useEffect } from 'react';
import { BookOpen, ChevronRight, ChevronDown } from 'lucide-react';
import { getMethodology } from '../services/api';

// Renders docs/methodology.md. Plain markdown is tier 1 (always shown);
// `::: detail <summary>` ... `:::` fences are tier-2 expandables rendered
// as keyboard-operable, ARIA-labelled disclosure sections.

function renderInline(t) {
  return t.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, i) => {
    if (part.startsWith('**')) return <strong key={i}>{part.slice(2, -2)}</strong>;
    if (part.startsWith('`')) return <code key={i} className="bg-gray-100 px-1 rounded text-xs">{part.slice(1, -1)}</code>;
    return part;
  });
}

// render a block of plain markdown lines (headings within a detail are
// downgraded; here we handle paragraphs, bullets, h2/h3)
function renderMarkdownLines(lines, keyPrefix) {
  const out = [];
  let list = null;
  const flush = () => {
    if (list) {
      out.push(<ul key={`${keyPrefix}-l${out.length}`} className="list-disc ml-5 space-y-1 mb-3">{list}</ul>);
      list = null;
    }
  };
  lines.forEach((line) => {
    if (line.startsWith('## ')) { flush(); out.push(<h2 key={`${keyPrefix}-${out.length}`} className="text-xl font-bold text-gray-900 mt-6 mb-2">{line.slice(3)}</h2>); }
    else if (line.startsWith('# ')) { flush(); out.push(<h1 key={`${keyPrefix}-${out.length}`} className="text-2xl font-bold text-gray-900 mb-3">{line.slice(2)}</h1>); }
    else if (line.startsWith('- ')) { list = list || []; list.push(<li key={list.length}>{renderInline(line.slice(2))}</li>); }
    else if (line.trim() === '') { flush(); }
    else { flush(); out.push(<p key={`${keyPrefix}-${out.length}`} className="mb-3 leading-relaxed">{renderInline(line)}</p>); }
  });
  flush();
  return out;
}

function DetailBlock({ summary, lines }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="my-3 border-l-2 border-blue-200 pl-3">
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="flex items-center space-x-1 text-sm font-medium text-blue-700 hover:text-blue-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 rounded"
      >
        {open ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        <span>{summary}</span>
      </button>
      {open && (
        <div className="mt-2 text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
          {renderMarkdownLines(lines, 'd')}
        </div>
      )}
    </div>
  );
}

// split the markdown into a sequence of {type:'md',lines} and
// {type:'detail',summary,lines}
function parse(md) {
  const blocks = [];
  let buffer = [];
  let inDetail = false;
  let detailSummary = '';
  let detailLines = [];
  const flushBuffer = () => {
    if (buffer.length) { blocks.push({ type: 'md', lines: buffer }); buffer = []; }
  };
  md.split('\n').forEach((line) => {
    const m = line.match(/^:::\s*detail\s*(.*)$/);
    if (m) { flushBuffer(); inDetail = true; detailSummary = m[1] || 'Show the detail'; detailLines = []; return; }
    if (line.trim() === ':::' && inDetail) {
      blocks.push({ type: 'detail', summary: detailSummary, lines: detailLines });
      inDetail = false; return;
    }
    if (inDetail) detailLines.push(line);
    else buffer.push(line);
  });
  flushBuffer();
  return blocks;
}

function MethodologyPanel() {
  const [markdown, setMarkdown] = useState(null);
  useEffect(() => {
    getMethodology().then((d) => setMarkdown(d.markdown))
      .catch(() => setMarkdown('# Methodology\nCould not load the methodology document.'));
  }, []);

  if (markdown === null) {
    return <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-md p-8 text-gray-500">Loading methodology…</div>;
  }

  const blocks = parse(markdown);
  return (
    <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-md p-8 text-gray-700">
      <div className="flex items-center space-x-2 mb-4 text-gray-900">
        <BookOpen className="w-6 h-6" />
        <span className="text-sm uppercase tracking-wide text-gray-400">Methodology - plain text with optional detail</span>
      </div>
      {blocks.map((b, i) =>
        b.type === 'detail'
          ? <DetailBlock key={i} summary={b.summary} lines={b.lines} />
          : <div key={i}>{renderMarkdownLines(b.lines, `s${i}`)}</div>
      )}
    </div>
  );
}

export default MethodologyPanel;
