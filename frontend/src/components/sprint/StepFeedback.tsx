import { AnimatePresence, motion } from 'framer-motion';
import { MessageSquare, Mic, Sparkles } from 'lucide-react';
import { useRef, useState } from 'react';
import type { SprintAnalysisResult } from '@/hooks/useSprintPractice';

interface Props {
  analysisResult: SprintAnalysisResult | null;
  error: string | null;
  userTranscript?: string;
  userAudioBase64?: string | null;
  onRetry: () => void;
  onNext: () => void;
}

type Tab = 'feedback' | 'better';

const TabBtn = ({ active, onClick, icon: Icon, label }: { active: boolean; onClick: () => void; icon: React.ElementType; label: string }) => (
  <button onClick={onClick}
    className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded-xl text-xs font-medium border-2 transition-all
      ${active ? 'bg-orange-500 text-white border-orange-500' : 'bg-white text-gray-600 border-gray-200 hover:border-orange-300'}`}
  >
    <Icon size={14} />
    <span>{label}</span>
  </button>
);

export function StepFeedback({ analysisResult, error, userTranscript, userAudioBase64, onRetry, onNext }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('feedback');
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const toggleAudio = () => {
    if (!userAudioBase64) return;
    if (!audioRef.current) {
      audioRef.current = new Audio(`data:audio/webm;base64,${userAudioBase64}`);
      audioRef.current.onended = () => setIsPlaying(false);
    }
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center">
        <p className="text-red-500 font-medium">{error}</p>
        <button onClick={onNext} className="px-6 py-3 bg-orange-500 text-white rounded-xl font-semibold">Next Exercise</button>
      </div>
    );
  }

  if (!analysisResult) return null;

  const { feedback, sample_answer } = analysisResult;

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Your response (audio + transcript) */}
        {(userTranscript || userAudioBase64) && (
          <div className="border border-gray-100 rounded-xl p-3 bg-white shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Your Response</span>
              {userAudioBase64 && (
                <button onClick={toggleAudio}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border ${isPlaying ? 'bg-red-50 border-red-200 text-red-600' : 'bg-orange-50 border-orange-200 text-orange-600'}`}
                >
                  <Mic size={12} />
                  {isPlaying ? 'Pause' : 'Play'}
                </button>
              )}
            </div>
            {userTranscript && <p className="text-sm text-gray-600 leading-relaxed">{userTranscript}</p>}
          </div>
        )}

        {/* Feedback tabs */}
        <div className="border border-gray-100 rounded-xl shadow-sm bg-white p-4">
          <div className="flex gap-2 mb-4">
            <TabBtn active={activeTab === 'feedback'} onClick={() => setActiveTab('feedback')} icon={MessageSquare} label="Feedback" />
            <TabBtn active={activeTab === 'better'} onClick={() => setActiveTab('better')} icon={Sparkles} label="Better Way" />
          </div>
          <AnimatePresence mode="wait">
            {activeTab === 'feedback' && (
              <motion.div key="feedback" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} transition={{ duration: 0.15 }}>
                <div className="text-sm text-gray-700 leading-relaxed ai-feedback-content" dangerouslySetInnerHTML={{ __html: feedback }} />
              </motion.div>
            )}
            {activeTab === 'better' && (
              <motion.div key="better" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }} transition={{ duration: 0.15 }}>
                <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl p-4 border border-orange-100">
                  <div className="flex items-center gap-2 mb-2"><Sparkles size={14} className="text-orange-500" /><span className="text-xs font-semibold text-orange-600 uppercase tracking-wide">Pro Response</span></div>
                  <div className="text-sm text-gray-700 leading-relaxed ai-feedback-content" dangerouslySetInnerHTML={{ __html: sample_answer }} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-100 bg-white flex gap-3">
        <button onClick={onRetry}
          className="flex-1 py-4 rounded-xl border-2 border-orange-400 text-orange-600 font-semibold hover:bg-orange-50"
        >
          Retry
        </button>
        <button onClick={onNext}
          className="flex-1 py-4 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold shadow-lg"
        >
          Next
        </button>
      </div>
    </div>
  );
}
