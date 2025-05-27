"use client"

import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';

export default function moduleHelp() {
  return (
    <div className="flex justify-center items-center mt-16">
      <div className="w-full max-w-lg md:max-w-2xl lg:max-w-4xl">

        <h2 className="text-3xl text-textG1 font-semibold mb-4 text-center">Información adicional sobre SecurAI</h2>
        
        <Accordion type="single" collapsible>
          <AccordionItem value="item-1">
            <AccordionTrigger>¿Dónde puedo encontrar más información?</AccordionTrigger>
                <AccordionContent>
                    Puedes encontrar más información sobre SecurAI en el 
                    <a 
                        href="https://github.com/Valeaal/SecurAI" 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        style={{textDecoration: 'underline', marginLeft: '4px' }}
                    >
                        repositorio de GitHub
                    </a>. <br />
                    Recomendamos la lectura de la memoria si quieres una visión detallada del proyecto SecurAI, aparte de la lectura del README.md que puedes encontrar en la página principal del repositorio.
                    </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-2">
            <AccordionTrigger>¿Cómo actualizo la verión de SecurAI?</AccordionTrigger>
            <AccordionContent>
                Ahora mismo, la manera más segura de actualizar SecurAI es eliminando de tu equipo la versión que tengas, e instalar
                <a 
                    href="https://github.com/Valeaal/SecurAI/releases/latest" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    style={{textDecoration: 'underline', marginLeft: '4px' }}
                >
                    la última versión.
                </a>. <br />
                La última versión siempre será la que tenga mejores funciones, y un funcionamiento más pulido. Recuerda que SecurAI es un proyecto open-source de recursos limitados.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-3">
            <AccordionTrigger>Tengo algunos problemas con SecurAI, ¿cómo puedos solucionarlos?</AccordionTrigger>
            <AccordionContent>
             Te recomendamos que accedeas a la
                <a 
                    href="https://github.com/Valeaal/SecurAI?tab=readme-ov-file#resolución-de-problemas" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    style={{textDecoration: 'underline', marginLeft: '4px' }}
                >
                    sección de solución de problemas
                </a> del README.md del repositorio del proyecto. <br />
                Si no encuentras la solución que buscas, puedes abrir una issue en el repositorio para que podamos ayudarte en la medida de lo posible, recuerda que SecurAI es un proyecto open-source de recursos limitados.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-4">
            <AccordionTrigger>¿Cómo puedo personalizar SecurAI?</AccordionTrigger>
            <AccordionContent>
              Si eres desarrollador y deseas agregar un nuevo módulo de detección en SecurAI, o si quieres modificar su comportamiento, el proceso es fácil y sencillo. Hemos diseñado la arquitectura para que los nuevos módulos se integren sin dificultad, y la documentación está disponible para guiarte paso a paso en la creación de nuevos módulos, o para cambiar cualquier componente que desees. <br></br>
              Te recomendamos encarecidamente que leas toda la memoria disponible en el 
              <a 
                href="https://github.com/Valeaal/SecurAI" 
                target="_blank" 
                rel="noopener noreferrer" 
                style={{textDecoration: 'underline', marginLeft: '4px' }}
            >
                repositorio de GitHub
            </a> antes de hacer ningún cambio, para comprender en profundiad el complejo funcionamiento de SecurAI. <br />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </div>
  );
}
