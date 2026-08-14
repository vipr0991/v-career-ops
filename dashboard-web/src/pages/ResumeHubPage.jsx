import React, { useState, useEffect } from 'react'

// Environment-aware API base
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

/* ── Candidate defaults ──────────────────────────────────────────────────── */
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

/* ── LaTeX source builder ────────────────────────────────────────────────── */
function buildLatex({ name, email, phone, linkedin, location, experience, skills, summary }) {
  const esc = s => (s||'').replace(/&/g,'\\&').replace(/%/g,'\\%').replace(/#/g,'\\#').replace(/_/g,'\\_').replace(/\$/g,'\\$')
  const expSec = experience.map(e=>`
    \\resumeSubheading
      {${esc(e.title)}}{${esc(e.location)}}
      {${esc(e.company)}}{${esc(e.period)}}
      \\resumeItemListStart
${e.bullets.map(b=>`        \\resumeItem{${esc(b)}}`).join('\n')}
      \\resumeItemListEnd`).join('\n')
  const skillLines = Object.entries(skills).map(([k,v])=>`     \\textbf{${esc(k)}}{: ${esc(v)}}`).join(' \\\\\n')
  const sumSec = summary
    ? `\n%-----------SUMMARY-----------\n\\section{Professional Summary}\n\\small{${esc(summary)}}\n`
    : ''
  return `\\documentclass[letterpaper,11pt]{article}
\\usepackage{latexsym}
\\usepackage[empty]{fullpage}
\\usepackage{titlesec}
\\usepackage[usenames,dvipsnames]{color}
\\usepackage{enumitem}
\\usepackage[hidelinks]{hyperref}
\\usepackage[english]{babel}
\\usepackage{tabularx}
\\addtolength{\\oddsidemargin}{-0.5in}\\addtolength{\\evensidemargin}{-0.5in}
\\addtolength{\\textwidth}{1.0in}\\addtolength{\\topmargin}{-.5in}\\addtolength{\\textheight}{1.0in}
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

/* ── Visual HTML resume (renders like a real PDF page) ───────────────────── */
function ResumePreview({ name, email, phone, linkedin, location, experience, skills, summary, targetRole, targetCompany }) {
  return (
    <div id="resume-visual" style={{
      fontFamily: 'Georgia, "Times New Roman", serif',
      fontSize: 11.5,
      color: '#000',
      background: '#fff',
      padding: '0.65in 0.75in',
      width: '8.5in',
      minHeight: '11in',
      boxSizing: 'border-box',
      margin: '0 auto',
      boxShadow: '0 6px 48px rgba(0,0,0,0.45)',
      lineHeight: 1.38,
    }}>
      {/* HEADING */}
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:4 }}>
        <div>
          <div style={{ fontSize:23, fontWeight:700, letterSpacing:0.4, fontFamily:'Arial, sans-serif' }}>{name}</div>
          <div style={{ fontSize:11, marginTop:3, color:'#444' }}>{location}</div>
        </div>
        <div style={{ textAlign:'right', fontSize:11, color:'#222', lineHeight:1.75 }}>
          <div><a href={`mailto:${email}`} style={{ color:'#000', textDecoration:'none' }}>{email}</a></div>
          <div>{phone}</div>
          <div><a href={`https://${linkedin}`} style={{ color:'#000', textDecoration:'none' }}>{linkedin}</a></div>
        </div>
      </div>
      <hr style={{ border:'none', borderTop:'1.5px solid #000', margin:'5px 0 9px' }} />

      {/* TAILORED FOR label */}
      {(targetRole || targetCompany) && (
        <div style={{ fontSize:10.5, color:'#555', fontStyle:'italic', marginBottom:10, background:'#f5f5f5', padding:'4px 8px', borderRadius:3 }}>
          Tailored for: <strong>{targetRole}</strong>{targetCompany ? ` at ${targetCompany}` : ''}
        </div>
      )}

      {/* SUMMARY */}
      {summary && (
        <>
          <VSection>Professional Summary</VSection>
          <p style={{ fontSize:11, margin:'3px 0 10px', lineHeight:1.5, color:'#111' }}>{summary}</p>
        </>
      )}

      {/* EXPERIENCE */}
      <VSection>Experience</VSection>
      {experience.map((exp, i) => (
        <div key={i} style={{ marginBottom:11 }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'baseline' }}>
            <span style={{ fontWeight:700, fontSize:12, fontFamily:'Arial, sans-serif' }}>{exp.title}</span>
            <span style={{ fontSize:10.5, color:'#444', flexShrink:0, marginLeft:8 }}>{exp.location}</span>
          </div>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'baseline', marginTop:1 }}>
            <span style={{ fontStyle:'italic', fontSize:11 }}>{exp.company}</span>
            <span style={{ fontStyle:'italic', fontSize:10.5, color:'#555', flexShrink:0, marginLeft:8 }}>{exp.period}</span>
          </div>
          <ul style={{ margin:'4px 0 0 16px', padding:0 }}>
            {exp.bullets.filter(b=>b.trim()).map((b,j)=>(
              <li key={j} style={{ fontSize:11, marginBottom:2.5, lineHeight:1.45 }}>{b}</li>
            ))}
          </ul>
        </div>
      ))}

      {/* SKILLS */}
      <VSection>Skills</VSection>
      <div style={{ marginTop:4 }}>
        {Object.entries(skills).map(([k,v])=>(
          <div key={k} style={{ fontSize:11, marginBottom:3.5, lineHeight:1.45 }}>
            <strong style={{ fontFamily:'Arial, sans-serif' }}>{k}: </strong>{v}
          </div>
        ))}
      </div>
    </div>
  )
}

