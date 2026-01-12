/**
 * Utility functions for Decision Calm Engine
 */

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind CSS classes with proper precedence
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format date to human-readable string
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

/**
 * Get color class for stress level
 */
export function getStressLevelColor(level: number): string {
  if (level >= 7) return 'bg-red-100 text-red-800 border-red-300';
  if (level >= 4) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
  return 'bg-green-100 text-green-800 border-green-300';
}

/**
 * Get color class for emotional risk
 */
export function getEmotionalRiskColor(risk: string): string {
  const riskLower = risk.toLowerCase();
  if (riskLower === 'high') return 'text-red-600';
  if (riskLower === 'medium') return 'text-yellow-600';
  return 'text-green-600';
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}
