"use client"

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
import { useRouter } from "next/navigation"
import { HelpCircle, ShieldAlert, BarChart2 } from "lucide-react";

// Definición de ListItem en JavaScript (sin tipos)
const ListItem = React.forwardRef(({ className, title, children, ...props }, ref) => {
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
          <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
            {children}
          </p>
        </a>
      </NavigationMenuLink>
    </li>
  );
});
ListItem.displayName = "ListItem";

export default function NavBar() {
  return (
    <header className="w-full p-4">
      <div className="flex flex-col md:flex-row items-center justify-between">
        <h1 className="text-2xl font-bold text-textG1 mb-4 md:mb-0">
          SecurAI
        </h1>

        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuLink href="/" className={navigationMenuTriggerStyle()}>
              Inicio
            </NavigationMenuLink>

            {/* Menú de Estadísticas de la Red */}
            <NavigationMenuItem>
              <NavigationMenuTrigger>Estadísticas de la red</NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid gap-3 p-4 md:w-[400px] lg:w-[450px] lg:grid-cols-[.75fr_1fr]">
                  <li className="row-span-3">
                    <div className="flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-muted/50 to-muted p-6 no-underline outline-none focus:shadow-md">
                      <BarChart2 className="h-6 w-6 text-textP1" />
                      <div className="mb-2 mt-4 text-lg font-medium">
                        Estadísticas de la red
                      </div>
                      <p className="text-sm leading-tight text-muted-foreground">
                        Estadísticas generales
                      </p>
                    </div>
                  </li>
                  <ListItem href="/network-statistics/traffic" title="Tráfico de red">
                    Datos sobre el tráfico de red, incluyendo las velocidades y el ancho de banda utilizado.
                  </ListItem>
                  <ListItem href="/network-statistics/errors" title="Errores de red">
                    Información detallada sobre los errores de red y los posibles problemas de conectividad.
                  </ListItem>
                  <ListItem href="/network-statistics/latency" title="Latencia de la red">
                    Estadísticas sobre la latencia de la red y cómo puede afectar al rendimiento del sistema.
                  </ListItem>
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>

            {/* Menú de Simulaciones de Ataque */}
            <NavigationMenuItem>
              <NavigationMenuTrigger>Simulaciones de ataque</NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid gap-3 p-4 md:w-[400px] lg:w-[600px] lg:grid-cols-[.75fr_1fr]">
                  <li className="row-span-3">
                    <div className="flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-muted/50 to-muted p-6 no-underline outline-none focus:shadow-md">
                      <ShieldAlert className="h-6 w-6 text-textP1" />
                      <div className="mb-2 mt-4 text-lg font-medium">
                        Simulaciones de ataque
                      </div>
                      <p className="text-sm leading-tight text-muted-foreground">
                        Simula ataques de red para evaluar la seguridad.
                      </p>
                    </div>
                  </li>
                  <ListItem href="/attack-simulations/arp-spoofing" title="ARP Spoofing">
                    Prueba la resistencia del sistema contra ataques de suplantación de direcciones MAC.
                  </ListItem>
                  <ListItem href="/attack-simulations/dos" title="Ataque DoS">
                    Simula un ataque de denegación de servicio para analizar la respuesta del sistema.
                  </ListItem>
                  <ListItem href="/attack-simulations/mitm" title="Man-in-the-Middle">
                    Prueba la detección de ataques de intermediario en la comunicación de red.
                  </ListItem>
                  <ListItem href="/attack-simulations/port-scanning" title="Escaneo de Puertos">
                    Simula un escaneo de puertos para detectar vulnerabilidades en la red.
                  </ListItem>
                  <ListItem href="/attack-simulations/dns-spoofing" title="DNS Spoofing">
                    Prueba ataques de falsificación de DNS y su impacto en la seguridad.
                  </ListItem>
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
                        Encuentra respuestas a las preguntas más frecuentes sobre el funcionamiento y el uso de SecurAI.<br></br> Centrado en el usuario: los desarrolladores deben de consultar la documentación.
                      </p>
                    </div>
                  </li>
                  <ListItem href="/help/detectionHelp" title="Ámbito de detección">
                    ¿Qué tipo de ataques puede prevenir SecurAI?
                  </ListItem>
                  <ListItem href="/help/bufferHelp" title="Cola de mensajes">
                    El buffer de paquetes de red es el elemento central de SecurAI
                  </ListItem>
                  <ListItem href="/help/moduleHelp" title="Módulos de detección">
                    Los módulos consultan la cola de paquetes para buscar amenazas en tu red
                  </ListItem>
                  <ListItem href="/help/objeto3" title="HUECO LIBRE">
                    Hueco libre
                  </ListItem>
                  <ListItem href="/help/advanced-settings" title="HUECO LIBRE">
                    Hueco libre
                  </ListItem>
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>

            <NavigationMenuLink className={navigationMenuTriggerStyle()}>
              Créditos
            </NavigationMenuLink>
          </NavigationMenuList>
        </NavigationMenu>
      </div>
    </header>
  );
}
