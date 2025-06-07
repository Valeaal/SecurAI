"use client";

import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Switch } from "@/components/ui/switch";
import { HelpCircle, ShieldAlert, BarChart2 } from "lucide-react";

// Definición de ListItem en JavaScript (sin tipos)
const ListItem = React.forwardRef(
  ({ className, title, children, ...props }, ref) => {
    return (
      <li>
        <NavigationMenuLink asChild>
          <a
            ref={ref}
            className={cn(
              "block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-gradient-to-b hover:from-muted/50 hover:to-muted focus:bg-gradient-to-b focus:from-muted/50 focus:to-muted focus:text-textP1",
              className
            )}
            {...props}
          >
            <div className="text-sm font-medium leading-none">{title}</div>
            <div className="line-clamp-2 text-sm leading-snug text-muted-foreground">
              {children}
            </div>
          </a>
        </NavigationMenuLink>
      </li>
    );
  }
);
ListItem.displayName = "ListItem";

// ListItemWithSwitch con uso de localStorage para persistencia
const ListItemWithSwitch = ({ title, description }) => {
  // Obtener el estado del switch desde localStorage o establecerlo en false si no existe
  const storedState = typeof window !== "undefined" ? localStorage.getItem(title) : null;
  const [isActive, setIsActive] = React.useState(
    storedState ? JSON.parse(storedState) : false
  );

  const handleToggle = () => {
    const newState = !isActive;
    setIsActive(newState);
    
    // Guardar el nuevo estado en localStorage
    if (typeof window !== "undefined") {
      localStorage.setItem(title, JSON.stringify(newState));
    }
    
    // Realizar la solicitud HTTP al cambiar el estado
    fetch("http://localhost:4000/loadAttackTests/startOrStop", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        attackName: title,
        isActive: newState,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Respuesta de la API:", data);
      })
      .catch((error) => {
        console.error("Error al hacer la solicitud:", error);
      });
  };

  return (
    <ListItem title={title}>
      <div className="flex items-center justify-between">
        <span className="line-clamp-2 mr-1 text-sm leading-snug text-muted-foreground">
          {description}
        </span>
        <Switch checked={isActive} onCheckedChange={handleToggle} />
      </div>
    </ListItem>
  );
};

export default function NavBar() {
  return (
    <header className="w-full p-4">
      <div className="flex flex-col md:flex-row items-center justify-between">
        <h1 className="text-2xl font-bold text-textG1 mb-4 md:mb-0">SecurAI</h1>

        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuLink
              href="/"
              className={navigationMenuTriggerStyle()}
            >
              Inicio
            </NavigationMenuLink>

            {/* Menú de Estadísticas de la Red */}
            <NavigationMenuItem>
              <NavigationMenuTrigger>
                Estadísticas de la red
              </NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid gap-3 p-4 md:w-[400px] lg:w-[450px] lg:grid-cols-[.75fr_1fr]">
                  <li className="row-span-3">
                    <div className="flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-muted/50 to-muted p-6 no-underline outline-none focus:shadow-md">
                      <BarChart2 className="h-6 w-6 text-textP1" />
                      <div className="mb-2 mt-4 text-lg font-medium">
                        Estadísticas de la red
                      </div>
                      <p className="text-sm leading-tight text-muted-foreground">
                        Estadísticas generales sobre la red y los paquetes que
                        le llegan a tu ordenador.
                      </p>
                    </div>
                  </li>
                  <div className="row-span-3 flex flex-col justify-center gap-4">
                    <ListItem href="/netStats/numberStats" title="Número de paquetes" className="flex-grow">
                      Información de la evolución del número de paquetes recibidos
                    </ListItem>
                    <ListItem href="/netStats/typeStats" title="Tipos de paquetes" className="flex-grow">
                      Clasificación de los tipos de paquetes (última capa)
                    </ListItem>
                  </div>
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>

            {/* Menú de Simulaciones de Ataque */}
            <NavigationMenuItem>
              <NavigationMenuTrigger>
                Simulaciones de ataque
              </NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid gap-3 p-4 md:w-[400px] lg:w-[600px] lg:grid-cols-[.75fr_1fr]">
                  <li className="row-span-3">
                    <div className="flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-muted/50 to-muted p-6 no-underline outline-none focus:shadow-md">
                      <ShieldAlert className="h-6 w-6 text-textP1" />
                      <div className="mb-2 mt-4 text-lg font-medium">
                        Simulaciones de ataque
                      </div>
                      <p className="text-sm leading-tight text-muted-foreground">
                        Simula ataques de red para evaluar la detección y la seguridad de los módulos que has activado.
                      </p>
                    </div>
                  </li>
                  <ListItemWithSwitch 
                    title="arpFlooding" 
                    description="Ataque no muy agresivo de desbordamiento de ARP" 
                  />
                  <ListItemWithSwitch 
                    title="tcpSYN" 
                    description="Denegación de servicio abriendo demasiadas conexiones TCP"
                  />
                  <ListItemWithSwitch 
                    title="dnsAmplification" 
                    description="Consulta masiva ANY a DNS para amplificar tráfico hacia víctima"
                  />
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>

            {/* Menú de Ayuda */}
            <NavigationMenuItem>
              <NavigationMenuTrigger>Ayuda</NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid gap-3 p-4 md:w-[400px] lg:w-[600px] lg:grid-cols-[.75fr_1fr]">
                  <li className="row-span-3">
                    <div className="flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-muted/50 to-muted p-6 no-underline outline-none focus:shadow-md">
                      <HelpCircle className="h-6 w-6 text-textP1" />
                      <div className="mb-2 mt-4 text-lg font-medium">
                        Centro de Ayuda
                      </div>
                      <p className="text-sm leading-tight text-muted-foreground">
                        Encuentra respuestas a las preguntas más frecuentes
                        sobre el funcionamiento y el uso de SecurAI.<br></br>{" "}
                        Centrado en el usuario: los desarrolladores deben de
                        consultar la documentación.
                      </p>
                    </div>
                  </li>
                  <ListItem href="/help/detectionHelp" title="Ámbito de detección">
                    ¿Qué tipo de ataques puede prevenir SecurAI?
                  </ListItem>
                  <ListItem href="/help/bufferHelp" title="Cola de mensajes">
                    El buffer de paquetes de red es el elemento central de
                    SecurAI
                  </ListItem>
                  <ListItem
                    href="/help/moduleHelp"
                    title="Módulos de detección"
                  >
                    Los módulos cogen paquetes de la cola para buscar amenazas en ellos
                  </ListItem>
                  <ListItem href="/help/statsHelp" title="Estadísticas">
                    ¿Qué miden esas métricas exactamente?
                  </ListItem>
                  <ListItem href="/help/moreHelp" title="Información detallada">
                    Solución de problemas, desarrollo de nuevos módulos, actualizaciones de SecurAI...
                  </ListItem>
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>

            <NavigationMenuLink
              href="/credits"
              className={navigationMenuTriggerStyle()}
            >
              Créditos
            </NavigationMenuLink>

          </NavigationMenuList>
        </NavigationMenu>
      </div>
    </header>
  );
}
