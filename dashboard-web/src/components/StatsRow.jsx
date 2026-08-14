export default function StatsRow({ stats, jobsCount }) {
  const cards = [
    { icon: '🎯', value: jobsCount || 0, label: 'Jobs Found' },
    { icon: '📊', value: stats?.total_scored || 0, label: 'Reports Scored' },
    { icon: '📄', value: stats?.total_outputs || 0, label: 'PDFs Generated' },
    { icon: '📁', value: stats?.total_jds || 0, label: 'JDs on File' },
  ]

  return (
    <div className="stats-row">
      {cards.map((card, i) => (
        <div className="stat-card" key={i}>
          <div className="stat-icon">{card.icon}</div>
          <div className="stat-value">{card.value}</div>
          <div className="stat-label">{card.label}</div>
        </div>
      ))}
    </div>
  )
}
