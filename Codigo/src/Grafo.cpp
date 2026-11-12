#ifndef GRAFO_CPP
#define GRAFO_CPP

#include "Grafo.h"

#include <algorithm>
#include <fstream>
#include <iomanip>
#include <sstream>

std::string clasificarDeterioro(int tiempoSinFrioMin) {
    if (tiempoSinFrioMin <= UMBRAL_OPTIMO_MIN) {
        return "OPTIMO";
    }
    if (tiempoSinFrioMin <= UMBRAL_CRITICO_MIN) {
        return "ALERTA_BACTERIANA";
    }
    return "DETERIORO_CRITICO";
}

namespace {
std::vector<std::string> splitPipe(const std::string& linea) {
    std::vector<std::string> partes;
    std::stringstream ss(linea);
    std::string item;
    while (std::getline(ss, item, '|')) {
        partes.push_back(item);
    }
    return partes;
}

std::string trimLine(const std::string& s) {
    size_t ini = s.find_first_not_of(" \t\r\n");
    if (ini == std::string::npos) return "";
    size_t fin = s.find_last_not_of(" \t\r\n");
    return s.substr(ini, fin - ini + 1);
}
} // namespace

// =====================================================
// METODOS DE LA CLASE VERTEX
// =====================================================

template <class T>
Vertex<T>::Vertex(const T& value) {
    data = value;
    inDegree = 0;
    outDegree = 0;
    predecessor = nullptr;
    distance = INT_MAX;
    color = 'w';
}

template <class T>
Vertex<T>::~Vertex() {
    for (int i = 0; i < connectedTo.size(); i++) {
        delete connectedTo.get(i);
    }
}

template <class T>
void Vertex<T>::addNeighbor(Vertex<T>* to, int weight, int distanciaKm, const std::string& medio) {
    Edge<T>* temp = new Edge<T>;
    temp->to = to;
    temp->weight = weight;
    temp->distanciaKm = distanciaKm;
    temp->medio = medio;
    outDegree++;
    to->inDegree++;
    connectedTo.insert(connectedTo.size(), temp);
}

template <class T>
int Vertex<T>::getWeight(const T& value) {
    for (int i = 0; i < connectedTo.size(); i++) {
        Edge<T>* temp = connectedTo.get(i);
        if (temp->to->data == value) {
            return temp->weight;
        }
    }
    return -1;
}

// =====================================================
// METODOS DE LA CLASE GRAPH
// =====================================================

template <class T>
Graph<T>::Graph() : count(0) {}

template <class T>
Graph<T>::~Graph() {
    for (int i = 0; i < vertexList.size(); i++) {
        delete vertexList.get(i);
    }
}

template <class T>
Vertex<T>* Graph<T>::addVertex(const T& value) {
    Vertex<T>* existente = getVertex(value);
    if (existente != nullptr) {
        return existente;
    }
    Vertex<T>* newVertex = new Vertex<T>(value);
    vertexList.insert(vertexList.size(), newVertex);
    lookup[value] = newVertex;
    count++;
    return newVertex;
}

template <class T>
Vertex<T>* Graph<T>::getVertex(const T& value) const {
    auto it = lookup.find(value);
    if (it != lookup.end()) {
        return it->second;
    }
    return nullptr;
}

template <class T>
void Graph<T>::addEdge(const T& from, const T& to, int weight, int distanciaKm, const std::string& medio) {
    Vertex<T>* fromVertex = getVertex(from);
    if (!fromVertex) {
        fromVertex = addVertex(from);
    }
    Vertex<T>* toVertex = getVertex(to);
    if (!toVertex) {
        toVertex = addVertex(to);
    }
    fromVertex->addNeighbor(toVertex, weight, distanciaKm, medio);
}

