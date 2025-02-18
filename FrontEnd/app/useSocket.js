import { useEffect } from 'react';
import { io } from 'socket.io-client';

const useSocket = (setBufferSize) => {
  useEffect(() => {
    // Conectar al servidor de Socket.IO
    const socket = io("http://localhost:4000", {
        withCredentials: true,
        transports: ["websocket", "polling"]
      });

    // Escuchar el evento 'buffer_status' emitido desde Flask
    socket.on('buffer_status', (data) => {
      console.log('Tamaño del buffer recibido:', data.size);
      setBufferSize(data.size); // Actualiza el estado con el tamaño del buffer
    });

    // Limpiar la conexión cuando el componente se desmonte
    return () => {
      socket.disconnect();
    };
  }, []);

  return;
};

export default useSocket;