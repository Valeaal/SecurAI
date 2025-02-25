"use client";

import { CheckCircle, AlertTriangle } from "lucide-react";
import useNotifierSocket from "../app/useSocket/useNotifierSocket"; // Importar desde la carpeta de hooks

export default function StatusCard() {
  const attacks = useNotifierSocket(); // Recibe el conjunto de ataques activos

  return (
    <div className="p-8 bg-darkP rounded-lg shadow-lg w-full text-center">
      {attacks.length > 0 ? (
        <>
          <AlertTriangle className="w-24 h-24 text-textP1 mx-auto mb-8" />
          <p className="text-textP2 font-semibold">Estás siendo atacado</p>
          <ul className="mt-4 text-textP2 text-sm">
            {attacks.map((attack, index) => (
              <li key={index}>Detectado por: {attack}</li>
            ))}
          </ul>
        </>
      ) : (
        <>
          <CheckCircle className="w-24 h-24 text-textG1 mx-auto mb-8" />
          <p className="text-textG2 font-semibold">
            No estás siendo atacado, SecurAI te protege.
          </p>
        </>
      )}
    </div>
  );
}
