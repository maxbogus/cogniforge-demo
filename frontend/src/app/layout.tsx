import '@/styles/globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <head>
        <title>CogniForge - Document Intelligence System</title>
        <meta name="description" content="RAG-powered document intelligence for due diligence and recruitment" />
      </head>
      <body className="h-full bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
        {children}
      </body>
    </html>
  )
}