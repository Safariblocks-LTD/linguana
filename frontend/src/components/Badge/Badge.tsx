'use client';

import { Award, Star, Zap, Trophy } from 'lucide-react';

interface BadgeProps {
  name: string;
  description: string;
  icon?: 'award' | 'star' | 'zap' | 'trophy';
  earned?: boolean;
  earnedAt?: Date;
}

const ICONS = {
  award: Award,
  star: Star,
  zap: Zap,
  trophy: Trophy,
};

export function Badge({ name, description, icon = 'award', earned = false, earnedAt }: BadgeProps) {
  const Icon = ICONS[icon];

  return (
    <div
      className={`card text-center transition-all ${
        earned ? 'bg-gradient-to-br from-primary/10 to-accent/10 border-2 border-primary' : 'opacity-50 grayscale'
      }`}
    >
      <div
        className={`w-16 h-16 rounded-full mx-auto mb-3 flex items-center justify-center ${
          earned ? 'bg-primary text-white' : 'bg-gray-200 text-gray-400'
        }`}
      >
        <Icon className="w-8 h-8" />
      </div>
      <h4 className="font-bold mb-1">{name}</h4>
      <p className="text-sm text-muted mb-2">{description}</p>
      {earned && earnedAt && (
        <p className="text-xs text-primary font-semibold">
          Earned {earnedAt.toLocaleDateString()}
        </p>
      )}
      {!earned && (
        <p className="text-xs text-muted">Not earned yet</p>
      )}
    </div>
  );
}
