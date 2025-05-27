"use client";
import Image from "next/image";
import { useState, useEffect } from "react";

export default function CreditsPage() {
  return (
    <div className="p-8 mt-8 max-w-4xl mx-auto text-center">
      <h2 className="text-3xl font-bold text-textG1 mb-6">Créditos del Proyecto</h2>

      <div className="flex flex-col items-center">
      <div className="w-32 h-32 mb-4 rounded-full overflow-hidden border-4 border-textP2 shadow-md">
          <Image
            src="/assets/images/valeaal.jpg"
            alt="Álvaro Valencia Villalón"
            width={128}
            height={128}
            className="rounded-full object-cover"
          />
        </div>

        <p className="text-lg text-textG2 mb-2">
          <strong>Autor:</strong> Álvaro Valencia Villalón
        </p>
        <p className="text-lg text-textG2 mb-2">
          <strong>Proyecto:</strong> Trabajo Fin de Grado en Ingeniería Informática
        </p>
        <p className="text-lg text-textG2 mb-2">
          <strong>Universidad:</strong> Universidad de Málaga (UMA)
        </p>
        <p className="text-lg text-textG2 mb-2">
          <strong>Repositorio:</strong>{" "}
          <a
            href="https://github.com/Valeaal/SecurAI"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:underline"
          >
            github.com/Valeaal/SecurAI
          </a>
        </p>
        <p className="text-lg text-textG2 mb-2">
          <strong>Versión:</strong> v4.0.2-beta (21 de mayo de 2025)
        </p>
      </div>

      <div className="mt-8">
        <h3 className="text-2xl font-semibold text-textP2 mb-4">Agradecimientos</h3>
        <ul className="list-disc list-inside text-textP2 space-y-2">
          <li>
            A mis tutores y profesores de la UMA por su orientación y apoyo continuo.
          </li>
          <li>
            A la comunidad de código abierto por proporcionar herramientas y recursos invaluables.
          </li>
          <li>
            A mi familia y amigos por su paciencia y motivación durante este proyecto.
          </li>
        </ul>
      </div>
    </div>
  );
}
