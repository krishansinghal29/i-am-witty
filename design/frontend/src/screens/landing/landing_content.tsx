import { useEffect, useRef } from 'react';
import type { MouseEvent } from 'react';
import './landing.css';

/** White r-spark glyph used inside the warm logo tile. */
function MarkWhite({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="30 18 52 54" aria-hidden="true">
      <g fill="#fff">
        <rect x="35.5" y="35" width="11.5" height="35" rx="5.75" />
        <path d="M42 46 C45 38 52 36.5 60 40.5" fill="none" stroke="#fff" strokeWidth="11.5" strokeLinecap="round" />
        <path d="M70 23 C70.8 29 72.6 30.8 79 31.5 C72.6 32.2 70.8 34 70 40 C69.2 34 67.4 32.2 61 31.5 C67.4 30.8 69.2 29 70 23 Z" />
      </g>
    </svg>
  );
}

/** Outlined "riffy" wordmark (Fredoka 600 → paths). */
function Wordmark() {
  return (
    <svg className="wordmark" viewBox="0 -76 206 104" aria-label="riffy">
      <path
        fill="#2B2F3A"
        d="M11.60 0.90L11.60 0.90Q7.90 0.90 6.35-0.15Q4.80-1.20 4.45-3Q4.10-4.80 4.10-6.70L4.10-6.70L4.10-41.60Q4.10-43.60 4.50-45.30Q4.90-47 6.45-48.05Q8-49.10 11.70-49.10L11.70-49.10Q15.20-49.10 16.75-48.15Q18.30-47.20 18.70-45.95Q19.10-44.70 19.10-43.80L19.10-43.80L17.90-43.20Q18.10-43.60 18.95-44.65Q19.80-45.70 21.30-46.85Q22.80-48 24.95-48.80Q27.10-49.60 29.90-49.60L29.90-49.60Q31-49.60 32.35-49.45Q33.70-49.30 35.15-48.85Q36.60-48.40 37.80-47.65Q39-46.90 39.75-45.80Q40.50-44.70 40.50-43.10L40.50-43.10Q40.50-39 38.60-36.15Q36.70-33.30 33.80-33.30L33.80-33.30Q32.10-33.30 31.40-33.60Q30.70-33.90 30.25-34.20Q29.80-34.50 29.20-34.75Q28.60-35 27-35L27-35Q25.50-35 24.15-34.60Q22.80-34.20 21.65-33.35Q20.50-32.50 19.85-31.25Q19.20-30 19.20-28.50L19.20-28.50L19.20-6.50Q19.20-4.60 18.85-2.85Q18.50-1.10 16.90-0.10Q15.30 0.90 11.60 0.90ZM54.40 0.90L54.40 0.90Q50.70 0.90 49.15-0.15Q47.60-1.20 47.25-2.95Q46.90-4.70 46.90-6.60L46.90-6.60L46.90-41.50Q46.90-43.50 47.25-45.20Q47.60-46.90 49.20-47.95Q50.80-49 54.50-49L54.50-49Q58.10-49 59.65-47.90Q61.20-46.80 61.55-45.10Q61.90-43.40 61.90-41.30L61.90-41.30L61.90-6.50Q61.90-4.60 61.55-2.85Q61.20-1.10 59.65-0.10Q58.10 0.90 54.40 0.90ZM54.40-56.30L54.40-56.30Q50.60-56.30 49.00-57.40Q47.40-58.50 47.05-60.30Q46.70-62.10 46.70-64.10L46.70-64.10Q46.70-66.20 47.10-67.95Q47.50-69.70 49.10-70.75Q50.70-71.80 54.50-71.80L54.50-71.80Q58.20-71.80 59.80-70.70Q61.40-69.60 61.75-67.80Q62.10-66 62.10-64L62.10-64Q62.10-62 61.75-60.20Q61.40-58.40 59.80-57.35Q58.20-56.30 54.40-56.30ZM83.90 1L83.90 1Q80.40 1 78.80-0.10Q77.20-1.20 76.85-2.95Q76.50-4.70 76.50-6.70L76.50-6.70L76.50-53.50Q76.50-56.90 77.60-60.20Q78.70-63.50 81.10-66.15Q83.50-68.80 87.20-70.40Q90.90-72 96.20-72L96.20-72Q98.10-72 99.85-71.65Q101.60-71.30 102.65-69.75Q103.70-68.20 103.70-64.50L103.70-64.50Q103.70-60.80 102.60-59.25Q101.50-57.70 99.75-57.35Q98-57 96.10-57L96.10-57Q94.80-57 93.95-56.85Q93.10-56.70 92.60-56.40Q92.10-56.10 91.85-55.40Q91.60-54.70 91.60-53.70L91.60-53.70L91.60-6.40Q91.60-4.50 91.20-2.80Q90.80-1.10 89.20-0.05Q87.60 1 83.90 1ZM73.40-48.30L73.40-48.30L84.40-48.30L98.20-48.70Q100.10-48.70 101.80-48.35Q103.50-48 104.60-46.40Q105.70-44.80 105.70-41.10L105.70-41.10Q105.70-37.70 104.65-36.10Q103.60-34.50 101.90-34.05Q100.20-33.60 98.20-33.60L98.20-33.60L85.10-33.90L73-33.90Q70.10-34 68.95-35.65Q67.80-37.30 67.80-41.20L67.80-41.20Q67.80-44.80 69.20-46.55Q70.60-48.30 73.40-48.30ZM124.40 1L124.40 1Q120.90 1 119.30-0.10Q117.70-1.20 117.35-2.95Q117-4.70 117-6.70L117-6.70L117-53.50Q117-56.90 118.10-60.20Q119.20-63.50 121.60-66.15Q124-68.80 127.70-70.40Q131.40-72 136.70-72L136.70-72Q138.60-72 140.35-71.65Q142.10-71.30 143.15-69.75Q144.20-68.20 144.20-64.50L144.20-64.50Q144.20-60.80 143.10-59.25Q142-57.70 140.25-57.35Q138.50-57 136.60-57L136.60-57Q135.30-57 134.45-56.85Q133.60-56.70 133.10-56.40Q132.60-56.10 132.35-55.40Q132.10-54.70 132.10-53.70L132.10-53.70L132.10-6.40Q132.10-4.50 131.70-2.80Q131.30-1.10 129.70-0.05Q128.10 1 124.40 1ZM113.90-48.30L113.90-48.30L124.90-48.30L138.70-48.70Q140.60-48.70 142.30-48.35Q144-48 145.10-46.40Q146.20-44.80 146.20-41.10L146.20-41.10Q146.20-37.70 145.15-36.10Q144.10-34.50 142.40-34.05Q140.70-33.60 138.70-33.60L138.70-33.60L125.60-33.90L113.50-33.90Q110.60-34 109.45-35.65Q108.30-37.30 108.30-41.20L108.30-41.20Q108.30-44.80 109.70-46.55Q111.10-48.30 113.90-48.30ZM165.80 21.10L165.80 21.10Q161.70 19.30 161.05 17.10Q160.40 14.90 162.10 11.20L162.10 11.20L187.20-44.90Q188.90-48.80 190.95-49.55Q193-50.30 197.10-48.70L197.10-48.70Q201.10-46.80 201.75-44.70Q202.40-42.60 200.80-39.10L200.80-39.10L175.60 17.40Q173.90 21.30 171.90 22.10Q169.90 22.90 165.80 21.10ZM180.90-19.40L174.50-2.20L151-38Q148.80-41.30 149.25-43.50Q149.70-45.70 153.20-48L153.20-48Q157.10-50.40 159.25-49.85Q161.40-49.30 163.60-45.90L163.60-45.90L180.90-19.40Z"
      />
    </svg>
  );
}

