"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { CheckCircle } from "lucide-react";

export default function Modulesection() {
  const [activeModules, setActiveModules] = useState({});
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Cargar los nombres de los algoritmos desde el backend al montar el componente
  useEffect(() => {
    const fetchmodules = async () => {
      try {
        const response = await fetch(
          "http://localhost:4000/loadDefenseAlgorithms/loadedNames",
          {
            method: "GET",
            headers: { "Content-Type": "application/json" },
          }
        );
        if (!response.ok) {
          throw new Error("Error al obtener los filtros");
        }
        const data = await response.json();
        console.log(data.algorithms);
        setModules(data.algorithms);
        setLoading(false);
      } catch (err) {
        console.error("Error al cargar filtros:", err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchmodules();
  }, []);

  const toggleModule = async (module, isActive) => {
    const endpoint = isActive
      ? "http://localhost:4000/loadDefenseAlgorithms/stopModule"
      : "http://localhost:4000/loadDefenseAlgorithms/startModule";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ algorithmName: module }),
      });

      if (!response.ok) {
        throw new Error(`Error en la petición: ${await response.text()}`);
      }

      const data = await response.json();
      console.log(data.message);

      // Si la petición es exitosa, actualizar el estado de los filtros
      setActiveModules((prev) => ({
        ...prev,
        [module]: !isActive,
      }));
    } catch (error) {
      console.error("Error al cambiar el estado del módulo:", error);
    }
  };

  if (loading) return <div>Cargando filtros...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="w-full h-screen p-4 gap-4 flex max-h-[calc(100vh-120px)]">

      <div className="flex-1 flex flex-col items-center justify-center h-full gap-4">
        <div className="p-8 bg-darkP rounded-lg shadow-lg w-full text-center">
          <CheckCircle className="w-24 h-24 text-textG1 mx-auto mb-8" />
          <p className="text-textG2 font-semibold">
            No estás siendo atacado, SecurAI te protege.
          </p>
        </div>
      </div>

      <div className="my-scrollbar w-1/3 flex flex-col justify-start items-center overflow-y-auto">
        <div className="grid grid-cols-2 gap-4 w-full">
          {modules.map((module) => {
            const isActive = !!activeModules[module];

            return (
              <Button
                key={module}
                variant={isActive ? "activeModule" : "module"}
                onClick={() => toggleModule(module, isActive)}
              >
                {module}
              </Button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
