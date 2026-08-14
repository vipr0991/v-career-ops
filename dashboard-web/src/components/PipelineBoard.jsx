import React from 'react'

const COLUMNS = [
  { id: 'new', label: 'New', className: 'new' },
  { id: 'evaluating', label: 'Evaluating', className: 'evaluating' },
  { id: 'scored', label: 'Scored', className: 'scored' },
  { id: 'applied', label: 'Applied', className: 'applied' },
  { id: 'interview', label: 'Interview', className: 'interview' },
  { id: 'offer', label: 'Offer', className: 'offer' },
]

function getScoreClass(score) {
  if (score == null) return ''
  if (score >= 70) return 'high'
  if (score >= 45) return 'medium'
  return 'low'
}

export default function PipelineBoard({ items, onCardClick, onStatusChange }) {
  const grouped = {}
  COLUMNS.forEach((col) => { grouped[col.id] = [] })

  ;(items || []).forEach((item) => {
    const status = (item.status || 'new').toLowerCase()
    if (grouped[status]) {
      grouped[status].push(item)
    } else {
      grouped['new'].push(item)
    }
  })

  return (
    <div className="kanban-board" id="pipeline-board">
      {COLUMNS.map((col) => (
        <div key={col.id} className={`kanban-column ${col.className}`}>
          <div className="kanban-column-header">
            <div className="kanban-column-title">
              <span className="dot" />
              {col.label}
            </div>
            <span className="kanban-count">{grouped[col.id].length}</span>
          </div>
          <div className="kanban-cards">
            {grouped[col.id].length === 0 ? (
              <div className="kanban-empty">No items</div>
            ) : (
              grouped[col.id].map((card) => (
                <div
                  key={card.id}
                  className="kanban-card"
                  onClick={() => onCardClick?.(card)}
                >
                  <div className="kanban-card-title">{card.role || card.title || 'Untitled'}</div>
                  <div className="kanban-card-company">{card.company || 'Unknown'}</div>
                  <div className="kanban-card-meta">
                    {card.score != null && (
                      <span className={`kanban-card-score ${getScoreClass(card.score)}`}>
                        {Math.round(card.score)}%
                      </span>
                    )}
                    {card.location && <span>{card.location}</span>}
                    {card.date && <span>{card.date}</span>}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
