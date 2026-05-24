import { ArrowRight, MessageSquare } from 'lucide-react';
import type { ExampleOptions, ExerciseExampleData } from '@/types/exercise';

const ExerciseExamplePage = ({
  exerciseExampleData,
  onNext,
}: {
  exerciseExampleData: ExerciseExampleData;
  onNext: () => void;
}) => {
  const exampleArray: ExampleOptions[] = Object.values(exerciseExampleData.examples || {}).flat();

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="flex-1 overflow-y-auto w-full">
        <div className="px-4 py-4">
          <div className="border border-gray-100 rounded-xl shadow-sm bg-white p-5">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center">
                <MessageSquare className="h-4 w-4 text-white" />
              </div>
              <h3 className="text-lg font-bold text-gray-800">Quick Example</h3>
            </div>
            <div className="space-y-3">
              {exampleArray.map((line, idx) => (
                <div key={idx}>
                  <div className="text-xs font-medium text-gray-400 mb-1 uppercase tracking-wide">{line.role}</div>
                  <div className={`text-gray-700 text-base leading-relaxed rounded-xl p-3 ${idx % 2 !== 0 ? 'bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-100' : 'bg-gray-50 border border-gray-100'}`}>
                    {line.content}
                  </div>
                  {idx < exampleArray.length - 1 && (
                    <div className="flex justify-center my-3">
                      <div className="w-6 h-0.5 bg-gradient-to-r from-orange-300 to-amber-300 rounded-full" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <div className="p-4 bg-white border-t border-gray-100">
        <button
          onClick={onNext}
          className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold py-4 rounded-xl shadow-lg flex items-center justify-center gap-2"
        >
          <span>Practice This Now</span>
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default ExerciseExamplePage;
