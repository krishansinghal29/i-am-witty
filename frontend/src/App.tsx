import { Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom';
import ExerciseFlow from './pages/exercise/ExerciseFlow';
import SprintExercise from './pages/practice/SprintExercise';

const EXERCISES = [
  { id: 'yesAnd', label: 'Yes And' },
  { id: 'misinterpretation', label: 'Misinterpret' },
  { id: 'loveHate', label: 'Love Hate' },
  { id: 'ifByXYouMeanY', label: 'If By X...' },
  { id: 'questionAnswerTease', label: 'Q&A Tease' },
  { id: 'vibing', label: 'Vibing' },
  { id: 'pushPull', label: 'Push Pull' },
];

function AppShell({ mode }: { mode: 'exercise' | 'sprint' }) {
  const navigate = useNavigate();
  const params = useParams<{ exerciseId?: string }>();
  const activeId = params.exerciseId ?? EXERCISES[0].id;

  const switchMode = (next: 'exercise' | 'sprint') => {
    if (next === mode) return;
    if (next === 'sprint') navigate(`/sprint/${activeId}/1`);
    else navigate(`/exercise/${activeId}/1`);
  };

  const switchExercise = (id: string) => {
    if (mode === 'sprint') navigate(`/sprint/${id}/1`);
    else navigate(`/exercise/${id}/1`);
  };

  return (
    <div className="flex flex-col h-screen bg-white max-w-md mx-auto overflow-hidden" style={{ boxShadow: '0 0 0 1px #f3f4f6' }}>
      {/* Mode toggle */}
      <div className="flex items-center gap-1 px-4 py-2 border-b border-gray-100 bg-white">
        <button
          onClick={() => switchMode('exercise')}
          className={`flex-1 py-1.5 rounded-lg text-sm font-medium transition-all ${mode === 'exercise' ? 'bg-orange-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
        >
          Regular
        </button>
        <button
          onClick={() => switchMode('sprint')}
          className={`flex-1 py-1.5 rounded-lg text-sm font-medium transition-all ${mode === 'sprint' ? 'bg-orange-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
        >
          Sprint
        </button>
      </div>

      {/* Exercise content */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {mode === 'exercise' ? <ExerciseFlow /> : <SprintExercise />}
      </div>

      {/* Bottom tab bar */}
      <div className="border-t border-gray-100 bg-white">
        <div className="flex overflow-x-auto scrollbar-hide">
          {EXERCISES.map(ex => (
            <button
              key={ex.id}
              onClick={() => switchExercise(ex.id)}
              className={`flex-shrink-0 px-3 py-3 text-xs font-medium whitespace-nowrap transition-all border-t-2 ${
                activeId === ex.id
                  ? 'border-orange-500 text-orange-600'
                  : 'border-transparent text-gray-400 hover:text-gray-600'
              }`}
            >
              {ex.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to={`/exercise/${EXERCISES[0].id}/1`} replace />} />
      <Route
        path="/exercise/:exerciseId/:count?"
        element={<AppShell mode="exercise" />}
      />
      <Route
        path="/sprint/:exerciseId/:count?"
        element={<AppShell mode="sprint" />}
      />
      <Route path="*" element={<Navigate to={`/exercise/${EXERCISES[0].id}/1`} replace />} />
    </Routes>
  );
}
