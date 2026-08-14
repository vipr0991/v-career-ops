export default function ScoreRing({ score, size = 60 }) {
  const radius = (size - 8) / 2
  const circumference = 2 * Math.PI * radius
  const percent = Math.min(100, Math.max(0, score || 0))
  const offset = circumference - (percent / 100) * circumference
  const level = percent >= 70 ? 'high' : percent >= 45 ? 'medium' : 'low'

  return (
    <div className="score-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle
          className="ring-bg"
          cx={size / 2}
          cy={size / 2}
          r={radius}
        />
        <circle
          className={`ring-fill ${level}`}
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <span className={`score-value ${level}`}>{percent}%</span>
    </div>
  )
}
