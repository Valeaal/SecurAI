"use client";

import { useState } from "react";
import useSocket from "../useSocket";

export default function Home() {
  const [bufferSize, setBufferSize] = useState(0);
  const maxBufferSize = 1000; // 🔹 Límite para la barra llena

  useSocket(setBufferSize);

  // 🔹 Calculamos el % de la barra basado en el tamaño del buffer
  const bufferPercentage = Math.min((bufferSize / maxBufferSize) * 100, 100);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-4">Estado del Buffer</h1>

      {/* Barra de progreso */}
      <div className="w-full max-w-md bg-gray-700 rounded-full h-8 overflow-hidden shadow-md">
        <div
          className="h-full bg-green-500 transition-all duration-200 ease-in-out"
          style={{ width: `${bufferPercentage}%` }}
        ></div>
      </div>

      <p className="mt-4 text-lg">Tamaño del buffer: {bufferSize}</p>
    </div>
  );
}
