import { CircularProgress } from '@mui/material';

export function StepAnalyzing() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-4 p-8">
      <CircularProgress size={48} sx={{ color: '#ea580c' }} />
      <p className="text-gray-500 font-medium">Analysing your response...</p>
      <p className="text-xs text-gray-400">This may take a few seconds</p>
    </div>
  );
}
