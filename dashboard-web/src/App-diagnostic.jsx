import React, { useState, useEffect } from 'react'

export default function App() {
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    console.log('[App] Component mounted')
    console.log('[App] Testing API resilience...')
    
    try {
      // Try to import and test the api-resilient module
      import('./api-resilient.js').then(api => {
        console.log('[App] api-resilient loaded successfully')
        console.log('[App] Available functions:', Object.keys(api))
        setStatus('ready')
      }).catch(err => {
        console.error('[App] Failed to load api-resilient:', err)
        setError(`Failed to load API module: ${err.message}`)
        setStatus('error')
      })
    } catch (err) {
      console.error('[App] Error:', err)
      setError(err.toString())
      setStatus('error')
    }
  }, [])

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif' }}>
      <h1>Career-Ops Diagnostic</h1>
      
      <div style={{ marginTop: '20px', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
        <p><strong>Status:</strong> {status}</p>
        
        {error && (
          <div style={{ padding: '10px', background: '#ffebee', color: '#c62828', borderRadius: '4px', marginTop: '10px' }}>
            <strong>Error:</strong> {error}
          </div>
        )}
        
        {status === 'ready' && (
          <div style={{ padding: '10px', background: '#e8f5e9', color: '#2e7d32', borderRadius: '4px', marginTop: '10px' }}>
            API Module loaded successfully! Ready to test backend connection...
          </div>
        )}
      </div>

      <div style={{ marginTop: '20px', padding: '20px', background: '#f5f5f5', borderRadius: '8px' }}>
        <h3>Debug Information</h3>
        <pre style={{ fontSize: '12px', overflow: 'auto' }}>
          Window location: {window.location.href}
          Backend endpoint: http://localhost:5000
          Frontend port: 5174
          Status: {status}
        </pre>
      </div>

      <div style={{ marginTop: '20px' }}>
        <p>Check browser console (F12) for detailed logs</p>
      </div>
    </div>
  )
}
