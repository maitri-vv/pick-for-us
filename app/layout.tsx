import type { Metadata } from 'next';
import './globals.css';
export const metadata:Metadata={title:'Pick For Us — less scrolling, more movie night',description:'A small trained AI finds your next movie—and a middle ground when two people cannot decide. No uploads, account connections or API keys.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>;}
