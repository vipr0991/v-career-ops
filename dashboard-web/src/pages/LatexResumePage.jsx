import React, { useState, useRef } from 'react'

/* ─── Candidate defaults (edit here or via the form) ─────────────────────── */
const CANDIDATE = {
  name:     'Vinay Prakash',
  email:    'vinay@email.com',
  linkedin: 'linkedin.com/in/vinayprakash',
  phone:    '+971 50 000 0000',
  location: 'Dubai, UAE',
}

const BASE_EXPERIENCE = [
  {
    title:    'AI Content & Automation Lead',
    company:  'Previous Company',
    location: 'Dubai, UAE',
    period:   'Jan 2023 – Present',
    bullets: [
      'Led AI-driven content strategy achieving 40% increase in organic reach across digital channels.',
      'Automated marketing workflows using Python and n8n, reducing manual effort by 60%.',
      'Developed and deployed GPT-powered tools for content generation and SEO optimisation.',
    ],
  },
  {
    title:    'Senior Digital Marketing Manager',
    company:  'Earlier Company',
    location: 'Dubai, UAE',
    period:   'Jul 2020 – Dec 2022',
    bullets: [
      'Managed $2M annual paid media budget across Google, Meta, and LinkedIn platforms.',
      'Built end-to-end marketing analytics dashboards using Power BI and Google Data Studio.',
      'Spearheaded regional campaigns across UAE, KSA, and Qatar markets.',
    ],
  },
]

const BASE_SKILLS = {
  'Core Skills':       'AI Content Strategy, Marketing Automation, SEO/SEM, Data Analytics, Campaign Management',
  'Tools & Platforms': 'HubSpot, Salesforce, Google Analytics, Meta Ads, LinkedIn Ads, n8n, Zapier',
  'Technical':         'Python, SQL, Power BI, Tableau, GPT APIs, Prompt Engineering',
  'Languages':         'English (Native), Arabic (Conversational)',
}

