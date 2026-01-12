import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Decision Calm Engine',
  description: 'Make calmer, better decisions in 60 seconds',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <a href="/" className="text-2xl font-bold text-calm-700">
                🧘 Decision Calm
              </a>
              <div className="flex gap-4">
                <a
                  href="/"
                  className="text-gray-600 hover:text-calm-700 transition-colors"
                >
                  New Session
                </a>
                <a
                  href="/history"
                  className="text-gray-600 hover:text-calm-700 transition-colors"
                >
                  History
                </a>
              </div>
            </div>
          </div>
        </nav>

        <main className="min-h-screen">
          {children}
        </main>

        <footer className="border-t border-gray-200 bg-gray-50 mt-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-sm text-gray-600">
              <p className="mb-2">
                Decision Calm Engine is NOT medical advice, therapy, or crisis intervention.
              </p>
              <p>
                For emergencies: <strong>US 988</strong> | <strong>EU 116 123</strong>
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
