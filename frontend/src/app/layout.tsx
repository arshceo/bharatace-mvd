import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

const inter = Inter({ 
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "BharatAce - Super Smart AI Campus Assistant",
  description: "Your personalized AI campus companion. Get intelligent answers with access to your attendance, marks, fees, timetable, and more.",
  keywords: ["BharatAce", "AI", "Campus Assistant", "Education", "Chatbot", "Student Portal"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
