const ICONS = ['🔍', '📡', '📊', '✨', '🚀']

export default function PipelineBar({ steps, activeStep, completedSteps, onStepClick }) {
  return (
    <div className="pipeline-bar">
      {steps.map((step, i) => {
        const isActive = activeStep === i
        const isCompleted = completedSteps.includes(i)
        let cls = 'pipeline-step'
        if (isActive) cls += ' active'
        else if (isCompleted) cls += ' completed'

        return (
          <div key={step} style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
            <div className={cls} onClick={() => onStepClick(i)} style={{ flex: 1 }}>
              <span className="step-icon">{isCompleted && !isActive ? '✓' : ICONS[i]}</span>
              <span>{step}</span>
            </div>
            {i < steps.length - 1 && <span className="pipeline-arrow">→</span>}
          </div>
        )
      })}
    </div>
  )
}
