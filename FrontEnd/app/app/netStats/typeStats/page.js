"use client";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import useTypeStatsSocket from "@/app/useSocket/useTypeStatsSocket";


export default function TypeStats() {
  const data = useTypeStatsSocket();
  
  // Colores de Tailwind (debes definir estos valores en tu configuración si no existen)
  const COLORS = ["#DEA5DF", "#DBFFC7", '#A0D8B3', '#FF8DAA', '#C2185B', '#76D7C4', '#FFEB3B' ];

  return (
    <div className="p-4 mt-8">
      <h2 className="text-2xl text-textG1 font-bold text-center">Distribución de tipos de paquetes</h2>

      {data.length === 0 ? (
        <p className="text-center text-textG2">Esperando datos...</p>
      ) : (
        <div>
          <ResponsiveContainer width="100%" height={600}>
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                outerRadius="80%"
                fill="#8884d8"
                label
              >
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