/* ─── LaTeX builder ────────────────────────────────────────────────────────── */
function buildLatex({ name, email, phone, linkedin, location, experience, skills, summary }) {
  const esc = s => (s||'').replace(/&/g,'\\&').replace(/%/g,'\\%').replace(/#/g,'\\#').replace(/_/g,'\\_').replace(/\$/g,'\\$')
  const expSec = experience.map(e => `
    \\resumeSubheading
      {${esc(e.title)}}{${esc(e.location)}}
      {${esc(e.company)}}{${esc(e.period)}}
      \\resumeItemListStart
${e.bullets.map(b=>`        \\resumeItem{${esc(b)}}`).join('\n')}
      \\resumeItemListEnd`).join('\n')
  const skillLines = Object.entries(skills).map(([k,v])=>`     \\textbf{${esc(k)}}{: ${esc(v)}}`).join(' \\\\\n')
  const sumSec = summary ? `\n%-----------SUMMARY-----------\n\\section{Professional Summary}\n\\small{${esc(summary)}}\n` : ''
  return `\\documentclass[letterpaper,11pt]{article}
\\usepackage{latexsym}
\\usepackage[empty]{fullpage}
\\usepackage{titlesec}
\\usepackage[usenames,dvipsnames]{color}
\\usepackage{enumitem}
\\usepackage[hidelinks]{hyperref}
\\usepackage[english]{babel}
\\usepackage{tabularx}
\\addtolength{\\oddsidemargin}{-0.5in}
\\addtolength{\\evensidemargin}{-0.5in}
\\addtolength{\\textwidth}{1.0in}
\\addtolength{\\topmargin}{-.5in}
\\addtolength{\\textheight}{1.0in}
\\urlstyle{same}\\raggedbottom\\raggedright\\setlength{\\tabcolsep}{0in}
\\titleformat{\\section}{\\vspace{-4pt}\\scshape\\raggedright\\large}{}{0em}{}[\\color{black}\\titlerule\\vspace{-5pt}]
\\newcommand{\\resumeItem}[1]{\\item\\small{{#1\\vspace{-2pt}}}}
\\newcommand{\\resumeSubheading}[4]{\\vspace{-2pt}\\item
  \\begin{tabularx}{\\textwidth}[t]{l@{\\extracolsep{\\fill}}r}
    \\textbf{#1} & #2 \\\\ \\textit{\\small#3} & \\textit{\\small#4} \\\\
  \\end{tabularx}\\vspace{-5pt}}
\\renewcommand{\\labelitemii}{$\\circ$}
\\newcommand{\\resumeSubHeadingListStart}{\\begin{itemize}[leftmargin=*]}
\\newcommand{\\resumeSubHeadingListEnd}{\\end{itemize}}
\\newcommand{\\resumeItemListStart}{\\begin{itemize}}
\\newcommand{\\resumeItemListEnd}{\\end{itemize}\\vspace{-5pt}}

\\begin{document}
\\begin{tabular*}{\\textwidth}{l@{\\extracolsep{\\fill}}r}
  \\textbf{\\Large ${esc(name)}} & Email: \\href{mailto:${email}}{${esc(email)}}\\\\
  ${esc(location)} & Mobile: ${esc(phone)} \\\\
  \\href{https://${linkedin}}{${esc(linkedin)}} & \\\\
\\end{tabular*}
${sumSec}
\\section{Experience}
  \\resumeSubHeadingListStart
${expSec}
  \\resumeSubHeadingListEnd

\\section{Skills}
 \\begin{itemize}[leftmargin=*,label={}]
    \\small{\\item{
${skillLines}
    }}
 \\end{itemize}
\\end{document}`
}

/* ─── Visual resume renderer (HTML, prints like a real resume) ─────────────── */
function ResumePreview({ name, email, phone, linkedin, location, experience, skills, summary, targetRole, targetCompany }) {
  return (
    <div id="resume-visual" style={{
      fontFamily: "'Times New Roman", serif',
      fontSize: 11,
      color: '#000',
      background: '#fff',
      padding: '0.6in 0.7in',
      width: '8.5in',
      minHeight: '11in',
      boxSizing: 'border-box',
      margin: '0 auto',
      boxShadow: '0 4px 40px rgba(0,0,0,0.35)',
      lineHeight: 1.35,
    }}>
      {/* HEADING */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
        <div>
          <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: 0.5 }}>{name}</div>
          {location && <div style={{ fontSize: 11, marginTop: 2, color: '#333' }}>{location}</div>}
        </div>
        <div style={{ textAlign: 'right', fontSize: 11, color: '#222', lineHeight: 1.7 }}>
          <div><a href={`mailto:${email}`} style={{ color: '#000' }}>{email}</a></div>
          <div>{phone}</div>
          <div><a href={`https://${linkedin}`} style={{ color: '#000' }}>{linkedin}</a></div>
        </div>
      </div>

      {/* horizontal rule */}
      <hr style={{ border: 'none', borderTop: '1px solid #000', margin: '4px 0 8px' }} />

      {/* TARGET ROLE badge (if set) */}
      {(targetRole || targetCompany) && (
        <div style={{ fontSize: 11, color: '#444', fontStyle: 'italic', marginBottom: 10 }}>
          {targetRole && <span>Tailored for: <strong>{targetRole}</strong></span>}
          {targetRole && targetCompany && <span> at </span>}
          {targetCompany && <strong>{targetCompany}</strong>}
        </div>
      )}

      {/* SUMMARY */}
      {summary && (
        <>
          <SectionHeader>Professional Summary</SectionHeader>
          <p style={{ fontSize: 11, margin: '4px 0 10px', lineHeight: 1.5 }}>{summary}</p>
        </>
      )}

      {/* EXPERIENCE */}
      <SectionHeader>Experience</SectionHeader>
      {experience.map((exp, i) => (
        <div key={i} style={{ marginBottom: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ fontWeight: 700, fontSize: 11.5 }}>{exp.title}</span>
            <span style={{ fontSize: 11, color: '#333' }}>{exp.location}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 1 }}>
            <span style={{ fontStyle: 'italic', fontSize: 11 }}>{exp.company}</span>
            <span style={{ fontStyle: 'italic', fontSize: 11, color: '#333' }}>{exp.period}</span>
          </div>
          <ul style={{ margin: '4px 0 0 18px', padding: 0 }}>
            {exp.bullets.filter(b => b.trim()).map((b, j) => (
              <li key={j} style={{ fontSize: 11, marginBottom: 2, lineHeight: 1.4 }}>{b}</li>
            ))}
          </ul>
        </div>
      ))}

      {/* SKILLS */}
      <SectionHeader>Skills</SectionHeader>
      <div style={{ marginTop: 4 }}>
        {Object.entries(skills).map(([k, v]) => (
          <div key={k} style={{ fontSize: 11, marginBottom: 3, lineHeight: 1.4 }}>
            <strong>{k}: </strong>{v}
          </div>
        ))}
      </div>
    </div>
  )
}

function SectionHeader({ children }) {
  return (
    <div style={{ marginTop: 10, marginBottom: 4 }}>
      <div style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.8, fontVariant: 'small-caps' }}>
        {children}
      </div>
      <hr style={{ border: 'none', borderTop: '1px solid #000', margin: '2px 0 6px' }} />
    </div>
  )
}

