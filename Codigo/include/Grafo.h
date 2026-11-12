#ifndef GRAFO_H
#define GRAFO_H

#include <climits>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <string>
#include <vector>

#include "List.h"

// Umbrales fisiologicos/microbiologicos para cachama de rio a ~27-30 C sin cadena de frio:
// <= 360 min (6 h): frescura optima
// 360..480 min (6-8 h): alerta bacteriana (mesofilas / rigor mortis)
// > 480 min (8 h): deterioro critico (no apto comercialmente sin frio)
constexpr int UMBRAL_OPTIMO_MIN = 360;
constexpr int UMBRAL_CRITICO_MIN = 480;

struct NodoInfo {
    std::string id;
    std::string nombre;
    std::string tipo;      // P, A, D, H, M, F, V
    std::string cuenca;
    int reportes = 0;
    bool tieneFrio = false;
    std::string observacion;
};

struct ResultadoBFS {
    std::string origen;
    std::string objetivoEncontrado;
    std::string tipoObjetivo;
    int saltos = -1;
    int tiempoRutaMin = 0;
    int tiempoSinFrioMin = 0;
    int distanciaKm = 0;
    bool alcanzado = false;
    std::vector<std::string> ruta;
    std::vector<std::string> ordenVisita;
};

struct RutaEvaluada {
    std::vector<std::string> nodos;
    int saltos = 0;
    int tiempoTotalMin = 0;
    int tiempoSinFrioMin = 0;
    int distanciaKm = 0;
    bool pasaPorDeterioro = false;
    bool encontroFrio = false;
    std::string primerNodoFrio;
    std::string estadoCachama; // OPTIMO, ALERTA_BACTERIANA, DETERIORO_CRITICO
};

template <class T>
class Vertex;

// =====================================================
// CLASE EDGE (Arista dirigida ponderada)
// =====================================================
template <class T>
class Edge {
public:
    Vertex<T>* to;
    int weight;        // Tiempo de traslado en minutos
    int distanciaKm;   // Distancia estimada en km
    std::string medio; // Fluvial_Canoa o Terrestre_Camion

    friend std::ostream& operator<<(std::ostream& out, Edge<T>* edge) {
        out << "-> " << edge->to->data
            << " (" << edge->weight << " min, "
            << edge->distanciaKm << " km, "
            << edge->medio << ")";
        return out;
    }
};

// =====================================================
// CLASE VERTEX (Vertice del grafo)
// =====================================================
template <class T>
class Vertex {
public:
    T data;
    int inDegree;
    int outDegree;
    List<Edge<T>*> connectedTo;
    Vertex<T>* predecessor;
    int distance;
    char color; // 'w' = no visitado, 'g' = en cola/pila, 'b' = procesado

    Vertex(const T& value);
    ~Vertex();
    void addNeighbor(Vertex<T>* to, int weight = 0, int distanciaKm = 0, const std::string& medio = "Fluvial_Canoa");
    int getWeight(const T& value);
};

// =====================================================
// CLASE GRAPH (Grafo dirigido con Lista de Adyacencia)
// =====================================================
template <class T>
class Graph {
private:
    void dfsRecursivo(
        Vertex<T>* actual,
        const std::set<T>& destinos,
        std::set<T>& enCamino,
        std::vector<T>& rutaActual,
        int tiempoAcumulado,
        int tiempoSinFrio,
        int distanciaAcumulada,
        bool frioActivo,
        const std::string& primerFrio,
        bool pasoDeterioro,
        std::vector<RutaEvaluada>& resultados
    ) const;

public:
    int count;
    List<Vertex<T>*> vertexList;
    std::map<T, Vertex<T>*> lookup;
    std::map<T, NodoInfo> metadata;

    Graph();
    ~Graph();

    Vertex<T>* addVertex(const T& value);
    Vertex<T>* getVertex(const T& value) const;
    void addEdge(const T& from, const T& to, int weight = 0, int distanciaKm = 0, const std::string& medio = "Fluvial_Canoa");

    bool cargarDesdeArchivo(const std::string& rutaArchivo);
    void resetRecorrido();
    void imprimirListaAdyacencia() const;

    ResultadoBFS bfsObjetivo(const T& origen, const std::set<std::string>& tiposObjetivo, bool exigirFrio);
    std::vector<RutaEvaluada> dfsTodasLasRutas(const T& origen, const std::set<T>& destinos) const;
    std::vector<T> obtenerPuntosPesca() const;
    NodoInfo obtenerInfo(const T& id) const;
};

std::string clasificarDeterioro(int tiempoSinFrioMin);

#endif
