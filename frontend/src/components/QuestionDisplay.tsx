import { CircularProgress } from '@mui/material';
import type { QuestionMessage } from '@/types/question';

const getRoleStyles = (role: string): string => {
  const map: Record<string, string> = {
    She: 'bg-pink-50 border-pink-200',
    You: 'bg-blue-50 border-blue-200',
    Topic: 'bg-purple-50 border-purple-200',
    He: 'bg-indigo-50 border-indigo-200',
    Image: 'bg-orange-50 border-orange-200',
  };
  return map[role] || 'bg-gray-50 border-gray-200';
};

interface Props {
  question: QuestionMessage[] | undefined;
  isLoading: boolean;
  className?: string;
  avatarUrl?: string;
}

export default function QuestionDisplay({ question, isLoading, className = '', avatarUrl }: Props) {
  if (isLoading) {
    return (
      <div className={`flex justify-center items-center p-6 ${className}`}>
        <CircularProgress size={32} />
      </div>
    );
  }

  if (!question || question.length === 0) {
    return <div className={`text-center text-gray-400 p-6 ${className}`}>No question available</div>;
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {question.map((msg, i) => (
        <div key={i} className={`rounded-lg p-4 border ${getRoleStyles(msg.role)}`}>
          <div className="flex items-center gap-2.5 mb-2">
            {avatarUrl && msg.role === 'She' && (
              <img
                src={avatarUrl}
                alt="avatar"
                className="w-10 h-10 rounded-full object-cover ring-2 ring-white shadow-sm"
              />
            )}
            <span className="text-sm text-gray-400 font-medium">
              {msg.role === 'Image' ? 'Flirt with balance: give a compliment, then tease.' : `${msg.role}:`}
            </span>
          </div>
          {msg.role === 'Image' ? (
            <div className="flex justify-center mt-3">
              <img
                src={msg.content}
                alt="Practice scenario"
                className="h-auto max-w-xs rounded-lg border border-gray-200 shadow-sm"
              />
            </div>
          ) : (
            <div className="text-gray-800 font-medium leading-relaxed">{msg.content}</div>
          )}
        </div>
      ))}
    </div>
  );
}
