export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen">
        <nav className="bg-white shadow-md border-b border-gray-200">
          <div className="max-w-6xl mx-auto px-4 py-5">
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
              My App
            </h1>
          </div>
        </nav>
        <main className="max-w-6xl mx-auto px-4 py-10">
          {children}
        </main>
      </body>
    </html>
  );
}