/* ─── Print helper ─────────────────────────────────────────────────────────── */
function printResume() {
  const el = document.getElementById('resume-visual')
  if (!el) return
  const w = window.open('', '_blank')
  w.document.write(`<!DOCTYPE html><html><head><title>Resume</title>
  <style>
    body { margin: 0; padding: 0; background: #fff; }
    @page { size: letter; margin: 0; }
    @media print { body { -webkit-print-color-adjust: exact; } }
  </style></head><body>`)
  w.document.write(el.outerHTML)
  w.document.write('</body></html>')
  w.document.close()
  w.focus()
  setTimeout(() => { w.print(); w.close() }, 400)
}

/* ─── Main component ───────────────────────────────────────────────────────── */
export default function LatexResumePage({ jobs, addToast, apiFetch }) {
  const [targetRole, setTargetRole]       = useState('')
  const [targetCompany, setTargetCompany] = useState('')
  const [summary, setSummary]             = useState('')
  const [experience, setExperience]       = useState(BASE_EXPERIENCE)
  const [skills, setSkills]               = useState(BASE_SKILLS)
  const [latex, setLatex]                 = useState('')
  const [generating, setGenerating]       = useState(false)
  const [activeTab, setActiveTab]         = useState('editor') // editor | visual | code

  const scoredJobs = (jobs || []).filter(j => j.score != null)

  /* fill fields from a scored job */
  const fillFromJob = (jobId) => {
    const job = scoredJobs.find(j => j.id === jobId)
    if (!job) return
    setTargetRole(job.role || job.title || '')
    setTargetCompany(job.company || '')
    addToast(`Loaded: ${job.role || job.title} at ${job.company}`, 'info')
  }

  /* generate latex + switch to visual tab */
  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const doc = buildLatex({ name: CANDIDATE.name, email: CANDIDATE.email, phone: CANDIDATE.phone, linkedin: CANDIDATE.linkedin, location: CANDIDATE.location, experience, skills, summary })
      setLatex(doc)
      try {
        await apiFetch('/api/save-latex', { method:'POST', body: JSON.stringify({ latex: doc, role: targetRole, company: targetCompany }) })
      } catch {}
      setActiveTab('visual')
      addToast('Resume generated', 'success')
    } catch (err) {
      addToast(`Generation failed: ${err.message}`, 'error')
    } finally {
      setGenerating(false)
    }
  }

  const downloadLatex = () => {
    const slug = (targetRole || 'resume').toLowerCase().replace(/\s+/g, '-')
    const a = document.createElement('a')
    a.href = URL.createObjectURL(new Blob([latex], { type: 'text/plain' }))
    a.download = `${slug}-resume.tex`
    a.click()
    addToast('.tex file downloaded', 'success')
  }

  /* experience / skills edit helpers */
  const updBullet  = (ei,bi,v) => setExperience(p=>p.map((e,i)=>i===ei?{...e,bullets:e.bullets.map((b,j)=>j===bi?v:b)}:e))
  const addBullet  = (ei)      => setExperience(p=>p.map((e,i)=>i===ei?{...e,bullets:[...e.bullets,'']}:e))
  const remBullet  = (ei,bi)   => setExperience(p=>p.map((e,i)=>i===ei?{...e,bullets:e.bullets.filter((_,j)=>j!==bi)}:e))
  const updField   = (ei,f,v)  => setExperience(p=>p.map((e,i)=>i===ei?{...e,[f]:v}:e))
  const updSkill   = (k,v)     => setSkills(p=>({...p,[k]:v}))

  const Tab = ({ id, icon, label, disabled }) => (
    <button
      disabled={disabled}
      onClick={() => setActiveTab(id)}
      style={{
        display: 'flex', alignItems: 'center', gap: 6,
        padding: '8px 18px', fontSize: 12, fontWeight: 600,
        cursor: disabled ? 'not-allowed' : 'pointer',
        border: 'none', borderRadius: 'var(--radius-sm)',
        background: activeTab === id ? 'var(--accent-primary)' : 'var(--bg-glass)',
        color: activeTab === id ? '#fff' : disabled ? 'var(--text-muted)' : 'var(--text-secondary)',
        opacity: disabled ? 0.5 : 1,
        transition: 'all 0.2s',
      }}
    >
      <span className="material-symbols-outlined" style={{ fontSize: 15 }}>{icon}</span>
      {label}
    </button>
  )

  return (
    <div className="page-content" id="latex-resume-page">

      {/* ── Top control bar ──────────────────────────────────────────────── */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <span className="material-symbols-outlined" style={{ color:'var(--accent-primary-light)' }}>description</span>
            LaTeX Resume Builder
          </div>
          <div style={{ display:'flex', gap:8 }}>
            <Tab id="editor" icon="edit"       label="Editor" />
            <Tab id="visual" icon="visibility"  label="Visual Preview" disabled={!latex} />
            <Tab id="code"   icon="code"        label="LaTeX Code"     disabled={!latex} />
            {latex && (
              <>
                <button onClick={printResume}   style={{ display:'flex', alignItems:'center', gap:6, padding:'8px 18px', fontSize:12, fontWeight:600, border:'none', borderRadius:'var(--radius-sm)', background:'var(--accent-secondary)', color:'#fff', cursor:'pointer' }}>
                  <span className="material-symbols-outlined" style={{fontSize:15}}>print</span> Print / PDF
                </button>
                <button onClick={downloadLatex} style={{ display:'flex', alignItems:'center', gap:6, padding:'8px 18px', fontSize:12, fontWeight:600, border:'none', borderRadius:'var(--radius-sm)', background:'var(--accent-success)', color:'#fff', cursor:'pointer' }}>
                  <span className="material-symbols-outlined" style={{fontSize:15}}>download</span> .tex
                </button>
              </>
            )}
          </div>
        </div>

        {/* Job selector row */}
        <div style={{ display:'grid', gridTemplateColumns:'1.2fr 1fr 2fr auto', gap:12, alignItems:'end', marginTop:16 }}>
          <div className="form-group" style={{margin:0}}>
            <label className="form-label">Auto-fill from scored job</label>
            <select className="form-select" onChange={e=>fillFromJob(e.target.value)} defaultValue="">
              <option value="">— Pick a scored job —</option>
              {scoredJobs.map(j=>(
                <option key={j.id} value={j.id}>{j.role||j.title} @ {j.company} ({Math.round(j.score||0)}%)</option>
              ))}
            </select>
          </div>
          <div className="form-group" style={{margin:0}}>
            <label className="form-label">Target Role</label>
            <input className="form-input" value={targetRole} onChange={e=>setTargetRole(e.target.value)} placeholder="e.g. Marketing Manager" />
          </div>
          <div className="form-group" style={{margin:0}}>
            <label className="form-label">Professional Summary (optional)</label>
            <input className="form-input" value={summary} onChange={e=>setSummary(e.target.value)} placeholder="One-line tailored summary…" />
          </div>
          <button className="btn btn-primary" onClick={handleGenerate} disabled={generating} style={{alignSelf:'end'}}>
            {generating
              ? <><span className="spinner"/> Generating…</>
              : <><span className="material-symbols-outlined" style={{fontSize:16}}>auto_awesome</span> Generate</>}
          </button>
        </div>
      </div>

      {/* ── EDITOR TAB ───────────────────────────────────────────────────── */}
      {activeTab === 'editor' && (
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16, marginTop:16 }}>

          {/* Experience */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <span className="material-symbols-outlined" style={{color:'var(--accent-secondary)'}}>work</span>
                Experience
              </div>
            </div>
            {experience.map((exp, ei) => (
              <div key={ei} style={{ marginBottom:20, borderBottom:'1px solid var(--border-subtle)', paddingBottom:16 }}>
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:8 }}>
                  {[['title','Job Title'],['company','Company'],['location','Location'],['period','Period']].map(([f,p])=>(
                    <input key={f} className="form-input" style={{fontSize:12}} value={exp[f]} onChange={e=>updField(ei,f,e.target.value)} placeholder={p} />
                  ))}
                </div>
                <div style={{fontSize:11,fontWeight:600,color:'var(--text-muted)',marginBottom:6}}>Bullet Points</div>
                {exp.bullets.map((b, bi) => (
                  <div key={bi} style={{display:'flex',gap:6,marginBottom:6}}>
                    <textarea className="form-input" style={{fontSize:12,minHeight:40,resize:'vertical',flex:1}} value={b} onChange={e=>updBullet(ei,bi,e.target.value)} placeholder="Achievement bullet…" />
                    <button onClick={()=>remBullet(ei,bi)} style={{background:'none',border:'none',color:'var(--accent-danger)',cursor:'pointer',fontSize:18,alignSelf:'flex-start',lineHeight:1}}>✕</button>
                  </div>
                ))}
                <button onClick={()=>addBullet(ei)} className="btn btn-secondary btn-sm" style={{marginTop:4}}>
                  <span className="material-symbols-outlined" style={{fontSize:14}}>add</span> Add Bullet
                </button>
              </div>
            ))}
          </div>

          {/* Skills */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <span className="material-symbols-outlined" style={{color:'var(--accent-warning)'}}>psychology</span>
                Skills
              </div>
              <span style={{fontSize:11,color:'var(--text-muted)'}}>Core skills preserved — refine wording only</span>
            </div>
            {Object.entries(skills).map(([k,v])=>(
              <div key={k} className="form-group">
                <label className="form-label" style={{fontSize:11}}>{k}</label>
                <textarea className="form-input" style={{fontSize:12,minHeight:52,resize:'vertical'}} value={v} onChange={e=>updSkill(k,e.target.value)} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── VISUAL PREVIEW TAB ───────────────────────────────────────────── */}
      {activeTab === 'visual' && latex && (
        <div style={{ marginTop:16 }}>
          {/* toolbar */}
          <div style={{ display:'flex', alignItems:'center', gap:12, padding:'12px 16px', background:'var(--bg-card)', borderRadius:'var(--radius-lg)', border:'1px solid var(--border-subtle)', marginBottom:16 }}>
            <span className="material-symbols-outlined" style={{color:'var(--accent-success)',fontSize:18}}>visibility</span>
            <span style={{fontSize:12,color:'var(--text-secondary)',flex:1}}>
              This is an accurate visual representation of your resume. Use <strong>Print / PDF</strong> to save it.
            </span>
            <button onClick={printResume} style={{display:'flex',alignItems:'center',gap:6,padding:'8px 16px',fontSize:12,fontWeight:600,border:'none',borderRadius:'var(--radius-sm)',background:'var(--accent-secondary)',color:'#fff',cursor:'pointer'}}>
              <span className="material-symbols-outlined" style={{fontSize:15}}>print</span> Print / Save as PDF
            </button>
            <button onClick={downloadLatex} style={{display:'flex',alignItems:'center',gap:6,padding:'8px 16px',fontSize:12,fontWeight:600,border:'none',borderRadius:'var(--radius-sm)',background:'var(--accent-success)',color:'#fff',cursor:'pointer'}}>
              <span className="material-symbols-outlined" style={{fontSize:15}}>download</span> Download .tex
            </button>
          </div>

          {/* A4/Letter page wrapper */}
          <div style={{ background:'#888', padding:'32px 24px', borderRadius:8, overflowX:'auto' }}>
            <ResumePreview
              name={CANDIDATE.name}
              email={CANDIDATE.email}
              phone={CANDIDATE.phone}
              linkedin={CANDIDATE.linkedin}
              location={CANDIDATE.location}
              experience={experience}
              skills={skills}
              summary={summary}
              targetRole={targetRole}
              targetCompany={targetCompany}
            />
          </div>
        </div>
      )}

      {/* ── LATEX CODE TAB ───────────────────────────────────────────────── */}
      {activeTab === 'code' && latex && (
        <div className="panel" style={{ marginTop:16 }}>
          <div className="panel-header">
            <div className="panel-title">
              <span className="material-symbols-outlined" style={{color:'var(--accent-primary-light)'}}>code</span>
              LaTeX Source
            </div>
            <div style={{display:'flex',gap:8}}>
              <button className="btn btn-secondary btn-sm" onClick={()=>{navigator.clipboard.writeText(latex);addToast('Copied!','success')}}>
                <span className="material-symbols-outlined" style={{fontSize:14}}>content_copy</span> Copy
              </button>
              <button className="btn btn-primary btn-sm" onClick={downloadLatex}>
                <span className="material-symbols-outlined" style={{fontSize:14}}>download</span> Download .tex
              </button>
            </div>
          </div>
          <div style={{ background:'rgba(99,102,241,0.07)', border:'1px solid rgba(99,102,241,0.2)', borderRadius:8, padding:'10px 14px', marginBottom:16, fontSize:12, color:'var(--text-secondary)' }}>
            <strong>Compile on</strong>{' '}
            <a href="https://www.overleaf.com" target="_blank" rel="noopener noreferrer" style={{color:'var(--accent-primary-light)'}}>Overleaf</a>
            {' '}or locally with <code>pdflatex resume.tex</code>
          </div>
          <pre style={{ background:'var(--bg-secondary)', border:'1px solid var(--border-subtle)', borderRadius:'var(--radius-md)', padding:20, fontSize:11, fontFamily:'var(--font-mono,monospace)', lineHeight:1.6, overflowX:'auto', whiteSpace:'pre-wrap', color:'var(--text-primary)', maxHeight:'70vh', overflowY:'auto' }}>
            {latex}
          </pre>
        </div>
      )}
    </div>
  )
}
