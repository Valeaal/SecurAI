"use client"

import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';

export default function detectionHelp() {
  return (
    <div className="flex justify-center items-center mt-16">
      <div className="w-full max-w-lg md:max-w-2xl lg:max-w-4xl">

        <h2 className="text-3xl text-textG1 font-semibold mb-4 text-center">Ámbito de detección de SecurAI, ¿hasta dónde puede proteger?</h2>
        
        <Accordion type="single" collapsible>
          <AccordionItem value="item-1">
            <AccordionTrigger>¿Qué es el "modo monitor" y por qué no se usa en SecurAI?</AccordionTrigger>
            <AccordionContent>
              El "modo monitor" es una característica avanzada de las tarjetas de red que permite capturar todo el tráfico de la red, incluso el que no está destinado al ordenador. Sin embargo, SecurAI no utiliza este modo. ¿Por qué? Porque para evitar complejidades innecesarias y que el sistema funcione sin requerir configuraciones avanzadas o permisos especiales, se emplea la tarjeta de red en su modo estándar. <br></br>
              Esto significa que SecurAI solo puede detectar el tráfico de red que va dirigido directamente hacia el ordenador, es decir, paquetes destinados específicamente a él, o a todos los dispositivos de la red.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-2">
            <AccordionTrigger>¿Cómo afecta el uso sin el modo monitor?</AccordionTrigger>
            <AccordionContent>
              El principal impacto es que SecurAI solo puede detectar tráfico destinado al propio ordenador, y no todo el tráfico que pasa por la red. Esto puede limitar la detección de ciertas amenazas, como ataques de "Man-in-the-Middle" o intentos de escaneo de puertos, que no necesariamente envían datos al ordenador que está ejecutando el software. <br></br>
              Sin embargo, esta configuración ayuda a que SecurAI sea más accesible para la mayoría de los usuarios sin necesidad de conocimientos técnicos avanzados.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-3">
            <AccordionTrigger>¿Esto implica una menor seguridad?</AccordionTrigger>
            <AccordionContent>
              No, el hecho de no usar el modo monitor no significa que la seguridad sea baja. SecurAI sigue siendo capaz de detectar y prevenir muchos tipos de ataques que afectan directamente a tu dispositivo, como el ARP Spoofing, ataques DoS, y otros intentos de acceso no autorizado. <br></br>
              La principal diferencia es que SecurAI está optimizado para proteger tu equipo desde su perspectiva de tráfico destinado a él, lo cual es una medida eficiente para la mayoría de los usuarios.
            </AccordionContent>
          </AccordionItem>

        </Accordion>
      </div>
    </div>
  );
}
