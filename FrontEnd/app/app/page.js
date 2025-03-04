"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import StatusCard from "@/components/statusCard";

export default function home() {
  const [activeModules, setActiveModules] = useState({});
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchModules = async () => {
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

    fetchModules();
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

      {/* Sección de estado */}
      <div className="flex-1 flex flex-col items-center justify-center h-full gap-4">
        <StatusCard />
      </div>

      {/* Sección de módulos */}
      <div className="my-scrollbar w-2/5 flex flex-col justify-start items-center overflow-y-auto">
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
