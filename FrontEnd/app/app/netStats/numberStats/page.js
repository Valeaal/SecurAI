"use client";
import { useState, useEffect } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import useStatsSocket from "@/app/useSocket/useNumberStatsSocket";

export default function numberStats() {
  const data = useStatsSocket(); // Obtener datos de paquetes del hook

  return (
    <div className="p-4 mt-8">
      <h2 className="text-2xl text-textG1 font-bold text-center">Historial del número de paquetes recibidos</h2>

      {/* Gráfico de Área */}
      <div className="">
        <ResponsiveContainer width="100%" height={600}>
          <AreaChart
            data={data}
            margin={{
              top: 10,
              right: 5,
              bottom: 35,
              left: 5,
            }}
          >
            {/* Cuadrícula con color textG2 */}
            <CartesianGrid stroke="currentColor" strokeOpacity={0.2} strokeDasharray="3 3" className="text-textG2" />
            
            {/* Eje X con color textG2 y título "Hora del conteo" */}
            <XAxis 
              dataKey="time" 
              tickLine={false} 
              axisLine={false} 
              tickMargin={18} 
              tick={{ fill: 'currentColor', fontSize: 14 }} 
              className="text-textG2"
              label={{
                value: 'Hora del conteo',
                position: 'bottom',
                fontSize: 16,
                fill: 'currentColor',
                offset: 20,
                fontWeight: 'bold',
              }}
            />

            {/* Eje Y con color textG2 y título "Número de paquetes recibidos" */}
            <YAxis 
              tickLine={false} 
              axisLine={false} 
              tick={{ fill: 'currentColor', fontSize: 14 }} 
              className="text-textG2"
              label={{
                value: 'Número de paquetes recibidos',
                angle: -90,
                position: 'insideLeft',
                fontSize: 16,
                fill: 'currentColor',
                offset: 5,
                dy : 120,
                fontWeight: 'bold',
              }}
            />

            {/* Tooltip con color textG2 */}
            <Tooltip contentStyle={{ color: '#8884d8' }} className="text-textG2" />

            {/* Gráfico de Área con color textP2 */}
            <Area
              type="monotone"
              dataKey="packets"
              stroke="currentColor" 
              fill="currentColor" 
              fillOpacity={0.4}
              className="text-textP2" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
