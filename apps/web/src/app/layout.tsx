import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';

const inter = Inter({ subsets: ['latin', 'latin-ext'] });

export const metadata: Metadata = {
  title: 'Spokojne Decyzje - Asystent Podejmowania Decyzji',
  description: 'Podejmuj spokojniejsze i lepsze decyzje w 60 sekund dzięki AI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pl">
      <body className={inter.className}>
        <nav className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <a href="/" className="text-2xl font-bold text-calm-700">
                🧘 Spokojne Decyzje
              </a>
              <div className="flex gap-4">
                <a
                  href="/"
                  className="text-gray-600 hover:text-calm-700 transition-colors"
                >
                  Nowa sesja
                </a>
                <a
                  href="/history"
                  className="text-gray-600 hover:text-calm-700 transition-colors"
                >
                  Historia
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
                Spokojne Decyzje NIE JEST poradą medyczną, terapią ani interwencją kryzysową.
              </p>
              <p>
                W nagłych wypadkach: <strong>Polska 116 123</strong> | <strong>Telefon Zaufania dla Dzieci i Młodzieży 116 111</strong>
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