const ArrowLine = () => (
  <svg className="arrline" width="40" height="20" viewBox="0 0 40 20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M2 10h32" />
    <path d="M28 4l7 6-7 6" />
  </svg>
);

export function LandingContent({ onOpenApp }: { onOpenApp?: (event: MouseEvent<HTMLAnchorElement>) => void }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const navRef = useRef<HTMLElement>(null);

  // Nav gets a soft shadow + border once the page is scrolled a little.
  useEffect(() => {
    const root = scrollRef.current;
    const nav = navRef.current;
    if (!root || !nav) return;
    const onScroll = () => nav.classList.toggle('scrolled', root.scrollTop > 8);
    onScroll();
    root.addEventListener('scroll', onScroll, { passive: true });
    return () => root.removeEventListener('scroll', onScroll);
  }, []);

  // Use native hash links so sections work without JavaScript and can be shared.
  useEffect(() => {
    const id = window.location.hash.slice(1);
    const section = document.getElementById(id);
    if (id && section && scrollRef.current?.contains(section)) {
      section.scrollIntoView({ block: 'start' });
    }
  }, []);

  const toTop = (e: MouseEvent) => {
    e.preventDefault();
    scrollRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="rl" ref={scrollRef} id="top">
        <a className="skip-link" href="#main">Skip to content</a>
        {/* ====================== NAV ====================== */}
        <header className="nav" ref={navRef}>
          <div className="wrap nav-in">
            <a className="brand" href="#top" onClick={toTop} aria-label="Riffy home">
              <span className="tile"><MarkWhite size={22} /></span>
              <Wordmark />
            </a>
            <nav className="nav-links" aria-label="Main navigation">
              <a className="lk" href="#product">Product</a>
              <a className="lk" href="#plans">Plans</a>
              <a className="lk" href="#team">Team</a>
              <a className="lk" href="#contact">Contact</a>
              <a className="btn btn-primary btn-sm" href="/app" onClick={onOpenApp}>Start practicing <span className="arr">→</span></a>
            </nav>
          </div>
        </header>

        <main id="main">
        {/* ====================== HERO ====================== */}
        <section className="hero">
          <div className="wrap hero-grid">
            <div className="hero-copy">
              <span className="eyebrow reveal" style={{ animationDelay: '.05s' }}>✨ A little gym for your social spark</span>
              <h1 className="head reveal" style={{ animationDelay: '.12s' }}>
                Get wittier,<br /><span className="grad">one tiny rep at a time.</span>
              </h1>
              <p className="sub reveal" style={{ animationDelay: '.2s' }}>
                Riffy is an AI-powered communication practice app. Build humour, storytelling,
                and conversation confidence with short voice exercises and personal feedback.
              </p>
              <div className="cta-row reveal" style={{ animationDelay: '.28s' }}>
                <a className="btn btn-primary" href="/app" onClick={onOpenApp}>Start practicing — it's free <span className="arr">→</span></a>
                <a className="btn btn-ghost" href="#how">See how it works</a>
              </div>
              <div className="trust reveal" style={{ animationDelay: '.36s' }}>
                <span><span className="ic">🎙️</span> Speak your answers</span>
                <span><span className="ic">🎧</span> Two-minute reps</span>
                <span><span className="ic">🔥</span> Gentle daily streaks</span>
              </div>
            </div>

            {/* phone peek */}
            <div className="stage reveal" style={{ animationDelay: '.3s' }}>
              <div className="glow" />
              <div className="chip-f chip-a">
                <span className="em">🎙️</span>
                <span className="t"><b>Recording…</b><s>react, don't rehearse</s></span>
              </div>
              <div className="chip-f chip-b">
                <span className="em">🧡</span>
                <span className="t"><b>Nice landing!</b><s>warmer than last time</s></span>
              </div>

              <div className="phone">
                <div className="scr">
                  <div className="notch" />
                  <div className="s-top">
                    <span className="s-flame">🔥 5</span>
                    <span className="s-actions">
                      <span className="s-tg">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="m22 2-7 20-4-9-9-4 20-7Z" />
                          <path d="M22 2 11 13" />
                        </svg>
                      </span>
                      <span className="s-chat">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M21 11.5a8.4 8.4 0 0 1-12.7 7.2L3 21l2.3-4A8.4 8.4 0 1 1 21 11.5Z" />
                        </svg>
                      </span>
                    </span>
                  </div>
                  <div className="s-week">
                    <span className="s-day done">✓</span><span className="s-day done">✓</span><span className="s-day miss">✕</span>
                    <span className="s-day now" /><span className="s-day up">·</span><span className="s-day up">·</span><span className="s-day up">·</span>
                  </div>
                  <div className="s-body">
                    <p className="s-hi">Hey, you 👋</p>
                    <div className="s-title">Today's plan</div>
                    <div className="s-card next">
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <span className="s-badge">NEXT UP</span>
                        <h4>Misinterpretation</h4>
                        <div className="s-meta">⏱ 2 min · Practice</div>
                      </div>
                      <div className="s-thumb p">🎭</div>
                    </div>
                    <div className="s-card">
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <h4>Yes, And</h4>
                        <div className="s-meta">⏱ 1 min · Sprint</div>
                      </div>
                      <div className="s-thumb g">⚡</div>
                    </div>
                  </div>
                  <div className="s-tabs">
                    <span className="s-tab on"><span className="d" />Home</span>
                    <span className="s-tab"><span className="d" />Practice</span>
                    <span className="s-tab"><span className="d" />Role play</span>
                    <span className="s-tab"><span className="d" />Profile</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="sec product-section" id="product" aria-labelledby="product-title">
          <div className="wrap">
            <div className="sec-head">
              <span className="kicker">The product</span>
              <h2 id="product-title">Practice for the conversations that matter.</h2>
              <p>For people who want to think on their feet, tell better stories, and feel more at ease with friends, on dates, or at work. Riffy gives you a private place to practice out loud.</p>
            </div>
            <div className="steps">
              <article className="step">
                <span className="ico" aria-hidden="true">🎙️</span>
                <h3>Short voice exercises</h3>
                <p>Practice a specific skill with a guided prompt. Try improvisation, playful responses, and storytelling in a few minutes.</p>
              </article>
              <article className="step">
                <span className="ico" aria-hidden="true">💬</span>
                <h3>AI conversation practice</h3>
                <p>Rehearse everyday situations through interactive role play. Experiment with different responses before using them in real life.</p>
              </article>
              <article className="step">
                <span className="ico" aria-hidden="true">✨</span>
                <h3>Feedback you can use</h3>
                <p>Reflect on your responses with AI-assisted feedback and example answers, then build consistency with a daily practice plan.</p>
              </article>
            </div>
            <p className="section-note">Try Riffy in your browser today. <a className="text-link" href="/app" onClick={onOpenApp}>Open the app <span aria-hidden="true">→</span></a></p>
          </div>
        </section>

        {/* ====================== HOW IT WORKS ====================== */}
        <section className="sec" id="how">
          <div className="wrap">
            <div className="sec-head">
              <span className="kicker">How it works</span>
              <h2>Three calm beats per rep</h2>
              <p>Every exercise runs the same gentle loop. You only control the start — then you react in the moment, so there's no time to overthink it.</p>
            </div>
            <div className="steps">
              <div className="step">
                <span className="n">01 · BRIEF</span>
                <div className="ico">📋</div>
                <h3>Read the moment</h3>
                <p>A tiny scene sets up — who's talking, what they just said, and the one move to try. Take your time here; this is the only timed-by-you part.</p>
                <ArrowLine />
              </div>
              <div className="step">
                <span className="n">02 · RESPOND</span>
                <div className="ico">🎙️</div>
                <h3>Riff out loud</h3>
                <p>The prompt is spoken and the mic opens on its own. You answer in real time — react, don't rehearse. That's where the spark actually grows.</p>
                <ArrowLine />
              </div>
              <div className="step">
                <span className="n">03 · REFLECT</span>
                <div className="ico">✨</div>
                <h3>Get a gentle read</h3>
                <p>Warm, specific feedback on what landed — plus one <em>Better Way</em> to try next time. Measured against your past self, never a leaderboard.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="sec plans-section" id="plans" aria-labelledby="plans-title">
          <div className="wrap">
            <div className="sec-head">
              <span className="kicker">Plans &amp; business model</span>
              <h2 id="plans-title">Start free. Make room for more.</h2>
              <p>Riffy is a consumer software product with a freemium subscription model: free daily practice, with paid Riffy+ access for people who want to practice more.</p>
            </div>
            <div className="plan-grid">
              <article className="plan-card">
                <span className="plan-label">Free practice</span>
                <h3>A little every day</h3>
                <p>Get started in the browser with a daily allowance of practice exercises.</p>
                <ul>
                  <li>Guided prompts and voice responses</li>
                  <li>Feedback on completed exercises</li>
                  <li>Daily practice and streak tracking</li>
                </ul>
                <a className="btn btn-ghost" href="/app" onClick={onOpenApp}>Start free <span className="arr">→</span></a>
              </article>
              <article className="plan-card plus-card">
                <span className="plan-label">Riffy+ · Paid subscription</span>
                <h3>Keep the practice going</h3>
                <p>Riffy+ removes the daily free practice limit and unlocks premium exercises.</p>
                <ul>
                  <li>Unlimited daily practice</li>
                  <li>Access to the premium exercise library</li>
                  <li>Monthly and annual subscription options</li>
                </ul>
                <a className="btn btn-primary" href="mailto:support@riffy.pro?subject=Riffy%2B%20plans">Ask about Riffy+ <span className="arr">→</span></a>
              </article>
            </div>
            <p className="section-note">The web app is available now. Riffy+ checkout is not available on the website; contact us for current pricing and subscription availability. Mobile store releases are in progress.</p>
          </div>
        </section>

        <section className="sec" id="team" aria-labelledby="team-title">
          <div className="wrap team-grid">
            <div className="team-intro">
              <span className="kicker">Our team</span>
              <h2 id="team-title">The person behind the practice.</h2>
              <p>We’re building Riffy around a simple idea: conversation skills get better when you have a comfortable place to practice them.</p>
            </div>
            <article className="team-card">
              <span className="team-avatar" aria-hidden="true">KS</span>
              <div>
                <span className="plan-label">Building Riffy</span>
                <h3>Krishan Singhal</h3>
                <p>Indian Institute of Technology, Kanpur alumnus.</p>
                <a className="text-link linkedin-link" href="https://www.linkedin.com/in/krishansinghal/" target="_blank" rel="noopener noreferrer" aria-label="Krishan Singhal on LinkedIn (opens in a new tab)">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M5.4 7.8H1.8V22h3.6V7.8ZM3.6 2a2.1 2.1 0 1 0 0 4.2 2.1 2.1 0 0 0 0-4.2ZM22 13.9c0-4.3-2.3-6.4-5.4-6.4-2.5 0-3.6 1.4-4.2 2.3v-2H8.8V22h3.6v-7.9c0-2.1.4-4.1 3-4.1 2.5 0 2.6 2.4 2.6 4.2V22h4v-8.1Z" /></svg>
                  View LinkedIn profile <span aria-hidden="true">↗</span>
                </a>
              </div>
            </article>
          </div>
        </section>

        <section className="sec contact-section" id="contact" aria-labelledby="contact-title">
          <div className="wrap">
            <div className="contact-card">
              <div>
                <span className="kicker">Get in touch</span>
                <h2 id="contact-title">Say hello to Riffy.</h2>
                <p>Questions about the product, subscriptions, or working with us? Reach the team by email.</p>
              </div>
              <a className="btn btn-ghost" href="mailto:support@riffy.pro">support@riffy.pro <span aria-hidden="true">↗</span></a>
            </div>
          </div>
        </section>

        {/* ====================== FINAL CTA ====================== */}
        <section className="final">
          <div className="wrap">
            <div className="cta-card">
              <span className="spark">✨</span>
              <h2>Ready to find your spark?</h2>
              <p>Two minutes today. A quicker, funnier you.</p>
              <a className="btn" href="/app" onClick={onOpenApp}>Start practicing <span className="arr">→</span></a>
              <p className="fine">Free to start · Two minutes a day</p>
            </div>
          </div>
        </section>

        </main>

        {/* ====================== FOOTER ====================== */}
        <footer>
          <div className="wrap">
            <div className="foot">
              <a className="brand" href="#top" onClick={toTop} aria-label="Riffy home">
                <span className="tile"><MarkWhite size={20} /></span>
                <Wordmark />
              </a>
              <nav className="foot-links" aria-label="Footer navigation">
                <a href="#product">Product</a>
                <a href="#plans">Plans</a>
                <a href="#team">Team</a>
                <a href="mailto:support@riffy.pro">Contact</a>
                <a href="/legal#privacy">Privacy</a>
                <a href="/legal#terms">Terms</a>
                <a href="/legal#account-deletion">Account deletion</a>
              </nav>
            </div>
            <p className="copy">© 2026 <b>Riffy</b> · Lower the stakes. Find your spark.</p>
          </div>
        </footer>
    </div>
  );
}
