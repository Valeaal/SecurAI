"use client"

import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';

export default function statsHelp() {
  return (
    <div className="flex justify-center items-center mt-16">
      <div className="w-full max-w-lg md:max-w-2xl lg:max-w-4xl">

        <h2 className="text-3xl text-textG1 font-semibold mb-4 text-center">Estadísticas de la red</h2>
        
        <Accordion type="single" collapsible>
          <AccordionItem value="item-1">
            <AccordionTrigger>¿Por qué querría ver estadísticas de la red?</AccordionTrigger>
            <AccordionContent>
              Entender el funcionamiento de la red ayuda a sacar conclusiones del estado de la misma. <br></br>
              Por ejemplo, esto permite saber si es normal que crezca mucho la cola de mensajes (debido a que la actividad de la red sea intensa) o si por el contrario quizás deberíamos de desactivar algunos módulos. <br></br>
              Las estadísticas empiezan a generarse una vez se abre la pantalla correspondiente, no corren en segundo plano para ahorrar recursos.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-2">
            <AccordionTrigger>Números de paquetes</AccordionTrigger>
            <AccordionContent>
              Esta estadística refleja en tiempo real el número de paquetes que el equipo va recibiendo. <br></br>
              Puede observar cómo el gráfico cambia conforme avanza el tiempo, y cómo se ajusta la escala del número de paquetes recibido.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-3">
            <AccordionTrigger>Tipos de paquetes</AccordionTrigger>
            <AccordionContent>
              Esta estadística refleja en tiempo real el tipo de paquetes que el equipo va recibiendo. <br></br>
              Con el tipo de paquete, nos referimos al protocolo conocido de la última capa que podemos detectar.
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </div>
  );
}
