"use client";

import { useState } from "react";
import useSocket from "../useSocket";

export default function BufferBar() {
  const [bufferSize, setBufferSize] = useState(0);
  const maxBuffer = 100000; // Máximo de paquetes antes de llenarse

  useSocket(setBufferSize);

  // Calcular el ancho de la barra en porcentaje
  const progress = Math.min((bufferSize / maxBuffer) * 100, 100);

  return (
    <div className="fixed bottom-0 left-0 right-0 p-4 bg-backgroundP z-50">
      <h2 className="text-textG2 text-lg font-bold mb-2">
        Estado de la cola de mensajes:
      </h2>
      <div className="w-full bg-textG2 rounded-full h-6 overflow-hidden">
        <div
          className="h-full bg-textG1 transition-all duration-300"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <p className="text-textG2 mt-2 text-sm">
        {bufferSize} / {maxBuffer} paquetes en cola para ser procesados o limpiados
      </p>
    </div>
  );
}