template <class T>
bool Graph<T>::cargarDesdeArchivo(const std::string& rutaArchivo) {
    std::ifstream archivo(rutaArchivo);
    if (!archivo.is_open()) {
        std::cerr << "Error: no se pudo abrir el archivo de red: " << rutaArchivo << std::endl;
        return false;
    }

    std::string linea;
    while (std::getline(archivo, linea)) {
        linea = trimLine(linea);
        if (linea.empty() || linea[0] == '#') {
            continue;
        }
        std::vector<std::string> campos = splitPipe(linea);
        if (campos.empty()) continue;

        if (campos[0] == "N" && campos.size() >= 8) {
            NodoInfo info;
            info.id = campos[1];
            info.nombre = campos[2];
            info.tipo = campos[3];
            info.cuenca = campos[4];
            info.reportes = std::stoi(campos[5]);
            info.tieneFrio = (std::stoi(campos[6]) != 0);
            info.observacion = campos[7];
            metadata[info.id] = info;
            addVertex(info.id);
        } else if (campos[0] == "E" && campos.size() >= 6) {
            std::string origen = campos[1];
            std::string destino = campos[2];
            int tiempo = std::stoi(campos[3]);
            int distKm = std::stoi(campos[4]);
            std::string medio = campos[5];
            addEdge(origen, destino, tiempo, distKm, medio);
        }
    }
    archivo.close();
    return true;
}

template <class T>
void Graph<T>::resetRecorrido() {
    for (int i = 0; i < vertexList.size(); i++) {
        Vertex<T>* v = vertexList.get(i);
        v->color = 'w';
        v->distance = INT_MAX;
        v->predecessor = nullptr;
    }
}

template <class T>
NodoInfo Graph<T>::obtenerInfo(const T& id) const {
    auto it = metadata.find(id);
    if (it != metadata.end()) {
        return it->second;
    }
    return NodoInfo{id, id, "?", "Desconocida", 0, false, ""};
}

template <class T>
std::vector<T> Graph<T>::obtenerPuntosPesca() const {
    std::vector<T> puntos;
    for (int i = 0; i < vertexList.size(); i++) {
        Vertex<T>* v = vertexList.get(i);
        NodoInfo info = obtenerInfo(v->data);
        if (info.tipo == "P") {
            puntos.push_back(v->data);
        }
    }
    return puntos;
}

template <class T>
void Graph<T>::imprimirListaAdyacencia() const {
    std::cout << "========================================================================" << std::endl;
    std::cout << "LISTA DE ADYACENCIA DEL GRAFO (" << count << " vertices)" << std::endl;
    std::cout << "========================================================================" << std::endl;
    for (int i = 0; i < vertexList.size(); i++) {
        Vertex<T>* v = vertexList.get(i);
        NodoInfo info = obtenerInfo(v->data);
        std::cout << "[" << std::setw(2) << (i + 1) << "] " << v->data
                  << " | Tipo: " << info.tipo
                  << " | Frio: " << (info.tieneFrio ? "SI" : "NO")
                  << " | Rep: " << info.reportes
                  << " | Grados(in=" << v->inDegree << ", out=" << v->outDegree << ")"
                  << std::endl;
        if (v->connectedTo.size() == 0) {
            std::cout << "      -> NULL (nodo sumidero / mercado final)" << std::endl;
        } else {
            for (int j = 0; j < v->connectedTo.size(); j++) {
                Edge<T>* arista = v->connectedTo.get(j);
                std::cout << "      " << arista << std::endl;
            }
        }
    }
}

template <class T>
ResultadoBFS Graph<T>::bfsObjetivo(const T& origen, const std::set<std::string>& tiposObjetivo, bool exigirFrio) {
    ResultadoBFS res;
    res.origen = origen;

    Vertex<T>* inicio = getVertex(origen);
    if (!inicio) {
        return res;
    }

    resetRecorrido();
    inicio->color = 'g';
    inicio->distance = 0;
    inicio->predecessor = nullptr;

    std::queue<Vertex<T>*> cola;
    cola.push(inicio);

    Vertex<T>* encontrado = nullptr;

    while (!cola.empty()) {
        Vertex<T>* actual = cola.front();
        cola.pop();
        res.ordenVisita.push_back(actual->data);

        NodoInfo infoActual = obtenerInfo(actual->data);
        bool cumpleTipo = (tiposObjetivo.find(infoActual.tipo) != tiposObjetivo.end());
        bool cumpleFrio = (!exigirFrio || infoActual.tieneFrio);

        if (actual != inicio && cumpleTipo && cumpleFrio && encontrado == nullptr) {
            encontrado = actual;
            break;
        }

        for (int i = 0; i < actual->connectedTo.size(); i++) {
            Edge<T>* arista = actual->connectedTo.get(i);
            Vertex<T>* vecino = arista->to;
            if (vecino->color == 'w') {
                vecino->color = 'g';
                vecino->distance = actual->distance + 1;
                vecino->predecessor = actual;
                cola.push(vecino);
            }
        }
        actual->color = 'b';
    }

    if (encontrado != nullptr) {
        res.alcanzado = true;
        res.objetivoEncontrado = encontrado->data;
        res.tipoObjetivo = obtenerInfo(encontrado->data).tipo;
        res.saltos = encontrado->distance;

        std::vector<std::string> camino;
        Vertex<T>* cur = encontrado;
        while (cur != nullptr) {
            camino.push_back(cur->data);
            cur = cur->predecessor;
        }
        std::reverse(camino.begin(), camino.end());
        res.ruta = camino;

        bool frioPrevio = obtenerInfo(origen).tieneFrio;
        for (size_t i = 0; i + 1 < camino.size(); i++) {
            Vertex<T>* u = getVertex(camino[i]);
            for (int j = 0; j < u->connectedTo.size(); j++) {
                Edge<T>* e = u->connectedTo.get(j);
                if (e->to->data == camino[i + 1]) {
                    res.tiempoRutaMin += e->weight;
                    res.distanciaKm += e->distanciaKm;
                    if (!frioPrevio) {
                        res.tiempoSinFrioMin += e->weight;
                    }
                    if (obtenerInfo(camino[i + 1]).tieneFrio) {
                        frioPrevio = true;
                    }
                    break;
                }
            }
        }
    }

    return res;
}

