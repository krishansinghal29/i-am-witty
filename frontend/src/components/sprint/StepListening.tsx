import { motion } from 'framer-motion';
import type { QuestionMessage } from '@/types/question';

interface Props {
  listeningLiveText: string;
  questionData?: QuestionMessage[];
  avatarUrl?: string | null;
}

export function StepListening({ listeningLiveText, questionData, avatarUrl }: Props) {
  const textParts = questionData?.filter(p => p.role !== 'Image' && p.content) ?? [];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 gap-6">
      {avatarUrl && (
        <motion.img
          src={avatarUrl}
          alt="AI persona"
          className="w-24 h-24 rounded-full object-cover ring-4 ring-orange-200 shadow-lg"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
        />
      )}
      {!avatarUrl && (
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center shadow-lg">
          <span className="text-white text-3xl">🔊</span>
        </div>
      )}

      <div className="w-full max-w-md bg-gray-50 rounded-2xl p-5 border border-gray-100 shadow-sm min-h-[100px]">
        {textParts.length > 1 ? (
          <div className="space-y-3">
            {textParts.map((part, i) => (
              <div key={i}>
                <div className="text-xs text-gray-400 font-medium mb-1">{part.role}:</div>
                <div className="text-gray-700 leading-relaxed">{
                  /* Show text up to the live reveal boundary */
                  listeningLiveText.length > 0 ? part.content : ''
                }</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-700 leading-relaxed text-center">{listeningLiveText}</p>
        )}
      </div>

      {/* Audio wave animation */}
      <div className="flex items-center gap-1.5">
        {[1, 2, 3, 4, 5].map(i => (
          <motion.div
            key={i}
            className="w-1.5 rounded-full bg-orange-400"
            animate={{ height: [12, 28, 12] }}
            transition={{ duration: 0.8, delay: i * 0.1, repeat: Infinity, ease: 'easeInOut' }}
          />
        ))}
      </div>

      <p className="text-sm text-gray-400">Listen carefully...</p>
    </div>
  );
}
