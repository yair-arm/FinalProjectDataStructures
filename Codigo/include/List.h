#ifndef LIST_H
#define LIST_H

#include <cassert>
#include <iostream>

// =====================================================
// ESTRUCTURA NODE (Nodo de la lista enlazada simple)
// =====================================================
template <typename T>
struct Node {
    T data;
    Node<T>* next;
};

// =====================================================
// CLASE LIST (Lista Enlazada Simple Genérica del Curso)
// =====================================================
template <typename T>
class List {
private:
    int count = 0;
    Node<T>* begin;
    Node<T>* makeNode(const T& value);
    void printReverseHelper(Node<T>* node) const;

public:
    List();
    ~List();

    void insert(int pos, const T& value);
    void erase(int pos);
    T& get(int pos) const;
    void clear();
    void print() const;
    void printReverse() const;
    int size() const;
};

#include "../src/List.cpp"

#endif
