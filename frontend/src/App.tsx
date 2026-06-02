import { Navigate, Route, Routes, useNavigate, useParams } from 'react-router-dom';
import SprintExercise from './pages/SprintExercise';

const EXERCISES = [
  { id: 'yesAnd', label: 'Yes And' },
  { id: 'misinterpretation', label: 'Misinterpret' },
  { id: 'misinterpretationTechniques', label: 'Misinterpret+' },
  { id: 'loveHate', label: 'Love Hate' },
  { id: 'ifByXYouMeanY', label: 'If By X...' },
  { id: 'questionAnswerTease', label: 'Q&A Tease' },
  { id: 'vibing', label: 'Vibing' },
  { id: 'pushPull', label: 'Push Pull' },
  { id: 'heightening', label: 'Heighten' },
  { id: 'firstUnusualThing', label: 'Unusual' },
];

function AppShell() {
  const navigate = useNavigate();
  const params = useParams<{ exerciseId?: string }>();
  const activeId = params.exerciseId ?? EXERCISES[0].id;

  return (
    <div className="flex flex-col h-screen bg-white max-w-md mx-auto overflow-hidden" style={{ boxShadow: '0 0 0 1px #f3f4f6' }}>
      <div className="flex-1 min-h-0 overflow-hidden">
        <SprintExercise />
      </div>
      <div className="border-t border-gray-100 bg-white">
        <div className="flex overflow-x-auto scrollbar-hide">
          {EXERCISES.map(ex => (
            <button
              key={ex.id}
              onClick={() => navigate(`/sprint/${ex.id}/1`)}
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
      <Route path="/" element={<Navigate to={`/sprint/${EXERCISES[0].id}/1`} replace />} />
      <Route path="/sprint/:exerciseId/:count?" element={<AppShell />} />
      <Route path="*" element={<Navigate to={`/sprint/${EXERCISES[0].id}/1`} replace />} />
    </Routes>
  );
}
