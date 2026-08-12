import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import QueryProvider from "@/providers/QueryProvider"; // <-- This will now work perfectly

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PayFriction Analytics",
  description: "Monitor and recover failed payment transactions",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50 text-gray-900`}>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}