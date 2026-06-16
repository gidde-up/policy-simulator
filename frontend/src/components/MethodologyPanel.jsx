import React, { useState, useEffect } from 'react';
import { BookOpen, ChevronDown, Plus, Minus, ListTree, Layers } from 'lucide-react';
import { getMethodology } from '../services/api';

// Renders docs/methodology.md as a two-tier reference:
//  - Tier 1 (plain markdown) is always shown, styled for a lay reader;
//  - `::: detail <summary>` ... `:::` fences are tier-2 disclosures with a
//    distinct "expert" style (equations, parameters, sources), collapsed
//    by default and keyboard-operable / ARIA-labelled.

function renderInline(t) {
  return t.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, i) => {
    if (part.startsWith('**')) return <strong key={i} className="font-semibold text-gray-900">{part.slice(2, -2)}</strong>;
    if (part.startsWith('`')) return <code key={i} className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded text-[0.85em] font-mono">{part.slice(1, -1)}</code>;
    return part;
  });
}

// Render plain-markdown lines: paragraphs, bullet lists, and small
// "label:" lead-ins. (The source has no h3/tables/ordered lists.)
function renderMarkdownLines(lines, keyPrefix, opts = {}) {
  const out = [];
  let list = null;
  const flush = () => {
    if (list) {
      out.push(<ul key={`${keyPrefix}-l${out.length}`} className="space-y-1.5 mb-3 ml-1">{list}</ul>);
      list = null;
    }
  };
  lines.forEach((line) => {
    if (line.startsWith('## ') || line.startsWith('# ')) return; // headers handled by the section shell
    if (line.startsWith('- ')) {
      list = list || [];
      list.push(
        <li key={list.length} className="flex items-start">
          <span className={`mt-2 mr-2 h-1.5 w-1.5 flex-shrink-0 rounded-full ${opts.expert ? 'bg-slate-400' : 'bg-blue-400'}`} />
          <span>{renderInline(line.slice(2))}</span>
        </li>
      );
    } else if (line.trim() === '') {
      flush();
    } else {
      flush();
      // a short "label:" lead-in (e.g. "Industrial and sectoral:") gets emphasis
      const isLabel = /:\s*$/.test(line) && line.length < 60;
      out.push(
        <p key={`${keyPrefix}-${out.length}`}
           className={isLabel
             ? 'font-semibold text-gray-800 mt-3 mb-1'
             : 'mb-3 leading-relaxed'}>
          {renderInline(line)}
        </p>
      );
    }
  });
  flush();
  return out;
}

function Detail({ summary, lines }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="my-4 rounded-lg border border-slate-200 bg-slate-50 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="w-full flex items-center justify-between px-4 py-2.5 text-left text-sm font-medium text-slate-700 hover:bg-slate-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
      >
        <span className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-slate-500" />
          <span>{summary || 'Show the detail and equations'}</span>
        </span>
        {open ? <Minus className="w-4 h-4 text-slate-500" /> : <Plus className="w-4 h-4 text-slate-500" />}
      </button>
      {open && (
        <div className="px-4 py-3 border-t border-slate-200 bg-white text-sm text-gray-600">
          <div className="mb-2 inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-[0.7rem] font-medium uppercase tracking-wide text-slate-500">
            Expert detail
          </div>
          {renderMarkdownLines(lines, 'd', { expert: true })}
        </div>
      )}
    </div>
  );
}

