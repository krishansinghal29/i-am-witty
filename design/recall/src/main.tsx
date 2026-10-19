import { StrictMode, Suspense, lazy } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom';
import { ToastProvider } from '@/components/Toast';
import { PracticePage } from '@/screens/practice/PracticePage';
import './styles.css';

// Admin (and Firebase with it) loads only when someone opens /admin.
const AdminLayout = lazy(() => import('@/screens/admin/AdminLayout').then((m) => ({ default: m.AdminLayout })));
const LibraryPage = lazy(() => import('@/screens/admin/LibraryPage').then((m) => ({ default: m.LibraryPage })));
const ItemFormRoute = lazy(() => import('@/screens/admin/ItemFormPage').then((m) => ({ default: m.ItemFormRoute })));

function Loading() {
  return (
    <div className="screen">
      <div className="loading" aria-label="Loading">
        <div className="spinner" />
      </div>
    </div>
  );
}

function NotFound() {
  return (
    <div className="screen">
      <main className="body">
        <div className="card empty">
          <b>That page doesn't exist.</b>
          <Link className="btn ghost sm" to="/">
            Go to today's recall
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
              <Route path="/" element={<PracticePage />} />
              <Route path="/admin" element={<AdminLayout />}>
                <Route index element={<LibraryPage />} />
                <Route path="new" element={<ItemFormRoute />} />
                <Route path="items/:id" element={<ItemFormRoute />} />
              </Route>
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </div>
      </ToastProvider>
    </BrowserRouter>
  </StrictMode>,
);
