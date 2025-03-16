import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Resume Rocket",
  description: "Optimize your resume for job applications",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}