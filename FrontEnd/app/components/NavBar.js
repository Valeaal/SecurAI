import * as React from "react";

import { HelpCircle } from "lucide-react";
import { BarChart2 } from "lucide-react";

import { cn } from "@/lib/utils";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";

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
            <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
              {children}
            </p>
          </a>
        </NavigationMenuLink>
      </li>
    );
  }
);
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
            <NavigationMenuLink className={navigationMenuTriggerStyle()}>
              Inicio
            </NavigationMenuLink>

            <NavigationMenuItem>
              <NavigationMenuTrigger>Estadísticas de la red</NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid gap-3 p-4 md:w-[400px] lg:w-[450px] lg:grid-cols-[.75fr_1fr]">
                  <li className="row-span-3">
                    <div className="flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-muted/50 to-muted p-6 no-underline outline-none focus:shadow-md">
                      <HelpCircle className="h-6 w-6 text-textP1" />
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

            <NavigationMenuItem>
              <NavigationMenuTrigger>Ayuda</NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid gap-3 p-4 md:w-[400px] lg:w-[450px] lg:grid-cols-[.75fr_1fr]">
                  <li className="row-span-3">
                    <div className="flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-muted/50 to-muted p-6 no-underline outline-none focus:shadow-md">
                      <HelpCircle className="h-6 w-6 text-textP1" />
                      <div className="mb-2 mt-4 text-lg font-medium">
                        Centro de Ayuda
                      </div>
                      <p className="text-sm leading-tight text-muted-foreground">
                        Encuentra respuestas a las preguntas más frecuentes sobre el sistema.
                      </p>
                    </div>
                  </li>
                  <ListItem href="/help/objeto1" title="Objeto 1">
                    Explicación detallada sobre el Objeto 1 y su funcionamiento en el sistema.
                  </ListItem>
                  <ListItem href="/help/objeto2" title="Objeto 2">
                    Información útil sobre el Objeto 2 y cómo interactúa con otros módulos.
                  </ListItem>
                  <ListItem href="/help/objeto3" title="Objeto 3">
                    Guía de uso del Objeto 3 y sus principales características.
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
