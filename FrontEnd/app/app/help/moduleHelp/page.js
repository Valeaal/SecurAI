"use client"

import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';

export default function moduleHelp() {
  return (
    <div className="flex justify-center items-center mt-16">
      <div className="w-full max-w-lg md:max-w-2xl lg:max-w-4xl">

        <h2 className="text-3xl text-textG1 font-semibold mb-4 text-center">Sistema modular de detección</h2>
        
        <Accordion type="single" collapsible>
          <AccordionItem value="item-1">
            <AccordionTrigger>¿Qué significa que el sistema sea modular?</AccordionTrigger>
            <AccordionContent>
              El sistema modular de SecurAI está diseñado para que puedas añadir, quitar o modificar módulos de detección de manera independiente sin afectar al funcionamiento del resto del sistema. Cada módulo se encarga de un tipo específico de detección, por ejemplo, ARP Spoofing, TCP SYN o DNS Amplification. Los módulos funcionan de forma autónoma, pero todos comparten una estructura común para facilitar su integración, la cola (buffer) de mensajes (paquetes). <br></br>
              Esto significa que puedes tener múltiples módulos activos al mismo tiempo, cada uno trabajando en sus propios parámetros, sin interferir con los demás.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-2">
            <AccordionTrigger>¿Cómo se gestionan los paquetes en el sistema modular?</AccordionTrigger>
            <AccordionContent>
              En SecurAI, los paquetes de red no se eliminan hasta que no hayan sido procesados por todos los módulos cargados en el sistema. Esto garantiza que cada módulo tenga la oportunidad de analizar el paquete y determinar si constituye una amenaza. El sistema no elimina el paquete hasta que todos los módulos hayan finalizado su análisis, lo que asegura que no se omitan posibles amenazas. <br></br>
              Esta metodología garantiza un análisis exhaustivo de cada paquete antes de ser descartado.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-3">
            <AccordionTrigger>En la interfaz, ¿cómo sé que módulos están activos en tiempo real?</AccordionTrigger>
            <AccordionContent>
              Los módulos en verde oscuro están desactivados en este momento es decir: El sistema los ha detectado como válidos pero el usuario no los ha activado ahora mismo.<br></br>
              Los módulos en verde más claro están activados en este momento es decir: Están filtrando los paquetes ahora mismo. 
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-4">
            <AccordionTrigger>¿Cómo puedo agregar un nuevo módulo de detección?</AccordionTrigger>
            <AccordionContent>
              Si eres desarrollador y deseas agregar un nuevo módulo de detección en SecurAI, el proceso es fácil y sencillo. Hemos diseñado la arquitectura para que los nuevos módulos se integren sin dificultad, y la documentación está disponible para guiarte paso a paso en la creación de nuevos módulos. <br></br>
              Los módulos pueden (y se recomienda) estar basados en algoritmos de IA, lo que permite una mayor adaptabilidad y capacidad para detectar patrones complejos. Si estás interesado, consulta la documentación para obtener ejemplos y detalles sobre cómo crear y cargar tu propio módulo de detección.
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </div>
  );
}
