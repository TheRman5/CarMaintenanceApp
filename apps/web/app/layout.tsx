import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "My Garage | Maintenance Tracker",
  description: "Keep track of vehicle maintenance, service records, and due dates.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
