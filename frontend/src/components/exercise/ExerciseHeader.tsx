import { motion } from 'framer-motion';
import type { ExerciseStep } from '@/types/exercise';

const STEPS: ExerciseStep[] = ['intro', 'example', 'practice', 'feedback'];
const STEP_LABELS: Record<ExerciseStep, string> = {
  intro: 'Learn',
  example: 'Example',
  practice: 'Practice',
  feedback: 'Review',
};

const StepDot = ({ step, currentStep, index }: { step: ExerciseStep; currentStep: ExerciseStep; index: number }) => {
  const currentIndex = STEPS.indexOf(currentStep);
  const isCompleted = index < currentIndex;
  const isCurrent = index === currentIndex;
  const isUpcoming = index > currentIndex;

  return (
    <div className="flex flex-col items-center">
      <motion.div
        className={`w-7 h-7 rounded-full flex items-center justify-center border-2 transition-colors duration-300
          ${isCompleted ? 'bg-orange-500 border-orange-500' : ''}
          ${isCurrent ? 'bg-orange-500 border-orange-500 shadow-lg shadow-orange-200' : ''}
          ${isUpcoming ? 'bg-white border-gray-200' : ''}
        `}
        animate={isCurrent ? { scale: [1, 1.05, 1] } : { scale: 1 }}
        transition={isCurrent ? { duration: 1.5, repeat: Infinity, ease: 'easeInOut' } : {}}
      >
        {isCompleted ? (
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-white">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        ) : (
          <span className={`text-xs font-bold ${isCurrent ? 'text-white' : 'text-gray-400'}`}>{index + 1}</span>
        )}
      </motion.div>
      <span className={`text-[10px] font-medium mt-1 ${isCurrent ? 'text-orange-600' : isCompleted ? 'text-orange-500' : 'text-gray-400'}`}>
        {STEP_LABELS[step]}
      </span>
    </div>
  );
};

export const ExerciseHeader = ({
  exerciseName,
  step,
}: {
  exerciseName: string;
  step: ExerciseStep;
}) => {
  const currentIndex = STEPS.indexOf(step);

  return (
    <div className="bg-white border-b border-gray-100 z-10 flex-none">
      <div className="px-4 h-12 flex items-center justify-center">
        <div className="font-semibold text-gray-800 text-base truncate max-w-[280px]">{exerciseName}</div>
      </div>
      <div className="px-6 pb-3 pt-1">
        <div className="relative flex items-start justify-between">
          <div className="absolute top-3.5 left-[14%] right-[14%] h-0.5 bg-gray-200 -z-0" />
          <motion.div
            className="absolute top-3.5 left-[14%] h-0.5 bg-orange-500 -z-0"
            initial={false}
            animate={{ width: currentIndex === 0 ? '0%' : currentIndex === 1 ? '24%' : currentIndex === 2 ? '48%' : '72%' }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
          />
          {STEPS.map((s, idx) => (
            <StepDot key={s} step={s} currentStep={step} index={idx} />
          ))}
        </div>
      </div>
    </div>
  );
};
