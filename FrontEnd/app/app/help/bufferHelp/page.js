"use client"

import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';

export default function bufferHelp() {
  return (
    <div className="flex justify-center items-center mt-16">
      <div className="w-full max-w-lg md:max-w-2xl lg:max-w-4xl"> 

        <h2 className="text-3xl text-textG1 font-semibold mb-4 text-center">La cola de mensajes</h2>
        
        <Accordion type="single" collapsible>
          <AccordionItem value="item-1">
            <AccordionTrigger>¿Qué es la cola (buffer) de mensajes (paquetes)?</AccordionTrigger>
            <AccordionContent>
              El buffer de mensajes es el componente central que almacena los paquetes de red recibidos por el ordenador, los diferentes módulos cargados van cogiendo paquetes del buffer y procesándolos. <br></br>
              Cuando un paquete de red es procesado por un módulo no se elimina del buffer, sino que se mantiene por si hubiera otro módulo que aún tuviera que analizarlo. <br></br>
              Cuando un paquete es procesado por todos los módulos cargados, es candidato de que se elimine del buffer.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-2">
            <AccordionTrigger>¿Por qué se llena el buffer de mensajes?</AccordionTrigger>
            <AccordionContent>
              Los paquetes contenidos en el buffer de mensajes no necesariamente falten por ser procesados: Es posible que hayan sido analizados por todos los módulos activos, pero aún no se hayan eliminado. Esto es tarea de la "hebra limpiadora". <br></br>
              Aún así, si el tamaño del buffer crece demasiado, puede ser signo de que los módulos activos sean demasiados y los paquetes tarden en procesarse (de manera que la hebra limpiadora no pueda limpiarlos). Ten en cuenta que un paquete tiene que ser procesado por todos los módulos antes de ser marcado como listo para eliminar.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-3">
            <AccordionTrigger>¿Por qué aumenta el número de mensajes de la cola?</AccordionTrigger>
            <AccordionContent>
              El número de paquetes puede aumentar por dos razones: Que tu ordenador tiene una actividad intensa de red en este momento y naturalmente le lleguen muchos paquetes o que tengas demasiados módulos activos simultáneamente, por lo que cada paquete tarda mucho en procesarse por todos. <br></br>
              Ten en cuenta que un paquete tiene que ser procesado por todos los módulos antes de ser marcado como listo para eliminar por la "hebra limpiadora".
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="item-4">
            <AccordionTrigger>¿Qué es la hebra limpiadora?</AccordionTrigger>
            <AccordionContent>
              La hebra limpiadora es un proceso de vital importancia, que elimina del buffer de mensajes aquellos que ya han sido procesados por todos los módulos cargados y marcados como tal. <br></br>
              La hebra se ejecuta periódicamente, y durante el tiempo que tarde en limpiar (generalmente imperceptible) el procesamiento de los módulos cargados se pausa.
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </div>
  );
}