function VSection({ children }) {
  return (
    <div style={{ marginTop:12, marginBottom:5 }}>
      <div style={{ fontSize:13, fontWeight:700, textTransform:'uppercase', letterSpacing:1, fontFamily:'Arial, sans-serif' }}>
        {children}
      </div>
      <hr style={{ border:'none', borderTop:'1px solid #000', margin:'2px 0 5px' }} />
    </div>
  )
}

/* ── Print to new window ─────────────────────────────────────────────────── */
function printResume() {
  const el = document.getElementById('resume-visual')
  if (!el) return
  const w = window.open('', '_blank')
  w.document.write(`<!DOCTYPE html><html><head><title>Resume</title>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; padding: 0; background: #fff; }
  @page { size: letter; margin: 0; }
  @media print { html,body { width:8.5in; height:11in; } }
</style></head><body>`)
  w.document.write(el.outerHTML)
  w.document.write('</body></html>')
  w.document.close()
  w.focus()
  setTimeout(() => { w.print() }, 500)
}

/* ══════════════════════════════════════════════════════════════════════════
   MAIN PAGE COMPONENT
═══════════════════════════════════════════════════════════════════════════ */
export default function ResumeHubPage({ jobs, onOptimizeResume, addToast }) {
  /* ── Uploaded files state ────────────────────────────────────── */
  const [resumes, setResumes]   = useState([])
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [deleting, setDeleting]   = useState(null)

  /* ── Resume Builder state ────────────────────────────────────── */
  const [selectedJobId, setSelectedJobId] = useState('')
  const [targetRole, setTargetRole]         = useState('')
  const [targetCompany, setTargetCompany]   = useState('')
  const [summary, setSummary]               = useState('')
  const [experience, setExperience]         = useState(BASE_EXPERIENCE)
  const [skills, setSkills]                 = useState(BASE_SKILLS)
  const [latex, setLatex]                   = useState('')
  const [generating, setGenerating]         = useState(false)
  const [builderTab, setBuilderTab]         = useState('editor')   // editor | visual | code
  const [builderOpen, setBuilderOpen]       = useState(false)

  const scoredJobs = (jobs || []).filter(j => j.score != null)

  useEffect(() => { fetchResumes() }, [])

  /* ── API: load uploaded resumes ──────────────────────────────── */
  const fetchResumes = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/resumes`)
      if (res.ok) { const d = await res.json(); setResumes(d.files || []) }
    } catch {
      addToast('Could not load resumes — backend offline?', 'warning')
    }
  }

  /* ── Select a scored job → auto-fill builder ─────────────────── */
  const handleJobSelect = (jobId) => {
    setSelectedJobId(jobId)
    if (!jobId) return
    const job = scoredJobs.find(j => j.id === jobId)
    if (!job) return
    setTargetRole(job.role || job.title || '')
    setTargetCompany(job.company || '')
    // Set a default summary mentioning the company
    setSummary(`Results-driven marketing professional with 7+ years of experience, seeking ${job.role || job.title} at ${job.company}.`)
    setBuilderOpen(true)
    setBuilderTab('editor')
    setLatex('')        // reset any previous output
    addToast(`Builder loaded for ${job.company}`, 'info')
  }

  /* ── Generate LaTeX + visual ─────────────────────────────────── */
  const handleGenerate = async () => {
    if (!targetRole && !targetCompany) {
      addToast('Select a job or enter a target role first', 'warning')
      return
    }
    setGenerating(true)
    try {
      const doc = buildLatex({ name: CANDIDATE.name, email: CANDIDATE.email, phone: CANDIDATE.phone, linkedin: CANDIDATE.linkedin, location: CANDIDATE.location, experience, skills, summary })
      setLatex(doc)
      // Save to backend (non-critical)
      try {
        await fetch(`${API_BASE}/api/save-latex`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ latex: doc, role: targetRole, company: targetCompany }),
        })
      } catch {}
      setBuilderTab('visual')
      addToast(`Resume generated for ${targetCompany || targetRole}`, 'success')
    } catch (err) {
      addToast(`Generation failed: ${err.message}`, 'error')
    } finally {
      setGenerating(false)
    }
  }

  const downloadLatex = () => {
    if (!latex) return
    const slug = (targetRole || 'resume').toLowerCase().replace(/\s+/g, '-')
    const a = document.createElement('a')
    a.href = URL.createObjectURL(new Blob([latex], { type: 'text/plain' }))
    a.download = `${slug}-${targetCompany || 'resume'}.tex`.replace(/\s+/g,'-').toLowerCase()
    a.click()
    addToast('.tex downloaded', 'success')
  }

  /* ── Experience / skills edit helpers ───────────────────────── */
  const updBullet = (ei,bi,v) => setExperience(p=>p.map((e,i)=>i===ei?{...e,bullets:e.bullets.map((b,j)=>j===bi?v:b)}:e))
  const addBullet = (ei)      => setExperience(p=>p.map((e,i)=>i===ei?{...e,bullets:[...e.bullets,'']}:e))
  const remBullet = (ei,bi)   => setExperience(p=>p.map((e,i)=>i===ei?{...e,bullets:e.bullets.filter((_,j)=>j!==bi)}:e))
  const updField  = (ei,f,v)  => setExperience(p=>p.map((e,i)=>i===ei?{...e,[f]:v}:e))
  const updSkill  = (k,v)     => setSkills(p=>({...p,[k]:v}))

  /* ── Upload helpers ──────────────────────────────────────────── */
  const handleUpload = async (files) => {
    if (!files?.length) return
    const file = files[0]
    const ext  = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
    if (!['.pdf','.docx','.doc','.tex'].includes(ext)) { addToast(`Unsupported type: ${ext}`, 'error'); return }
    if (file.size > 10*1024*1024) { addToast('File too large (max 10MB)', 'error'); return }
    setUploading(true)
    const fd = new FormData(); fd.append('file', file)
    try {
      const res = await fetch(`${API_BASE}/api/upload-resume`, { method:'POST', body:fd })
      if (res.ok) { addToast(`Uploaded: ${file.name}`, 'success'); fetchResumes() }
      else {
        const d = await res.json().catch(()=>({}))
        addToast(d.detail || `Upload failed (${res.status})`, 'error')
      }
    } catch (err) { addToast(`Upload error: ${err.message}`, 'error') }
    finally { setUploading(false) }
  }

  const handleDeleteResume = async (filename) => {
    if (!window.confirm(`Delete "${filename}"?`)) return
    setDeleting(filename)
    try {
      const res = await fetch(`${API_BASE}/api/resumes?filename=${encodeURIComponent(filename)}`, { method:'DELETE' })
      if (res.ok) { setResumes(p=>p.filter(r=>r.name!==filename)); addToast('Deleted', 'success') }
      else addToast('Delete failed', 'error')
    } catch { addToast('Delete error', 'error') }
    finally { setDeleting(null) }
  }

  /* ── Sub-tab button style ────────────────────────────────────── */
  const tabBtn = (id) => ({
    display:'flex', alignItems:'center', gap:5,
    padding:'7px 16px', fontSize:12, fontWeight:600,
    cursor:'pointer', border:'none', borderRadius:'var(--radius-sm)',
    background: builderTab===id ? 'var(--accent-primary)' : 'var(--bg-glass)',
    color: builderTab===id ? '#fff' : 'var(--text-secondary)',
    transition:'all 0.2s',
  })

  /* ═══════════════════════════════════════════════════════════════
     RENDER
  ════════════════════════════════════════════════════════════════ */
  return (
    <div className="page-content" id="resume-hub-page">

      {/* ── 1. UPLOAD ZONE ────────────────────────────────────────── */}
      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
        onDrop={e => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files) }}
        onDragOver={e => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => !uploading && document.getElementById('resume-file-input')?.click()}
        style={{ opacity: uploading ? 0.6 : 1, pointerEvents: uploading ? 'none' : 'auto' }}
      >
        <span className="material-symbols-outlined">{uploading ? 'hourglass_empty' : 'cloud_upload'}</span>
        <h3>{uploading ? 'Uploading…' : 'Upload Resume'}</h3>
        <p>Drag & drop PDF, DOCX, or TEX — or click to browse</p>
        <p style={{ fontSize:11, color:'var(--text-muted)' }}>Max 10 MB · .pdf .docx .doc .tex</p>
        <input id="resume-file-input" type="file" accept=".pdf,.docx,.doc,.tex" style={{ display:'none' }} onChange={e=>handleUpload(e.target.files)} disabled={uploading} />
      </div>

      {/* ── 2. RESUME LIBRARY ─────────────────────────────────────── */}
      <div className="panel" style={{ marginTop:20 }}>
        <div className="panel-header">
          <div className="panel-title">
            <span className="material-symbols-outlined" style={{color:'var(--accent-primary-light)'}}>folder</span>
            Resume Library
          </div>
          <div style={{display:'flex',gap:10,alignItems:'center'}}>
            <span className="section-count">{resumes.length} files</span>
            {resumes.length > 0 && (
              <button className="btn btn-secondary btn-sm" onClick={async()=>{
                if(!window.confirm(`Delete all ${resumes.length} files?`)) return
                for(const f of resumes){ try{ await fetch(`${API_BASE}/api/resumes?filename=${encodeURIComponent(f.name)}`,{method:'DELETE'}) }catch{} }
                setResumes([]); addToast('All resumes deleted','info')
              }}>
                <span className="material-symbols-outlined" style={{fontSize:14}}>delete_sweep</span> Clear All
              </button>
            )}
          </div>
        </div>
        {resumes.length === 0
          ? <div style={{textAlign:'center',padding:28,color:'var(--text-muted)',fontSize:13}}>No uploads yet. Drag a file above to add one.</div>
          : (
            <div className="resume-list">
              {resumes.map((file,i) => {
                const isPdf = file.name?.endsWith('.pdf')
                const isTex = file.name?.endsWith('.tex')
                const isDel = deleting === file.name
                return (
                  <div key={i} className="resume-card" style={{opacity:isDel?0.5:1}}>
                    <div className={`resume-card-icon ${isTex?'tex':''}`}>
                      <span className="material-symbols-outlined">
                        {isPdf?'picture_as_pdf':isTex?'code':'description'}
                      </span>
                    </div>
                    <div className="resume-card-info">
                      <div className="resume-card-name">{file.name}</div>
                      <div className="resume-card-detail">{file.size} · {file.date}</div>
                      <div className="resume-card-actions">
                        <a href={`${API_BASE}/resumes/${file.name}`} download className="btn btn-secondary btn-sm" style={{padding:'4px 10px',fontSize:11}}>
                          <span className="material-symbols-outlined" style={{fontSize:14}}>download</span> Download
                        </a>
                        <button onClick={()=>handleDeleteResume(file.name)} disabled={isDel} style={{background:'none',border:'none',cursor:isDel?'not-allowed':'pointer',color:'var(--text-muted)',padding:4}}>
                          <span className="material-symbols-outlined" style={{fontSize:16}}>delete</span>
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )
        }
      </div>

      {/* ── 3. RESUME BUILDER — triggered by job selection ────────── */}
      <div className="panel" style={{ marginTop:20 }}>
        <div className="panel-header">
          <div className="panel-title">
            <span className="material-symbols-outlined" style={{color:'var(--accent-success)'}}>auto_awesome</span>
            LaTeX Resume Builder
          </div>
          <span style={{fontSize:12,color:'var(--text-muted)'}}>Select a scored job to generate a tailored resume</span>
        </div>

        {/* Job picker → auto-fills everything */}
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 2fr auto', gap:12, alignItems:'end', marginBottom: builderOpen ? 20 : 0 }}>
          <div className="form-group" style={{margin:0}}>
            <label className="form-label">Company / Job to target</label>
            <select className="form-select" value={selectedJobId} onChange={e=>handleJobSelect(e.target.value)}>
              <option value="">— Select a scored job —</option>
              {scoredJobs.length===0
                ? <option disabled>No scored jobs yet — score one on the Jobs page</option>
                : scoredJobs.map(j=>(
                  <option key={j.id} value={j.id}>
                    {j.role||j.title} @ {j.company} · {Math.round(j.score||0)}%
                  </option>
                ))}
            </select>
          </div>
          <div className="form-group" style={{margin:0}}>
            <label className="form-label">Target Role</label>
            <input className="form-input" value={targetRole} onChange={e=>setTargetRole(e.target.value)} placeholder="Auto-filled from job" />
          </div>
          <div className="form-group" style={{margin:0}}>
            <label className="form-label">Summary line</label>
            <input className="form-input" value={summary} onChange={e=>setSummary(e.target.value)} placeholder="Auto-filled — edit to refine" />
          </div>
          <button className="btn btn-primary" onClick={handleGenerate} disabled={generating || !builderOpen} style={{alignSelf:'end'}}>
            {generating
              ? <><span className="spinner"/> Generating…</>
              : <><span className="material-symbols-outlined" style={{fontSize:15}}>auto_awesome</span> Generate Resume</>}
          </button>
        </div>

        {/* Builder body — only visible once a job is selected */}
        {builderOpen && (
          <>
            {/* Sub-tab bar */}
            <div style={{display:'flex',gap:8,marginBottom:16,borderBottom:'1px solid var(--border-subtle)',paddingBottom:12,flexWrap:'wrap'}}>
              <button style={tabBtn('editor')} onClick={()=>setBuilderTab('editor')}>
                <span className="material-symbols-outlined" style={{fontSize:14}}>edit</span> Editor
              </button>
              <button style={{...tabBtn('visual'), opacity:!latex?0.45:1, cursor:!latex?'not-allowed':'pointer'}}
                onClick={()=>latex&&setBuilderTab('visual')} disabled={!latex}>
                <span className="material-symbols-outlined" style={{fontSize:14}}>visibility</span> Visual Preview
              </button>
              <button style={{...tabBtn('code'), opacity:!latex?0.45:1, cursor:!latex?'not-allowed':'pointer'}}
                onClick={()=>latex&&setBuilderTab('code')} disabled={!latex}>
                <span className="material-symbols-outlined" style={{fontSize:14}}>code</span> LaTeX Code
              </button>
              {latex && (
                <div style={{marginLeft:'auto',display:'flex',gap:8}}>
                  <button onClick={printResume} style={{display:'flex',alignItems:'center',gap:5,padding:'7px 14px',fontSize:12,fontWeight:600,border:'none',borderRadius:'var(--radius-sm)',background:'var(--accent-secondary)',color:'#fff',cursor:'pointer'}}>
                    <span className="material-symbols-outlined" style={{fontSize:14}}>print</span> Print / PDF
                  </button>
                  <button onClick={downloadLatex} style={{display:'flex',alignItems:'center',gap:5,padding:'7px 14px',fontSize:12,fontWeight:600,border:'none',borderRadius:'var(--radius-sm)',background:'var(--accent-success)',color:'#fff',cursor:'pointer'}}>
                    <span className="material-symbols-outlined" style={{fontSize:14}}>download</span> .tex
                  </button>
                </div>
              )}
            </div>

            {/* EDITOR */}
            {builderTab === 'editor' && (
              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
                {/* Experience */}
                <div>
                  <div style={{fontSize:12,fontWeight:700,color:'var(--text-secondary)',marginBottom:12,display:'flex',alignItems:'center',gap:6}}>
                    <span className="material-symbols-outlined" style={{fontSize:16,color:'var(--accent-secondary)'}}>work</span> Experience
                  </div>
                  {experience.map((exp,ei)=>(
                    <div key={ei} style={{marginBottom:18,paddingBottom:14,borderBottom:'1px solid var(--border-subtle)'}}>
                      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:7,marginBottom:8}}>
                        {[['title','Job Title'],['company','Company'],['location','Location'],['period','Period']].map(([f,ph])=>(
                          <input key={f} className="form-input" style={{fontSize:12}} value={exp[f]} onChange={e=>updField(ei,f,e.target.value)} placeholder={ph}/>
                        ))}
                      </div>
                      <div style={{fontSize:11,fontWeight:600,color:'var(--text-muted)',marginBottom:5}}>Bullets</div>
                      {exp.bullets.map((b,bi)=>(
                        <div key={bi} style={{display:'flex',gap:6,marginBottom:5}}>
                          <textarea className="form-input" style={{fontSize:12,minHeight:38,resize:'vertical',flex:1}} value={b} onChange={e=>updBullet(ei,bi,e.target.value)} placeholder="Achievement…"/>
                          <button onClick={()=>remBullet(ei,bi)} style={{background:'none',border:'none',color:'var(--accent-danger)',cursor:'pointer',fontSize:17,lineHeight:1,alignSelf:'flex-start',paddingTop:4}}>✕</button>
                        </div>
                      ))}
                      <button onClick={()=>addBullet(ei)} className="btn btn-secondary btn-sm" style={{marginTop:4}}>
                        <span className="material-symbols-outlined" style={{fontSize:13}}>add</span> Add Bullet
                      </button>
                    </div>
                  ))}
                </div>
                {/* Skills */}
                <div>
                  <div style={{fontSize:12,fontWeight:700,color:'var(--text-secondary)',marginBottom:12,display:'flex',alignItems:'center',gap:6}}>
                    <span className="material-symbols-outlined" style={{fontSize:16,color:'var(--accent-warning)'}}>psychology</span>
                    Skills <span style={{fontSize:10,fontWeight:400,color:'var(--text-muted)',marginLeft:4}}>— refine wording; core skills preserved</span>
                  </div>
                  {Object.entries(skills).map(([k,v])=>(
                    <div key={k} className="form-group">
                      <label className="form-label" style={{fontSize:11}}>{k}</label>
                      <textarea className="form-input" style={{fontSize:12,minHeight:50,resize:'vertical'}} value={v} onChange={e=>updSkill(k,e.target.value)}/>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* VISUAL PREVIEW */}
            {builderTab === 'visual' && latex && (
              <div>
                <div style={{display:'flex',alignItems:'center',gap:10,padding:'10px 14px',background:'rgba(16,185,129,0.08)',border:'1px solid rgba(16,185,129,0.25)',borderRadius:8,marginBottom:16,fontSize:12,color:'var(--text-secondary)'}}>
                  <span className="material-symbols-outlined" style={{color:'var(--accent-success)',fontSize:18}}>visibility</span>
                  <span style={{flex:1}}>Visual representation of your resume for <strong>{targetCompany || targetRole}</strong>. Use <strong>Print / PDF</strong> to save.</span>
                  <button onClick={printResume} style={{display:'flex',alignItems:'center',gap:5,padding:'6px 14px',fontSize:12,fontWeight:600,border:'none',borderRadius:'var(--radius-sm)',background:'var(--accent-secondary)',color:'#fff',cursor:'pointer'}}>
                    <span className="material-symbols-outlined" style={{fontSize:14}}>print</span> Print / PDF
                  </button>
                </div>
                <div style={{background:'#777',padding:'28px 20px',borderRadius:8,overflowX:'auto'}}>
                  <ResumePreview
                    name={CANDIDATE.name} email={CANDIDATE.email}
                    phone={CANDIDATE.phone} linkedin={CANDIDATE.linkedin}
                    location={CANDIDATE.location}
                    experience={experience} skills={skills}
                    summary={summary} targetRole={targetRole} targetCompany={targetCompany}
                  />
                </div>
              </div>
            )}

            {/* LATEX CODE */}
            {builderTab === 'code' && latex && (
              <div>
                <div style={{display:'flex',alignItems:'center',gap:10,padding:'10px 14px',background:'rgba(99,102,241,0.07)',border:'1px solid rgba(99,102,241,0.2)',borderRadius:8,marginBottom:12,fontSize:12,color:'var(--text-secondary)'}}>
                  <span style={{flex:1}}>
                    Compile on <a href="https://www.overleaf.com" target="_blank" rel="noopener noreferrer" style={{color:'var(--accent-primary-light)'}}>Overleaf</a>
                    {' '}or locally: <code>pdflatex resume.tex</code>
                  </span>
                  <button onClick={()=>{navigator.clipboard.writeText(latex);addToast('Copied!','success')}} className="btn btn-secondary btn-sm">
                    <span className="material-symbols-outlined" style={{fontSize:13}}>content_copy</span> Copy
                  </button>
                  <button onClick={downloadLatex} className="btn btn-primary btn-sm">
                    <span className="material-symbols-outlined" style={{fontSize:13}}>download</span> .tex
                  </button>
                </div>
                <pre style={{background:'var(--bg-secondary)',border:'1px solid var(--border-subtle)',borderRadius:'var(--radius-md)',padding:18,fontSize:11,fontFamily:'var(--font-mono,monospace)',lineHeight:1.6,overflowX:'auto',whiteSpace:'pre-wrap',color:'var(--text-primary)',maxHeight:'65vh',overflowY:'auto'}}>
                  {latex}
                </pre>
              </div>
            )}
          </>
        )}

        {/* placeholder when no job selected yet */}
        {!builderOpen && (
          <div style={{textAlign:'center',padding:'28px 0',color:'var(--text-muted)',fontSize:13}}>
            <span className="material-symbols-outlined" style={{fontSize:36,display:'block',marginBottom:8,opacity:0.4}}>description</span>
            Select a scored job above to open the resume builder.
          </div>
        )}
      </div>

    </div>
  )
}
