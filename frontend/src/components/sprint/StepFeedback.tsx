import { AnimatePresence, motion } from 'framer-motion';
import { MessageSquare, Mic, Sparkles } from 'lucide-react';
import { useRef, useState } from 'react';
import type { SprintAnalysisResult } from '@/hooks/useSprintPractice';

interface Props {
  analysisResult: SprintAnalysisResult | null;
  error: string | null;
  hasRefined: boolean;
  userTranscript?: string;
  userAudioBase64?: string | null;
  onRefine: () => void;
  onNext: () => void;
}

type Tab = 'content' | 'voice' | 'better';

const TabBtn = ({ active, onClick, icon: Icon, label }: { active: boolean; onClick: () => void; icon: React.ElementType; label: string }) => (
  <button onClick={onClick}
    className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded-xl text-xs font-medium border-2 transition-all
      ${active ? 'bg-orange-500 text-white border-orange-500' : 'bg-white text-gray-600 border-gray-200 hover:border-orange-300'}`}
  >
    <Icon size={14} />
    <span>{label}</span>
  </button>
);

function ScoreCircle({ score, label, color }: { score: number; label: string; color: string }) {
  return (
    <div className="flex flex-col items-center gap-1">
      <div className={`w-14 h-14 rounded-full flex items-center justify-center border-4 font-bold text-lg`}
        style={{ borderColor: color, color }}
      >
        {score}
      </div>
      <p className="text-xs text-gray-400">{label}</p>
    </div>
  );
}

export function StepFeedback({ analysisResult, error, hasRefined, userTranscript, userAudioBase64, onRefine, onNext }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('content');
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

  const { text_score, voice_score, overall_score, text_feedback, voice_feedback, sample_answer, filler_words_detail, improvement_tips, pace_wpm, confidence_level } = analysisResult;

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Score row */}
        <div className="flex justify-around py-4 bg-gradient-to-r from-orange-50 to-amber-50 rounded-2xl border border-orange-100">
          <ScoreCircle score={text_score} label="Content" color="#ea580c" />
          <ScoreCircle score={voice_score} label="Voice" color="#d97706" />
          <ScoreCircle score={overall_score} label="Overall" color="#16a34a" />
        </div>

        {/* Voice metrics */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-gray-50 rounded-xl p-3 border border-gray-100">
            <p className="font-bold text-gray-700">{pace_wpm}</p>
            <p className="text-xs text-gray-400">WPM</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-3 border border-gray-100">
            <p className="font-bold text-gray-700 capitalize">{confidence_level}</p>
            <p className="text-xs text-gray-400">Confidence</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-3 border border-gray-100">
            <p className="font-bold text-gray-700">{filler_words_detail.total_count}</p>
            <p className="text-xs text-gray-400">Fillers</p>
          </div>
        </div>

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

        {/* Refinement comparison */}
        {analysisResult.refinement_comparison && (
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-700 leading-relaxed">
            <p className="font-semibold mb-1">vs. First Attempt</p>
            <p>{analysisResult.refinement_comparison}</p>
          </div>
        )}

        {/* Feedback tabs */}
        <div className="border border-gray-100 rounded-xl shadow-sm bg-white p-4">
          <div className="flex gap-2 mb-4">
            <TabBtn active={activeTab === 'content'} onClick={() => setActiveTab('content')} icon={MessageSquare} label="Content" />
            <TabBtn active={activeTab === 'voice'} onClick={() => setActiveTab('voice')} icon={Mic} label="Voice" />
            <TabBtn active={activeTab === 'better'} onClick={() => setActiveTab('better')} icon={Sparkles} label="Better Way" />
          </div>
          <AnimatePresence mode="wait">
            {activeTab === 'content' && (
              <motion.div key="content" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} transition={{ duration: 0.15 }}>
                <div className="text-sm text-gray-700 leading-relaxed ai-feedback-content" dangerouslySetInnerHTML={{ __html: text_feedback }} />
              </motion.div>
            )}
            {activeTab === 'voice' && (
              <motion.div key="voice" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} transition={{ duration: 0.15 }}>
                <div className="text-sm text-gray-700 leading-relaxed ai-feedback-content" dangerouslySetInnerHTML={{ __html: voice_feedback }} />
                {improvement_tips.length > 0 && (
                  <ul className="mt-3 space-y-1">
                    {improvement_tips.map((tip, i) => (
                      <li key={i} className="text-xs text-gray-600 flex gap-2"><span className="text-orange-400">•</span>{tip}</li>
                    ))}
                  </ul>
                )}
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
        {!hasRefined && (
          <button onClick={onRefine}
            className="flex-1 py-4 rounded-xl border-2 border-orange-400 text-orange-600 font-semibold hover:bg-orange-50"
          >
            Refine
          </button>
        )}
        <button onClick={onNext}
          className="flex-1 py-4 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold shadow-lg"
        >
          Next
        </button>
      </div>
    </div>
  );
}
