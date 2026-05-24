import { AnimatePresence, motion } from 'framer-motion';
import { ArrowRight, ChevronDown, ChevronUp, MessageSquare, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { CircularProgress } from '@mui/material';
import QuestionDisplay from '@/components/QuestionDisplay';
import { useUser } from '@/contexts/UserContext';
import { preFetchGenerateQuestion } from '@/hooks';
import { useEvaluateResponse } from '@/hooks/useEvaluateResponse';
import type { QuestionMessage } from '@/types/question';
import { useQueryClient } from '@tanstack/react-query';

const TabButton = ({ active, onClick, icon: Icon, label }: { active: boolean; onClick: () => void; icon: React.ElementType; label: string }) => (
  <button
    onClick={onClick}
    className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl font-medium transition-all text-sm border-2
      ${active ? 'bg-gradient-to-r from-orange-500 to-orange-600 text-white border-orange-500 shadow-md' : 'bg-white text-gray-600 border-gray-200 hover:border-orange-300 hover:bg-orange-50'}
    `}
  >
    <Icon size={16} />
    <span>{label}</span>
  </button>
);

const ExerciseFeedbackPage = ({
  exerciseId,
  question,
  userResponse,
  count,
  onNext,
}: {
  exerciseId: string;
  question?: string | QuestionMessage[];
  userResponse?: string;
  count: number;
  onNext: () => void;
}) => {
  const { uid } = useUser();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'feedback' | 'alternative'>('feedback');
  const [isQuestionExpanded, setIsQuestionExpanded] = useState(false);

  const { data, isLoading } = useEvaluateResponse(uid, exerciseId, question, userResponse);

  // Pre-fetch next question
  if (data?.success) {
    preFetchGenerateQuestion(queryClient, uid, exerciseId, count + 1);
  }

  const formattedQuestion = Array.isArray(question) ? question : undefined;

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="flex-1 overflow-y-auto w-full">
        <div className="px-4 py-4 space-y-4">
          {/* Question & Response collapsible */}
          <div
            className="border border-gray-100 rounded-xl shadow-sm bg-white p-3 cursor-pointer"
            onClick={() => setIsQuestionExpanded(v => !v)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare size={14} className="text-gray-400" />
                <span className="font-medium text-gray-600 text-sm">Situation & Response</span>
              </div>
              <div className="flex items-center gap-1 text-xs text-gray-400">
                {isQuestionExpanded ? 'Hide' : 'Show'}
                {isQuestionExpanded ? <ChevronUp size={18} className="text-gray-400" /> : <ChevronDown size={18} className="text-gray-400" />}
              </div>
            </div>
            <AnimatePresence>
              {isQuestionExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="pt-3 space-y-3">
                    {formattedQuestion && <QuestionDisplay question={formattedQuestion} isLoading={false} />}
                    {userResponse && (
                      <div className="bg-gray-50 rounded-lg p-3 border-l-4 border-orange-400">
                        <div className="text-xs font-medium text-orange-600 mb-1">YOUR RESPONSE</div>
                        <div className="text-gray-700 text-sm leading-relaxed">{userResponse}</div>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            {!isQuestionExpanded && userResponse && (
              <p className="text-xs text-gray-400 mt-2 line-clamp-1 pl-5">"{userResponse}"</p>
            )}
          </div>

          {/* AI Feedback tabs */}
          <div className="border border-gray-100 rounded-xl shadow-sm bg-white p-4">
            <div className="flex gap-2 mb-4">
              <TabButton active={activeTab === 'feedback'} onClick={() => setActiveTab('feedback')} icon={MessageSquare} label="AI Coach" />
              <TabButton active={activeTab === 'alternative'} onClick={() => setActiveTab('alternative')} icon={Sparkles} label="Better Way" />
            </div>
            <AnimatePresence mode="wait">
              {activeTab === 'feedback' && (
                <motion.div key="feedback" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} transition={{ duration: 0.15 }}>
                  {isLoading ? (
                    <div className="flex justify-center py-8"><CircularProgress size={28} /></div>
                  ) : (
                    <div className="text-gray-700 leading-relaxed text-sm ai-feedback-content" dangerouslySetInnerHTML={{ __html: data?.evaluation?.feedback || '' }} />
                  )}
                </motion.div>
              )}
              {activeTab === 'alternative' && (
                <motion.div key="alternative" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }} transition={{ duration: 0.15 }}>
                  <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl p-4 border border-orange-100">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles size={16} className="text-orange-500" />
                      <span className="text-xs font-semibold text-orange-600 uppercase tracking-wide">Pro Response</span>
                    </div>
                    {isLoading ? (
                      <div className="flex justify-center py-8"><CircularProgress size={28} /></div>
                    ) : (
                      <div className="text-gray-700 leading-relaxed text-sm ai-feedback-content" dangerouslySetInnerHTML={{ __html: data?.evaluation?.sample_answer || '' }} />
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
      <div className="p-4 bg-white border-t border-gray-100">
        <button
          onClick={onNext}
          className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold py-4 rounded-xl shadow-lg flex items-center justify-center gap-2"
        >
          <span>Continue</span>
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default ExerciseFeedbackPage;
