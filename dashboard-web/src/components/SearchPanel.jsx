import { useState } from 'react'

const LOCATIONS = [
  'Dubai', 'Abu Dhabi', 'Riyadh', 'Jeddah', 'Doha',
  'Bangalore', 'Remote', 'Any'
]

const CURRENCIES = ['AED', 'QAR', 'SAR', 'INR', 'USD']

export default function SearchPanel({ onSearch, loading }) {
  const [title, setTitle] = useState('Marketing Manager')
  const [location, setLocation] = useState('Dubai')
  const [currency, setCurrency] = useState('AED')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch({ title, location, currency })
  }

  return (
    <div className="search-panel">
      <h2>🔍 Job Search Filters</h2>
      <form onSubmit={handleSubmit}>
        <div className="search-grid">
          <div className="form-group">
            <label className="form-label" htmlFor="search-title">Job Title / Keywords</label>
            <input
              id="search-title"
              className="form-input"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Marketing Manager, AI Content Lead"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="search-location">Location</label>
            <select
              id="search-location"
              className="form-select"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            >
              {LOCATIONS.map(loc => (
                <option key={loc} value={loc}>{loc}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="search-currency">Currency</label>
            <select
              id="search-currency"
              className="form-select"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
            >
              {CURRENCIES.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">&nbsp;</label>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !title.trim()}
              id="search-btn"
            >
              {loading ? (
                <><span className="spinner"></span> Searching...</>
              ) : (
                <>🔍 Search</>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
