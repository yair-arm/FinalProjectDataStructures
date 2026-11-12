#include <fstream>
#include <iomanip>
#include <iostream>
#include <set>
#include <string>
#include <vector>

#include "Grafo.h"

using namespace std;

namespace {
void imprimirRuta(const vector<string>& ruta) {
    for (size_t i = 0; i < ruta.size(); i++) {
        cout << ruta[i];
        if (i + 1 < ruta.size()) cout << " -> ";
    }
}

struct ResumenPunto {
    string punto;
    string cuenca;
    int reportes = 0;
    int saltosBFSActual = -1;
    int tiempoSinFrioBFSActual = 0;
    string primerFrioActual;
    int mejorSinFrioDFSActual = 0;
    string estadoDFSActual;
    int totalRutasActual = 0;
    int rutasOptActual = 0;

    int saltosBFSOpt = -1;
    int tiempoSinFrioBFSOpt = 0;
    string primerFrioOpt;
    int mejorSinFrioDFSOpt = 0;
    string estadoDFSOpt;
    int totalRutasOpt = 0;
    int rutasOptOpt = 0;
};

void resolverIncognita1BFS(Graph<string>& grafo, const string& nombreEscenario) {
    cout << "\n------------------------------------------------------------------------" << endl;
    cout << "INCOGNITA 1 (BFS): Punto con Red de Frio (A/F/V) mas cercano en saltos" << endl;
    cout << "Escenario: " << nombreEscenario << endl;
    cout << "------------------------------------------------------------------------" << endl;

    vector<string> puntos = grafo.obtenerPuntosPesca();
    set<string> objetivosFrio = {"A", "F", "V"};

    cout << left << setw(22) << "Punto de Pesca"
         << setw(8) << "Saltos"
         << setw(24) << "Primer Nodo con Frio"
         << setw(14) << "T.SinFrio(m)"
         << setw(18) << "Estado Cachama"
         << "Ruta BFS" << endl;

    for (const string& p : puntos) {
        ResultadoBFS r = grafo.bfsObjetivo(p, objetivosFrio, true);
        cout << left << setw(22) << p;
        if (r.alcanzado) {
            cout << setw(8) << r.saltos
                 << setw(24) << r.objetivoEncontrado
                 << setw(14) << r.tiempoSinFrioMin
                 << setw(18) << clasificarDeterioro(r.tiempoSinFrioMin);
            imprimirRuta(r.ruta);
            cout << endl;
        } else {
            cout << setw(8) << "N/A"
                 << setw(24) << "SIN COBERTURA"
                 << setw(14) << "-"
                 << setw(18) << "DETERIORO_CRITICO"
                 << "Sin ruta a frio" << endl;
        }
    }
}

void resolverIncognita2DFS(const Graph<string>& grafo, const string& nombreEscenario, const string& puntoEspecifico = "") {
    cout << "\n------------------------------------------------------------------------" << endl;
    cout << "INCOGNITA 2 (DFS): Rutas completas hacia mercados y riesgo de deterioro" << endl;
    cout << "Escenario: " << nombreEscenario << " | Especie: Cachama de rio (optimo <=360m, critico >480m)" << endl;
    cout << "------------------------------------------------------------------------" << endl;

    set<string> destinosFinales = {"Puerto_Gaitan", "Puerto_Lopez", "Villavicencio", "Bogota"};
    vector<string> puntos = puntoEspecifico.empty() ? grafo.obtenerPuntosPesca() : vector<string>{puntoEspecifico};

    for (const string& p : puntos) {
        vector<RutaEvaluada> rutas = grafo.dfsTodasLasRutas(p, destinosFinales);
        if (rutas.empty()) {
            cout << " * " << p << ": Sin rutas registradas hacia mercados." << endl;
            continue;
        }
        int optimas = 0, alertas = 0, criticas = 0;
        for (const auto& r : rutas) {
            if (r.estadoCachama == "OPTIMO") optimas++;
            else if (r.estadoCachama == "ALERTA_BACTERIANA") alertas++;
            else criticas++;
        }

        const RutaEvaluada& mejor = rutas.front();
        const RutaEvaluada& peor = rutas.back();
        cout << " * " << p << " (Rutas=" << rutas.size()
             << " | Optimas=" << optimas
             << ", Alerta=" << alertas
             << ", Criticas=" << criticas << ")" << endl;
        cout << "   Mejor ruta: sinFrio=" << mejor.tiempoSinFrioMin << " min, total="
             << mejor.tiempoTotalMin << " min [" << mejor.estadoCachama << "] -> ";
        imprimirRuta(mejor.nodos);
        cout << endl;

        if (!puntoEspecifico.empty()) {
            cout << "   Detalle de todas las rutas DFS (" << rutas.size() << "):" << endl;
            for (size_t k = 0; k < rutas.size(); k++) {
                cout << "     " << setw(2) << (k + 1) << ") sinFrio=" << setw(3) << rutas[k].tiempoSinFrioMin
                     << " min | total=" << setw(3) << rutas[k].tiempoTotalMin
                     << " min | " << setw(18) << rutas[k].estadoCachama
                     << " | 1erFrio=" << setw(20) << rutas[k].primerNodoFrio << " | ";
                imprimirRuta(rutas[k].nodos);
                cout << endl;
            }
        } else if (peor.tiempoSinFrioMin != mejor.tiempoSinFrioMin) {
            cout << "   Peor ruta:  sinFrio=" << peor.tiempoSinFrioMin << " min, total="
                 << peor.tiempoTotalMin << " min [" << peor.estadoCachama << "] -> ";
            imprimirRuta(peor.nodos);
            cout << endl;
        }
    }
}

vector<ResumenPunto> generarComparativa(Graph<string>& actual, Graph<string>& optimizada, const string& rutaCsv) {
    set<string> objetivosFrio = {"A", "F", "V"};
    set<string> mercadosPrincipales = {"Puerto_Gaitan", "Puerto_Lopez", "Villavicencio", "Bogota"};
    vector<string> puntos = actual.obtenerPuntosPesca();
    vector<ResumenPunto> tabla;

    for (const string& p : puntos) {
        ResumenPunto row;
        NodoInfo info = actual.obtenerInfo(p);
        row.punto = p;
        row.cuenca = info.cuenca;
        row.reportes = info.reportes;

        ResultadoBFS bfsA = actual.bfsObjetivo(p, objetivosFrio, true);
        row.saltosBFSActual = bfsA.alcanzado ? bfsA.saltos : -1;
        row.tiempoSinFrioBFSActual = bfsA.tiempoSinFrioMin;
        row.primerFrioActual = bfsA.alcanzado ? bfsA.objetivoEncontrado : "NINGUNO";

        auto dfsA = actual.dfsTodasLasRutas(p, mercadosPrincipales);
        row.totalRutasActual = static_cast<int>(dfsA.size());
        for (const auto& r : dfsA) {
            if (r.estadoCachama == "OPTIMO") row.rutasOptActual++;
        }
        row.mejorSinFrioDFSActual = dfsA.empty() ? 999 : dfsA.front().tiempoSinFrioMin;
        row.estadoDFSActual = dfsA.empty() ? "SIN_RUTA" : dfsA.front().estadoCachama;

        ResultadoBFS bfsO = optimizada.bfsObjetivo(p, objetivosFrio, true);
        row.saltosBFSOpt = bfsO.alcanzado ? bfsO.saltos : -1;
        row.tiempoSinFrioBFSOpt = bfsO.tiempoSinFrioMin;
        row.primerFrioOpt = bfsO.alcanzado ? bfsO.objetivoEncontrado : "NINGUNO";

        auto dfsO = optimizada.dfsTodasLasRutas(p, mercadosPrincipales);
        row.totalRutasOpt = static_cast<int>(dfsO.size());
        for (const auto& r : dfsO) {
            if (r.estadoCachama == "OPTIMO") row.rutasOptOpt++;
        }
        row.mejorSinFrioDFSOpt = dfsO.empty() ? 999 : dfsO.front().tiempoSinFrioMin;
        row.estadoDFSOpt = dfsO.empty() ? "SIN_RUTA" : dfsO.front().estadoCachama;

        tabla.push_back(row);
    }

    ofstream out(rutaCsv);
    if (out.is_open()) {
        out << "punto,cuenca,reportes,saltos_bfs_actual,tiempo_sin_frio_bfs_actual,primer_frio_actual,"
            << "mejor_sin_frio_dfs_actual,estado_dfs_actual,rutas_totales_actual,rutas_optimas_actual,"
            << "saltos_bfs_opt,tiempo_sin_frio_bfs_opt,primer_frio_opt,"
            << "mejor_sin_frio_dfs_opt,estado_dfs_opt,rutas_totales_opt,rutas_optimas_opt,reduccion_tiempo_pct\n";
        for (const auto& r : tabla) {
            double red = 0.0;
            if (r.tiempoSinFrioBFSActual > 0) {
                red = 100.0 * (r.tiempoSinFrioBFSActual - r.tiempoSinFrioBFSOpt) / static_cast<double>(r.tiempoSinFrioBFSActual);
            }
            out << r.punto << "," << r.cuenca << "," << r.reportes << ","
                << r.saltosBFSActual << "," << r.tiempoSinFrioBFSActual << "," << r.primerFrioActual << ","
                << r.mejorSinFrioDFSActual << "," << r.estadoDFSActual << "," << r.totalRutasActual << "," << r.rutasOptActual << ","
                << r.saltosBFSOpt << "," << r.tiempoSinFrioBFSOpt << "," << r.primerFrioOpt << ","
                << r.mejorSinFrioDFSOpt << "," << r.estadoDFSOpt << "," << r.totalRutasOpt << "," << r.rutasOptOpt << ","
                << fixed << setprecision(2) << red << "\n";
        }
        out.close();
    }

    cout << "\n========================================================================" << endl;
    cout << "COMPARATIVA GLOBAL: RED ACTUAL VS RED OPTIMIZADA (3 CENTROS A+F)" << endl;
    cout << "========================================================================" << endl;
    cout << left << setw(22) << "Punto de Pesca"
         << setw(14) << "BFS Actual"
         << setw(14) << "BFS Optim."
         << setw(16) << "SinFrio Act(m)"
         << setw(16) << "SinFrio Opt(m)"
         << setw(12) << "Mejora (%)" << endl;

    double sumaAct = 0.0, sumaOpt = 0.0;
    int puntosCritActual = 0, puntosCritOpt = 0;
    int totalRutasAct = 0, optRutasAct = 0, totalRutasOpt = 0, optRutasOpt = 0;

    for (const auto& r : tabla) {
        double red = 0.0;
        if (r.tiempoSinFrioBFSActual > 0) {
            red = 100.0 * (r.tiempoSinFrioBFSActual - r.tiempoSinFrioBFSOpt) / static_cast<double>(r.tiempoSinFrioBFSActual);
        }
        sumaAct += r.tiempoSinFrioBFSActual;
        sumaOpt += r.tiempoSinFrioBFSOpt;
        if (r.tiempoSinFrioBFSActual > UMBRAL_OPTIMO_MIN) puntosCritActual++;
        if (r.tiempoSinFrioBFSOpt > UMBRAL_OPTIMO_MIN) puntosCritOpt++;
        totalRutasAct += r.totalRutasActual;
        optRutasAct += r.rutasOptActual;
        totalRutasOpt += r.totalRutasOpt;
        optRutasOpt += r.rutasOptOpt;

        cout << left << setw(22) << r.punto
             << setw(14) << (to_string(r.saltosBFSActual) + " saltos")
             << setw(14) << (to_string(r.saltosBFSOpt) + " saltos")
             << setw(16) << r.tiempoSinFrioBFSActual
             << setw(16) << r.tiempoSinFrioBFSOpt
             << fixed << setprecision(1) << red << "%" << endl;
    }

    double promAct = sumaAct / tabla.size();
    double promOpt = sumaOpt / tabla.size();
    double mejoraProm = 100.0 * (promAct - promOpt) / promAct;

    cout << "\nRESUMEN CUANTITATIVO:" << endl;
    cout << " - Puntos de pesca evaluados: " << tabla.size() << endl;
    cout << " - Tiempo medio sin frio (BFS hacia 1er frio): Actual = " << fixed << setprecision(1) << promAct
         << " min vs Optimizada = " << promOpt << " min (Reduccion = " << mejoraProm << "%)" << endl;
    cout << " - Puntos con riesgo de deterioro (>360 min) en ruta minima BFS: Actual = "
         << puntosCritActual << "/" << tabla.size() << " vs Optimizada = " << puntosCritOpt << "/" << tabla.size() << endl;
    cout << " - Rutas DFS totales en estado OPTIMO (<=360 min sin frio): Actual = "
         << optRutasAct << "/" << totalRutasAct << " (" << (100.0 * optRutasAct / totalRutasAct)
         << "%) vs Optimizada = " << optRutasOpt << "/" << totalRutasOpt
         << " (" << (100.0 * optRutasOpt / totalRutasOpt) << "%)" << endl;
    cout << " - CSV exportado en: " << rutaCsv << endl;

    return tabla;
}
} // namespace

