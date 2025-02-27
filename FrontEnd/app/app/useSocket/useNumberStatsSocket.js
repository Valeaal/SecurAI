"use client";
import { useState, useEffect, useRef } from "react";
import io from "socket.io-client";

// Conexión al backend
const socket = io("http://localhost:4000");

export default function useStatsSocket() {
  const [data, setData] = useState([]); // Mantiene el historial de datos
  const packetCountRef = useRef(0); // Usamos useRef para mantener el contador sin causar re-renderizados innecesarios

  useEffect(() => {
    // Función para manejar los paquetes entrantes
    function handleNewPacket() {
      packetCountRef.current += 1; // Incrementamos el contador directamente en la referencia
    }

    // Escuchar los paquetes del backend
    socket.on("packet_layer_info", handleNewPacket);

    // Intervalo para guardar los datos cada 30 segundos
    const interval = setInterval(() => {
      const timestamp = new Date().toLocaleTimeString(); // Hora actual
      const newEntry = { time: timestamp, packets: packetCountRef.current }; // Crear nuevo registro con el número de paquetes recibidos

      setData((prevData) => {
        const updatedData = [...prevData, newEntry]; // Añadir el nuevo dato
        return updatedData.length > 15 ? updatedData.slice(1) : updatedData;
      });

      // Resetea el contador de paquetes
      packetCountRef.current = 0;
    }, 5000);

    // Cleanup: Cuando el componente se desmonta, limpia el intervalo y la suscripción al socket
    return () => {
      clearInterval(interval); // Limpiar el intervalo
      socket.off("packet_layer_info", handleNewPacket); // Limpiar la suscripción
    };
  }, []); // Este efecto solo se ejecuta una vez cuando el componente se monta

  return data; // Devuelve los datos con los registros de los paquetes
}
