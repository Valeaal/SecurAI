import { useEffect, useState } from "react";
import { io } from "socket.io-client";

const useNotifierSocket = () => {
  const [attacks, setAttacks] = useState(new Map()); // Usamos un Map para asociar el módulo con su timestamp

  useEffect(() => {
    const socket = io("http://localhost:4000", {
      withCredentials: true,
      transports: ["websocket", "polling"],
    });

    socket.on("notify_attack", (data) => {
      console.log("Ataque detectado:", data.module_source, "Hora:", data.timestamp);

      setAttacks((prevAttacks) => {
        const updatedAttacks = new Map(prevAttacks);
        updatedAttacks.set(data.module_source, Date.now());
        return updatedAttacks;
      });
    });

    // Función que limpia los ataques antiguos cada segundo
    const cleanupAttacks = () => {
      setAttacks((prevAttacks) => {
        const now = Date.now();
        const updatedAttacks = new Map();
        
        prevAttacks.forEach((timestamp, module) => {
          // Mantener solo los módulos que han sido actualizados en los últimos 5 segundos
          if (now - timestamp < 1000) {
            updatedAttacks.set(module, timestamp);
          }
        });

        return updatedAttacks;
      });
    };

    // Limpiar los ataques cada 1 segundo
    const intervalId = setInterval(cleanupAttacks, 1000);

    // Limpiar intervalos y desconectar al desmontar el componente
    return () => {
      clearInterval(intervalId);
      socket.disconnect();
    };
  }, []);

  // Convertir el Map a un Array para React
  return Array.from(attacks.keys()); // Devuelve solo los módulos (claves del Map)
};

export default useNotifierSocket;
