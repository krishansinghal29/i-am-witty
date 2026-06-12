import { useEffect } from 'react';
import { IonPage } from '@ionic/react';
import './legal.css';

const LAST_UPDATED = 'June 9, 2026';
const CONTACT_EMAIL = 'support@riffy.pro';

function scrollToHash() {
  const id = window.location.hash.replace('#', '');
  if (!id) return;

  window.setTimeout(() => {
    document.getElementById(id)?.scrollIntoView({ block: 'start' });
  }, 0);
}

export function LegalPage() {
  useEffect(() => {
    scrollToHash();
    window.addEventListener('hashchange', scrollToHash);
    return () => window.removeEventListener('hashchange', scrollToHash);
  }, []);

  return (
    <IonPage>
      <div className="legal">
        <header className="legal-nav">
          <a className="legal-brand" href="/">
            Riffy
          </a>
          <nav aria-label="Legal sections">
            <a href="#privacy">Privacy</a>
            <a href="#terms">Terms</a>
            <a href="#account-deletion">Account deletion</a>
          </nav>
        </header>

        <main className="legal-main">
          <section className="legal-hero" aria-labelledby="legal-title">
            <p className="legal-kicker">Legal</p>
            <h1 id="legal-title">Riffy Legal</h1>
            <p>
              This public page contains the Privacy Policy, Terms of Service,
              and account deletion instructions for Riffy and riffy.pro.
            </p>
            <span>Last updated: {LAST_UPDATED}</span>
          </section>

          <section className="legal-jump" aria-label="Quick links">
            <a href="#privacy">Privacy Policy</a>
            <a href="#terms">Terms of Service</a>
            <a href="#account-deletion">Account deletion</a>
          </section>

          <article className="legal-section" id="privacy">
            <p className="legal-kicker">Privacy Policy</p>
            <h2>Privacy Policy</h2>
            <p>
              Riffy is a private practice app for social wit, voice reps,
              storytelling, and confidence. This Privacy Policy explains what
              information Riffy collects, how it is used, and the choices you
              have when you use the Riffy app or website.
            </p>

            <h3>Information we collect</h3>
            <ul>
              <li>
                Account and session information, including guest session IDs,
                app user IDs, sign-in identifiers, and basic profile state.
              </li>
              <li>
                Practice activity, including onboarding choices, exercise
                progress, streaks, attempts, transcripts, audio you choose to
                submit, and generated feedback.
              </li>
              <li>
                Subscription and entitlement information from Google Play,
                RevenueCat, and other app-store systems used to verify Riffy+
                access.
              </li>
              <li>
                Device and app information such as platform, app version,
                release channel, notification permission status, push tokens,
                logs, diagnostics, and usage analytics.
              </li>
              <li>
                Support messages and any information you include when you
                contact us.
              </li>
            </ul>

            <h3>How we use information</h3>
            <ul>
              <li>Provide, secure, maintain, and improve Riffy.</li>
              <li>
                Create practice plans, process voice or text attempts, generate
                feedback, and track progress.
              </li>
              <li>
                Verify subscriptions, restore purchases, and enforce free-tier
                limits and Riffy+ access.
              </li>
              <li>
                Send reminders or service messages when you choose to enable
                them.
              </li>
              <li>Respond to support, deletion, privacy, and safety requests.</li>
              <li>
                Understand app performance and product usage through analytics
                and diagnostics.
              </li>
            </ul>

            <h3>Sharing and service providers</h3>
            <p>
              We do not sell your personal information. We share information
              with service providers only as needed to run Riffy, including
              hosting, databases, authentication, app-store billing,
              subscription verification, analytics, transcription, AI
              processing, support, diagnostics, and security services. We may
              also disclose information when required by law or to protect
              users, Riffy, or the public.
            </p>

            <h3>Practice content and voice data</h3>
            <p>
              Your Riffy practice is private by default. Practice submissions
              are used to run the exercise, generate feedback, maintain your
              history, and improve reliability and safety. They are not posted
              publicly by Riffy.
            </p>

            <h3>Retention</h3>
            <p>
              We keep information for as long as needed to provide Riffy,
              comply with law, prevent abuse, resolve disputes, maintain
              records, and operate backups. You can request account deletion as
              described in the account deletion section below.
            </p>

            <h3>Your choices</h3>
            <ul>
              <li>You can use Riffy as a guest or sign in where available.</li>
              <li>You can disable notifications in your device settings.</li>
              <li>
                You can request deletion of your Riffy account and associated
                data.
              </li>
              <li>
                You can contact us at{' '}
                <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> for
                privacy questions.
              </li>
            </ul>

            <h3>Children</h3>
            <p>
              Riffy is not directed to children under 13. If you believe a
              child has provided personal information to Riffy, contact us and
              we will review the request.
            </p>
          </article>

          <article className="legal-section" id="terms">
            <p className="legal-kicker">Terms of Service</p>
            <h2>Terms of Service</h2>
            <p>
              These Terms govern your use of Riffy, including the Riffy mobile
              app, website, exercises, feedback, subscriptions, and related
              services. By using Riffy, you agree to these Terms.
            </p>

            <h3>Using Riffy</h3>
            <p>
              Riffy provides practice prompts and feedback for entertainment,
              learning, and self-improvement. Riffy is not medical, mental
              health, legal, financial, or professional advice.
            </p>

            <h3>Accounts</h3>
            <p>
              You are responsible for the activity on your account and for
              keeping your sign-in method secure. You may not use Riffy to
              abuse, harass, impersonate, exploit, or harm others.
            </p>

            <h3>Subscriptions and billing</h3>
            <p>
              Riffy+ may be offered as an auto-renewing subscription, including
              monthly and annual plans. On Android, digital subscriptions are
              purchased through Google Play Billing. Prices, renewal timing,
              taxes, trials, cancellation rules, and refunds may be handled by
              the app store where you purchased.
            </p>
            <p>
              To cancel an active Google Play subscription, open Google Play and
              go to Payments and subscriptions, then Subscriptions, then Riffy.
              Deleting your Riffy account does not automatically cancel an
              active Google Play subscription.
            </p>

            <h3>User content</h3>
            <p>
              You keep ownership of practice responses you submit. You grant
              Riffy permission to process that content as needed to provide the
              app, generate feedback, troubleshoot issues, improve safety, and
              operate the service.
            </p>

            <h3>Service changes</h3>
            <p>
              We may change, suspend, or discontinue parts of Riffy. We may
              update these Terms, and continued use after an update means you
              accept the updated Terms.
            </p>

            <h3>Disclaimer and liability</h3>
            <p>
              Riffy is provided as is and as available. To the maximum extent
              permitted by law, Riffy disclaims warranties and will not be
              liable for indirect, incidental, special, consequential, or
              punitive damages arising from your use of the service.
            </p>

            <h3>Contact</h3>
            <p>
              Questions about these Terms can be sent to{' '}
              <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.
            </p>
          </article>

          <article className="legal-section legal-section-strong" id="account-deletion">
            <p className="legal-kicker">Account deletion</p>
            <h2>Account deletion</h2>
            <p>
              You can request deletion of your Riffy account and associated app
              data at any time. This section is public and does not require you
              to sign in.
            </p>

            <h3>How to request deletion</h3>
            <ol>
              <li>
                In Riffy, open Profile, then Account deletion to return to this
                page.
              </li>
              <li>
                Open Profile, then Chat with us, and send the message
                "Delete my Riffy account"; or email{' '}
                <a href={`mailto:${CONTACT_EMAIL}?subject=Delete%20my%20Riffy%20account`}>
                  {CONTACT_EMAIL}
                </a>{' '}
                with the subject "Delete my Riffy account".
              </li>
              <li>
                Use the email address linked to your Riffy account when
                possible. We may ask you to verify account ownership before
                processing the deletion.
              </li>
            </ol>

            <h3>What is deleted</h3>
            <p>
              When your deletion request is verified and processed, we delete
              or de-identify your Riffy account data, including profile state,
              onboarding choices, progress, streaks, practice history,
              submitted transcripts and audio where stored, reminders, and
              registered notification devices.
            </p>

            <h3>What may be retained</h3>
            <p>
              We may retain limited information where required for legal,
              security, fraud prevention, accounting, dispute resolution,
              support, backup, or compliance purposes. Subscription transaction
              records may also remain with Google Play, RevenueCat, or other
              payment processors according to their own policies. Aggregated or
              de-identified analytics may be retained because they no longer
              identify a specific Riffy account.
            </p>

            <h3>Google Play subscriptions</h3>
            <p>
              Account deletion does not automatically cancel an active Google
              Play subscription. If you have Riffy+ through Google Play, cancel
              it in Google Play by opening Payments and subscriptions, then
              Subscriptions, then Riffy, then Cancel subscription.
            </p>
          </article>
        </main>
      </div>
    </IonPage>
  );
}
