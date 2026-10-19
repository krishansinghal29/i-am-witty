import { StrictMode, Suspense, lazy, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom';
import { ToastProvider } from '@/components/Toast';
import './styles.css';

// Admin (and Firebase with it) loads only when someone opens /admin.
const AdminLayout = lazy(() => import('@/screens/admin/AdminLayout').then((m) => ({ default: m.AdminLayout })));
const LibraryPage = lazy(() => import('@/screens/admin/LibraryPage').then((m) => ({ default: m.LibraryPage })));
const ItemFormRoute = lazy(() => import('@/screens/admin/ItemFormPage').then((m) => ({ default: m.ItemFormRoute })));
const QuickAddPage = lazy(() => import('@/screens/admin/QuickAddPage').then((m) => ({ default: m.QuickAddPage })));
const CuesPage = lazy(() => import('@/screens/admin/CuesPage').then((m) => ({ default: m.CuesPage })));

function Loading() {
  return (
    <div className="screen">
      <div className="loading" aria-label="Loading">
        <div className="spinner" />
      </div>
    </div>
  );
}

// Practice moved into the Riffy app. Hosting already redirects "/", so this
// only catches in-app navigation to it.
const APP_RECALL_URL = 'https://riffy.pro/app/recall';

function OpenInApp() {
  useEffect(() => {
    window.location.replace(APP_RECALL_URL);
  }, []);
  return (
    <div className="screen">
      <main className="body">
        <div className="card empty">
          <b>Recall now lives in the Riffy app.</b>
          <a className="btn ghost sm" href={APP_RECALL_URL}>
            Open Recall
          </a>
        </div>
      </main>
    </div>
  );
}

function NotFound() {
  return (
    <div className="screen">
      <main className="body">
        <div className="card empty">
          <b>That page doesn't exist.</b>
          <Link className="btn ghost sm" to="/admin">
            Go to the library
          </Link>
        </div>
      </main>
    </div>
  );
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ToastProvider>
        <div className="app">
          <Suspense fallback={<Loading />}>
            <Routes>
              <Route path="/" element={<OpenInApp />} />
              <Route path="/admin" element={<AdminLayout />}>
                <Route index element={<LibraryPage />} />
                <Route path="new" element={<ItemFormRoute />} />
                <Route path="items/:id" element={<ItemFormRoute />} />
                <Route path="quick" element={<QuickAddPage />} />
                <Route path="cues" element={<CuesPage />} />
              </Route>
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </div>
      </ToastProvider>
    </BrowserRouter>
  </StrictMode>,
);