int main(int argc, char* argv[]) {
    Graph<string> redActual;
    Graph<string> redOptimizada;

    if (!redActual.cargarDesdeArchivo("data/red_actual.txt") ||
        !redOptimizada.cargarDesdeArchivo("data/red_optimizada.txt")) {
        cerr << "Verifique que ejecuta el programa desde la carpeta Codigo/." << endl;
        return 1;
    }

    bool modoBatch = (argc > 1 && string(argv[1]) == "--batch");
    if (modoBatch) {
        cout << "=== PROYECTO FINAL ESTRUCTURAS DE DATOS - RED PESQUERA PUERTO GAITAN ===" << endl;
        cout << "\n[1] LISTA DE ADYACENCIA - RED ACTUAL\n";
        redActual.imprimirListaAdyacencia();

        cout << "\n[2] LISTA DE ADYACENCIA - RED OPTIMIZADA\n";
        redOptimizada.imprimirListaAdyacencia();

        resolverIncognita1BFS(redActual, "RED ACTUAL (Sin centros de frio en cuencas)");
        resolverIncognita1BFS(redOptimizada, "RED OPTIMIZADA (3 Centros A+F estrategicos)");

        resolverIncognita2DFS(redActual, "RED ACTUAL");
        resolverIncognita2DFS(redOptimizada, "RED OPTIMIZADA");

        generarComparativa(redActual, redOptimizada, "data/comparativa_resultados.csv");
        return 0;
    }

    int opcion = -1;
    do {
        cout << "\n========================================================================" << endl;
        cout << " SISTEMA DE OPTIMIZACION DE ACOPIO PESQUERO (PUERTO GAITAN - META)" << endl;
        cout << "========================================================================" << endl;
        cout << " 1. Imprimir Lista de Adyacencia (Red Actual)" << endl;
        cout << " 2. Imprimir Lista de Adyacencia (Red Optimizada)" << endl;
        cout << " 3. Resolver Incognita 1 (BFS - Centro de Frio mas cercano)" << endl;
        cout << " 4. Resolver Incognita 2 (DFS - Todas las rutas y deterioro Cachama)" << endl;
        cout << " 5. Consultar rutas DFS detalladas de un punto de pesca especifico" << endl;
        cout << " 6. Comparativa Global Antes vs Despues y exportar CSV" << endl;
        cout << " 0. Salir" << endl;
        cout << "Seleccione una opcion: ";
        if (!(cin >> opcion)) break;

        switch (opcion) {
            case 1:
                redActual.imprimirListaAdyacencia();
                break;
            case 2:
                redOptimizada.imprimirListaAdyacencia();
                break;
            case 3:
                resolverIncognita1BFS(redActual, "RED ACTUAL");
                resolverIncognita1BFS(redOptimizada, "RED OPTIMIZADA");
                break;
            case 4:
                resolverIncognita2DFS(redActual, "RED ACTUAL");
                resolverIncognita2DFS(redOptimizada, "RED OPTIMIZADA");
                break;
            case 5: {
                vector<string> puntos = redActual.obtenerPuntosPesca();
                cout << "\nPuntos disponibles:" << endl;
                for (size_t i = 0; i < puntos.size(); i++) {
                    cout << "  " << (i + 1) << ". " << puntos[i] << endl;
                }
                cout << "Ingrese el numero del punto: ";
                size_t idx = 0;
                cin >> idx;
                if (idx >= 1 && idx <= puntos.size()) {
                    resolverIncognita2DFS(redActual, "RED ACTUAL", puntos[idx - 1]);
                    resolverIncognita2DFS(redOptimizada, "RED OPTIMIZADA", puntos[idx - 1]);
                } else {
                    cout << "Seleccion invalida." << endl;
                }
                break;
            }
            case 6:
                generarComparativa(redActual, redOptimizada, "data/comparativa_resultados.csv");
                break;
            case 0:
                cout << "Finalizando sistema..." << endl;
                break;
            default:
                cout << "Opcion no valida." << endl;
                break;
        }
    } while (opcion != 0);

    return 0;
}
