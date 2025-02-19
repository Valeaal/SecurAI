"use client";

import { useState } from "react";
import useSocket from "../../useSocket";

export default function BufferBar() {
  const [bufferSize, setBufferSize] = useState(0);
  const maxBuffer = 1500; // Máximo de paquetes antes de llenarse

  useSocket(setBufferSize);

  // Calcular el ancho de la barra en porcentaje
  const progress = Math.min((bufferSize / maxBuffer) * 100, 100);

  return (
    <div className="w-full max-w-lg">
      <h2 className="text-textP2 text-lg font-bold mb-2">Estado del Buffer</h2>
      <div className="w-full bg-textP2 rounded-full h-6 overflow-hidden">
        <div
          className="h-full bg-textG1 transition-all duration-300"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <p className="text-textG2 mt-2 text-sm">Tamaño actual: {bufferSize} / {maxBuffer}</p>
    </div>
  );
}
