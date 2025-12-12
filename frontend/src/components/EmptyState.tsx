'use client';
import { Database, Brain, Shield } from 'lucide-react';

interface EmptyStateProps {
    onSuggestionClick: (suggestion: string) => void;
}

const suggestions = [
    {
        icon: Database,
        text: 'Quais os pilares de Data Mesh segundo a Zhamak?',
    },
    {
        icon: Brain,
        text: 'Tendências de IA Generativa para 2025',
    },
    {
        icon: Shield,
        text: 'Framework de governança de dados da McKinsey',
    },
];

export function EmptyState({ onSuggestionClick }: EmptyStateProps) {
    return (
        <div className="flex flex-col items-center justify-center h-full py-12">
            <h1 className="font-serif text-3xl text-gray-800 mb-2">StratGov AI</h1>
            <p className="text-gray-500 mb-8">Consultoria estratégica baseada em evidências</p>

            <div className="grid gap-4 w-full max-w-xl">
                {suggestions.map((s, i) => (
                    <button
                        key={i}
                        onClick={() => onSuggestionClick(s.text)}
                        className="flex items-center gap-4 p-4 bg-white rounded-xl border border-gray-200 hover:border-navy hover:shadow-md transition-all text-left group"
                    >
                        <div className="w-10 h-10 rounded-lg bg-gray-50 flex items-center justify-center group-hover:bg-navy/5">
                            <s.icon size={20} className="text-gray-400 group-hover:text-navy" />
                        </div>
                        <span className="text-gray-700 group-hover:text-gray-900">{s.text}</span>
                    </button>
                ))}
            </div>
        </div>
    );
}
