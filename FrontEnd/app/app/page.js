"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function FilterSection() {
  const [activeFilters, setActiveFilters] = useState({});
  const [filters, setFilters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Cargar los nombres de los algoritmos desde el backend al montar el componente
  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const response = await fetch("http://localhost:4000/loadDefenseAlgorithms/loadedNames", {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });
        if (!response.ok) {
          throw new Error("Error al obtener los filtros");
        }
        const data = await response.json();
        // data debería tener la forma { algorithms: [...] }
        setFilters(data.algorithms);
        setLoading(false);
      } catch (err) {
        console.error("Error al cargar filtros:", err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchFilters();
  }, []);

  const handleFilterClick = (filter) => {
    setActiveFilters((prev) => ({
      ...prev,
      [filter]: !prev[filter],
    }));

    // Aquí podrías enviar una petición HTTP para notificar el cambio si es necesario.
    console.log(`Filtro ${filter} ${!activeFilters[filter] ? "activado" : "desactivado"}`);
  };

  if (loading) return <div>Cargando filtros...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="w-full h-screen flex max-h-[calc(100vh-120px)]">
      <div className="flex-1"></div>

      <div className="my-scrollbar w-1/3 p-4 flex flex-col justify-start items-center overflow-y-auto">
        <div className="grid grid-cols-2 gap-4 w-full">
          {filters.map((filter) => (
            <Button
              key={filter}
              variant={activeFilters[filter] ? "activeFilter" : "filter"}
              onClick={() => handleFilterClick(filter)}
            >
              {filter}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
