import { Geist, Geist_Mono } from "next/font/google";
import NavBar from "../components/NavBar";
import BufferBar from "../components/BufferBar";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "SecurAI",
  description: "Protegiendo tu red con inteligencia artificial",
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-backgroundP`}
      >
        {/* Asegúrate de que el NavBar tenga un alto fijo o no se quede pegado al borde superior */}
        <NavBar />
        
        {children}

        <BufferBar /> {/* Se mantiene fijo en la parte inferior */}
      </body>
    </html>
  );
}