// Parse into a hero (pre-first-h2) and numbered sections, each carrying an
// ordered sequence of md / detail blocks.
function parse(md) {
  let heroTitle = 'How this simulator works';
  const heroBlocks = [];
  const sections = [];
  let cur = null;            // current section object (null => hero)
  let buffer = [];
  let inDetail = false, detailSummary = '', detailLines = [];

  const bucket = () => (cur ? cur.blocks : heroBlocks);
  const flushBuffer = () => {
    if (buffer.length) { bucket().push({ type: 'md', lines: buffer }); buffer = []; }
  };

  md.split('\n').forEach((line) => {
    const dm = line.match(/^:::\s*detail\s*(.*)$/);
    if (dm) { flushBuffer(); inDetail = true; detailSummary = dm[1] || ''; detailLines = []; return; }
    if (line.trim() === ':::' && inDetail) {
      bucket().push({ type: 'detail', summary: detailSummary, lines: detailLines });
      inDetail = false; return;
    }
    if (inDetail) { detailLines.push(line); return; }

    const h2 = line.match(/^##\s+(?:(\d+)\.\s*)?(.*)$/);
    if (h2) {
      flushBuffer();
      cur = { num: h2[1] || String(sections.length + 1), title: h2[2], blocks: [] };
      sections.push(cur);
      return;
    }
    const h1 = line.match(/^#\s+(.*)$/);
    if (h1 && !cur) { heroTitle = h1[1]; return; }

    buffer.push(line);
  });
  flushBuffer();
  return { heroTitle, heroBlocks, sections };
}

function MethodologyPanel() {
  const [markdown, setMarkdown] = useState(null);
  useEffect(() => {
    getMethodology().then((d) => setMarkdown(d.markdown))
      .catch(() => setMarkdown('# Methodology\nCould not load the methodology document.'));
  }, []);

  if (markdown === null) {
    return (
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-md p-8 text-gray-500">
        Loading methodology...
      </div>
    );
  }

  const { heroTitle: title, heroBlocks, sections } = parse(markdown);

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      {/* Hero */}
      <div className="rounded-2xl shadow-md overflow-hidden">
        <div className="bg-gradient-to-r from-blue-700 to-blue-900 text-white p-7">
          <div className="flex items-center space-x-2 mb-2 text-blue-200">
            <BookOpen className="w-5 h-5" />
            <span className="text-xs uppercase tracking-widest">Methodology</span>
          </div>
          <h1 className="text-2xl font-bold mb-3">{title}</h1>
          <div className="text-blue-50 text-sm leading-relaxed max-w-2xl">
            {renderMarkdownLines(heroBlocks.flatMap(b => b.lines || []), 'hero')}
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="inline-flex items-center rounded-full bg-white/15 px-3 py-1 text-xs">
              Tier 1 - plain language, always shown
            </span>
            <span className="inline-flex items-center rounded-full bg-white/10 px-3 py-1 text-xs text-blue-100">
              <Layers className="w-3.5 h-3.5 mr-1" /> Tier 2 - expand for equations and sources
            </span>
          </div>
        </div>
      </div>

      {/* Table of contents */}
      <div className="bg-white rounded-2xl shadow-md p-5">
        <div className="flex items-center space-x-2 mb-3 text-gray-500">
          <ListTree className="w-4 h-4" />
          <span className="text-xs uppercase tracking-wide">On this page</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {sections.map((s) => (
            <button
              key={s.num}
              onClick={() => scrollTo(`methodology-${s.num}`)}
              className="flex items-center space-x-3 text-left p-2 rounded-lg hover:bg-blue-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
            >
              <span className="flex-shrink-0 h-7 w-7 rounded-full bg-blue-100 text-blue-700 text-sm font-bold flex items-center justify-center">
                {s.num}
              </span>
              <span className="text-sm text-gray-700">{s.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Sections */}
      {sections.map((s) => (
        <section
          key={s.num}
          id={`methodology-${s.num}`}
          className="bg-white rounded-2xl shadow-md p-6 scroll-mt-4"
        >
          <div className="flex items-center space-x-3 mb-4 pb-3 border-b border-gray-100">
            <span className="flex-shrink-0 h-9 w-9 rounded-full bg-blue-600 text-white text-base font-bold flex items-center justify-center">
              {s.num}
            </span>
            <h2 className="text-xl font-bold text-gray-900">{s.title}</h2>
          </div>
          <div className="text-gray-700">
            {s.blocks.map((b, i) =>
              b.type === 'detail'
                ? <Detail key={i} summary={b.summary} lines={b.lines} />
                : <div key={i}>{renderMarkdownLines(b.lines, `s${s.num}-${i}`)}</div>
            )}
          </div>
        </section>
      ))}

      <p className="text-center text-xs text-gray-400 pb-4">
        Full lever notes: docs/levers/ and the assumptions popover beside each
        lever. This is a training simulator, not a forecast or a policy
        recommendation.
      </p>
    </div>
  );
}

export default MethodologyPanel;
