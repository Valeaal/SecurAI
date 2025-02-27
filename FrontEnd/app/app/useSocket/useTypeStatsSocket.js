"use client";
import { useState, useEffect, useRef } from "react";
import io from "socket.io-client";

// Conexión al backend
const socket = io("http://localhost:4000");

export default function useTypeStatsSocket() {
  const [data, setData] = useState([]); // Historial acumulado de tipos de paquetes
  const packetTypeCountRef = useRef(new Map()); // Mapa para contar paquetes por tipo

  useEffect(() => {
    function handleNewPacket(packet) {
      const { last_layer } = packet; // Suponiendo que los paquetes tienen un campo "type"
      
      // Actualizamos el contador sin resetearlo
      packetTypeCountRef.current.set(last_layer, (packetTypeCountRef.current.get(last_layer) || 0) + 1);

      // Convertimos el mapa en un array de objetos y actualizamos el estado
      setData(Array.from(packetTypeCountRef.current.entries()).map(([name, value]) => ({ name, value })));
    }

    socket.on("packet_layer_info", handleNewPacket);

    return () => {
      socket.off("packet_layer_info", handleNewPacket);
    };
  }, []);

  return data; // Devuelve los datos acumulados
}
