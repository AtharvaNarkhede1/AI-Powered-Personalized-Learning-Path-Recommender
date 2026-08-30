import React from 'react';

/**
 * Tiny, dependency-free markdown renderer.
 * Handles: **bold**, *italic*, `code`, [text](url), headings (#),
 * bullet lists (-, *, •, 1.), and blank-line paragraphs.
 * Enough for the assistant + path-explanation replies.
 */

function renderInline(text, keyPrefix) {
  const nodes = [];
  // token regex: bold, italic, code, link
  const re = /(\*\*([^*]+)\*\*)|(\*([^*]+)\*)|(`([^`]+)`)|(\[([^\]]+)\]\(([^)]+)\))/g;
  let last = 0;
  let m;
  let i = 0;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) nodes.push(text.slice(last, m.index));
    if (m[2] !== undefined) {
      nodes.push(<strong key={`${keyPrefix}-b-${i}`}>{m[2]}</strong>);
    } else if (m[4] !== undefined) {
      nodes.push(<em key={`${keyPrefix}-i-${i}`}>{m[4]}</em>);
    } else if (m[6] !== undefined) {
      nodes.push(<code key={`${keyPrefix}-c-${i}`} className="md-code">{m[6]}</code>);
    } else if (m[8] !== undefined) {
      nodes.push(
        <a key={`${keyPrefix}-l-${i}`} href={m[9]} target="_blank" rel="noopener noreferrer">
          {m[8]}
        </a>
      );
    }
    last = m.index + m[0].length;
    i += 1;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

export default function Markdown({ text = '', className = '' }) {
  const lines = String(text).replace(/\r\n/g, '\n').split('\n');
  const blocks = [];
  let list = null;
  let para = [];

  const flushPara = () => {
    if (para.length) {
      blocks.push({ type: 'p', content: para.join(' ') });
      para = [];
    }
  };
  const flushList = () => {
    if (list) {
      blocks.push({ type: 'ul', items: list });
      list = null;
    }
  };

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) {
      flushPara();
      flushList();
      continue;
    }
    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    const bullet = line.match(/^([-*•]|\d+\.)\s+(.*)$/);
    if (heading) {
      flushPara();
      flushList();
      blocks.push({ type: 'h', level: heading[1].length, content: heading[2] });
    } else if (bullet) {
      flushPara();
      if (!list) list = [];
      list.push(bullet[2]);
    } else {
      flushList();
      para.push(line);
    }
  }
  flushPara();
  flushList();

  return (
    <div className={`md ${className}`}>
      {blocks.map((b, idx) => {
        if (b.type === 'h') {
          const Tag = `h${Math.min(b.level + 2, 5)}`;
          return <Tag key={idx} className="md-h">{renderInline(b.content, `h${idx}`)}</Tag>;
        }
        if (b.type === 'ul') {
          return (
            <ul key={idx} className="md-ul">
              {b.items.map((it, j) => <li key={j}>{renderInline(it, `li${idx}-${j}`)}</li>)}
            </ul>
          );
        }
        return <p key={idx} className="md-p">{renderInline(b.content, `p${idx}`)}</p>;
      })}
    </div>
  );
}
