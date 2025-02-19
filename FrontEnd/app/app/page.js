"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function FilterSection() {
  const [activeFilters, setActiveFilters] = useState({});

  const handleFilterClick = (filter) => {
    setActiveFilters((prev) => ({
      ...prev,
      [filter]: !prev[filter],
    }));

    // TODO: Enviar petición HTTP aquí
    console.log(`Filtro ${filter} ${!activeFilters[filter] ? "activado" : "desactivado"}`);
  };

  const filters = [
    "Filtro de lo que sea 1",
    "Filtro de lo que sea 2",
    "Filtro de lo que sea 3",
    "Filtro de lo que sea 4",
    "Filtro de lo que sea 5",
    "Filtro de lo que sea 6",
    "Filtro de lo que sea 7",
  ];

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
