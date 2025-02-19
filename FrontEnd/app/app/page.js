"use client";

import { Button } from "@/components/ui/button"; // Asegúrate de importar el componente Button desde ShadCN

export default function FilterSection() {
  return (
    <div className="w-full h-screen flex">
      {/* Sección izquierda y central (vacías por ahora, puedes llenarlas con contenido) */}
      <div className="flex-1"></div>

      {/* Sección derecha para los botones */}
      <div className="w-1/3 p-4 flex flex-col gap-6 justify-start items-center max-h-screen overflow-y-auto scrollbar-thin scrollbar-thumb-rounded-full scrollbar-thumb-green-600">
        {/* Título o texto opcional si lo necesitas */}
        <h2 className="text-white text-2xl font-semibold mb-4">Filtros de Red</h2>

        {/* Contenedor de los botones en dos columnas */}
        <div className="grid grid-cols-2 gap-4 w-full">
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 1
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 2
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 3
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 4
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 5
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 6
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 7
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 8
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 9
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 10
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 11
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 12
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 8
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 9
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 10
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 11
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 12
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 8
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 9
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 10
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 11
          </Button>
          <Button className="h-24 text-lg font-bold bg-green-600 hover:bg-green-700 text-white">
            Filtro 12
          </Button>
        </div>
      </div>
    </div>
  );
}