template <class T>
void Graph<T>::dfsRecursivo(
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
) const {
    NodoInfo info = obtenerInfo(actual->data);
    bool frioAhora = frioActivo || info.tieneFrio;
    std::string nodoFrio = primerFrio;
    if (!frioActivo && info.tieneFrio) {
        nodoFrio = actual->data;
    }
    bool deterioroAhora = pasoDeterioro || (info.tipo == "D");

    if (rutaActual.size() > 1 && destinos.find(actual->data) != destinos.end()) {
        RutaEvaluada r;
        r.nodos = rutaActual;
        r.saltos = static_cast<int>(rutaActual.size()) - 1;
        r.tiempoTotalMin = tiempoAcumulado;
        r.tiempoSinFrioMin = tiempoSinFrio;
        r.distanciaKm = distanciaAcumulada;
        r.pasaPorDeterioro = deterioroAhora;
        r.encontroFrio = frioAhora;
        r.primerNodoFrio = nodoFrio.empty() ? "NINGUNO" : nodoFrio;
        r.estadoCachama = clasificarDeterioro(tiempoSinFrio);
        resultados.push_back(r);
    }

    for (int i = 0; i < actual->connectedTo.size(); i++) {
        Edge<T>* arista = actual->connectedTo.get(i);
        Vertex<T>* siguiente = arista->to;
        if (enCamino.find(siguiente->data) == enCamino.end()) {
            enCamino.insert(siguiente->data);
            rutaActual.push_back(siguiente->data);

            int nuevoSinFrio = frioAhora ? tiempoSinFrio : (tiempoSinFrio + arista->weight);
            dfsRecursivo(
                siguiente,
                destinos,
                enCamino,
                rutaActual,
                tiempoAcumulado + arista->weight,
                nuevoSinFrio,
                distanciaAcumulada + arista->distanciaKm,
                frioAhora,
                nodoFrio,
                deterioroAhora,
                resultados
            );

            rutaActual.pop_back();
            enCamino.erase(siguiente->data);
        }
    }
}

template <class T>
std::vector<RutaEvaluada> Graph<T>::dfsTodasLasRutas(const T& origen, const std::set<T>& destinos) const {
    std::vector<RutaEvaluada> resultados;
    Vertex<T>* inicio = getVertex(origen);
    if (!inicio) {
        return resultados;
    }

    std::set<T> enCamino;
    std::vector<T> rutaActual;
    enCamino.insert(origen);
    rutaActual.push_back(origen);

    dfsRecursivo(inicio, destinos, enCamino, rutaActual, 0, 0, 0, false, "", false, resultados);

    std::sort(resultados.begin(), resultados.end(), [](const RutaEvaluada& a, const RutaEvaluada& b) {
        if (a.tiempoSinFrioMin != b.tiempoSinFrioMin) {
            return a.tiempoSinFrioMin < b.tiempoSinFrioMin;
        }
        return a.tiempoTotalMin < b.tiempoTotalMin;
    });
    return resultados;
}

template class Edge<std::string>;
template class Vertex<std::string>;
template class Graph<std::string>;

#endif
